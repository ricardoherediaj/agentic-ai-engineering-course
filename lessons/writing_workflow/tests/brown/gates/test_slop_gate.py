"""Tests for the deterministic slop gate that feeds Brown's review loop."""

import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from brown.builders import build_slop_gate
from brown.config_app import SlopGateConfig
from brown.entities.articles import Article
from brown.entities.exceptions import InvalidConfigurationException
from brown.entities.reviews import ArticleReviews
from brown.gates import ARTICLE_LEVEL, SlopGate, append_gate_reviews, load_check_module, section_of

STUB_CHECK = """
import re

def load_words():
    return ["leverage"]


def load_patterns():
    return [(re.compile(r"not a (ladder|toolchain)", re.I), "two-beat reversal")]


def g05_slop(body, word_terms, patterns):
    hits = [
        {"tier": "pattern", "level": "fail", "match": m.group(0), "label": label, "line": 1}
        for rx, label in patterns
        for m in re.finditer(rx, body)
    ]
    return {"id": "G-05", "status": "FAIL" if hits else "PASS", "value": len(hits), "hits": hits}
"""

ARTICLE = """# Title

## Introduction
Some prose.

## The setup
My setup is not a ladder. It is a way of working.
"""


def _harness(root: Path) -> Path:
    (root / "checks").mkdir(parents=True, exist_ok=True)
    (root / "checks" / "check.py").write_text(textwrap.dedent(STUB_CHECK), encoding="utf-8")
    return root


def _gate(tmp_path: Path) -> SlopGate:
    return SlopGate(load_check_module(_harness(tmp_path / "harness")))


def test_gate_reviews_are_mechanics_reviews_located_in_their_section(tmp_path: Path) -> None:
    reviews = _gate(tmp_path).reviews(ARTICLE)
    assert len(reviews) == 1
    assert reviews[0].profile == "mechanics"
    assert reviews[0].location == "The setup"
    assert "not a ladder" in reviews[0].comment


def test_section_of_uses_the_heading_above_and_falls_back(tmp_path: Path) -> None:
    assert section_of(ARTICLE, "not a ladder") == "The setup"
    assert section_of("plain prose without headings", "prose") == ARTICLE_LEVEL
    assert section_of(ARTICLE, "text that is not in the article") == ARTICLE_LEVEL


def test_append_gate_reviews_keeps_a_hit_in_the_loop(tmp_path: Path) -> None:
    empty = ArticleReviews(article=Article(content=ARTICLE), reviews=[])
    assert len(append_gate_reviews(empty, _gate(tmp_path)).reviews) == 1
    assert append_gate_reviews(empty, None).reviews == []


def test_build_slop_gate_is_off_by_default(tmp_path: Path) -> None:
    app_config = SimpleNamespace(slop_gate=SlopGateConfig(enabled=False, harness_path=str(tmp_path)))
    assert build_slop_gate(app_config) is None


def test_build_slop_gate_uses_the_config_then_the_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _harness(tmp_path / "harness")
    from_config = build_slop_gate(SimpleNamespace(slop_gate=SlopGateConfig(enabled=True, harness_path=str(harness))))
    assert isinstance(from_config, SlopGate)

    monkeypatch.setenv("UNDERDOC_HARNESS_PATH", str(harness))
    from_env = build_slop_gate(SimpleNamespace(slop_gate=SlopGateConfig(enabled=True, harness_path=None)))
    assert isinstance(from_env, SlopGate)


def test_build_slop_gate_fails_loudly_without_a_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UNDERDOC_HARNESS_PATH", raising=False)
    app_config = SimpleNamespace(slop_gate=SlopGateConfig(enabled=True, harness_path=None))
    with pytest.raises(InvalidConfigurationException, match="harness path"):
        build_slop_gate(app_config)


def test_load_check_module_reports_a_missing_harness(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="check.py"):
        load_check_module(tmp_path)
