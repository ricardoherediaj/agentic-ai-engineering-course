# RAG is a Data Engineering Heavy Problem: Building a Football ETL for AI

*How to use a Pydantic airlock and a Golden Dataset to set the information right for your RAG*

In today's fast-paced world, organizations must continually leverage data-driven intelligence to unlock strategic value. In our previous publication, our team shared the high-level architecture of the enterprise sports intelligence solution we launched ([Building a RAG System That Generates Football Post-Match Tactical Reports Automatically](https://substack.com/@thenetpass14/p-182493528)); today, we delve into what our engineers consider the single most crucial pillar of the entire infrastructure: the data engineering pipeline. It's not just about generative artificial intelligence; it's about building an unshakeable operational foundation.

**RAG efficiency relies on great Data Engineering.**

To achieve optimal performance, our team focused on architecting a robust ETL (Extract, Transform, Load) paradigm—a transformative game-changer designed to proactively prevent retrieval anomalies and poor synthesis, thereby empowering our language models to seamlessly deliver highly accurate, contextual outputs.

Now that we've established the core thesis, let us delve into the origin of our data streams, the external endpoints we integrated, and the key architectural decisions our team made to scale this pipeline.

Overview of the system architecture delivered via modern visual schema standards.

### Where the Data Comes From

Our team set out with a clear business objective: to automatically generate concise, highly synthesized executive post-match reports by aggregating disparate public data feeds into a unified ecosystem. By centralizing these assets, stakeholders save valuable time previously lost navigating fragmented sources, allowing them to focus on what truly drives impact—high-level tactical analysis and strategic decision-making.

To build these actionable tactical intelligence reports, our team identified that capturing granular match event data was crucial.

We re-architected and introduced significant improvements to the extraction frameworks originally developed for our [previous dashboard project](https://ricardoheredia.substack.com/p/building-your-own-football-analytics). This strategic upgrade allowed our engineers to scale operations from localized single-match capture to an industrialized pipeline capable of indexing over a hundred fixtures across a competitive campaign.

Our core data ecosystem leverages complementary leading sources:

- **WhoScored:** Providing extensive event telemetry featuring thousands of distinct actions per fixture—including detailed passing matrices, spatial coordinates, and defensive metrics.

- **Fotmob:** Serving as a crucial repository for specialized analytical metrics such as expected goals (xG), shot counts, and advanced shot quality indices.

These upstream sources provide synergistic value: where one system delivers continuous numerical measurements, the other verifies discrete categorical occurrences. They seamlessly complement one another across our analytical layer.

During this integration phase, our team encountered an immediate architectural challenge: **Entity Resolution.**

Disparate external providers inevitably leverage inconsistent naming conventions—for instance, one source may denote a club as “R. Madrid” while another utilizes “Real Madrid.” This is where robust entity resolution comes in. Our team engineered a unified mapping schema to ensure our downstream RAG system recognizes these variations as identical entities rather than distinct organizations.

_This mapping configuration serves as the foundational glue across our pipeline; it represents a simple yet highly effective enterprise mechanism to prevent silent data corruption._

### Extracting the Data

Now that we've explored our ingestion sources, let's move on to the extraction mechanisms. Our engineering team scaled our scraping modules from a manual single-run utility to an automated pipeline processing numerous fixtures across the opening phase of a leading European talent-incubator league.

Why focus on this specific domestic league? It represents an elite competitive environment renowned for developing world-class emerging talent; monitoring these rising stars provides significant strategic foresight for modern sports analytics.

Throughout the extraction lifecycle, our team adhered strictly to a core data governance principle: **the Raw information is immutable.** Ingested JSON payloads are persisted in their exact native state directly into an isolated "Raw Zone" repository. Consequently, if our analysts refine downstream tactical metric calculations or discover edge cases in the transformation logic, our team can seamlessly re-process the data without re-scraping external endpoints.

A high-level architectural overview of our extraction framework:

```
Scraper WhoScored --(JSON)--> [ Raw Zone /whoscored/ ]
                                            |
 Scraper Fotmob   --(JSON)--> [ Raw Zone /fotmob/   ]
                                            |
                              [ scrape_all_matches.py ]
                                            |
                               ( Orchestration & Logs )
```

- **The Workers:** Specialized, modular scraping agents—each designed with a clear single responsibility—engineered to seamlessly extract and persist raw payloads into our infrastructure.
