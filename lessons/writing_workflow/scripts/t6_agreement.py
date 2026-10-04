#!/usr/bin/env python3

"""Compare the T6 labeling sheet against the LLM judge outputs.

The sheet is a markdown file of checkboxes (`- [x] metric.criterion: reason`) grouped as
`## <slug> · <bucket>` / `### <Metric>` / `#### "<section>"`. Judges write `judge_*.json` per slug, where each
criterion has a `reason` made of `<section title>:\\n**<0|1>:** <why>` blocks.

Items are matched by slug + metric + criterion + section: normalized title first, then position among the
sections left unmatched on both sides (only when both sides left the same number, otherwise it is ambiguous).

Usage:
    uv run python scripts/t6_agreement.py [--sheet PATH] [--outputs DIR] [--baseline-sheet PATH]
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

WORKFLOW_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHEET = WORKFLOW_ROOT.parents[1] / "odd" / "labels" / "t6-validation-sheet.md"
DEFAULT_OUTPUTS = WORKFLOW_ROOT / "outputs" / "s1" / "s1-t6-validation-r1"

JUDGE_PREFIXES = {
    "follows_gt_": "follows_gt",
    "user_intent_": "user_intent",
    "voice_adherence_": "voice",
}
SLUG_RE = re.compile(r"^##\s+(\S+)\s+·")
SECTION_RE = re.compile(r'^####\s+"?(.*?)"?\s*$')
ITEM_RE = re.compile(r"^- \[([ xX])\]\s+([a-z_]+)\.([a-z_]+):\s*(.*)$")
JUDGE_BLOCK_RE = re.compile(r"(?m)^(.+):\n\*\*([01])(?:\.0+)?:\*\*\s*")


@dataclass
class Item:
    slug: str
    metric: str
    criterion: str
    section: str
    position: int
    value: int
    reason: str = ""


@dataclass
class Disagreement:
    sheet: Item
    judge: Item


@dataclass
class Flip:
    slug: str
    metric: str
    section: str
    criterion: str
    before: int
    after: int


@dataclass
class Report:
    per_metric: dict[str, tuple[int, int]] = field(default_factory=dict)
    overall: tuple[int, int] = (0, 0)
    disagreements: list[Disagreement] = field(default_factory=list)
    unmatched_sheet: list[Item] = field(default_factory=list)
    unmatched_judge: list[Item] = field(default_factory=list)


def normalize_title(title: str) -> frozenset[str]:
    """Normalize a section title into a set of parts, so `A + B` equals `A / B`."""
    parts = re.split(r"\s[+/]\s", title)
    return frozenset(" ".join(re.sub(r"[^a-z0-9]+", " ", p.lower()).split()) for p in parts)


def parse_sheet(text: str) -> list[Item]:
    items: list[Item] = []
    slug = section = ""
    seen: dict[tuple[str, str], list[str]] = defaultdict(list)
    for line in text.splitlines():
        if m := SLUG_RE.match(line):
            slug, section = m.group(1), ""
        elif m := SECTION_RE.match(line):
            section = m.group(1)
        elif (m := ITEM_RE.match(line)) and slug and section:
            metric, criterion = m.group(2), m.group(3)
            sections = seen[(slug, metric)]
            if section not in sections:
                sections.append(section)
            items.append(Item(slug, metric, criterion, section, sections.index(section), int(m.group(1) != " "), m.group(4)))
    return items


def parse_judges(outputs: Path) -> list[Item]:
    items: list[Item] = []
    for slug_dir in sorted(p for p in Path(outputs).iterdir() if p.is_dir()):
        for judge_file in sorted(slug_dir.glob("judge_*.json")):
            for key, payload in json.loads(judge_file.read_text()).items():
                metric, criterion = _split_judge_key(key)
                reason = payload.get("reason", "")
                matches = list(JUDGE_BLOCK_RE.finditer(reason))
                for index, match in enumerate(matches):
                    end = matches[index + 1].start() if index + 1 < len(matches) else len(reason)
                    items.append(
                        Item(
                            slug_dir.name,
                            metric,
                            criterion,
                            match.group(1).strip(),
                            index,
                            int(match.group(2)),
                            reason[match.end() : end].strip(),
                        )
                    )
    return items


def _split_judge_key(key: str) -> tuple[str, str]:
    for prefix, metric in JUDGE_PREFIXES.items():
        if key.startswith(prefix):
            return metric, key[len(prefix) :]
    raise ValueError(f"Unknown judge criterion key: {key}")


def _group(items: list[Item]) -> dict[tuple[str, str, str], list[Item]]:
    grouped: dict[tuple[str, str, str], list[Item]] = defaultdict(list)
    for item in items:
        grouped[(item.slug, item.metric, item.criterion)].append(item)
    return grouped


def _pair(sheet_rows: list[Item], judge_rows: list[Item]) -> tuple[list[tuple[Item, Item]], list[Item], list[Item]]:
    pairs: list[tuple[Item, Item]] = []
    left_sheet, left_judge = list(sheet_rows), list(judge_rows)
    for s in sheet_rows:
        for j in left_judge:
            if normalize_title(s.section) == normalize_title(j.section):
                pairs.append((s, j))
                left_sheet.remove(s)
                left_judge.remove(j)
                break
    if left_sheet and len(left_sheet) == len(left_judge):
        pairs.extend(zip(sorted(left_sheet, key=lambda i: i.position), sorted(left_judge, key=lambda i: i.position)))
        left_sheet, left_judge = [], []
    return pairs, left_sheet, left_judge


def compare(sheet: list[Item], judge: list[Item]) -> Report:
    report = Report()
    sheet_groups, judge_groups = _group(sheet), _group(judge)
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for key in sorted(set(sheet_groups) | set(judge_groups)):
        pairs, left_sheet, left_judge = _pair(sheet_groups.get(key, []), judge_groups.get(key, []))
        report.unmatched_sheet.extend(left_sheet)
        report.unmatched_judge.extend(left_judge)
        for s, j in pairs:
            totals[key[1]][0] += 1
            if s.value == j.value:
                totals[key[1]][1] += 1
            else:
                report.disagreements.append(Disagreement(s, j))
    report.per_metric = {metric: (n, agree) for metric, (n, agree) in sorted(totals.items())}
    report.overall = (sum(n for n, _ in report.per_metric.values()), sum(a for _, a in report.per_metric.values()))
    return report


def baseline_flips(baseline: list[Item], current: list[Item]) -> list[Flip]:
    base = {(i.slug, i.metric, i.criterion, i.section): i for i in baseline}
    flips = []
    for item in current:
        before = base.get((item.slug, item.metric, item.criterion, item.section))
        if before and before.value != item.value:
            flips.append(Flip(item.slug, item.metric, item.section, item.criterion, before.value, item.value))
    return flips


def _pct(agree: int, n: int) -> str:
    return f"{100 * agree / n:.1f}%" if n else "n/a"


def _short(slug: str) -> str:
    return slug[:10] + "…" + slug[-12:] if len(slug) > 24 else slug


def render(report: Report, flips: list[Flip] | None = None) -> str:
    lines = ["Agreement (sheet vs judge)"]
    for metric, (n, agree) in report.per_metric.items():
        lines.append(f"  {metric:<12} {agree}/{n} = {_pct(agree, n)}")
    n, agree = report.overall
    lines.append(f"  overall      {agree}/{n} = {_pct(agree, n)}")
    lines.append(f"\nDisagreements: {len(report.disagreements)}")
    for d in report.disagreements:
        s, j = d.sheet, d.judge
        lines.append(
            f"- [{_short(s.slug)}] {s.metric}.{s.criterion} · {s.section!r}: sheet={s.value} judge={j.value}"
            f" (judge section {j.section!r})\n    judge reason: {' '.join(j.reason.split())[:300]}"
        )
    lines.append(f"\nUnmatched sheet items: {len(report.unmatched_sheet)}")
    lines.extend(f"- [{_short(i.slug)}] {i.metric}.{i.criterion} · {i.section!r}" for i in report.unmatched_sheet)
    lines.append(f"Unmatched judge items: {len(report.unmatched_judge)}")
    lines.extend(f"- [{_short(i.slug)}] {i.metric}.{i.criterion} · {i.section!r}" for i in report.unmatched_judge)
    if flips is not None:
        lines.append(f"\nFlips vs baseline: {len(flips)}")
        lines.extend(f"- [{_short(f.slug)}] {f.metric}.{f.criterion} · {f.section!r}: {f.before} -> {f.after}" for f in flips)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument("--outputs", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--baseline-sheet", type=Path, default=None)
    parser.add_argument("--slug", default=None, help="Only score posts whose slug starts with this prefix.")
    args = parser.parse_args(argv)

    def keep(items: list[Item]) -> list[Item]:
        return [i for i in items if args.slug is None or i.slug.startswith(args.slug)]

    sheet_items = keep(parse_sheet(args.sheet.read_text()))
    report = compare(sheet_items, keep(parse_judges(args.outputs)))
    flips = baseline_flips(keep(parse_sheet(args.baseline_sheet.read_text())), sheet_items) if args.baseline_sheet else None
    print(render(report, flips))
    return 0


if __name__ == "__main__":
    sys.exit(main())
