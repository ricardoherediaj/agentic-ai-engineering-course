# ruff: noqa: E501
"""Prompt template and few-shot examples for the VoiceAdherence evaluation metric.

The voice rules are loaded from the generated Underdoc profiles
(`inputs/profiles/underdoc/`, synced from the harness). The few-shot examples pair each
published ground truth (positive) with an off-voice rewrite (negative), labeled by hand.
"""

import re
from pathlib import Path

from brown.evals.metrics.base import CriterionScore

from .types import (
    VoiceAdherenceArticleScores,
    VoiceAdherenceCriterionScores,
    VoiceAdherenceMetricFewShotExample,
    VoiceAdherenceMetricFewShotExamples,
    VoiceAdherenceSectionScores,
)

# Profiles that carry voice rules. Structure/article profiles are about layout, not voice.
VOICE_PROFILE_FILES = ("tonality_profile.md", "mechanics_profile.md", "terminology_profile.md")

SYSTEM_PROMPT = """You are an expert editor and evaluator of authorial voice. Your task is to judge whether a generated
article follows the voice of its author, using ONLY the voice rules provided below. You do not judge topic coverage, 
correctness or structure against any reference article.

## INSTRUCTIONS

1. Sections are divided by H2 headers ("##"). Anything between two H2 headers is a section. The introduction between the
title and the first H2 is the first section, titled "Introduction". Never include the title or subtitle in a section. If the
article has no H2 headers, use the highest heading level present below the title as the section separator instead.
2. For every section, assign a binary score (0 or 1) for each criterion below. Criteria are completely independent: a 0 in 
one criterion never affects another. Score each section in isolation.
3. Be strict and literal: a single clear violation inside a section makes that criterion 0 for the section. A criterion is 1 
only if the whole section is free of that violation.
4. Give a brief reason per score that quotes the exact words that justify it, whatever the score. Quote violations for 0 
and the evidence of compliance for 1.
5. Quoted material (someone else's words, titles, links, code blocks and diagrams) is not the author's voice. Ignore it
when scoring.

## CRITERIA

1. **first_person_voice** (rule: first person singular, gate G-04): the narrator is "I". "We" is acceptable only when it means 
the author plus named others, or writer and reader together in a walkthrough moment. Score 0 if "we", "our team" or "our" is 
the default narration of the author's own work or views.
2. **concrete_specifics** (rule: specificity, named things and exact numbers): tools, books and people are named, and claims 
carry exact numbers. Score 0 if the section replaces them with abstractions ("a book I read", "an LLM", "top providers", 
"significant improvements", "over a hundred", "numerous").
3. **no_slop_vocabulary** (rule: banned vocabulary, gate G-05): score 0 if the section contains any word or phrase from the 
banned vocabulary list in the voice rules (for example leverage, harness as a verb, delve, dive into, crucial, critical, 
seamlessly, robust, significant, game-changer, transformative, unlock, elevate, "whether you're X or Y"), unless it is quoted 
or technically required.
4. **no_slop_structures** (rule: banned opening moves and sentence structures): score 0 if the section contains any of: "In today's
fast-paced world" style openers, roadmap throat-clearing ("I'll go over..."), "It isn't just X, it's Y", "This is where X comes 
in", meta transitions ("Now that we've explored X, let's move on"), a two-beat inversion punch or an "X, not Y" tail, a trailing 
tag sentence that restates the previous one, or the Everyone/Nobody hook. Vocabulary alone does not count here.
5. **spoken_rhythm_and_punctuation** (rules: paragraph statistics and punctuation): paragraphs are short, mostly one to two 
sentences, never more than four and roughly under 45 words, and the section has no em dashes ("—") and no semicolons. Score 0 
if the section has long polished paragraphs, an em dash or a semicolon.
6. **no_invented_biography** (rule: never invent a biographical premise): the author is a solo writer. Score 0 if the section
contains ANY biographical or first-person experiential claim, meaning something the author did, owns, pays for, verified, tested,
asked, felt, or lived at a specific time or place ("I pay for Cursor", "I verified the prices in November 2025", "I asked the
agent"), that is NOT supported by the article guideline or the research below. Also score 0 for an invented team, method,
advice received or credential. The article cannot vouch for itself: a claim being stated directly in the article is NOT support.
Look for the claim in the guideline or research; if it is not there, score 0. Stable identity facts in the voice rules'
author profile (solo author, career move from medicine to tech, football analytics) count as supported. Generic first-person
opinions and recommendations ("I think", "I recommend", "I prefer short functions") are not biographical claims and are fine.

## VOICE RULES (authoritative source for every criterion)

<voice_rules>
{voice_rules}
</voice_rules>

## ARTICLE GUIDELINE AND RESEARCH (the only support for biographical claims)

<article_guideline>
{guideline}
</article_guideline>

<research>
{research}
</research>

## FEW-SHOT EXAMPLES

Labeled examples showing how to apply the criteria. Each published article is followed by an off-voice rewrite of it:
<few-shot-examples>
{examples}
</few-shot-examples>

## INPUT

<generated_output>
{output}
</generated_output>

Think through your answer step by step, and provide the requested evaluation for every section and every criterion.
"""


