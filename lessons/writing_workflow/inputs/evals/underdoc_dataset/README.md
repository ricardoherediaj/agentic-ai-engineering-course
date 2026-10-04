# Underdoc eval dataset

Evaluation dataset for Brown built from 26 published posts of The Underdoc newsletter. It mirrors the course dataset
(`inputs/evals/dataset/`): `metadata.json` plus one folder per sample under `data/` with `article_guideline.md`,
`research.md` and `article_ground_truth.md`, loaded by `brown.evals.dataset.EvalDataset`.

The purpose is to measure how well Brown reproduces Ricardo's voice from a short brief, so guidelines are deliberately
short idea captures (at most 300 words), not outlines of the finished post.

## Buckets

| Bucket | Meaning | Posts | few_shot | validation | test | extended |
| --- | --- | --- | --- | --- | --- | --- |
| builds | Something Ricardo built with code | 12 | 1 | 1 | 4 | 6 |
| explainers | Concept, tool or framework explained | 6 | 0 | 1 | 2 | 3 |
| bridge | Career, mindset, personal | 5 | 1 | 0 | 2 | 2 |
| field-notes | News, event recap, opinion | 3 | 0 | 0 | 2 | 1 |
| **Total** | | 26 | 2 | 2 | 10 | 12 |

Five explainers were fixed up front (scouting parts I and II, uv, MCP, the Twelve framework post) and the event recap
`2025-06-08` was fixed as field-notes. The other 20 were labelled by reading them; one reason per post is stored in
`bucket_reason` in `metadata.json` and repeated below. Judgment call: `2025-08-12-using-agentic-ides-...` is an
explainer (tool guide and comparison, no single build).

## Splits

| Split | Count | Use |
| --- | --- | --- |
| few_shot | 2 | `is_few_shot_example: true`; shown to the writer as examples |
| validation | 2 | prompt/profile tuning |
| test | 10 | reported results; balanced by bucket (4 builds, 2 explainers, 2 bridge, 2 field-notes), 2026 posts preferred |
| extended | 12 | extra coverage, not used for headline results |

Few-shot buckets: builds + bridge. Validation buckets: builds + explainers. The noise subset (`noise_subset: true`) is
3 test posts spanning builds, explainers and bridge: `2026-03-03-wordalisation-...`,
`2026-03-09-how-a-football-framework-...`, `2026-02-21-embrace-your-weirdness`.

Extra metadata keys (`bucket`, `split`, `noise_subset`, `bucket_reason`) are ignored by `EvalDataset.load_dataset`,
which reads only the keys it knows, so `metadata.json` stays loader-compatible.

### Reserved posts

`2026-07-12-i-automated-my-personal-finance-tracking` and `2025-08-31-uv-the-tool-that-helps-you-manage` are used as
Brown style examples at generation time. Evaluating on them would leak, so both are `extended` and must never move
to few_shot, validation or test.

### Samples

