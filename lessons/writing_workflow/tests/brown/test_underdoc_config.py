import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

from brown.config_app import AppConfig

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "underdoc-gemini-flash.yaml"
SCRIPT = ROOT / "scripts" / "sync_underdoc_profiles.py"
PROFILES = ROOT / "inputs" / "profiles" / "underdoc"
HARNESS = Path(os.environ.get("UNDERDOC_HARNESS_DIR", "~/Documents/TheUnderdoc/harness")).expanduser()
FIXED_FILES = [
    "article_profile.md",
    "mechanics_profile.md",
    "structure_profile.md",
    "terminology_profile.md",
    "tonality_profile.md",
]
COURSE_PROHIBITION = "Avoid singular first person"


@pytest.fixture
def in_project_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)


def test_config_parses_with_app_config_model(in_project_root: None) -> None:
    config = AppConfig.from_yaml(CONFIG)

    assert config.context.profiles_uri == Path("inputs/profiles/underdoc")
    assert config.context.character_profile == "ricardo_heredia.md"
    assert config.context.examples_uri == Path("inputs/examples/underdoc")


def test_config_only_differs_from_course_config_in_voice_keys() -> None:
    import yaml

    underdoc = yaml.safe_load(CONFIG.read_text())
    course = yaml.safe_load((ROOT / "configs" / "course-gemini-flash.yaml").read_text())

    for key in ("profiles_uri", "character_profile", "examples_uri"):
        underdoc["context"].pop(key)
        course["context"].pop(key)
    assert underdoc == course


def test_all_profile_files_resolve_and_are_non_empty(in_project_root: None) -> None:
    config = AppConfig.from_yaml(CONFIG)
    profiles = config.context.profiles_uri

    paths = [profiles / name for name in FIXED_FILES]
    paths.append(profiles / "character_profiles" / config.context.character_profile)

    assert len(paths) == 6
    for path in paths:
        assert path.is_file(), path
        assert path.read_text().strip(), path


def test_examples_are_the_two_reserved_posts() -> None:
    names = sorted(p.name for p in (ROOT / "inputs" / "examples" / "underdoc").glob("*.md"))

    assert names == [
        "2025-08-31-uv-the-tool-that-helps-you-manage.md",
        "2026-07-12-i-automated-my-personal-finance-tracking.md",
    ]


def test_no_course_team_voice_mandate_leaks() -> None:
    assert COURSE_PROHIBITION in (ROOT / "inputs" / "profiles" / "mechanics_profile.md").read_text()

    for path in (PROFILES / "mechanics_profile.md", PROFILES / "character_profiles" / "ricardo_heredia.md"):
        text = path.read_text()
        assert COURSE_PROHIBITION not in text
        assert "we,' our,' and 'us'" not in text


def test_generated_files_carry_do_not_edit_header() -> None:
    for name in FIXED_FILES:
        assert "do not edit" in (PROFILES / name).read_text().splitlines()[0].lower()


@pytest.mark.skipif(not HARNESS.is_dir(), reason="harness directory not available")
def test_sync_script_is_deterministic_and_matches_committed(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("sync_underdoc_profiles", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["sync_underdoc_profiles"] = module
    spec.loader.exec_module(module)

    first, second = tmp_path / "a", tmp_path / "b"
    module.sync(HARNESS, first)
    module.sync(HARNESS, second)

    files = sorted(p.relative_to(first) for p in first.rglob("*.md"))
    assert len(files) == 6
    for rel in files:
        assert (first / rel).read_bytes() == (second / rel).read_bytes()
        assert (first / rel).read_bytes() == (PROFILES / rel).read_bytes(), f"committed {rel} is stale; rerun the sync script"


def test_sync_script_cli_help_runs() -> None:
    result = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)

    assert result.returncode == 0
    assert "--harness" in result.stdout