def load_voice_rules(profiles_dir: Path) -> str:
    """Load the voice profile files into one string for the prompt.

    Args:
        profiles_dir: Directory containing the generated Underdoc profiles.

    Returns:
        The concatenated profile text, without the generated-file banner comments.

    """
    parts = []
    for filename in VOICE_PROFILE_FILES:
        text = (Path(profiles_dir) / filename).read_text()
        text = re.sub(r"<!-- GENERATED FILE.*?-->\n*", "", text, flags=re.DOTALL)
        parts.append(f'<profile name="{filename}">\n{text.strip()}\n</profile>')
    return "\n\n".join(parts)


def _section(
    title: str,
    first_person: tuple[int, str],
    specifics: tuple[int, str],
    vocabulary: tuple[int, str],
    structures: tuple[int, str],
    rhythm: tuple[int, str],
    biography: tuple[int, str],
) -> VoiceAdherenceSectionScores:
    def score(pair: tuple[int, str]) -> CriterionScore:
        return CriterionScore(score=pair[0], reason=pair[1])

    return VoiceAdherenceSectionScores(
        title=title,
        scores=VoiceAdherenceCriterionScores(
            first_person_voice=score(first_person),
            concrete_specifics=score(specifics),
            no_slop_vocabulary=score(vocabulary),
            no_slop_structures=score(structures),
            spoken_rhythm_and_punctuation=score(rhythm),
            no_invented_biography=score(biography),
        ),
    )


EXAMPLES_DIR = Path(__file__).parent / "examples"

# --- Post 1: "A Thank You, Two Ideas From a Book..." (bridge) ---

THANK_YOU_GT_SCORES = VoiceAdherenceArticleScores(
    sections=[
        _section(
            "Introduction",
            (1, "Narrated with 'I': 'I wanted to thank you', 'I wrote about football, AI, RAG systems'."),
            (1, "Names concrete topics: 'football, AI, RAG systems, agentic IDEs'."),
            (1, "No banned vocabulary in the section."),
            (1, "Plain opener ('What a year, captain…'), no banned opener, transition or inversion."),
            (1, "One to two sentence paragraphs, no em dash or semicolon."),
            (1, "Only states things the author did (wrote the newsletter), nothing invented."),
        ),
        _section(
            "The Book That Made Me Rethink About Purpose",
            (1, "'I recently finished reading', 'This was the book that really hit me'. Singular first person."),
            (1, "Names the book (So Good They Can't Ignore You), Cal Newport and Julián Campos with a link."),
            (1, "No banned vocabulary ('brilliant' is not on the list)."),
            (1, "'Here's the deal.' is a plain beat, no inversion punch or banned transition."),
            (1, "Short paragraphs and fragments, no em dash or semicolon."),
            (1, "'Too many decisions made using this mantra' is the author's own stated experience."),
        ),
        _section(
            "Passion Mindset vs. Craft Mindset",
            (1, "'This made me rethink how I approach my own career', 'I've been unknowingly following'."),
            (1, "Names Timothée Chalamet, the SAG Awards, Daniel Day-Lewis, Marlon Brando, Viola Davis, '5.5 years'."),
            (1, "No banned vocabulary."),
            (
                0,
                "'passion comes after you develop mastery, not before' is an 'X, not Y' tail, and 'The craft mindset flips this' sets up a reversal.",
            ),
            (1, "Paragraphs of one to three short sentences, no em dash or semicolon."),
            (1, "'Since I pivoted from medicine' is on record in the author profile."),
        ),
    ]
)

