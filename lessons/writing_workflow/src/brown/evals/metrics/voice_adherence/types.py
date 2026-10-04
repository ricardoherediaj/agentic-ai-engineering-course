"""Type definitions for the voice_adherence evaluation metric.

Each criterion is a binary 0/1 score per section, derived from one concrete rule in the
Underdoc voice profiles (`inputs/profiles/underdoc/`) and harness gates
(`checks/check.py`, `checks/calibration.md`).
"""

from pathlib import Path

import pydantic
from opik.evaluation.metrics import score_result

from brown.evals.metrics.base import (
    BaseExample,
    BaseFewShotExamples,
    CriteriaScores,
    CriterionScore,
    aggregate_section_scores_to_results,
)


class VoiceAdherenceCriterionScores(CriteriaScores):
    """Scores for all voice criteria of a single section.

    Attributes:
        first_person_voice: Source: mechanics_profile "First person singular" (gate G-04).
        concrete_specifics: Source: tonality_profile "Specificity: named things and exact numbers".
        no_slop_vocabulary: Source: mechanics_profile slop blacklist, banned vocabulary (gate G-05).
        no_slop_structures: Source: mechanics_profile slop blacklist, banned openings and structures.
        spoken_rhythm_and_punctuation: Source: calibration.md paragraph stats and mechanics_profile punctuation rule.
        no_invented_biography: Source: tonality_profile "Never invent a biographical premise".

    """

    first_person_voice: CriterionScore = pydantic.Field(
        description=(
            "1 if the section narrates in first person singular ('I') and uses 'we' only for Ricardo plus named others "
            "or reader-and-writer in a walkthrough moment. 0 if 'we'/'our team' is the default narration. "
            "Source: mechanics_profile 'First person singular' (G-04)."
        )
    )
    concrete_specifics: CriterionScore = pydantic.Field(
        description=(
            "1 if claims carry exact numbers and tools, books or people are named ('99.4% faithfulness', 'Cal Newport'). "
            "0 if the section relies on abstractions ('a book I read', 'significant improvements', 'top providers'). "
            "Source: tonality_profile 'Specificity: named things and exact numbers'."
        )
    )
    no_slop_vocabulary: CriterionScore = pydantic.Field(
        description=(
            "1 if the section contains none of the banned slop vocabulary (leverage, harness as a verb, delve, crucial, "
            "critical, seamlessly, robust, significant, game-changer, ...). 0 if it contains at least one. "
            "Source: mechanics_profile 'Banned vocabulary' (G-05)."
        )
    )
    no_slop_structures: CriterionScore = pydantic.Field(
        description=(
            "1 if the section avoids banned openings and structures: 'In today's fast-paced world', roadmap throat-clearing "
            "('I'll cover...'), 'It's not just X, it's Y', 'This is where X comes in', meta transitions "
            "('Now that we've explored X, let's move on'), two-beat inversion punches and X/not-Y tails. 0 otherwise. "
            "Source: mechanics_profile 'Banned opening moves' and 'Banned sentence structures'."
        )
    )
    spoken_rhythm_and_punctuation: CriterionScore = pydantic.Field(
        description=(
            "1 if paragraphs are short (mostly 1-2 sentences, never more than 4, roughly under 45 words) and the section "
            "has no em dashes and no semicolons. 0 if it has long polished paragraphs, an em dash or a semicolon. "
            "Source: calibration.md descriptive statistics and mechanics_profile 'Punctuation: no em-dashes, no semicolons'."
        )
    )
    no_invented_biography: CriterionScore = pydantic.Field(
        description=(
            "1 if every biographical or first-person experiential claim (something the author did, owns, pays for, "
            "verified, felt, at a time or place) is supported by the article guideline or the research, or is a stable "
            "author-profile fact. 0 if any such claim is unsupported, or if it invents a team, a method or advice "
            "received. Generic opinions ('I think', 'I recommend') are fine. "
            "Source: tonality_profile 'Never invent a biographical premise'."
        )
    )


class VoiceAdherenceSectionScores(pydantic.BaseModel):
    """Section evaluation with scores across all voice criteria."""

    title: str = pydantic.Field(description="The title of the section being evaluated.")
    scores: VoiceAdherenceCriterionScores = pydantic.Field(description="The scores of the section being evaluated.")

    def to_context(self) -> str:
        """Convert the section scores to a formatted XML string for use as context in prompts."""
        scores_xml = self.scores.to_context()

        return f"""
<section_scores>
    <section_title>{self.title}</section_title>
{scores_xml}</section_scores>
"""


class VoiceAdherenceArticleScores(pydantic.BaseModel):
    """Article-level scores for the voice_adherence metric (all sections, all criteria)."""

    sections: list[VoiceAdherenceSectionScores]

    def to_context(self) -> str:
        """Convert all section scores to a formatted string for use as context in prompts."""
        context_body = "".join([f"\t{section.to_context()}\n" for section in self.sections])

        return f"<article_scores>\n{context_body}\n</article_scores>"

    def to_score_result(self, prefix: str) -> list[score_result.ScoreResult]:
        """Aggregate section scores into one ScoreResult per criterion."""
        return aggregate_section_scores_to_results(self.sections, prefix)


class VoiceAdherenceMetricFewShotExample(BaseExample):
    """A single few-shot example: an article and its labeled scores (no ground truth needed)."""

    output: str
    scores: VoiceAdherenceArticleScores
    guideline: str | None = None
    research: str | None = None

    @classmethod
    def from_markdown(
        cls,
        output_file: Path,
        scores: VoiceAdherenceArticleScores,
        guideline: str | None = None,
        research: str | None = None,
    ) -> "VoiceAdherenceMetricFewShotExample":
        """Create an example from a markdown file and its labeled scores (optionally with its guideline and research)."""
        return cls(output=output_file.read_text(), scores=scores, guideline=guideline, research=research)

    def to_context(self) -> str:
        """Convert the example to a formatted string for use as context in prompts."""
        support = ""
        if self.guideline is not None or self.research is not None:
            support = f"""
<article_guideline>
{self.guideline or ""}
</article_guideline>
<research>
{self.research or ""}
</research>
"""
        return f"""{support}
<output>
{self.output}
</output>
{self.scores.to_context()}
"""


class VoiceAdherenceMetricFewShotExamples(BaseFewShotExamples[VoiceAdherenceMetricFewShotExample]):
    """Collection of few-shot examples for the voice_adherence metric."""

    pass
