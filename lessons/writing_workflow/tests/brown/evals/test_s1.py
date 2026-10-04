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
