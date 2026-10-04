#!/usr/bin/env python3

"""Summarize S1 runs: baseline vs new voice per metric, against the noise floor."""

import json
import statistics
from collections import defaultdict
from pathlib import Path

import click


def _metric_scores(run: dict) -> dict[str, dict[str, float]]:
    """sample -> metric -> mean over criteria."""
    return {
        sample: {metric: statistics.fmean(criteria.values()) for metric, criteria in metrics.items() if criteria}
        for sample, metrics in run["samples"].items()
    }


def _mean_per_metric(runs: list[dict]) -> dict[str, float]:
    values: dict[str, list[float]] = defaultdict(list)
    for run in runs:
        for metrics in _metric_scores(run).values():
            for metric, value in metrics.items():
                values[metric].append(value)
    return {m: statistics.fmean(v) for m, v in values.items()}


def _noise_std(noise_runs: list[dict]) -> dict[str, float]:
    """Std across repeats per sample, averaged over samples, per metric."""
    per_sample: dict[tuple[str, str], list[float]] = defaultdict(list)
    for run in noise_runs:
        for sample, metrics in _metric_scores(run).items():
            for metric, value in metrics.items():
                per_sample[(metric, sample)].append(value)
    stds: dict[str, list[float]] = defaultdict(list)
    for (metric, _), values in per_sample.items():
        if len(values) >= 2:
            stds[metric].append(statistics.stdev(values))
    return {m: statistics.fmean(v) for m, v in stds.items()}


def summarize(baseline: list[dict], new: list[dict], noise: list[dict], noise_new: list[dict] | None = None) -> dict[str, dict]:
    """Per metric: baseline mean, new mean, delta, noise std, verdict (`delta > noise std` beats noise).

    `noise` and `noise_new` are repeat groups of one arm each; their stds are averaged when both are given.
    """
    base_mean, new_mean = _mean_per_metric(baseline), _mean_per_metric(new)
    noise_std = _noise_std(noise)
    if noise_new:
        other = _noise_std(noise_new)
        noise_std = {
            m: statistics.fmean([v for v in (noise_std.get(m), other.get(m)) if v is not None]) for m in set(noise_std) | set(other)
        }
    rows = {}
    for metric in sorted(set(base_mean) & set(new_mean)):
        delta = new_mean[metric] - base_mean[metric]
        std = noise_std.get(metric)
        verdict = "no noise data" if std is None else ("beats noise" if delta > std else "within noise")
        rows[metric] = {"baseline": base_mean[metric], "new": new_mean[metric], "delta": delta, "noise_std": std, "verdict": verdict}
    return rows


def format_table(rows: dict[str, dict]) -> str:
    lines = [f"{'metric':<22}{'baseline':>10}{'new':>10}{'delta':>10}{'noise_std':>11}  verdict"]
    for metric, r in rows.items():
        std = "n/a" if r["noise_std"] is None else f"{r['noise_std']:.3f}"
        lines.append(f"{metric:<22}{r['baseline']:>10.3f}{r['new']:>10.3f}{r['delta']:>+10.3f}{std:>11}  {r['verdict']}")
    return "\n".join(lines)


def _load(dirs: tuple[Path, ...]) -> list[dict]:
    return [json.loads((d / "scores.json").read_text()) for d in dirs]


@click.command()
@click.option("--baseline", "baseline", multiple=True, required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--new", "new", multiple=True, required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--noise-baseline", multiple=True, type=click.Path(exists=True, path_type=Path), help="Baseline noise repeat dirs.")
@click.option("--noise-new", multiple=True, type=click.Path(exists=True, path_type=Path), help="New-voice noise repeat dirs.")
def main(baseline: tuple[Path, ...], new: tuple[Path, ...], noise_baseline: tuple[Path, ...], noise_new: tuple[Path, ...]) -> None:
    """Each option takes experiment dirs under outputs/s1/ (repeatable)."""
    click.echo(format_table(summarize(_load(baseline), _load(new), _load(noise_baseline), _load(noise_new))))


if __name__ == "__main__":
    main()
