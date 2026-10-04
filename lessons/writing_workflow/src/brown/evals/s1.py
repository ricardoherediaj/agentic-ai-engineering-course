"""Pure helpers for the S1 evaluation protocol (Underdoc voice experiment).

Sample filtering, on-disk resume cache, bounded exponential backoff on provider
429/5xx errors, and scores export. No provider or Opik imports here, so everything is
unit-testable offline.
"""

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

T = TypeVar("T")

# Buckets whose research dossier is real. Bridge/field-notes and the extended split carry placeholders.
RESEARCH_BUCKETS = {"builds", "explainers"}
_RETRYABLE_TEXT = re.compile(r"\b(429|5\d\d)\b|RESOURCE_EXHAUSTED|rate.?limit|overloaded", re.IGNORECASE)


class ProviderUnavailableError(RuntimeError):
    """Raised when a provider keeps answering 429/5xx after the bounded retries."""


def select_samples(metadata: list[dict[str, Any]], split: str | None = None, noise_subset: bool = False) -> list[dict[str, Any]]:
    """Filter metadata entries by `split` and/or `noise_subset`, keeping file order."""
    selected = metadata
    if split:
        selected = [m for m in selected if m.get("split") == split]
    if noise_subset:
        selected = [m for m in selected if m.get("noise_subset") is True]
    return selected


def skip_reason(metric: str, sample_meta: dict[str, Any]) -> str | None:
    """Return why `metric` must be skipped for the sample, or None when it applies.

    UserIntent scores research anchoring, which is meaningless for placeholder research.
    """
    if metric != "user_intent":
        return None
    if sample_meta.get("bucket") in RESEARCH_BUCKETS and sample_meta.get("split") != "extended":
        return None
    return "placeholder research (bucket/split has no real dossier)"


def is_retryable(error: BaseException) -> bool:
    """True for provider rate limits (429) and server errors (5xx), walking the exception chain."""
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        status = getattr(current, "status_code", None) or getattr(getattr(current, "response", None), "status_code", None)
        if isinstance(status, int):
            return status == 429 or 500 <= status < 600
        if _RETRYABLE_TEXT.search(str(current)):
            return True
        current = current.__cause__ or current.__context__
    return False


def with_backoff(
    fn: Callable[[], T],
    retries: int = 5,
    base_delay: float = 2.0,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call `fn`, retrying retryable errors with exponential backoff (base, 2*base, ...).

    Raises:
        ProviderUnavailableError: after `retries` retries of a 429/5xx error.
    """
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as e:
            if not is_retryable(e):
                raise
            if attempt == retries:
                raise ProviderUnavailableError(f"Provider unavailable after {retries} retries: {e}") from e
            sleep(base_delay * 2**attempt)
    raise AssertionError("unreachable")


def hash_key(key: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(key, sort_keys=True, default=str).encode()).hexdigest()[:16]


class ItemCache:
    """Per-sample directory cache. An item is valid only if its key hash matches.

    Layout: `<root>/<name>` plus `<root>/<name>.key` holding the key hash.
    """

    def __init__(self, root: Path, key: dict[str, Any]) -> None:
        self.root = root
        self.key_hash = hash_key(key)

    def get(self, name: str) -> str | None:
        item, key_file = self.root / name, self.root / f"{name}.key"
        if item.exists() and key_file.exists() and key_file.read_text().strip() == self.key_hash:
            return item.read_text(encoding="utf-8")
        return None

    def put(self, name: str, content: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / name).write_text(content, encoding="utf-8")
        (self.root / f"{name}.key").write_text(self.key_hash)

    def get_or_compute(
        self,
        name: str,
        produce: Callable[[], str],
        retries: int = 5,
        base_delay: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> str:
        cached = self.get(name)
        if cached is not None:
            return cached
        content = with_backoff(produce, retries=retries, base_delay=base_delay, sleep=sleep)
        self.put(name, content)
        return content


def write_scores(
    out_dir: Path,
    experiment: str,
    samples: dict[str, dict[str, dict[str, float]]],
    skipped: dict[str, dict[str, str]] | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Write `scores.json`: sample -> metric -> criterion -> aggregated score."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "scores.json"
    payload = {"experiment": experiment, "opik_experiment": experiment, "samples": samples, "skipped": skipped or {}, **(extra or {})}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _resolved_config_file() -> Path:
    from brown.config import get_settings

    return Path(get_settings().CONFIG_FILE).resolve()


def apply_config_file(config_file: Path) -> Any:
    """Point Brown at `config_file` and return the loaded app config.

    `import brown` calls `get_settings()` at import time, which caches the default config before a CLI
    option can set `CONFIG_FILE`. Clear both caches after setting the env var and fail loudly if the
    resolved file still differs, so a run can never silently use the wrong provider.
    """
    import os

    from brown.config import get_settings
    from brown.config_app import get_app_config

    os.environ["CONFIG_FILE"] = str(config_file)
    get_settings.cache_clear()
    get_app_config.cache_clear()
    resolved = _resolved_config_file()
    if resolved != Path(config_file).resolve():
        raise RuntimeError(f"CONFIG_FILE mismatch: requested {Path(config_file).resolve()}, Brown resolved {resolved}")
    return get_app_config()


def config_model_ids(app_config: Any) -> set[str]:
    """All model ids an app config uses, including node tools."""
    ids = set()
    for node in app_config.nodes.values():
        ids.add(node.model_id.value)
        for tool in (getattr(node, "tools", None) or {}).values():
            ids.add(tool.model_id.value)
    return ids
