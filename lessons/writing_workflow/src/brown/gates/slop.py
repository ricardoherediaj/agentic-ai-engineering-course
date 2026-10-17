"""Deterministic slop gate for the article review loop.

The gate runs the Underdoc harness `checks/check.py` (G-05) on every draft and turns its hits into
`Review` entries, so the editor has to fix what a regex can prove. It is local and free: no model
call, no tokens. Off unless the config enables it (`slop_gate`).
"""

import importlib.util
import re
from pathlib import Path
from types import ModuleType
from typing import Any

from loguru import logger

from brown.entities.reviews import ArticleReviews, Review

GATE_PROFILE = "mechanics"
ARTICLE_LEVEL = "Article level"
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$", re.M)


def load_check_module(harness_path: Path) -> ModuleType:
    """Import `<harness>/checks/check.py` by path: the harness is stdlib-only and is not installed."""
    path = Path(harness_path).expanduser() / "checks" / "check.py"
    if not path.is_file():
        raise FileNotFoundError(f"harness check.py not found at `{path}`")
    spec = importlib.util.spec_from_file_location("underdoc_harness_check", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load `{path}` as a module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SlopGate:
    """The harness slop gate exposed as a source of reviews."""

    def __init__(self, check_module: ModuleType) -> None:
        self._check = check_module
        self._words = check_module.load_words()
        self._patterns = check_module.load_patterns()

    def hits(self, article_markdown: str) -> list[dict[str, Any]]:
        result = self._check.g05_slop(article_markdown, self._words, self._patterns)
        return list(result.get("hits") or [])

    def reviews(self, article_markdown: str) -> list[Review]:
        """One review per hit, located in the section that holds it."""
        return [
            Review(
                profile=GATE_PROFILE,
                location=section_of(article_markdown, hit["match"]),
                comment=f'{hit["level"]} slop gate hit ({hit["label"]}): "{hit["match"]}"',
            )
            for hit in self.hits(article_markdown)
        ]


def section_of(article_markdown: str, snippet: str) -> str:
    """Title of the heading above the snippet, or `Article level` when the snippet cannot be located."""
    index = article_markdown.find(snippet)
    if index == -1:
        return ARTICLE_LEVEL
    titles = _HEADING.findall(article_markdown[:index])
    return titles[-1].strip() if titles else ARTICLE_LEVEL


def append_gate_reviews(reviews: ArticleReviews, gate: SlopGate | None) -> ArticleReviews:
    """Append the gate hits to the reviewer's output.

    The review loop stops early only when it gets no reviews at all, so appending here is what keeps
    a draft with regex-provable slop inside the review/edit cycle until the hits are gone.
    """
    if gate is None:
        return reviews
    gate_reviews = gate.reviews(reviews.article.to_markdown())
    if not gate_reviews:
        return reviews
    logger.info(f"Slop gate: {len(gate_reviews)} hit(s) added as reviews: {[(review.location, review.comment) for review in gate_reviews]}")
    return ArticleReviews(article=reviews.article, reviews=[*reviews.reviews, *gate_reviews])
