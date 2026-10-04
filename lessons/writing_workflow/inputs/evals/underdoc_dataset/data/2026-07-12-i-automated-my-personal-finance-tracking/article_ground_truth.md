# I Automated My Personal Finance Tracking With a Claude Skill and Two MCP Servers

*A simple approach using a custom skill*

For the past few years, my personal “finance system” was just noting down expenses in Notes app.

At the end of the month I'd copy everything into a “cleaner format”, add up the totals, and try to understand where my money actually went.

More recently I moved the capture part to Notion, which made the notes prettier but didn't remove the manual copying making it boring still.

For me, knowing my balance at the end of the month matters because I can tell how much I spent, saved, and invested, and that helps me decide how I organize the next month. The issue comes when tracking lags two weeks behind, so entries pile up.

## Notion 🤝 Superhuman

One day probably in 2024, in an online investing community I'm part of, the owner shared a finance template built in an app called Coda (now renamed as [Superhuman](https://superhuman.com/docs/use-cases/project-management?utm_source=google-brand&utm_medium=cpc&utm_campaign=23174568893&utm_bu=corp&utm_content=816119603654&utm_term=superhuman%20docs&target=&targetid=kwd-2108297563608&adgroup=187069800683&device=c&matchtype=e&placement=&network=g&extension=&clickid=CjwKCAjw9szSBhBNEiwAC57SqyMKV-0HurOgEeMXZH4BxQGZO7uVjEN532s5Xw3BZL6Xbdb7cdLSnxoCqsYQAvD_BwE&gad_source=1&gad_campaignid=23174568893&gbraid=0AAAABBoNLYwk8VMfb3d8vDr_SKSgMMt5x&gclid=CjwKCAjw9szSBhBNEiwAC57SqyMKV-0HurOgEeMXZH4BxQGZO7uVjEN532s5Xw3BZL6Xbdb7cdLSnxoCqsYQAvD_BwE)). I see it like Notion but with steroids.

The template has three pages with databases and charts linked between each other: one for expenses, one for income, and a balance page that recalculates income, spending, and savings per month on its own. For each row you just need a date, and the monthly formulas do the rest.

Here are pictures with some mocked data:

So my process became: register expenses in Notion each day → then move them to Superhuman at the end of the week or month, row by row.

There were like thirty plus entries every single month, and doing it by hand became tedious.

## A Simple Solution

Both Notion and Superhuman have MCP servers, which means Claude can read and write to them directly. I’m trying to make Claude the manager of many areas of my life by using its skills. So far I have a writing skill that helps me create and review articles like this one. Now I’ve created one to automate my finances.

So I wrote a Claude Code skill called `finance-sync` that does the tedious part for me by connecting to both Notion and Superhuman through the MCP servers in my Claude settings.

