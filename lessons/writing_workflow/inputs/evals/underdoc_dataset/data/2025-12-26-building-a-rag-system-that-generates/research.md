# Research dossier: football RAG system overview

Facts reconstructed from the published post and the project repository.

## Product and demo
- Live demo hosted on Hugging Face Spaces; users pick a provider and paste their own API key. Source: https://huggingface.co/spaces/rheredia8/football-rag-intelligence
- Source code is open source. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- The system ingests Eredivisie match data from WhoScored and Fotmob into a vector database and generates tactical commentary grounded in statistics. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Scale: 108 matches indexed, roughly 1,355 events per match; providers supported: Anthropic Claude, OpenAI and Gemini; about $0.50 total to test everything. Source: https://huggingface.co/spaces/rheredia8/football-rag-intelligence
- Dual mode: natural-language questions go to the LLM; visualization commands (for example passing network, shot map) bypass the LLM and render with matplotlib. Source: https://github.com/ricardoherediaj/football-rag-intelligence

## Architecture
- ChromaDB retrieval uses team names and metadata filtering rather than pure semantic search. Source: https://docs.trychroma.com/
- 2-chunk design per match: summary chunk for filtering, tactical chunk with 38 pre-calculated features for generation. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Metrics computed at ingestion include PPDA, progressive passes, field tilt and compactness. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Raw data passes a Pydantic validation pipeline into a "golden dataset" before indexing. Source: https://docs.pydantic.dev/
- Output validation: every statistic cited in the response is checked against the golden dataset. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Latency: text analysis about 6-7 seconds; visualizations under one second. Source: https://huggingface.co/spaces/rheredia8/football-rag-intelligence

## Initial evaluation (10 diverse matches, LLM-as-a-judge with rubrics and reference answers)
- Retrieval accuracy 100% with metadata filtering versus 70% for pure semantic search. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Faithfulness 99.4% (one rounding discrepancy). Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Tactical insight 95.0%. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Cost about $0.0001 per query with Claude Haiku 4.5. Source: https://docs.anthropic.com/en/docs/about-claude/models
- Known limitation: occasional wrong team names or statistics. Source: https://github.com/ricardoherediaj/football-rag-intelligence

## Context and roadmap
- Visualizations come from an earlier dashboard project (six-plot match dashboard). Source: https://github.com/ricardoherediaj/football-analytics-tutorials
- Planned posts: ETL pipeline, prompt engineering (prompt V1.0 at 1,800 tokens down to V3.5 at 360), evaluation-driven development, deployment to HF Spaces, scaling to production. Source: https://github.com/ricardoherediaj/football-rag-intelligence
