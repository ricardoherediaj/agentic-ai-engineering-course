# Research dossier: football match-report package and skill

Facts reconstructed from the published post and the repository.

## Repository and package
- The tutorial repo started a year earlier as a match-dashboard notebook; it was refactored into a Python package. Source: https://github.com/ricardoherediaj/football-analytics-tutorials
- Package lives in `src/football_match_report/`, split into core, io and viz modules; also ships tests and a CI workflow. Source: https://github.com/ricardoherediaj/football-analytics-tutorials/tree/main
- The skill is in `skills/football-match-report/` with a SKILL.md, reference docs and scripts. Source: https://github.com/ricardoherediaj/football-analytics-tutorials/tree/main
- Input: one WhoScored match URL. Output: two PNGs (team report and a new zone-analysis figure), 24 charts in total (two figures of twelve panels). Source: https://github.com/ricardoherediaj/football-analytics-tutorials

## Data and visuals
- WhoScored via headless Chromium supplies the full event stream (passes, tackles, carries, recoveries with coordinates) behind passing networks, defensive blocks, progressive passes and carries, and xT momentum. Source: https://www.whoscored.com/
- FotMob via plain requests with no token supplies shots with xG and xGOT, official stats, player of the match and team colours. Source: https://www.fotmob.com/
- Chart blueprint: Post-Match-Report-2.0; UEFA pitch 105x68, black background, shirt numbers in nodes, circles for starters and squares for subs, xT momentum bar; sixteen chart types. Source: https://github.com/adnaaan433/Post-Match-Report-2.0
- Tested on Salzburg 0-3 Real Madrid (Club World Cup) and Chelsea 2-1 Tottenham. Source: https://github.com/ricardoherediaj/football-analytics-tutorials

## Build process
- Stack: Hermes Agent running DeepSeek V4 Flash inside the Orca agentic development environment; a 3-4 hour session produced the package structure, scrapers, tests, CI and skill packaging. Source: https://github.com/NousResearch/hermes-agent
- Orca site. Source: https://www.onorca.dev/
- Bug found by human review: every node rendered as a circle because WhoScored sets `isFirstEleven` only for starters, substitutes get `NaN`, and `bool(np.nan)` is `True` in Python. Source: https://github.com/ricardoherediaj/football-analytics-tutorials
- Next steps: player-level dashboards, more leagues and competitions, persistent storage; related project: Football RAG. Source: https://github.com/ricardoherediaj/football-rag-intelligence
