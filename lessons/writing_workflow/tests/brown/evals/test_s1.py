"""Offline tests for the S1 protocol helpers (filters, cache, backoff, scores, summary)."""

import importlib.util
import json
from pathlib import Path

import pytest

from brown.evals import s1

ROOT = Path(__file__).resolve().parents[3]

META = [
    {"name": "a", "directory": "data/a", "bucket": "builds", "split": "test", "noise_subset": True},
    {"name": "b", "directory": "data/b", "bucket": "bridge", "split": "test", "noise_subset": True},
    {"name": "c", "directory": "data/c", "bucket": "explainers", "split": "test", "noise_subset": False},
    {"name": "d", "directory": "data/d", "bucket": "builds", "split": "extended", "noise_subset": False},
    {"name": "e", "directory": "data/e", "bucket": "field-notes", "split": "validation"},
]


def test_select_by_split_and_noise() -> None:
    assert [m["name"] for m in s1.select_samples(META, split="test")] == ["a", "b", "c"]
    assert [m["name"] for m in s1.select_samples(META, split="test", noise_subset=True)] == ["a", "b"]
    assert [m["name"] for m in s1.select_samples(META)] == ["a", "b", "c", "d", "e"]
    assert s1.select_samples(META, split="few_shot") == []


def test_user_intent_skipped_for_placeholder_research() -> None:
    assert s1.skip_reason("user_intent", META[0]) is None
    assert s1.skip_reason("user_intent", META[2]) is None
    assert s1.skip_reason("user_intent", META[1]) is not None  # bridge
    assert s1.skip_reason("user_intent", META[3]) is not None  # extended
    assert s1.skip_reason("voice_adherence", META[1]) is None


def test_cache_hit_skips_generation(tmp_path: Path) -> None:
    calls = []

    def produce() -> str:
        calls.append(1)
        return "article"

    cache = s1.ItemCache(tmp_path / "x", key={"config": "c", "repeat": 1})
    assert cache.get_or_compute("article.md", produce, retries=1, sleep=lambda _: None) == "article"
    assert cache.get_or_compute("article.md", produce, retries=1, sleep=lambda _: None) == "article"
    assert len(calls) == 1
    # A different key invalidates the cached item.
    other = s1.ItemCache(tmp_path / "x", key={"config": "other", "repeat": 1})
    other.get_or_compute("article.md", produce, retries=1, sleep=lambda _: None)
    assert len(calls) == 2