THANK_YOU_OFF_VOICE_SCORES = VoiceAdherenceArticleScores(
    sections=[
        _section(
            "Introduction",
            (0, "'our team wanted to take a brief moment', 'our publication': team 'we' replaces 'I'."),
            (0, "Only generic categories ('sports analytics', 'artificial intelligence implementations'), no exact numbers."),
            (0, "'seamlessly leverage', 'crucial' are banned."),
            (0, "'In today's fast-paced world' opener and 'It's not just a minor operational adjustment; it's a holistic blueprint'."),
            (0, "Long multi-clause paragraphs, an em dash ('experiments—valuable') and semicolons."),
            (0, "Invents a team and a 'mission' ('our team', 'our community') for a solo author."),
        ),
        _section(
            "The Book That Made Me Rethink About Purpose",
            (0, "'Our team recently had the opportunity': team narration."),
            (0, "'a seminal volume on professional mastery' hides the book title and author name."),
            (0, "'delve' and 'game-changer' are banned."),
            (1, "No banned structure appears here. The slop is vocabulary and register, not a banned sentence shape."),
            (0, "Em dash ('premise that...—a premise') and a semicolon ('counter-narrative; through empirical case studies')."),
            (0, "'Our team' invents a group reading the book."),
        ),
        _section(
            "Passion Mindset vs. Craft Mindset",
            (0, "'our team', 'we have been fortunate': team 'we' throughout."),
            (0, "'a prominent performing artist', 'a major industry awards event' replace Chalamet, the SAG Awards and the numbers."),
            (0, "'seamlessly follows' is banned."),
            (
                0,
                "'this is where the craft-centric mindset comes in', 'Now that we've explored..., let's move on' and 'not an innate phenomenon—it is'.",
            ),
            (0, "Em dashes, semicolons and long polished paragraphs."),
            (0, "'prompted our team to re-evaluate our long-term trajectory' invents a team history."),
        ),
    ]
)

# --- Post 2: "RAG is a Data Engineering Heavy Problem..." (builds) ---

RAG_GT_SCORES = VoiceAdherenceArticleScores(
    sections=[
        _section(
            "Introduction",
            (1, "'today, I want to talk about', 'I've launched': singular first person."),
            (1, "Names the previous post, ETL and the Pydantic airlock."),
            (0, "'the most critical part of the system' uses banned 'critical'."),
            (0, "'So, I'll go over the origin of the data, the sources I used...' is roadmap throat-clearing."),
            (0, "Em dash in 'Extract, Transform, Load — the process that prevents bad retrieval'."),
            (1, "Only describes the author's own system and post."),
        ),
        _section(
            "Where the Data Comes From",
            (1, "'I wanted to use match event data', 'The first wall I hit': singular first person."),
            (1, "Names WhoScored, Fotmob, xG, '1,300+ events per match', '108 matches', 'R. Madrid' vs 'Real Madrid'."),
            (1, "No banned vocabulary."),
            (1, "No banned opener, transition or inversion. 'It's a simple but effective way...' is a plain statement."),
            (1, "Short paragraphs, no em dash or semicolon."),
            (1, "Describes the author's own project work."),
        ),
        _section(
            "Extracting the Data",
            (1, "'I used just 108 matches', 'I save the JSON exactly as it comes': singular first person."),
            (1, "Names the Eredivisie, '108 matches', 'Raw Zone', the exact rule and the file name."),
            (1, "No banned vocabulary."),
            (1, "'Why the Dutch league?' is a mid-section question, not a self-answered hook, and no banned structure appears."),
            (1, "Short paragraphs, no em dash or semicolon."),
            (1, "Describes the author's own design decisions."),
        ),
    ]
)

RAG_OFF_VOICE_SCORES = VoiceAdherenceArticleScores(
    sections=[
        _section(
            "Introduction",
            (0, "'our team shared', 'we delve': team narration."),
            (
                0,
                "'enterprise sports intelligence solution' and 'single most crucial pillar' are abstractions, though the link names the earlier post.",
            ),
            (0, "'leverage', 'unlock', 'delve', 'crucial', 'robust', 'seamlessly', 'game-changer' are banned."),
            (
                0,
                "'In today's fast-paced world', 'It's not just about generative artificial intelligence; it's about...' and 'Now that we've established the core thesis, let us delve...'.",
            ),
            (0, "Em dash ('paradigm—a transformative game-changer') and semicolons."),
            (0, "'what our engineers consider' invents an engineering team."),
        ),
        _section(
            "Where the Data Comes From",
            (0, "'Our team set out', 'We re-architected': team narration."),
            (0, "'thousands of distinct actions', 'over a hundred fixtures' replace '1,300+' and '108'."),
            (0, "'crucial', 'leverages', 'seamlessly', 'significant' are banned."),
            (0, "'This is where robust entity resolution comes in' is a banned structure."),
            (0, "Em dashes ('impact—high-level') and semicolons, with long paragraphs."),
            (0, "'our engineers' invents a team and 'stakeholders' who save time."),
        ),
        _section(
            "Extracting the Data",
            (0, "'Our engineering team scaled our scraping modules': team narration."),
            (0, "'numerous fixtures', 'a leading European talent-incubator league' replace '108 matches' and 'Eredivisie'."),
            (0, "'significant', 'seamlessly' are banned."),
            (0, "'Now that we've explored our ingestion sources, let's move on to the extraction mechanisms' is a banned meta transition."),
            (0, "Semicolon ('league renowned...; monitoring') and long paragraphs."),
            (0, "'our analysts', 'our engineering team' invents a team."),
        ),
    ]
)

