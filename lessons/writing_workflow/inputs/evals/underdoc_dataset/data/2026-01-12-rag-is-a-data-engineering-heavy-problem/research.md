# Research dossier: football RAG data pipeline

Facts reconstructed from the published post and the project repository.

## Project and sources
- The system is the Football RAG Intelligence project; code is public. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Dataset scale: 108 matches from the first leg of the Eredivisie season, reusing and extending scrapers from an earlier single-match dashboard project. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- WhoScored provides event data with more than 1,300 events per match (passes, tackles, coordinates); it only flags whether an action was a shot. Source: https://www.whoscored.com/
- Fotmob provides shot details such as xG and shot counts and quality, complementing WhoScored. Source: https://www.fotmob.com/
- Entity resolution problem: one source writes "R. Madrid" and the other "Real Madrid"; a mapping file is the glue that avoids silent data corruption. Source: https://github.com/ricardoherediaj/football-rag-intelligence

## Pipeline design
- Raw Zone: scraped JSON is stored exactly as received (immutable) so metrics can be recomputed without re-scraping. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Components: one worker scraper per source with a single responsibility, a local raw directory, and an orchestrator script (`scrape_all_matches.py`) that finds missing matches and triggers workers. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Pydantic contracts act as an "airlock": a payload missing xG, with null team IDs or wrong types fails fast and never reaches the vector database. Source: https://docs.pydantic.dev/
- The transform step pre-calculates more than 30 tactical metrics (the post cites verticality and PPDA as examples) so the LLM reasons over a compact summary instead of 1,300 raw events. Source: https://github.com/ricardoherediaj/football-rag-intelligence
- Output of the ETL is `matches_gold.json`, the source of truth for reports, evaluations and rebuilds. Source: https://github.com/ricardoherediaj/football-rag-intelligence

## Vector store
- ChromaDB with a 2-chunk layout per match: a summary chunk (teams, date, score, competition) for finding the match through metadata filtering, and a tactical chunk (pre-calculated metrics) for generation. Source: https://docs.trychroma.com/
- A `sanitize_metadata()` helper prevents crashes on `None` values during indexing; chunking logic lives in `scripts/rebuild_chromadb.py`. Source: https://github.com/ricardoherediaj/football-rag-intelligence

## Bug anecdote
- An early ETL bug in team-ID mapping swapped home and away stats, making the system claim Zwolle dominated a match they actually lost 2-8 (Heracles vs PEC Zwolle). Source: https://www.sofascore.com/football/match/heracles-almelo-pec-zwolle/wjbsCjb
