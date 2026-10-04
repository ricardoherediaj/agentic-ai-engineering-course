import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SLUG = "2025-01-01-demo"

SHEET = f"""# header

## {SLUG} · explainers

### FollowsGT

#### "Introduction"

- [x] follows_gt.content: same topic
- [ ] follows_gt.flow: extra anecdote <- me: fine

#### "Second Part"

- [x] follows_gt.content: ok

### UserIntent

#### "Alpha thing + Beta thing"

- [x] user_intent.guideline_adherence: ok

#### "Gamma"

- [ ] user_intent.guideline_adherence: bad

### VoiceAdherence

#### "Introduction"

- [x] voice.first_person_voice: "I did"

#### "Only in sheet"

- [x] voice.first_person_voice: "I did it"
"""


def _load():
    spec = importlib.util.spec_from_file_location("t6_agreement", ROOT / "scripts" / "t6_agreement.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _judge(criteria: dict[str, list[tuple[str, int, str]]]) -> dict:
    out = {}
    for key, rows in criteria.items():
        reason = "\n\n".join(f"{title}:\n**{score}:** {why}" for title, score, why in rows)
        out[key] = {"score": sum(r[1] for r in rows) / len(rows), "reason": reason + "\n\n"}
    return out


def _write_outputs(tmp_path: Path) -> Path:
    slug_dir = tmp_path / SLUG
    slug_dir.mkdir(parents=True)
    (slug_dir / "judge_follows_gt.json").write_text(
        json.dumps(
            _judge(
                {
                    "follows_gt_content": [("Introduction", 1, "same"), ("Second Part", 0, "missing")],
                    "follows_gt_flow": [("Introduction", 0, "extra"), ("Second Part", 0, "missing")],
                    "follows_gt_structure": [("Introduction", 0, "x"), ("Second Part", 0, "x")],
                }
            )
        )
    )
    (slug_dir / "judge_user_intent.json").write_text(
        json.dumps(
            _judge(
                {
                    "user_intent_guideline_adherence": [
                        ("Alpha thing / Beta thing", 1, "ok"),
                        ("Different title entirely", 1, "judge likes it"),
                    ],
                }
            )
        )
    )
    (slug_dir / "judge_voice_adherence.json").write_text(
        json.dumps(
            _judge(
                {
                    "voice_adherence_first_person_voice": [
                        ("Introduction", 1, "I"),
                        ("Only in judge", 1, "I"),
                        ("Another one", 1, "I"),
                    ],
                }
            )
        )
    )
    return tmp_path


def test_parse_sheet_reads_checkbox_state_and_sections():
    mod = _load()

    items = mod.parse_sheet(SHEET)

    assert len(items) == 7
    first = items[0]
    assert (first.slug, first.metric, first.criterion, first.section) == (
        SLUG,
        "follows_gt",
        "content",
        "Introduction",
    )
    assert first.value == 1
    assert items[1].value == 0
    assert items[1].position == 0
    assert items[2].position == 1


def test_parse_judge_splits_per_section_scores(tmp_path):
    mod = _load()
    outputs = _write_outputs(tmp_path)

    items = mod.parse_judges(outputs)

    voice = [i for i in items if i.metric == "voice"]
    assert [(i.section, i.value) for i in voice] == [("Introduction", 1), ("Only in judge", 1), ("Another one", 1)]
    assert {i.criterion for i in items if i.metric == "follows_gt"} == {"content", "flow", "structure"}


def test_compare_matches_by_title_then_position_and_reports_unmatched(tmp_path):
    mod = _load()
    outputs = _write_outputs(tmp_path)

    report = mod.compare(mod.parse_sheet(SHEET), mod.parse_judges(outputs))

    # follows_gt: Introduction x2 + Second Part x1 matched by title, judge has two extra criterion rows (structure)
    # user_intent: "Alpha thing + Beta thing" matches by normalized title, "Gamma" by position fallback
    # voice: Introduction matches by title
    assert report.per_metric["follows_gt"] == (3, 2)
    assert report.per_metric["user_intent"] == (2, 1)
    assert report.per_metric["voice"] == (1, 1)
    assert report.overall == (6, 4)
    disagreements = {(d.sheet.section, d.sheet.criterion) for d in report.disagreements}
    assert ("Second Part", "content") in disagreements
    assert ("Gamma", "guideline_adherence") in disagreements
    unmatched_sheet = {(i.section, i.criterion) for i in report.unmatched_sheet}
    unmatched_judge = {(i.section, i.criterion) for i in report.unmatched_judge}
    assert ("Only in sheet", "first_person_voice") in unmatched_sheet
    assert ("Only in judge", "first_person_voice") in unmatched_judge
    assert ("Second Part", "flow") in unmatched_judge
    assert ("Another one", "first_person_voice") in unmatched_judge


def test_baseline_flips_count_changed_items():
    mod = _load()
    current = SHEET.replace("- [x] follows_gt.content: same topic", "- [ ] follows_gt.content: same topic")

    flips = mod.baseline_flips(mod.parse_sheet(SHEET), mod.parse_sheet(current))

    assert [(f.section, f.criterion, f.before, f.after) for f in flips] == [("Introduction", "content", 1, 0)]


def test_cli_prints_per_metric_overall_and_flips(tmp_path, capsys):
    mod = _load()
    outputs = _write_outputs(tmp_path / "out")
    sheet = tmp_path / "sheet.md"
    sheet.write_text(SHEET.replace('- [x] voice.first_person_voice: "I did"', '- [ ] voice.first_person_voice: "I did"'))
    baseline = tmp_path / "base.md"
    baseline.write_text(SHEET)

    code = mod.main(["--sheet", str(sheet), "--outputs", str(outputs), "--baseline-sheet", str(baseline)])

    out = capsys.readouterr().out
    assert code == 0
    assert "follows_gt" in out and "user_intent" in out and "voice" in out
    assert "overall" in out.lower()
    assert "Disagreements" in out
    assert "Flips vs baseline: 1" in out
    assert "Unmatched" in out
