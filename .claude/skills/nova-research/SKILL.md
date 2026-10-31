---
name: nova-research
description: "Runs the full Nova research workflow to produce a research.md document for an article. Use when the user wants to research a topic for an article, gather and curate sources, or prepare research before writing. Triggers on: 'research this topic', 'run the research workflow', 'prepare research for this article', 'gather sources for', or any request to turn an article guideline into a research.md."
---

# Nova Research

Run the complete research workflow using the `nova` MCP server.

Research directory: $ARGUMENTS

## Execution

1. If the research directory above is empty and the user did not give an
   absolute path to the folder containing `article_guideline.md`, your first
   and only action is to ask the user for that path. A topic name is not a
   path: do not search or glob for guideline files to guess it.
2. Call the `nova:get_research_instructions` tool. It returns the complete,
   step-by-step research workflow. Follow it exactly; do not improvise the
   sequence.
3. Use Nova's tools by their fully qualified names, for example:
   - `nova:extract_guidelines_urls` — extract URLs from the article guideline
   - `nova:scrape_research_urls` — scrape the selected research-result sources
   - `nova:run_web_research` — fill gaps with additional queries
   - `nova:create_research_file` — produce the final research.md
4. Pause at every human-in-the-loop decision point defined in the workflow and
   wait for the user's choice before continuing.

## After Completion

Show the user the path to the generated research.md and briefly summarize
which sources were kept and which were discarded.