# --- Biography grounding: same claims, one supported by the guideline/research and one not ---

BIOGRAPHY_GUIDELINE = """Write a short post on using an agentic IDE for football analytics.
Anchor: Ricardo has a Cursor Pro subscription (20 USD/month, checked on the Cursor pricing page in November 2025).
Anchor: he asked the agent to refactor the xG pipeline and it touched 14 files."""

BIOGRAPHY_RESEARCH = """Cursor pricing page (retrieved 2025-11-12): Pro plan, 20 USD per month.
Author notes: the xG pipeline refactor was run through the Cursor agent and touched 14 files."""

BIOGRAPHY_GROUNDED_SCORES = VoiceAdherenceArticleScores(
    sections=[
        _section(
            "What the Agent Costs",
            (1, "'I pay for Cursor', 'I checked the prices': singular first person."),
            (1, "Names Cursor, the Pro plan and '20 USD a month'."),
            (1, "No banned vocabulary."),
            (1, "No banned opener, transition or inversion."),
            (1, "Short paragraphs, no em dash or semicolon."),
            (
                1,
                "'I pay for Cursor' and 'I checked the prices in November 2025' are both in the guideline and research (Cursor Pro, 20 USD, November 2025). 'I think it is worth it' is a generic opinion.",
            ),
        ),
    ]
)

BIOGRAPHY_UNSUPPORTED_SCORES = VoiceAdherenceArticleScores(
    sections=[
        _section(
            "What the Agent Costs",
            (1, "'I pay', 'I tested': singular first person."),
            (1, "Names Cursor, Copilot, '10 USD a month' and 'March 2024'."),
            (1, "No banned vocabulary."),
            (1, "No banned opener, transition or inversion."),
            (1, "Short paragraphs, no em dash or semicolon."),
            (
                0,
                "'I also pay for Copilot' and 'I tested it for six months in March 2024' are experiential claims that appear nowhere in the guideline or research, even though the article states them directly. 'I recommend starting with the free tier' would be fine, but these two claims are invented.",
            ),
        ),
    ]
)

DEFAULT_FEW_SHOT_EXAMPLES = VoiceAdherenceMetricFewShotExamples(
    examples=[
        VoiceAdherenceMetricFewShotExample.from_markdown(
            output_file=EXAMPLES_DIR / "thank_you" / "article_ground_truth.md", scores=THANK_YOU_GT_SCORES
        ),
        VoiceAdherenceMetricFewShotExample.from_markdown(
            output_file=EXAMPLES_DIR / "thank_you" / "article_off_voice.md", scores=THANK_YOU_OFF_VOICE_SCORES
        ),
        VoiceAdherenceMetricFewShotExample.from_markdown(
            output_file=EXAMPLES_DIR / "rag_etl" / "article_ground_truth.md", scores=RAG_GT_SCORES
        ),
        VoiceAdherenceMetricFewShotExample.from_markdown(
            output_file=EXAMPLES_DIR / "rag_etl" / "article_off_voice.md", scores=RAG_OFF_VOICE_SCORES
        ),
        VoiceAdherenceMetricFewShotExample.from_markdown(
            output_file=EXAMPLES_DIR / "biography" / "article_grounded.md",
            scores=BIOGRAPHY_GROUNDED_SCORES,
            guideline=BIOGRAPHY_GUIDELINE,
            research=BIOGRAPHY_RESEARCH,
        ),
        VoiceAdherenceMetricFewShotExample.from_markdown(
            output_file=EXAMPLES_DIR / "biography" / "article_unsupported.md",
            scores=BIOGRAPHY_UNSUPPORTED_SCORES,
            guideline=BIOGRAPHY_GUIDELINE,
            research=BIOGRAPHY_RESEARCH,
        ),
    ]
)


NOT_PROVIDED = "(not provided: no biographical or experiential claim can be supported, so any such claim scores 0)"


def get_eval_prompt(
    output: str,
    voice_rules: str,
    few_shot_examples: VoiceAdherenceMetricFewShotExamples,
    guideline: str | None = None,
    research: str | None = None,
) -> str:
    """Generate the evaluation prompt for the voice_adherence metric.

    Args:
        output: The generated article to be evaluated.
        voice_rules: The voice profile text embedded as the authoritative rule source.
        few_shot_examples: Labeled examples to guide the judge.
        guideline: The article guideline the article was generated from (support for biographical claims).
        research: The research the article was generated from (support for biographical claims).

    Returns:
        The complete formatted prompt string ready for LLM invocation.

    """
    return SYSTEM_PROMPT.format(
        examples=few_shot_examples.to_context(),
        voice_rules=voice_rules,
        guideline=guideline or NOT_PROVIDED,
        research=research or NOT_PROVIDED,
        output=output,
    )
