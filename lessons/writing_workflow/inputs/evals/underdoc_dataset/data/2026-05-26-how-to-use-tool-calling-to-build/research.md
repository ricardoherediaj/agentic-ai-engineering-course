# Research dossier: football stats-analyst agent with tool calling

Facts reconstructed from the published post.

## Project
- Built with teammates during the Twelve Football Context Engineering course. Source: https://twelve.football/courses/context-engineering-for-football
- Goal: a basic stats analyst agent answering questions grounded in the Premier League 2024/2025 season dataset from Wyscout. Source: https://twelve.football/courses/context-engineering-for-football
- Stack: Pydantic models for validation and structured outputs, OpenAI tool calling, DuckDB as lightweight SQL and vector store, OpenAI LLM and embedding models, Streamlit as demo frontend. Source: https://duckdb.org/

## Iterations
- v1: a Python script with about 1,400 lines of regex and if/else pattern matching; it broke on new phrasing and lost context on follow-ups. Source: https://twelve.football/courses/context-engineering-for-football
- Pydantic was used for structured output and to evaluate responses against a benchmark; an LLM verdict returned `passed: bool` and `reason: str`. Source: https://docs.pydantic.dev/
- DuckDB runs in-process, reads Wyscout parquet files natively and, through the VSS extension, stores player and team embeddings for name resolution. Source: https://duckdb.org/docs/stable/core_extensions/vss
- v2 tools: `query_player_stats`, `query_team_stats`, `query_ranking`, `get_league_standings`. Tool descriptions are what the LLM reads to decide when to call. Source: https://platform.openai.com/docs/guides/function-calling
- Tool count went from 9 to 4 after overlapping descriptions made the model pick the wrong tool (for example `get_top_scorers` instead of `query_ranking` with `metric=goals`); this reduced routing errors more than prompt tweaks. Source: https://platform.openai.com/docs/guides/function-calling
- A Python alias map (for example "CB" to "Central Defender") was deleted once the same mapping was written into the tool description. Source: https://platform.openai.com/docs/guides/function-calling
- Memory: conversation state kept via `previous_response_id` in the OpenAI Responses API, a one-line fix. Source: https://platform.openai.com/docs/api-reference/responses

## Evaluation
- Benchmark of 61 questions rerun after every change, scored by an LLM judge against expected outputs. Source: https://twelve.football/courses/context-engineering-for-football
- Final held-out test: 21 unseen questions, 21 correct; the agent was explicitly built to refuse out-of-scope questions. Source: https://twelve.football/courses/context-engineering-for-football
- Scope limit: one league, one season. Source: https://twelve.football/courses/context-engineering-for-football
