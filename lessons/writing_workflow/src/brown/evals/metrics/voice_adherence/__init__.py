"""Voice adherence evaluation metric.

This metric judges whether a generated article follows the Underdoc authorial voice
(first person singular, concrete specifics, no AI-slop, spoken rhythm, no invented
biography). It needs no ground truth: only the article and the voice profiles.
"""

from .metric import VoiceAdherenceMetricLLMJudge

__all__ = ["VoiceAdherenceMetricLLMJudge"]
