# Article Guideline

- **Working title:** Why the data pipeline, not the model, decides RAG quality (football ETL case).
- **Bucket:** builds
- **Audience:** data and AI practitioners building LLM applications
- **Angle:** Second post of a series on the football RAG project; argue that ingestion discipline is where reliability is won, using his own pipeline as evidence.

## Section intents

1. Connect to the previous series post and state the thesis that retrieval quality is mostly a data engineering matter.
2. Explain where the match data comes from, why two sources are needed, and the first integration obstacle he hit.
3. Show how raw data is stored and validated before anything reaches the vector store.
4. Explain why raw events are condensed into a few interpretable metrics before the LLM sees anything.
5. Describe how documents are structured in the vector database and how a match is looked up.
6. Share one early bug that taught him to distrust the pipeline, then tease the next post (prompting).

## Sources

- https://github.com/ricardoherediaj/football-rag-intelligence
