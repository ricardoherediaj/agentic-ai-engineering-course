# How To Use Tool Calling To Build a Football Agent

*A basic stats analyst use case*

You may have seen people trying to build agents using different solutions, with code, no-code/low-code alternatives, different frameworks and models, depending on the use case.

There’s not just one way of building them, it depends on what you want to achieve and the level of control you want to have over your agentic system.

Today, I want to talk to you about a real use case applied to football so you can see how is it to define the scope of building an agent, the rationale behind choosing certain tools, the errors, and thoughts on the process.

### A Basic Stats Analyst

I recently built an agent with my teammates during the [Context Engineering course by Twelve Football](https://twelve.football/courses/context-engineering-for-football) that finished just a couple weeks ago.

Screenshot of the Streamlit demo

The goal was to build a basic stats analyst agent that answered questions grounded on the Premier League 2024/2025 season dataset from Wyscout.

For that we used a defined set of tools:

- Pydantic models for data validation and structured outputs

- OpenAI tool calling

- DuckDB as our light weight SQL and vector database

- OpenAI LLM and embeddings models

- Streamlit as frontend for demo purposes

Down the road, we found out these were our preferred tools to build it, but it started out slightly different.

### The First Version (v1)

In the beginning we had a shaky Python script with ~1,400 lines of regex code that relied heavily on pattern matching, and it broke every time we asked something different.

The LLM was giving responses but only those that were included in the if/else loops.

Questions like these were answered pretty well, but if you wanted to follow up the conversation, it lost context entirely. Also note that the wording is too verbose on metrics, a weird way to display the stats cause nobody talks like that.

So with every new question, we needed to patch more code.

We weren’t using the LLM properly to interrogate the dataset well.

### The Data Goes First

Before any answer reached the user, it had to pass through two data layers.

The first was **Pydantic**. We used it both to structured the output and to evaluate the responses against our questions benchmark. The LLM returned a verdict whether an answer was faithful or correct against a typed schema that matched our benchmark.

`passed: bool`, `reason: str`.

If the output didn’t match, it failed explicitly to avoid wrong responses and data leakage downstream.

The second was **[DuckDB](https://duckdb.org/)**, a lightweight SQL database that runs in-process without servers or heavy infrastructure. It read the Wyscout parquet files natively and, through its vector similarity extension (VSS), also stored the player and team embeddings for name resolution. Giving us the power of SQL queries and vector storage in the same tables.

Both of these were used to making sure the data the agent worked with was grounded data and it gave back grounded answers.

DuckD Database Schema.

### How the Tools Work (v2)

Now with the data layer in place, we needed the agent to actually use it.

So we used **Tool calling**.

It is how the LLM interacts with the database without touching it directly. The user asks a question, the LLM decides which tool to call and with what parameters, Python executes it against DuckDB, the result comes back, and the LLM writes the answer from that data.

We defined 4 tools: `query_player_stats`, `query_team_stats`, `query_ranking`, and `get_league_standings`.

Each tool has a name, a description, and a parameters schema. The description is what the LLM reads to decide whether to use it. The parameters tell it what arguments to pass.

Here’s how we defined the position filter inside `query_player_stats`:

That description is doing what you’d write as a Python dictionary. The alias mapping, the edge cases, and the `forward` exception all lives in a string the LLM reads at inference time.

And it worked.

Here’s the agent handling a multi-step question about Salah, where it had to build a custom opponent bucket, compare it against the rest of the season, then filter again by Champions League teams, all in the same conversation:

Questions answers about a player in many turns.

But we started with 9 tools.

There were separate tools for top scorers, best passers, most progressive carriers, each its own function.

The problem was the LLM kept picking the wrong one because the descriptions overlapped. It would call `get_top_scorers` when it should have called `query_ranking` with `metric=goals`.

So we merged them down to 4, with broader scope and cleaner descriptions.

Going from 9 to 4 reduced routing errors more than any prompt tweak we tried. With fewer tools the LLM had fewer decisions to get wrong.

While building the position filter, we had a Python dictionary in `agent_tools.py` that mapped user aliases to database values at execution time.

Every time the LLM passed `"CB"`, Python caught it and translated it to `"Central Defender"`.

It worked. But we deleted it.

We realized the same logic could live in the tool description instead. If you write it clearly enough, like documentation, the LLM passes the right value before the code ever runs.

### **Memory**

In v1, the conversation had no memory between turns. If you followed up on a question, the context was entirely lost.

We fixed it with one line of code using the OpenAI Responses API. It kept the conversation state through `previous_response_id`. You pass the last response ID and the API handles the rest.

This how it looks in code:

This is how it looked in the Streamlit UI:

Salah follow-up chain

### How We Knew It Worked

We built a benchmark of 61 questions and ran it after every change we made. Each answer was scored by an LLM judge against the expected output, so we didn't have to go through them manually.

At the end, we threw 21 random questions at it that none of us had prepared for. It got 21 out of 21.

The screenshot also shows the agent refusing questions it can't answer. That's something we had to build explicitly in order to make it refuse out of scope questions and not hallucinated.

### Wrapping Up

Right now it only covers the Premier League 2024/25. Just one league and one season.

The interesting question is whether the same approach holds when you scale it. More leagues, more seasons, harder questions.

That’s what we want to find out next.

Till next time,

Ricardo.
