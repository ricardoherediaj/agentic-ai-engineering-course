import pytest
from pydantic import ValidationError

from brown.evals.metrics import build_evaluation_metrics
from brown.evals.metrics.base import CriterionScore
from brown.evals.metrics.voice_adherence import VoiceAdherenceMetricLLMJudge, prompts
from brown.evals.metrics.voice_adherence.types import (
    VoiceAdherenceArticleScores,
    VoiceAdherenceCriterionScores,
    VoiceAdherenceSectionScores,
)
from brown.models import ModelConfig, SupportedModels

CRITERIA = [
    "first_person_voice",
    "concrete_specifics",
    "no_slop_vocabulary",
    "no_slop_structures",
    "spoken_rhythm_and_punctuation",
    "no_invented_biography",
]


def make_scores(values: dict[str, int]) -> VoiceAdherenceCriterionScores:
    return VoiceAdherenceCriterionScores(**{c: CriterionScore(score=values.get(c, 1), reason=f"{c} reason") for c in CRITERIA})


@pytest.fixture
def mixed_scores() -> VoiceAdherenceArticleScores:
    return VoiceAdherenceArticleScores(
        sections=[
            VoiceAdherenceSectionScores(title="Introduction", scores=make_scores({"first_person_voice": 0, "no_slop_vocabulary": 0})),
            VoiceAdherenceSectionScores(title="Body", scores=make_scores({"no_slop_vocabulary": 0})),
        ]
    )


def make_metric(scores: VoiceAdherenceArticleScores) -> VoiceAdherenceMetricLLMJudge:
    return VoiceAdherenceMetricLLMJudge(model=SupportedModels.FAKE_MODEL, model_config=ModelConfig(mocked_response=scores))


def test_criterion_score_rejects_non_binary() -> None:
    with pytest.raises(ValidationError):
        CriterionScore(score=2, reason="nope")


def test_criteria_scores_require_all_criteria() -> None:
    with pytest.raises(ValidationError):
        VoiceAdherenceCriterionScores(first_person_voice=CriterionScore(score=1, reason="x"))


def test_criteria_have_source_rule_in_description() -> None:
    for field in VoiceAdherenceCriterionScores.model_fields.values():
        assert "Source:" in (field.description or "")


def test_aggregation_per_criterion(mixed_scores: VoiceAdherenceArticleScores) -> None:
    results = make_metric(mixed_scores).score(output="Some article.")

    assert isinstance(results, list)
    by_name = {r.name: r.value for r in results}
    assert set(by_name) == {f"voice_adherence_{c}" for c in CRITERIA}
    assert by_name["voice_adherence_first_person_voice"] == 0.5
    assert by_name["voice_adherence_no_slop_vocabulary"] == 0.0
    assert by_name["voice_adherence_concrete_specifics"] == 1.0


def test_ground_truth_is_not_required(mixed_scores: VoiceAdherenceArticleScores) -> None:
    results = make_metric(mixed_scores).score(output="Article.", expected_output="ignored")
    assert len(results) == len(CRITERIA)


def test_empty_sections_return_empty_list() -> None:
    assert make_metric(VoiceAdherenceArticleScores(sections=[])).score(output="") == []


def test_fake_model_requires_mocked_response() -> None:
    with pytest.raises(AssertionError, match="Mocked response is required for fake model"):
        VoiceAdherenceMetricLLMJudge(model=SupportedModels.FAKE_MODEL, model_config=ModelConfig(mocked_response=None))


def test_prompt_contains_criteria_and_voice_rules(mixed_scores: VoiceAdherenceArticleScores) -> None:
    metric = make_metric(mixed_scores)
    prompt = prompts.get_eval_prompt(output="MY ARTICLE", voice_rules=metric.voice_rules, few_shot_examples=metric.few_shot_examples)

    for criterion in CRITERIA:
        assert criterion in prompt
    assert "First person singular" in prompt  # embedded from mechanics profile
    assert "Banned vocabulary" in prompt
    assert "MY ARTICLE" in prompt
    assert "GENERATED FILE" not in prompt


def test_voice_rules_path_is_configurable(tmp_path, mixed_scores: VoiceAdherenceArticleScores) -> None:
    for name in prompts.VOICE_PROFILE_FILES:
        (tmp_path / name).write_text(f"CUSTOM RULES {name}")
    metric = VoiceAdherenceMetricLLMJudge(
        model=SupportedModels.FAKE_MODEL,
        model_config=ModelConfig(mocked_response=mixed_scores),
        profiles_dir=tmp_path,
    )
    assert "CUSTOM RULES tonality_profile.md" in metric.voice_rules


def test_few_shot_examples_are_valid_and_cover_on_and_off_voice() -> None:
    examples = prompts.DEFAULT_FEW_SHOT_EXAMPLES.examples
    assert len(examples) == 4
    for example in examples:
        assert example.output.strip()
        assert example.scores.sections
    assert "<example_4>" in prompts.DEFAULT_FEW_SHOT_EXAMPLES.to_context()


def test_registry_exposes_voice_adherence(mixed_scores: VoiceAdherenceArticleScores) -> None:
    metrics = build_evaluation_metrics(["voice_adherence"], SupportedModels.FAKE_MODEL, ModelConfig(mocked_response=mixed_scores))
    assert len(metrics) == 1 and metrics[0].name == "voice_adherence"


def test_registry_still_rejects_unknown_metric(mixed_scores: VoiceAdherenceArticleScores) -> None:
    with pytest.raises(ValueError, match="Unknown metric name"):
        build_evaluation_metrics(["nope"], SupportedModels.FAKE_MODEL, ModelConfig(mocked_response=mixed_scores))
