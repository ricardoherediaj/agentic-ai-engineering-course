# RAG is a Data Engineering Heavy Problem: Building a Football ETL for AI

*How to use a Pydantic airlock and a Golden Dataset to set the information right for your RAG*

In my last post, I shared the big picture of the Football RAG system I’ve launched ( [Building a RAG System That Generates Football Post-Match Tactical Reports Automatically](https://substack.com/@thenetpass14/p-182493528)), and today, I want to talk about what is for me the most critical part of the system: the data pipeline.

**RAG efficiency relies on great Data Engineering.**

This refers to building a solid ETL process: Extract, Transform, Load — the process that prevents bad retrieval and bad generation, helping the system produce accurate responses.

So, I’ll go over the origin of the data, the sources I used, and the decisions I made to build the pipeline.

Overview of the system thanks to Nano Banana Pro.

### Where the Data Comes From

Starting from the main goal of the system: automatically provide concise post match reports using free updated post match data from a league gathered in one place. That way, you can save time hopping from one site to another and focus on what really matters: the analysis.

To build these tactical reports, I wanted to use **match event data**.

I reused and improved a version of the scrapers I built for my [previous dashboard project](https://ricardoheredia.substack.com/p/building-your-own-football-analytics). The goal was to move from scraping one match for a plot to indexing 108 matches for a system.

The main data sources are:

- **WhoScored:** with more than 1,300+ events per match: passes, tackles, coordinates.

- **Fotmob:** source for more specific match data like xG, numbers of shots and shot quality.

Fotmob provides the shot as a number, whereas WhoScored only provides if the action was a shot (True) or not (False). They complement each other.

The first wall I hit in this Data Engineering process was: **Entity Resolution.**

Source A calls the team “R. Madrid,” Source B calls them “Real Madrid.” I needed to map them, so the RAG system wouldn’t think they are different teams.

_This file is the glue. It’s a simple but effective way to prevent silent data corruption._

### Extracting the Data

The scrapers development evolved from a one-off scraping to more matches. In this case I used just 108 matches from the first leg of the Eredivisie league.

Why the Dutch league? It’s a league I’m really curious about, they are one of the best breeding talent leagues in Europe and it is always worth it looking at their emergent talents.

The scrapers followed a simple rule: **the Raw information is immutable.** I save the JSON exactly as it comes from the web into a “Raw Zone” (local for now). That way if I find a bug in my tactical metrics calculation later, I don’t need to scrape the web again. I just re-run it from the raw files.

Quick summary of how it works:

```
Scraper WhoScored --(JSON)--> [ Raw Zone /whoscored/ ]
                                            |
 Scraper Fotmob   --(JSON)--> [ Raw Zone /fotmob/   ]
                                            |
                              [ scrape_all_matches.py ]
                                            |
                               ( Orchestration & Logs )
```

- **The Workers:** Specialized scrapers (one for WhoScored, another for Fotmob) designed with a single responsibility: extracting raw data.

