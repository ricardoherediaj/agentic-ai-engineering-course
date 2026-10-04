# Article Guideline

- **Working title:** Lessons from building a stats-analyst agent with tool calling.
- **Bucket:** builds
- **Audience:** data and AI practitioners building LLM applications and football analysts curious about agents
- **Angle:** A candid build log: scope, stack, a bad first version, the redesign around tools, and how the team checked it worked.

## Section intents

1. Set expectations: agents can be built many ways, and this is one real football case with its mistakes.
2. Describe the goal, the dataset and the chosen stack.
3. Explain the failing first approach and why it could not scale.
4. Explain the data layers that keep answers grounded.
5. Walk through how tools are defined, what the model reads, and the tool-design changes that improved routing.
6. Cover conversation memory and the evaluation approach, then end with limits and what to test next.

## Sources

- https://twelve.football/courses/context-engineering-for-football
- https://duckdb.org/
