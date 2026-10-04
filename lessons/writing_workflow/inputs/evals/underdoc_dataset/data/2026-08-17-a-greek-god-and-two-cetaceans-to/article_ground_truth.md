# A Greek God and Two Cetaceans to Build With AI

*Testing Hermes Agent + DeepSeek V4 Flash inside Orca as a Claude Code alternative*

> Messenger of the Gods
>
> Protector of travelers
>
> Oh so many titles
>
> Great is your speed
>
> Great is your might

As a Greek mythology lover I could not help to look for a poem or related phrase to Hermes and use it to open the article with it since I’ll be talking about an agent that carries his name. You can read the full poem some good fella wrote in [Reddit](https://www.reddit.com/r/Hellenism/comments/12cu6hf/poem_for_hermes_day/).

With this in mind, last week I built a [football analytics Skill](https://ricardoheredia.substack.com/p/a-claude-skill-to-build-your-own?r=56fjux&utm_campaign=post&utm_medium=web) for my football analytics tutorial repo using a stack I felt curious about: Hermes Agent + DeepSeek V4 Flash + Orca ADE.

Since someone I follow on X mentioned it, I decided to give it a go with a simple task: refactor the old repo and package it as a Skill to automate the process of generating football post match reports for teams and players.

In this article I’m talking about how to set it up, how much it costed, how I reviewed it, and the potential of using these harnesses for agentic coding.

### The Setup

[Hermes](https://github.com/NousResearch/hermes-agent) is Nous Research's autonomous agent → it’s MIT-licensed, it’s like a general agent with persistent memory and its own skills that good at code. Depending on their plan, they include more than 300+ models.

[DeepSeek V4 Flash](https://api-docs.deepseek.com/updates/) is the model I used, both the Flash and the official 0731, a 284B-parameter mixture-of-experts model with 1M-token context, built specifically for agentic and coding tasks.

[Orca](https://www.onorca.dev/) is the ADE (Agentic Development Environment) that runs both. It’s helpful to orchestrate agents and session to writes code so you can direct it and review it. Orca runs any CLI agent (Hermes, Claude Code, Codex, etc.) in isolated git worktrees, with terminals, diffs, and browser preview in one app.

#### Installing the pieces

[Hermes Agent](https://hermes-agent.nousresearch.com/) installs with one command:

```
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

It pulls in uv, Python 3.11.15, ripgrep, ffmpeg, and Chromium (via Playwright) as dependencies, and drops the binary at this path:

```
~/.local/bin/hermes
```

You can also run:

```
hermes doctor
```

To check if it came back clean, with no critical errors.

Nous Portal is the provider behind it

```
hermes portal
```

It oppens an OAuth login in the browser, and once you’re in, in the billing and tool layer (Nous Portal).

I loaded $5.10 in credit ($5 top-up + $0.10 courtesy of the subscription) and got access to a tool gateway with many perks: top LLM model providers, web search/extract via Firecrawl, image and video generation via FAL, speech-to-text via Whisper, text-to-speech, and browser automation, all callable from Hermes.

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) was the main model I ran, Nous Portal exposes both `deepseek-v4-flash` at $0.11 / $0.22 per Mtok and a cheaper `deepseek-v4-flash-0731` variant. More on the actual split in the cost section below.

[Orca](https://www.onorca.dev/) is where I actually worked. I installed it directly from its web. Once installed, you can get Hermes set as the default agent CLI inside Orca, and that’s the set I actually worked with: Orca as the workspace → Hermes as the CLI agent → DeepSeek as the model underneath.

Once installations were verified, I registered the football repo as its own workspace

```
orca repo add --path ~/orca/workspaces/football-analytics-tutorials
```

#### The Approach and How Much it Costed

Together, Hermes and Orca give you what's called a **harness** (the tools, memory, and execution control around a model), already built for you.

What I had to design was the **goal** **loop** → which is how you give it a goal, how you check its work, and when you call it done.

I asked Hermes to refactor the repo into a package and wrap it as a Skill that could be useful for any agent. Basically what I did was setting the /goal functionality and told it to:

- Check the [repo](https://github.com/ricardoherediaj/football-analytics-tutorials) and understand how it was structured: the web scraping, the visualization code, the metrics.

- A simple way of parametrizing the process with scripts and testing using software engineering best practices.

- Wrapping it under a skill that receives an input URL and outputs a rendered match report.

After the generation, I reviewed the generated charts (a process called human in the loop) and flagged what looked off.

There were minimal things in the charts like bad rendering on pass networks, stat labels that were unreadable against the background.

So I pointed them out to Hermes, which re-ran the tests and re-rendered the charts. I was based solely on how the chart looked like, so no elaborated eval for now. Same thing for both team and player reports.

When I checked the match report was good enough, I asked the LLM to document the results in a **SESSION.md**, to keep track of what was done, including decisions, mistakes and how it fixed it.

This helped a ton to build the player report, which was built a bit different than the match report, with a set of specific charts.

The model made less mistakes this time cause it had the context of what was being built.

#### Checking costs in Nous Portal

Verifying how much credits/tokens is the agent spending is crucial for budget and observability matters.

In Nous Portal you can track this easily, they even give you a CSV to export for analytics purposes.

Looking at the numbers the whole session cost $2.88.

Almost all of that went to two DeepSeek V4 Flash variant models, the default `deepseek/deepseek-v4-flash`which processed 119.5 million input tokens and 351K output tokens for $2.82, and the cheaper `deepseek/deepseek-v4-flash-0731` which added 24.5 million input tokens and 213K output for another $0.05.

Combined: ~144 million tokens for $2.87. The rest was a few free calls to Step 3.7 Flash and some Firecrawl tool usage for lighter tasks along the way.

### Key Takeaways

**Cost effective models can do real work if the harness carries the memory.** DeepSeek V4 Flash isn’t Claude of course but for the price, what it offers, and a tool gateway, the output was pretty decent. Hopefully there’ll be more competent models at better prices and with better harnesses.

**SESSION.md helped the agent to improve the task.** The player report came out with fewer mistakes than the match report, the fact that I had it to keep record of what broke last time and read before it started also improved the output.

**Human-in-the-loop by analyzing the report result.** There was a noticeable error in the match report where substitute players kept showing up labeled on the pass network with the same marker as starters a bug I caught cause I looked at the chart, flagged it, and told Hermes where the error was. It found the fix and ultimately solved it.

If you’ve ben using agentic coding tools and/or open models, what challenges have you find so far? Let me know in the comments!

PS: As effect of August 16th DeepSeek increased their [model pricing](https://api-docs.deepseek.com/quick_start/pricing/) for V4 series.

* * *

Till next time,

Ricardo.
