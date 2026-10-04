#!/usr/bin/env python3

"""Run the S1 protocol on the Underdoc dataset (local, cached, resumable).

Reuses Brown's workflow and metrics; leaves `brown_run_eval.py` untouched. Each repeat is a
separate Opik experiment (`<name>-r<i>`) and writes `outputs/s1/<name>-r<i>/scores.json`.
Generated articles and judge results are cached per sample, so a rerun skips finished items.
On persistent provider 429/5xx the run stops, keeps the cache and exits non-zero.
"""

import asyncio
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

import click
from loguru import logger

from brown.evals import s1

DEFAULT_DATASET_DIR = Path("inputs/evals/underdoc_dataset")
EXIT_PROVIDER_UNAVAILABLE = 75


def _config_fingerprint(config: Path) -> dict:
    return {"config": config.name, "config_sha": hashlib.sha256(config.read_bytes()).hexdigest()[:12]}


def _generate(sample_dir: Path, sample, work_dir: Path) -> str:
    """Run Brown's generate-article workflow for one sample (errors propagate, unlike the Opik task)."""
    from langchain_core.runnables.config import RunnableConfig

    from brown.builders import build_short_term_memory
    from brown.config_app import get_app_config
    from brown.workflows import build_generate_article_workflow

    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "article_guideline.md").write_text(sample.article_guideline, encoding="utf-8")
    (work_dir / "research.md").write_text(sample.research, encoding="utf-8")

    async def run() -> str:
        async with build_short_term_memory(get_app_config()) as checkpointer:
            workflow = build_generate_article_workflow(checkpointer=checkpointer)
            config = RunnableConfig(configurable={"thread_id": str(uuid.uuid4())})
            await workflow.ainvoke({"dir_path": work_dir}, config)
        return (work_dir / "article.md").read_text(encoding="utf-8")

    return asyncio.run(run())


def _judge(metric, sample, article: str) -> str:
    """Run one metric and return its aggregated criterion scores as JSON text."""
    result = asyncio.run(
        metric.ascore(
            output=article,
            input=sample.article_guideline,
            context={"research": sample.research},
            expected_output=sample.ground_truth_article,
            reference=sample.ground_truth_article,
        )
    )
    results = result if isinstance(result, list) else [result]
    return json.dumps({r.name: {"score": r.value, "reason": r.reason} for r in results}, ensure_ascii=False)


def _criterion_scores(raw: str, metric_name: str) -> dict[str, float]:
    return {name.removeprefix(f"{metric_name}_"): v["score"] for name, v in json.loads(raw).items()}


