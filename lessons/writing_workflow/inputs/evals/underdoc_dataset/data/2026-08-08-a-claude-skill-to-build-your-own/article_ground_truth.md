# A Claude Skill to Build Your Own Football Analytics Post Match Reports Automatically

*Use an Agent to create a Custom Skill*

A year ago, I built this [football-analytics-tutorial repo](https://github.com/ricardoherediaj/football-analytics-tutorials/tree/main) for anyone wanting to practice their Python coding skills with football. In that article I explained what a post match dashboard was and the plots I decided to include.

Although it worked as a standalone notebook and was well received, I wanted to give it some love. I wanted to improve it as a Python package and create a Skill that anyone can reuse to plug it into their preferred agent in order to automate the generation of single post match reports.

Much has changed in the AI landscape since I created that notebook.

Yesterday I was playing around with a setup I saw on [X/Twitter](https://x.com/theunderdoc14) → Hermes Agent + DeepSeek V4 Flash + Orca as Agentic IDE, so I decided to set it up and test it by giving it this repo and letting it run with clear goals: refactor it, improve the report, test it and build the skill.

In this article I’ll talk about the repo itself, the skill and its result. I’ll talk briefly about the tools I used to generate this but will leave the setup details and what they are for another article since I believe they deserve their own piece.

What you’ll get in this article: a skill that receives one URL from WhoScored as input and generates a 24-chart report out, ready to use in an agent that can run the whole thing for you.

Let’s see what changed.

## The new feature

I wanted to make a simple skill which core capability was just one thing → you input a Match URL from WhoScored and obtain a post match report out.

```
uv run football-match-report scrape "<whoscored-url>" --out ./data
uv run football-match-report render --data ./data --out ./report
```

These two commands turn any match into two PNGs: the team report and the zone analysis (a new part of the report I included)

I tested it end to end on Salzburg 0–3 Real Madrid from last year Club World Cup, and on Chelsea 2–1 Tottenham from the Premier League from last season.

#### Data Sources

The report merges two data sources:

- WhoScored, scraped through headless Chromium, provides the full event stream: passes, tackles, carries, and recoveries with coordinates. That powers the passing networks, defensive blocks, progressive passes and carries, and the xT momentum chart.

- FotMob, fetched with plain requests and no token, provides shots with xG and xGOT, the official stats, the player of the match, and real team colors. A tricky part: mapping the date and team names which is pretty much solved from the WhoScored data (check the repo for more details)

The charts follow the [Post-Match-Report-2.0](https://github.com/adnaaan433/Post-Match-Report-2.0) blueprint from my pal Adnaan. The pitch is rendered using UEFA pitch coordinates at 105×68, black background, shirt numbers inside player nodes, circles for starters and squares for subs, and an xT momentum bar. Assembling sixteen chart types into two figures of twelve panels each.

## The professional Python package

**The repo now behaves like a real open-source package.**

The code lives in `src/football_match_report/`, split into core, io, and viz modules.

```
src/football_match_report/     # the package
  core/events.py               # event pipeline: carries, possession, xT, UEFA scaling
  core/stats.py                # match/shot statistics
  io/whoscored.py              # Playwright scraper
  io/fotmob.py                 # FotMob API (id resolve, matchDetails)
  viz/pass_network.py          # passing networks (shirt numbers, line heights)
  viz/defensive_block.py       # defensive KDE heatmaps
  viz/progressive.py           # progressive passes & carries
  viz/shots.py                 # shot map + goalkeeper saves
  viz/momentum.py              # xT momentum chart
  viz/match_stats.py           # stats bars
  viz/zones.py                 # 8 advanced zone charts
  viz/report.py                # 2x 4x3 figure assembly
  cli.py                       # scrape + render commands
skills/football-match-report/  # installable agent skill (SKILL.md + thin wrappers)
tests/                         # offline unit + render tests (synthetic match data)
docs/                          # sample report images
```

This way you can use the package to install, import, test, and extend it as you wish. The scraping logic, the coordinate conversions, and the chart code are separate modules with single responsibilities in order to follow software development best practices.

## The Skill Itself

**The same repo ships as an installable agent skill →**`skills/football-match-report/` contains a SKILL.md, reference docs, and the scripts the agent needs.

An agent that has this skill installed can run the whole workflow from a natural-language request, because the skill carries the knowledge: the commands, the data format, the coordinate conventions, the verification steps.

Launching it from Hermes, my code agent, takes one request.

The skill lives in the agent’s skills folder. From there, asking for the report for a WhoScored URL match is enough. The agent hands me the two PNGs.

That’s the shift I wanted to give it and what I love about the process of creating skills. You can move all the knowledge from your head into a document and then handing over the execution to the agent.

## The process

The original dashboard was created along with by Claude Sonnet 4 in Cursor last year but this version was built on a different setup, one I chose as an alternative to Claude Code.

I built it with this agent stack:

[Hermes](https://github.com/NousResearch/hermes-agent/tree/main) running DeepSeek V4 Flash as the default model, inside [Orca](https://www.onorca.dev/), an agentic development environment.

The agent did the heavy lifting during the 3-4 hours session: the package structure, the scrapers, the test suite, the CI workflow, the skill packaging.

I did the human in the loop review by opening the rendered PNGs and looking at potential errors.

Doing this loop I caught some rendering issues problems, like: every player node rendered as a circle, because WhoScored only sets `isFirstEleven` on starters, substitutes get `NaN`, and `bool(np.nan)` evaluates to `True` in Python.

So in order to fix it I had to: tell the agent where the fix was → tell it to test it again with the data and logic → check the rendered result again.

How I set up that stack, the models, the cost, and why it works as a Claude Code alternative deserves its own post in the upcoming days.

## Next steps

Using this report as the foundation to generate a new player-level dashboards with top passers, individual pass maps, per-player shot and defensive stats from that specific match.

Maybe more leagues and competitions and a simple persistent storage for the scraped data would turn one-off reports into a history you can track (which is something I was trying to do with my [Football RAG project](https://github.com/ricardoherediaj/football-rag-intelligence)).

## Why this matters

This is an improved version of the tutorial repo.

You as a fan, technical person, or curious coach/scout that knows Python and wants to see tactical execution from a match, flag a concrete player, analysts spot patterns across matches, can reuse this in a more straightforward way.

The difference now is that instead of plotting everything each time by yourself you can run two commands or a Skill in natural language with an agent.

If you build football analytics, or you build with agents, the repo is open source: https://github.com/ricardoherediaj/football-analytics-tutorials

Enjoy it, and feel free to share with anyone!

* * *

Till next time,

Ricardo.
