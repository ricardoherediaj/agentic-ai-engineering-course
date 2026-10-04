"""Check the Underdoc eval dataset for guideline leakage.

For every sample, the guideline must have at most 300 words and must not share any word
8-gram with the ground-truth article (code blocks, URLs and heading lines are ignored).

Usage:
    uv run python scripts/check_underdoc_leakage.py [dataset_dir]
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_GUIDELINE_WORDS = 300
NGRAM_SIZE = 8
DEFAULT_DATASET_DIR = Path(__file__).resolve().parents[1] / "inputs" / "evals" / "underdoc_dataset"

_CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
_URL = re.compile(r"https?://\S+")
_HEADING = re.compile(r"^#{1,6}\s.*$", re.MULTILINE)
_WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


@dataclass(frozen=True)
class SampleResult:
    name: str
    guideline_words: int
    shared_ngram_words: int
    passed: bool


def _words(text: str) -> list[str]:
    text = _CODE_BLOCK.sub(" ", text)
    text = _URL.sub(" ", text)
    text = _HEADING.sub(" ", text)
    return _WORD.findall(text.lower().replace("’", "'"))


def _ngrams(words: list[str], size: int) -> set[tuple[str, ...]]:
    return {tuple(words[i : i + size]) for i in range(len(words) - size + 1)}


def shared_ngram_length(guideline: str, ground_truth: str, size: int = NGRAM_SIZE) -> int:
    """Return `size` if the texts share any word n-gram of that size, else 0."""
    shared = _ngrams(_words(guideline), size) & _ngrams(_words(ground_truth), size)
    return size if shared else 0


def check_sample(name: str, guideline: str, ground_truth: str) -> SampleResult:
    guideline_words = len(guideline.split())
    shared = shared_ngram_length(guideline, ground_truth)
    return SampleResult(name, guideline_words, shared, guideline_words <= MAX_GUIDELINE_WORDS and shared == 0)


def check_dataset(dataset_dir: Path) -> list[SampleResult]:
    metadata = json.loads((dataset_dir / "metadata.json").read_text())
    results = []
    for entry in metadata:
        sample_dir = dataset_dir / entry["directory"]
        guideline = (sample_dir / entry.get("article_guideline_path", "article_guideline.md")).read_text(encoding="utf-8")
        ground_truth = (sample_dir / entry.get("ground_truth_article_path", "article_ground_truth.md")).read_text(encoding="utf-8")
        results.append(check_sample(Path(entry["directory"]).name, guideline, ground_truth))
    return results


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    results = check_dataset(Path(args[0]) if args else DEFAULT_DATASET_DIR)

    print(f"{'sample':<55} {'words':>5} {'8-gram':>6}  status")
    for r in results:
        print(f"{r.name:<55} {r.guideline_words:>5} {r.shared_ngram_words:>6}  {'ok' if r.passed else 'FAIL'}")
    failures = [r for r in results if not r.passed]
    print(f"\n{len(results)} samples, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
