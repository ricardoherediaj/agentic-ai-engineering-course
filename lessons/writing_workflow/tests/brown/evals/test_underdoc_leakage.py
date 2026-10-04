import importlib.util
import json
from pathlib import Path

from brown.evals.dataset import EvalDataset

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "check_underdoc_leakage.py"
DATASET_DIR = ROOT / "inputs" / "evals" / "underdoc_dataset"


def _load_script():
    spec = importlib.util.spec_from_file_location("check_underdoc_leakage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


leakage = _load_script()

GROUND_TRUTH = (
    "# A Title\n\n"
    "I built a small pipeline last winter that scrapes match events every night and stores them in a database "
    "so that I could finally stop copying numbers by hand.\n\n"
    "```python\nprint('this code block is ignored by the check at all')\n```\n"
)


def _make_dataset(tmp_path: Path, guideline: str, ground_truth: str = GROUND_TRUTH) -> Path:
    sample_dir = tmp_path / "data" / "sample"
    sample_dir.mkdir(parents=True)
    (sample_dir / "article_guideline.md").write_text(guideline)
    (sample_dir / "article_ground_truth.md").write_text(ground_truth)
    (sample_dir / "research.md").write_text("# Research\n")
    (tmp_path / "metadata.json").write_text(json.dumps([{"name": "Sample", "directory": "data/sample"}]))
    return tmp_path


def test_clean_guideline_passes(tmp_path: Path) -> None:
    guideline = "# Brief\n\nTitle idea: automating nightly data capture.\nSections: motivation, approach, outcome."
    results = leakage.check_dataset(_make_dataset(tmp_path, guideline))

    assert len(results) == 1
    assert results[0].passed
    assert results[0].shared_ngram_words == 0


def test_long_guideline_fails(tmp_path: Path) -> None:
    guideline = "# Brief\n\n" + " ".join(f"word{i}" for i in range(leakage.MAX_GUIDELINE_WORDS + 1))
    result = leakage.check_dataset(_make_dataset(tmp_path, guideline))[0]

    assert not result.passed
    assert result.guideline_words > leakage.MAX_GUIDELINE_WORDS


def test_copied_ngram_fails(tmp_path: Path) -> None:
    copied = "scrapes match events every night and stores them in a database"
    guideline = f"# Brief\n\nThe post should explain how it {copied} for readers."
    result = leakage.check_dataset(_make_dataset(tmp_path, guideline))[0]

    assert not result.passed
    assert result.shared_ngram_words >= leakage.NGRAM_SIZE


def test_code_urls_and_titles_are_ignored(tmp_path: Path) -> None:
    guideline = (
        "# A Title\n\nSee https://example.com/this/code/block/is/ignored for details.\n"
        "```python\nprint('this code block is ignored by the check at all')\n```\n"
    )
    result = leakage.check_dataset(_make_dataset(tmp_path, guideline))[0]

    assert result.passed


def test_main_exits_non_zero_on_failure(tmp_path: Path) -> None:
    guideline = "# Brief\n\nIt scrapes match events every night and stores them in a database."
    dataset_dir = _make_dataset(tmp_path, guideline)

    assert leakage.main([str(dataset_dir)]) == 1


def test_real_dataset_loads_with_expected_splits() -> None:
    dataset = EvalDataset.load_dataset(DATASET_DIR, name="underdoc", description="Underdoc eval dataset")
    metadata = json.loads((DATASET_DIR / "metadata.json").read_text())

    assert len(dataset.samples) == 26
    assert sum(sample.is_few_shot_example for sample in dataset.samples) == 2
    splits = [m["split"] for m in metadata]
    assert {s: splits.count(s) for s in set(splits)} == {"few_shot": 2, "validation": 2, "test": 10, "extended": 12}
    assert sum(m["noise_subset"] for m in metadata) == 3
    assert all(m["split"] == "test" for m in metadata if m["noise_subset"])
    reserved = {"2026-07-12-i-automated-my-personal-finance-tracking", "2025-08-31-uv-the-tool-that-helps-you-manage"}
    assert {m["split"] for m in metadata if Path(m["directory"]).name in reserved} == {"extended"}


def test_real_dataset_has_no_leakage() -> None:
    results = leakage.check_dataset(DATASET_DIR)

    assert len(results) == 26
    assert [r.name for r in results if not r.passed] == []