| Sample | Bucket | Split | Noise | Reason |
| --- | --- | --- | --- | --- |
| `2025-06-08-3-data-driven-strategies-for-football` | field-notes | extended |  | Event recap from a football analytics workshop, opinion-style takeaways. |
| `2025-06-11-5-actionable-tips-and-resources-to` | bridge | extended |  | Personal lessons and curated resources for getting into football analytics. |
| `2025-06-27-the-art-of-football-data-scouting` | explainers | extended |  | Explains a data-driven scouting method through a club case study. |
| `2025-07-06-the-art-of-football-data-scouting-d2a` | explainers | extended |  | Continues the scouting method: profile identification, search and shortlist. |
| `2025-07-09-how-to-scrape-transfermarkt-with` | builds | extended |  | Walks through the Python scraper he built, its design and storage. |
| `2025-07-20-how-to-use-fbref-for-football-scouting` | builds | extended |  | Shows his Python scraping and cleaning code for a free stats site. |
| `2025-07-27-building-your-own-football-analytics` | builds | extended |  | Describes a six-plot match dashboard he built in Python and its repo. |
| `2025-08-12-using-agentic-ides-for-football-analytics` | explainers | validation |  | Explains what agentic IDEs are and compares two of them with a reusable setup framework. |
| `2025-08-23-the-data-learning-diary-tracking` | bridge | extended |  | Personal learning and note-taking habit; no code. |
| `2025-08-31-uv-the-tool-that-helps-you-manage` | explainers | extended |  | Explains what uv is and why to use it, with a setup example on his tutorial repo. |
| `2025-09-29-understanding-model-context-protocol` | explainers | test |  | Explains what MCP is, its architecture and primitives, using a collaborative server as the example. |
| `2025-12-26-building-a-rag-system-that-generates` | builds | validation |  | Announces and explains the football RAG system he built, with architecture, demo and repo. |
| `2025-12-31-a-thank-you-two-ideas-from-a-book` | bridge | few_shot |  | Year-end thank-you plus a career-mindset reflection from a book; no code. |
| `2026-01-12-rag-is-a-data-engineering-heavy-problem` | builds | few_shot |  | Walks through the ETL code and contracts Ricardo built for his football RAG system. |
| `2026-01-22-farewell-fbref-advanced-stats-when` | field-notes | test |  | Short reaction to a news event in the football data world, with opinion and advice. |
| `2026-01-30-from-vibes-to-metrics-how-i-evaluated` | builds | extended |  | Details the evaluation harness and prompt iterations he built for his RAG system. |
| `2026-02-10-shipping-a-rag-system-app-to-hf-spaces` | builds | extended |  | Explains the UI and deployment he built and shipped for his RAG system. |
| `2026-02-21-embrace-your-weirdness` | bridge | test | yes | Personal essay on career identity and unusual skill combinations; no code. |
| `2026-03-03-wordalisation-and-context-engineering` | builds | test | yes | Describes concrete prompt and context changes he made in his own RAG codebase. |
| `2026-03-09-how-a-football-framework-for-measuring` | explainers | test | yes | Explains a performance-measurement framework and shows how it transfers to other domains. |
| `2026-05-05-got-interviewed-by-ryan-day-in-his` | bridge | test |  | Expands on his answers in a newsletter interview about learning and side projects. |
| `2026-05-26-how-to-use-tool-calling-to-build` | builds | test |  | Retrospective on an agent his team built in a course, with stack, iterations and results. |
| `2026-06-27-venezuelas-earthquake-tragedy-whats` | field-notes | test |  | Time-sensitive news and call to action about a disaster; not technical. |
| `2026-07-12-i-automated-my-personal-finance-tracking` | builds | extended |  | Describes a Claude skill and two MCP servers he built to automate expense syncing. |
| `2026-08-08-a-claude-skill-to-build-your-own` | builds | test |  | Reports refactoring a repo into a package and an installable agent skill, with code layout. |
| `2026-08-17-a-greek-god-and-two-cetaceans-to` | builds | test |  | Hands-on setup and cost report of an agentic coding stack used to build a real skill. |

## Ground truth

`article_ground_truth.md` is the published post text with the title as an H1 and the subtitle in italics. Removed:
front matter, Substack image embeds (captions kept), subscribe and share widgets, avatar and likes footers. All prose
and headings are kept verbatim.

## Leakage rules

Guidelines must not copy phrasing, examples, numbers-as-conclusions or conclusions from the post. Each guideline gives a
working title, angle, audience, 4-6 section intents (what each section must achieve, not what it says) and source URLs.

`scripts/check_underdoc_leakage.py` enforces, per sample:

- guideline at most 300 words;
- no word 8-gram shared between guideline and ground truth (code blocks, URLs and heading lines ignored).

Run `uv run python scripts/check_underdoc_leakage.py`; it exits non-zero on any failure. Tests live in
`tests/brown/evals/test_underdoc_leakage.py`.

## Research

`research.md` is a source dossier (bullet facts, numbers, tools, each with a source link) for builds and explainers in
the few_shot, validation and test splits (9 samples). Public URLs were spot-checked where reachable (the Wordalisation
article and the MinIO MCP server README); the rest was reconstructed from links and claims in the post.

Bridge and field-notes posts, and every `extended` post, have a one-line placeholder stating that no research dossier
applies. **UserIntent `research_anchoring` is not scored for them.**

Known caveat: dossiers are reconstructed from the published post, so `research_anchoring` is an upper bound (the
research always contains what the post uses). The bias is identical for both arms of any comparison, so relative
differences remain meaningful.
