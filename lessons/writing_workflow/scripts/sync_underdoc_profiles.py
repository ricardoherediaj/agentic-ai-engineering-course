#!/usr/bin/env python3

"""Build Brown's Underdoc profile set (inputs/profiles/underdoc/) from the Underdoc harness repo.

The harness stays canonical. This script only concatenates and re-heads its voice references into the six
files Brown loads from `profiles_uri`. Output is deterministic: same harness bytes in, same bytes out.

Usage:
    uv run python scripts/sync_underdoc_profiles.py [--harness PATH] [--output PATH]

The harness path defaults to $UNDERDOC_HARNESS_DIR, then ~/Documents/TheUnderdoc/harness.
"""

import argparse
import os
import re
from pathlib import Path

DEFAULT_HARNESS = "~/Documents/TheUnderdoc/harness"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "inputs" / "profiles" / "underdoc"
REFERENCES = "skill/references"
SKILL = "skill/SKILL.md"
AUTHOR_PROFILE = f"{REFERENCES}/author-profile.md"
CHARACTER_FILE = "ricardo_heredia.md"

BUCKET_ROUTING = """## Bucket routing (which structure to follow)

Pick the bucket first (see the bucket table in the article profile), then follow its structure. Structure templates are advisory;
the voice rules win on any conflict.

| Bucket | Structure to follow |
|---|---|
| Builds (`builds`) | Build story structure: pain, manual process, build, what broke, takeaway |
| Explainers (`explainers`) | Explainer post structure: friction, definition plus analogy, worked example, takeaway |
| Bridge (`bridge`) | Conceptual post structure: idea, framework, story as evidence, reader's mirror |
| Field notes (`field-notes`) | Short (400-900 words); open on the take, no template; end on the reader's next action or a flat note |
"""

TERMINOLOGY_NOTE = (
    "The measured terminology rules (voice-terminology.md) come first; the word-level rules from the other harness "
    "files (small rules, banned vocabulary, words and usage) follow."
)


def read(harness: Path, rel: str) -> str:
    return (harness / rel).read_text(encoding="utf-8").strip("\n")


def demote(text: str, levels: int = 1) -> str:
    """Push markdown headings down by `levels`, ignoring fenced code blocks."""
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and re.match(r"#{1,6} ", line):
            line = "#" * min(6, len(line) - len(line.lstrip("#")) + levels) + line.lstrip("#")
        out.append(line)
    return "\n".join(out)


def section(text: str, heading: str) -> str:
    """Return a `## heading` block (heading line included) up to the next `## ` heading."""
    match = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Section '## {heading}' not found")
    return f"## {heading}{match.group(1)}".rstrip("\n")


def header(sources: list[str], extra: str = "") -> str:
    files = ", ".join(sources)
    note = f"\n\n{extra}" if extra else ""
    return (
        f"<!-- GENERATED FILE, do not edit by hand. Source: Underdoc harness repo (TheUnderdoc/harness). "
        f"Files: {files}. Regenerate with scripts/sync_underdoc_profiles.py. -->{note}\n"
    )


