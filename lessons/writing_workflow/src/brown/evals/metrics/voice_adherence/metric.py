"""Implementation of the VoiceAdherence evaluation metric.

One judge call per article scores every H2 section against every voice criterion
(binary 0/1) and aggregates per criterion, exactly like `follows_gt`.
"""

from pathlib import Path
from typing import Any, cast

from opik.evaluation.metrics import score_result

from brown.evals.metrics.base import BrownBaseMetric
from brown.models import ModelConfig, SupportedModels

from . import prompts
from .types import VoiceAdherenceArticleScores

DEFAULT_PROFILES_DIR = Path(__file__).parents[5] / "inputs" / "profiles" / "underdoc"


class VoiceAdherenceMetricLLMJudge(BrownBaseMetric):
    """Judges how well an article follows the Underdoc authorial voice.

    Args:
        model: The judge model. Defaults to GOOGLE_GEMINI_37_FLASH.
        name: Metric name, used as score prefix. Defaults to "voice_adherence".
        model_config: Model configuration. Defaults to temperature 0.0, medium thinking.
        track: Whether to track the metric in observability tools.
        project_name: Optional tracking project name.
        profiles_dir: Directory with the generated Underdoc voice profiles. Defaults to
            `inputs/profiles/underdoc`.

    """

    def __init__(
        self,
        model: SupportedModels = SupportedModels.GOOGLE_GEMINI_37_FLASH,
        name: str = "voice_adherence",
        model_config: ModelConfig | None = None,
        track: bool = True,
        project_name: str | None = None,
        profiles_dir: Path | None = None,
    ) -> None:
        model_config = model_config or ModelConfig(temperature=0.0, thinking_level="medium", include_thoughts=False, max_retries=3)
        super().__init__(
            model=model,
            name=name,
            structured_output_type=VoiceAdherenceArticleScores,
            few_shot_examples=prompts.DEFAULT_FEW_SHOT_EXAMPLES,
            model_config=model_config,
            track=track,
            project_name=project_name,
        )
        self.profiles_dir = Path(profiles_dir) if profiles_dir else DEFAULT_PROFILES_DIR
        self.voice_rules = prompts.load_voice_rules(self.profiles_dir)

    async def ascore(
        self,
        output: str,
        input: str | None = None,
        context: dict[str, Any] | None = None,
        **ignored_kwargs: Any,
    ) -> score_result.ScoreResult | list[score_result.ScoreResult]:
        """Score the generated article against the voice rules.

        Args:
            output: The generated article (Markdown).
            input: The article guideline. Support for biographical claims (`no_invented_biography`).
            context: Dict with a "research" key. Support for biographical claims (`no_invented_biography`).
            **ignored_kwargs: Ignored (e.g. expected_output; no ground truth needed).

        Returns:
            One ScoreResult per criterion, aggregated across sections.

        """
        model_client = self.init_model()

        llm_query = prompts.get_eval_prompt(
            output=output,
            voice_rules=self.voice_rules,
            few_shot_examples=self.few_shot_examples,
            guideline=input,
            research=(context or {}).get("research"),
        )
        response = cast(
            VoiceAdherenceArticleScores,
            await model_client.ainvoke([{"role": "user", "content": llm_query}]),
        )

        if not response:
            raise ValueError("Model failed to return a structured response.")

        return response.to_score_result(self.name)