def _log_to_opik(experiment: str, dataset_name: str, rows: list[dict], metric_names: list[str]) -> None:
    """Best-effort: register the cached results as an Opik experiment. Never fails the run."""
    try:
        import opik
        from opik import evaluation
        from opik.evaluation.metrics import base_metric, score_result

        by_name = {r["name"]: r for r in rows}

        class CachedMetric(base_metric.BaseMetric):
            def score(self, name: str, **_: object) -> list[score_result.ScoreResult]:
                raw = by_name.get(name, {}).get("raw", {}).get(self.name)
                if raw is None:
                    return []
                return [score_result.ScoreResult(name=n, value=v["score"], reason=v["reason"]) for n, v in json.loads(raw).items()]

        dataset = opik.Opik().get_or_create_dataset(dataset_name)
        dataset.insert([{"name": r["name"], "input": r["input"]} for r in rows])
        evaluation.evaluate(
            dataset=dataset,
            task=lambda item: {"output": by_name[item["name"]]["article"]},
            scoring_metrics=[CachedMetric(name=m) for m in metric_names],
            experiment_name=experiment,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Opik logging skipped for `{experiment}`: {e}")


@click.command()
@click.option(
    "--dataset-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=DEFAULT_DATASET_DIR, show_default=True
)
@click.option("--split", type=click.Choice(["few_shot", "validation", "test", "extended"]), default=None, help="Metadata split filter.")
@click.option("--noise-subset", is_flag=True, help="Only samples with `noise_subset: true`.")
@click.option("--repeats", type=click.IntRange(min=1), default=1, show_default=True)
@click.option(
    "--config", "config_file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, help="Brown CONFIG_FILE."
)
@click.option("--judge-model", type=str, default="opencode_go:gpt-6-luna", show_default=True)
@click.option("--metrics", "metrics", multiple=True, default=["follows_gt", "user_intent", "voice_adherence"], show_default=True)
@click.option("--experiment-name", required=True, help="Base name; runs are `<name>-r<i>`.")
@click.option("--out-root", type=click.Path(path_type=Path), default=Path("outputs/s1"), show_default=True)
@click.option("--retries", type=int, default=5, show_default=True, help="Backoff retries on 429/5xx per call.")
@click.option("--no-opik", is_flag=True, help="Skip Opik experiment logging.")
def main(
    dataset_dir: Path,
    split: str | None,
    noise_subset: bool,
    repeats: int,
    config_file: Path,
    judge_model: str,
    metrics: tuple[str, ...],
    experiment_name: str,
    out_root: Path,
    retries: int,
    no_opik: bool,
) -> None:
    """Generate (cached) and judge (cached) the selected Underdoc samples."""
    os.environ["CONFIG_FILE"] = str(config_file)  # before any brown import reads settings

    from brown.evals.dataset import EvalDataset
    from brown.evals.metrics import build_evaluation_metrics
    from brown.models.config import ModelConfig
    from brown.models.get_model import SupportedModels

    metadata = json.loads((dataset_dir / "metadata.json").read_text())
    selected = s1.select_samples(metadata, split=split, noise_subset=noise_subset)
    if not selected:
        raise click.ClickException("No samples match the given filters.")
    dataset = EvalDataset.load_dataset(dataset_dir, name=dataset_dir.name, description="Underdoc S1 dataset")
    by_dir = {s.directory.as_posix(): s for s in dataset.samples}

    model = SupportedModels(judge_model)
    model_config = (
        ModelConfig(temperature=0.0, thinking_level="high", include_thoughts=False, max_retries=3)
        if model.value.startswith("google_genai:")
        else ModelConfig(temperature=0.0, max_retries=3)
    )
    metric_objs = dict(zip(metrics, build_evaluation_metrics(list(metrics), model, model_config), strict=True))
    fingerprint = _config_fingerprint(config_file)

    for repeat in range(1, repeats + 1):
        experiment = f"{experiment_name}-r{repeat}"
        run_dir = out_root / experiment
        scores: dict[str, dict[str, dict[str, float]]] = {}
        skipped: dict[str, dict[str, str]] = {}
        opik_rows: list[dict] = []
        try:
            for meta in selected:
                sample = by_dir[Path(meta["directory"]).as_posix()]
                slug = Path(meta["directory"]).name
                sample_dir = run_dir / slug
                logger.info(f"[{experiment}] {slug}")
                gen_cache = s1.ItemCache(sample_dir, {**fingerprint, "sample": slug, "repeat": repeat})
                article = gen_cache.get_or_compute(
                    "article.md", lambda s=sample, d=sample_dir: _generate(d, s, d / "work"), retries=retries
                )
                article_sha = hashlib.sha256(article.encode()).hexdigest()[:12]
                scores[meta["name"]], raw_by_metric = {}, {}
                for name in metrics:
                    reason = s1.skip_reason(name, meta)
                    if reason:
                        skipped.setdefault(meta["name"], {})[name] = reason
                        continue
                    judge_cache = s1.ItemCache(sample_dir, {"judge": judge_model, "metric": name, "article": article_sha})
                    raw = judge_cache.get_or_compute(
                        f"judge_{name}.json", lambda n=name, s=sample, a=article: _judge(metric_objs[n], s, a), retries=retries
                    )
                    raw_by_metric[name] = raw
                    scores[meta["name"]][name] = _criterion_scores(raw, name)
                opik_rows.append({"name": meta["name"], "input": sample.article_guideline, "article": article, "raw": raw_by_metric})
        except s1.ProviderUnavailableError as e:
            s1.write_scores(run_dir, experiment, scores, skipped, extra={"complete": False})
            logger.error(f"Stopping: {e}. Cache kept under `{run_dir}`; rerun the same command to resume.")
            click.echo(f"PROVIDER UNAVAILABLE (429/5xx): partial cache kept in {run_dir}. Rerun to resume.", err=True)
            sys.exit(EXIT_PROVIDER_UNAVAILABLE)

        path = s1.write_scores(run_dir, experiment, scores, skipped, extra={"complete": True, **fingerprint, "judge_model": judge_model})
        logger.success(f"Wrote {path}")
        if not no_opik:
            _log_to_opik(experiment, f"{dataset_dir.name}", opik_rows, list(metrics))


if __name__ == "__main__":
    main()