def build_files(harness: Path) -> dict[str, str]:
    """Return {relative output path: content} for the six Brown profile files."""
    ref = lambda name: f"{REFERENCES}/{name}"  # noqa: E731
    skill = read(harness, SKILL)
    mechanics = read(harness, ref("voice-mechanics.md"))
    blacklist = read(harness, ref("ai-slop-blacklist.md"))

    files: dict[str, str] = {}

    srcs = [ref("voice-mechanics.md"), ref("ai-slop-blacklist.md")]
    blacklist_parts = [
        section(blacklist, h)
        for h in ("Banned opening moves", "Banned sentence structures", "Banned vocabulary (unless quoting or technically required)")
    ]
    files["mechanics_profile.md"] = (
        header(
            srcs,
            "Where the slop blacklist and the voice rules disagree, the voice rules in this file win. "
            "Only the blacklist's banned lists are included; its older style rules are superseded by the voice rules.",
        )
        + "\n"
        + mechanics
        + "\n\n## Slop blacklist (banned openings, structures, vocabulary)\n\n"
        + demote("\n\n".join(blacklist_parts), 1)
        + "\n"
    )

    srcs = [
        ref("voice-structure.md"),
        SKILL,
        ref("build-story-structure.md"),
        ref("explainer-post-structure.md"),
        ref("conceptual-post-structure.md"),
    ]
    files["structure_profile.md"] = (
        header(srcs)
        + "\n"
        + read(harness, ref("voice-structure.md"))
        + "\n\n"
        + BUCKET_ROUTING
        + "\n"
        + demote(read(harness, ref("build-story-structure.md")), 1)
        + "\n\n"
        + demote(read(harness, ref("explainer-post-structure.md")), 1)
        + "\n\n"
        + demote(read(harness, ref("conceptual-post-structure.md")), 1)
        + "\n"
    )

    srcs = [ref("voice-tonality.md")]
    files["tonality_profile.md"] = header(srcs) + "\n" + read(harness, ref("voice-tonality.md")) + "\n"

    srcs = [SKILL, ref("on-writing-well.md")]
    article_parts = [section(skill, h) for h in ("Buckets", "Gate zero: the takeaway test", "Common mistakes")]
    files["article_profile.md"] = (
        header(srcs)
        + "\n# Article profile\n\nCore rules for every Underdoc article: pick a bucket, pass the takeaway test, make the post standalone, "
        "never invent facts. The numbers in the voice files are descriptive, never quotas.\n\n"
        + "\n\n".join(article_parts)
        + "\n\n## Standalone check\n\nEvery post lands with zero prior posts read. Never open on series context "
        '("In my last post..."); one linked line, after the hook, at most.\n\n'
        + "## No invented facts\n\nHooks and story beats come only from facts on record (topic file, research, the author profile, or "
        "what the author said). A premise that exists to make the hook work is a fabrication. If a fact is missing, leave it out.\n\n"
        + demote(read(harness, ref("on-writing-well.md")), 1)
        + "\n"
    )

    srcs = [ref("voice-terminology.md"), ref("voice-mechanics.md"), ref("ai-slop-blacklist.md"), ref("on-writing-well.md")]
    terminology = re.sub(r"\A# [^\n]*\n+", "", read(harness, ref("voice-terminology.md")))
    terminology_parts = [
        terminology,
        section(mechanics, "Small rules `[advisory]`"),
        section(blacklist, "Banned vocabulary (unless quoting or technically required)"),
        section(read(harness, ref("on-writing-well.md")), "Words and usage"),
    ]
    files["terminology_profile.md"] = (
        header(srcs, TERMINOLOGY_NOTE)
        + "\n# Terminology profile\n\n"
        + demote("\n\n".join(terminology_parts), 1)
        + "\n\n"
        + "## Naming consistency\n\nCall one thing by one name for the whole piece. Do not rename the same object for variety "
        '(synonym cycling). Name tools, books and people exactly; never "an LLM" or "a book I read".\n'
    )

    srcs = [AUTHOR_PROFILE]
    files[f"character_profiles/{CHARACTER_FILE}"] = header(srcs) + "\n" + read(harness, AUTHOR_PROFILE) + "\n"
    return files


def sync(harness: Path, output: Path) -> list[Path]:
    """Write the profile files under `output`. Returns the written paths."""
    harness = harness.expanduser()
    if not harness.is_dir():
        raise FileNotFoundError(f"Harness directory not found: {harness}")
    written = []
    for rel, content in build_files(harness).items():
        path = output / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--harness", default=os.environ.get("UNDERDOC_HARNESS_DIR", DEFAULT_HARNESS), help="Path to the Underdoc harness repo."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output profiles directory.")
    args = parser.parse_args()
    for path in sync(Path(args.harness), args.output):
        print(path)


if __name__ == "__main__":
    main()
