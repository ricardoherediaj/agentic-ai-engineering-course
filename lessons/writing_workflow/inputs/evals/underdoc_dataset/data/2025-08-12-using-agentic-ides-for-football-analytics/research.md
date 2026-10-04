# Research dossier: agentic IDEs for football analytics

Facts reconstructed from the published post.

## Background
- Andrej Karpathy's talk "Software Is Changing (Again)" at AI Startup School is the source of the idea that developers now spend more time thinking, planning and reviewing LLM-generated code than writing from scratch. Source: https://www.youtube.com/watch?v=LCEmiRjPEtQ
- Agentic IDEs (Cursor, Trae) offer multiple LLM providers, codebase and documentation indexing, MCP integration, autonomous file edits and completions; agentic CLIs such as Claude Code and Gemini CLI are the terminal counterpart. Source: https://www.datacamp.com/tutorial/cursor-ai-code-editor
- Cursor rules examples can be found in a community collection. Source: https://github.com/PatrickJS/awesome-cursorrules/tree/main

## Setup framework described
- Three files at project start: `rules.mdc` (agent rules: role, Python version, libraries, style), `project_context.md` (goal, components, steps, plot and colour specs) and a task log (`tasks.md` / `project_log2025.md`). Source: https://github.com/PatrickJS/awesome-cursorrules/tree/main
- Initialise Git at the start and commit before accepting agent suggestions. Source: https://www.datacamp.com/tutorial/cursor-ai-code-editor
- Index only necessary folders and library docs so the agent sees current versions (for example pandas, matplotlib). Source: https://www.datacamp.com/tutorial/cursor-ai-code-editor

## Examples
- Example 1: the six-plot match dashboard; errors included confusing coordinate systems (0-100 vs 120x80), misnamed columns and repeated matplotlib functions, solved by documenting dimensions as context. Source: https://github.com/ricardoherediaj/football-analytics-tutorials
- Example 2: on-ball sequences with GPT-5 in Cursor (Trae did not have it yet) on Salzburg vs Real Madrid from the Club World Cup; the agent picked a pass by Dean Huijsen and computed distance gained of about 39-43 m in two cases. Source: https://github.com/ricardoherediaj/football-analytics-tutorials

## Tool comparison (as of the post)
- Cursor: Agent mode with Claude Sonnet 4 rated best; broad model range; easier MCP setup (for example Supabase); Pro plan $20/month with rate limits changed quietly after "unlimited" was advertised. Source: https://www.datacamp.com/tutorial/cursor-ai-code-editor
- Trae: first month $3 then $10; 600 requests per month; Builder and Builder-with-MCP modes; MCP marketplace; SOLO mode behind a waitlist. Source: https://www.datacamp.com/tutorial/trae-ai
