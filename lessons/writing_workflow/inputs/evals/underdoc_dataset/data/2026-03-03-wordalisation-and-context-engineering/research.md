# Research dossier: Wordalisation and context engineering for the football RAG

Facts reconstructed from the published post and the linked sources.

## Wordalisation
- Term coined by David Sumpter (Soccermatics, Twelve Football): wordalisations are factual representations of data in words. Source: https://soccermatics.medium.com/introducing-wordalisations-automated-explanations-of-data-8e6687ad2d77
- Method: describe the quality and metrics in words (poor, average, good, outstanding), supply a small written training set explaining what metrics mean in football terms, add example reports, then feed everything to an existing LLM. Source: https://soccermatics.medium.com/introducing-wordalisations-automated-explanations-of-data-8e6687ad2d77
- Applied to the RAG project: raw floats (for example PPDA 4.8, xG 1.2) are classified into qualitative labels before the call, derived from real Eredivisie 2025-2026 distributions rather than arbitrary thresholds. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Model used: claude-haiku-4.5. Smoke-test example: Heracles vs PEC Zwolle; same pipeline data, very different prose. Source: https://docs.anthropic.com/en/docs/about-claude/models

## Context engineering (from a course lesson)
- Course: Agentic AI Engineering from Towards AI (context engineering lesson). Source: https://academy.towardsai.net/courses/agent-engineering
- Recommendation: prefer YAML over JSON for structured prompt input, as it is more token-efficient and reads closer to prose; he compared both on his `<tactical_labels>` block. Source: https://academy.towardsai.net/courses/agent-engineering
- "Lost in the middle": models underweight content in the middle of long contexts, so critical instructions go at the start (system prompt) and end (`<instructions>` block) with dynamic match data in between. Source: https://arxiv.org/abs/2307.03172
- Prompt caching: keep static content (system prompt, few-shot examples) first so the provider can cache the prefix. Source: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- Resulting data flow: numbers, then labels, then LLM, then football insight. Source: https://github.com/ricardoherediaj/football-rag-intelligence