class _Err(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


def test_backoff_retries_then_succeeds() -> None:
    attempts = []
    sleeps: list[float] = []

    def flaky() -> str:
        attempts.append(1)
        if len(attempts) < 3:
            raise _Err(429)
        return "ok"

    assert s1.with_backoff(flaky, retries=5, base_delay=1.0, sleep=sleeps.append) == "ok"
    assert sleeps == [1.0, 2.0]


def test_backoff_stops_cleanly_on_429_and_keeps_cache(tmp_path: Path) -> None:
    cache = s1.ItemCache(tmp_path / "x", key={"k": 1})
    cache.get_or_compute("done.md", lambda: "kept", retries=1, sleep=lambda _: None)

    def always_429() -> str:
        raise _Err(429)

    with pytest.raises(s1.ProviderUnavailableError):
        cache.get_or_compute("new.md", always_429, retries=2, base_delay=0.0, sleep=lambda _: None)
    assert (tmp_path / "x" / "done.md").read_text() == "kept"
    assert not (tmp_path / "x" / "new.md").exists()


def test_non_retryable_error_propagates() -> None:
    def boom() -> str:
        raise ValueError("bad")

    with pytest.raises(ValueError):
        s1.with_backoff(boom, retries=3, sleep=lambda _: None)


def test_is_retryable() -> None:
    assert s1.is_retryable(_Err(503))
    assert s1.is_retryable(RuntimeError("RESOURCE_EXHAUSTED 429"))
    assert not s1.is_retryable(_Err(400))
    assert not s1.is_retryable(ValueError("nope"))


def test_write_scores_shape(tmp_path: Path) -> None:
    s1.write_scores(
        tmp_path,
        experiment="exp-r1",
        samples={"a": {"voice_adherence": {"first_person_voice": 1.0, "concrete_specifics": 0.5}}},
        skipped={"b": {"user_intent": "placeholder research"}},
    )
    data = json.loads((tmp_path / "scores.json").read_text())
    assert data["experiment"] == "exp-r1"
    assert data["samples"]["a"]["voice_adherence"]["concrete_specifics"] == 0.5
    assert data["skipped"]["b"]["user_intent"] == "placeholder research"


def _load_summary():
    spec = importlib.util.spec_from_file_location("s1_summary", ROOT / "scripts" / "s1_summary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(samples: dict) -> dict:
    return {"experiment": "x", "samples": samples, "skipped": {}}


def test_summary_math() -> None:
    summary = _load_summary()
    base = [_run({"a": {"m": {"c1": 0.5, "c2": 0.5}}, "b": {"m": {"c1": 0.7, "c2": 0.5}}})]
    new = [_run({"a": {"m": {"c1": 1.0, "c2": 0.8}}, "b": {"m": {"c1": 1.0, "c2": 0.8}}})]
    noise = [
        _run({"a": {"m": {"c1": 0.5}}, "b": {"m": {"c1": 0.5}}}),
        _run({"a": {"m": {"c1": 0.7}}, "b": {"m": {"c1": 0.5}}}),
    ]
    rows = summary.summarize(base, new, noise)
    row = rows["m"]
    assert row["baseline"] == pytest.approx(0.55)
    assert row["new"] == pytest.approx(0.9)
    assert row["delta"] == pytest.approx(0.35)
    # std over 2 repeats: a -> 0.1414, b -> 0
    assert row["noise_std"] == pytest.approx(0.1414213 / 2, rel=1e-4)
    assert row["verdict"] == "beats noise"


def test_summary_verdict_within_noise() -> None:
    summary = _load_summary()
    base = [_run({"a": {"m": {"c": 0.5}}})]
    new = [_run({"a": {"m": {"c": 0.55}}})]
    noise = [_run({"a": {"m": {"c": 0.4}}}), _run({"a": {"m": {"c": 0.6}}})]
    assert summary.summarize(base, new, noise)["m"]["verdict"] == "within noise"
    assert "m" in summary.format_table(summary.summarize(base, new, noise))


def test_apply_config_file_overrides_cached_settings(tmp_path, monkeypatch) -> None:
    """Regression: `import brown` caches settings with the default config before `--config` is applied."""
    from brown.config import get_settings
    from brown.config_app import get_app_config

    get_settings()  # simulate the import-time cache with the default config
    target = Path("configs/underdoc-fallback.yaml").resolve()
    monkeypatch.delenv("CONFIG_FILE", raising=False)

    app_config = s1.apply_config_file(target)

    assert Path(get_settings().CONFIG_FILE).resolve() == target
    model_ids = s1.config_model_ids(app_config)
    assert model_ids and all(m.startswith("opencode_go:") for m in model_ids)
    get_settings.cache_clear()
    get_app_config.cache_clear()


def test_apply_config_file_raises_on_mismatch(monkeypatch) -> None:
    monkeypatch.setattr(s1, "_resolved_config_file", lambda: Path("configs/course-gemini-flash.yaml").resolve())
    with pytest.raises(RuntimeError, match="CONFIG_FILE"):
        s1.apply_config_file(Path("configs/underdoc-fallback.yaml"))


def _make_metric_pkg(root: Path, prompt: str = "p", example: str = "e") -> None:
    pkg = root / "m"
    (pkg / "examples" / "x").mkdir(parents=True, exist_ok=True)
    (pkg / "prompts.py").write_text(prompt)
    (pkg / "types.py").write_text("t")
    (pkg / "examples" / "x" / "a.md").write_text(example)


def test_metric_version_changes_with_rubric_and_is_stable_otherwise(tmp_path: Path) -> None:
    _make_metric_pkg(tmp_path)
    base = s1.metric_version("m", tmp_path)
    assert s1.metric_version("m", tmp_path) == base
    (tmp_path / "m" / "prompts.py").write_text("p2")
    assert s1.metric_version("m", tmp_path) != base
    _make_metric_pkg(tmp_path, example="e2")
    assert s1.metric_version("m", tmp_path) != base


def test_judge_cache_invalidates_on_metric_version(tmp_path: Path) -> None:
    _make_metric_pkg(tmp_path)
    calls = []

    def judge(version: str) -> str:
        cache = s1.ItemCache(tmp_path / "out", {"judge": "j", "metric": "m", "metric_version": version, "article": "a"})
        return cache.get_or_compute("judge_m.json", lambda: calls.append(1) or "r", retries=0)

    judge(s1.metric_version("m", tmp_path))
    judge(s1.metric_version("m", tmp_path))
    assert len(calls) == 1  # unchanged rubric hits the cache
    (tmp_path / "m" / "prompts.py").write_text("changed")
    judge(s1.metric_version("m", tmp_path))
    assert len(calls) == 2  # changed rubric re-judges


def test_real_metrics_have_versions() -> None:
    for name in ("follows_gt", "user_intent", "voice_adherence"):
        assert len(s1.metric_version(name)) == 12


def test_generator_code_version_tracks_get_model(tmp_path: Path) -> None:
    f = tmp_path / "get_model.py"
    f.write_text("a")
    base = s1.generator_code_version((f,))
    assert s1.generator_code_version((f,)) == base
    f.write_text("b")
    assert s1.generator_code_version((f,)) != base
    assert len(s1.generator_code_version()) == 12


def test_runner_keys_include_versions() -> None:
    src = (ROOT / "scripts" / "underdoc_run_eval.py").read_text()
    assert "s1.generator_code_version()" in src
    assert "s1.metric_version(name)" in src
    assert "s1.corpus_version(" in src
    assert "s1.input_version(" in src
    assert "s1.voice_rules_version(" in src


def test_generator_code_version_tracks_a_package_dir(tmp_path: Path) -> None:
    package = tmp_path / "nodes"
    package.mkdir()
    (package / "a.py").write_text("a")
    base = s1.generator_code_version((package,))
    (package / "a.py").write_text("b")
    assert s1.generator_code_version((package,)) != base


def _write_voice_profiles(root: Path) -> None:
    from brown.evals.metrics.voice_adherence import prompts as voice_prompts

    for name in voice_prompts.VOICE_PROFILE_FILES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"RULES {name}")


def test_corpus_version_tracks_profile_and_example_edits(tmp_path: Path) -> None:
    profiles, examples = tmp_path / "profiles", tmp_path / "examples"
    examples.mkdir()
    (examples / "post.md").write_text("e")
    _write_voice_profiles(profiles)

    base = s1.corpus_version(profiles, examples)
    assert s1.corpus_version(profiles, examples) == base
    (profiles / "mechanics_profile.md").write_text("changed")
    after_profile = s1.corpus_version(profiles, examples)
    assert after_profile != base
    (examples / "post.md").write_text("changed")
    assert s1.corpus_version(profiles, examples) != after_profile


def test_voice_rules_version_tracks_voice_profile_content(tmp_path: Path) -> None:
    _write_voice_profiles(tmp_path)
    base = s1.voice_rules_version(tmp_path)
    assert s1.voice_rules_version(tmp_path) == base
    (tmp_path / "tonality_profile.md").write_text("changed")
    assert s1.voice_rules_version(tmp_path) != base


def test_judge_cache_invalidates_on_voice_rules(tmp_path: Path) -> None:
    profiles = tmp_path / "profiles"
    _write_voice_profiles(profiles)
    calls: list[int] = []

    def judge(rules: str) -> str:
        cache = s1.ItemCache(
            tmp_path / "out",
            {"judge": "j", "metric": "voice_adherence", "metric_version": "v", "article": "a", "voice_rules": rules},
        )
        return cache.get_or_compute("judge_voice_adherence.json", lambda: calls.append(1) or "r", retries=0)

    judge(s1.voice_rules_version(profiles))
    judge(s1.voice_rules_version(profiles))
    assert len(calls) == 1  # unchanged rules hit the cache
    (profiles / "mechanics_profile.md").write_text("changed")
    judge(s1.voice_rules_version(profiles))
    assert len(calls) == 2  # a profile edit re-judges


def test_input_version_tracks_guideline_and_research() -> None:
    base = s1.input_version("G", "R")
    assert s1.input_version("G", "R") == base
    assert s1.input_version("G2", "R") != base
    assert s1.input_version("G", "R2") != base


def test_current_item_ids_keeps_only_this_runs_samples() -> None:
    spec = importlib.util.spec_from_file_location("underdoc_run_eval", Path("scripts/underdoc_run_eval.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    items = [{"id": "a", "name": "Post A"}, {"id": "x", "name": "Other run"}, {"id": "a2", "name": "Post A"}, {"id": "b", "name": "Post B"}]

    assert mod._current_item_ids(items, {"Post A": {}, "Post B": {}}) == ["a", "b"]