> In case you’re not familiar with [skills](https://claude.com/skills) yet, as defined by Anthropic they basically are:
>
> A way to turn your expertise, procedures, and best practices into reusable capabilities so Claude can apply them automatically, every time.
>
> And if you want a quick understanding on what MCP is you can read this [article](https://ricardoheredia.substack.com/p/understanding-model-context-protocol?utm_source=profile&utm_medium=reader2) with a practical example I built a while ago or redirect to the [official site](https://modelcontextprotocol.io/docs/getting-started/intro).

The daily habit stays the same: I type each expense into a small Notion database, one per month, with four fields: concept, amount, a free-text category, and a date. There's a fifth field too, a checkbox called `Synced`, which is the actual checkpoint that lets me know what I have already tracked.

Notion table with fictional data

When I want to sync, I run the skill.

Claude reads every row where the checkbox is unchecked, figures out whether each one is an expense or income, maps my lazy free-text categories to the real category rows in Superhuman, shows me a summary table, and waits for my confirmation.

Only then does it write the rows into Superhuman and ticks the checkboxes back in Notion.

The Superhuman balance page actually needs nothing from the skill cause its formulas pick up the new rows by date and recalculate the month on their own.

## How to set it up for yourself

**Create free accounts** in Notion and Superhuman.

**Connect the MCP servers.** To do it Claude Desktop, you can go to Settings, [Connectors](https://claude.com/connectors), and Add them. I added [Notion](https://developers.notion.com/guides/mcp/overview) and [Superhuman](https://developers.notion.com/guides/mcp/overview) the same way you’d connect to any other app: log in, authorize, done.

**Grab the template and write the skill.** I made a copy with mocked data of my Superhuman doc so you can duplicate this [Finances 2026 template](https://docs.superhuman.com/d/finances-2026_d9AGlDBJpds) yourself, so instead of starting from a blank page you have some fake data to play around with.

Once you have your own copy, adding the skill is as simple as dropping in a markdown file that tells Claude the shape of your tables: the column IDs, the category list, and one hard rule, never mark a row as synced until the write actually succeeds. I put my own version in this Drive [link](https://drive.google.com/drive/folders/18Z55FPb4pnPe4QaYi0wimHhMslwzNzNI?usp=sharing), so you can download the files and adapt them.

This is how it’s structured:

```
finance-sync/
├── SKILL.md # the file that tells Claude how to do the task
└── references/ # folder Claude uses as a reference to run the skill right
    ├── notion.md # reference of the Notion database tracker
    ├── coda.md # Coda/Superhuman template, rename it to superhuman.md
    └── categories.md # existing categories reference
```

To install it: in Claude Desktop, go to Settings → Capabilities → Skills → Add → Upload or "Write the skill's instructions," and paste it in. If you use Claude Code instead, drop the same file at `~/.claude/skills/finance-sync/SKILL.md`, plus its `references/` folder, and Claude picks it up automatically.

**Run it once and check by hand before trusting it.** The first time, I compared Claude’s proposed summary against my own notes for one full month before saying go. After that, I just run it.

## Three problems I found out

**The first problem was duplicates.** If I run the sync twice, I don't want my rent showing up twice in October for example. There's no reliable way to detect duplicates on the Superhuman side, so the `Synced` checkbox in Notion is the only source of truth for what's pending.

The ordering is what makes it safe: rows get marked as synced only after the Superhuman write succeeds. If the write fails halfway, the unwritten rows stay unchecked and nothing is lost. If you run the skill on a month with no pending rows it just reports "nothing pending" and touches nothing.

The only caveat: if that checkbox is wrong, the sync is wrong too. There's no real duplicate detection here, just one checkbox per row. For a personal tracker, that's good enough.

**The second problem was categories.** Notion lets me type whatever category I want; Superhuman expects a reference to an existing category row. Most of the time the mapping is obvious. But when I typed "Donation" for a charity gift and no such category existed in Superhuman, instead of guessing Claude proposed creating the new category and asked me first. I said yes, and it created the row and used it. That confirmation step I like: the model classifies but I approve.

**The third problem** was that the Superhuman MCP has a 30 message quota for the free plan which is the one I’m using, so this made me want to look for other flexible options but keeping the same workflow.

## The first real run

The first time I ran it for real, I had 5 unsynced rows from June and 19 from July, eleven days of expenses I hadn't moved, which tells you how well the manual process was going.

One run: 24 expenses and 1 income written into the template, two new categories created with my confirmation, every checkbox ticked, and the July balance recalculated by the time the skill reported back.

The part that used to take me more than 30 minutes now takes a couple of seconds by just writing:"sync my finances." or “/finance-sync”

## What I'd tell you to steal

Build a skill that moves the data to wherever you actually analyze it, and use a checkbox to track what's already been moved. Any two tools with MCP servers can play these roles.

My version still has rough edges. The template doc only works for one year, so I’ll need a new one every January. And the whole thing trusts one checkbox right now.

That’s what I want to find out next: how it holds up after a few more months of real use.

I hope this approach gives you an idea on how to use Claude to work with skills and MCP servers to automate boring tasks.

* * *

Till next time,

Ricardo.
