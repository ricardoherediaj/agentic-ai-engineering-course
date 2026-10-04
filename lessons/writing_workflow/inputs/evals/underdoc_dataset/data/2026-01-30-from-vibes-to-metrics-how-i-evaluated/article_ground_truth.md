# From Vibes to Metrics: How I Evaluated A Football RAG System

Before I started building this project, my initial workflow for creating post match reports was based in pure vibes.

I would write a massive prompt, ask the LLM to analyze a match, read the response, and think, _“good enough.”_

This approach is not bad at the beginning, but if you want a **successful** system that generates trustworthy outputs, they should be evaluated from beginning to end both subjectively and **objectively**.

### Moving to EDD

After reviewing different approaches, I adopted the **Evaluation Driven Development (EDD)**, a methodology discussed by [Hugo Bowne-Anderson](https://open.substack.com/users/63978139-hugo-bowne-anderson?utm_source=mentions) in [Decoding AI Magazine](https://open.substack.com/pub/decodingml) article [Escaping POC Purgatory: Evaluation-Driven Development for AI Systems](https://www.decodingai.com/p/escaping-poc-purgatory-evaluation).

Where the core philosophy is:

> _**You cannot optimize what you cannot measure**_

So instead of treating evaluation as a final step, you build the test harness _before_ you finish building the system.

I’ll walk you through thow I used EDD to engineer my prompts in three steps:

1. **The Metrics:** Why I chose **Retrieval Accuracy**, **Faithfulness**, and **Tactical Insights** rules **.**

2. **The Optimization Loop:** Moving from **Prompt V1.0** (1800 tokens, slower, and a bit more expensive) to **Prompt V3.5** (360 tokens, more precise to what I wanted).

3. **The Results:** Critical bugs caught at the beginning.

### Golden Answers

In my [previous article](https://www.google.com/search?q=LINK_TO_PREVIOUS_ARTICLE), I broke down how I built the **Golden Dataset** (`matches_gold.json`) since it’s crucial to understand _why_ that dataset exists in the context of evaluation.

In standard software engineering, you write unit tests based on expected inputs and outputs, that’s the traditional software development lifecycle (SDLC).

Traditional software development: linear, testable, predictable. [Escaping POC Purgatory: Evaluation-Driven Development for AI Systems](https://www.decodingai.com/p/escaping-poc-purgatory-evaluation).

When working with LLMs, defining “expected output” is harder because these models are non-deterministic, meaning you can give an LLM the same input and get two different outputs.

This leads to a more dynamic process through the entire GenAI application lifecycle. More iterations during your development and your way to production.

Evaluation & Monitoring are part of the process since day one. [Escaping POC Purgatory: Evaluation-Driven Development for AI Systems](https://www.decodingai.com/p/escaping-poc-purgatory-evaluation).

In order to battle with that non-deterministic nature, I wanted to grade the system responses. See if they matched with the answers I was expecting.

That meant combining football knowledge with technology capabilities and creating a “Source of Truth” that I trusted 100% → **The** **Golden Dataset**. A ground truth that acts as the teacher’s answer key, containing the exact stats (validated by Pydantic before) for every match.

Without this, I would be just guessing and depending entirely on the LLM’s capacity.

Now that I had the answer key in hand, I needed a way to automate the grading of the system.

### The Judge: A 3-Metric Framework

Since human evaluation doesn't go that far as LLM can, I adopted the "LLM-as-a-Judge" methodology. In the book _AI Engineering_, Chip Huyen identifies the AI judge as:

> A critical evaluation method, noting its specific utility in measuring complex metrics such as the "factual consistency between the response and the whole context”. (Huyen, 2024).

By implementing this, we can automate the evaluation without only relying on manual review.

The evaluation harness uses the **LLM-as-a-Judge** pattern:

1. **The Analyst:** Claude 3 Haiku (Fast, Cheap ~$0.0001 per query) generates the report. It's optimized for speed but since speed comes with trade-offs, Haiku can occasionally miss nuances or hallucinate stats.

2. **The Judge:** Claude 3.5 Sonnet (Stronger, Slower) grades the report. It catches these issues. It's slower and more expensive, but it only runs during evaluation, not intended for production. This means I can test rigorously without blowing my API budget.

Why Anthropic's models? Honestly, I had a remaining balance there from previous experiments and wanted to blow them away. But I could have used Gemini, OpenAI, whatever. You can use any other "bigger" model for this, even a local one with Ollama.

#### The 3-Metric System

However, I needed to know why a report failed. If it was hallucination or did it ignore the charts or any other relevant part?

The evaluation framework measures three dimensions:

**1\. Retrieval Accuracy (30%)** \- Did we find the right match?

Early on, I noticed reports would analyze the wrong match or mix up team stats. The system would retrieve “Ajax vs. Heracles” when I asked about “Ajax vs. Telstar.” (I’ll show you an error like this at the end).

This metric uses metadata filtering to verify the system found the exact match requested. It’s deterministic in a way so either it got the right match (100%) or it didn’t (0%).

**Evaluation Result: 100%** ✅

**2\. Faithfulness (30%)** \- Are the numbers accurate?

This is the guardrail preventing “hallucinations” where the model invents stats.

Early reports claiming “Ajax had 73% possession” when the actual number was 64.3%. Or “Player #14 made 28 passes” when it was 23.

The judge uses regex to extract every number from the report, then cross-checks it against `matches_gold.json`. Any number not in the source data = hallucination = failed faithfulness check.

**Evaluation Result: 99.4%** ✅

**3\. Tactical Insight (40%)** \- Is the analysis tactically sound?

I broke it into four measurable components:

- **Specificity (10%)**: Does it cite concrete evidence? Counts specific references like player IDs, exact percentages, tactical metrics.

- **Visual Grounding (10%)**: Does it reference what’s actually in the visualizations? Reports should mention “The Passing Network shows Player #14 as the hub” and not just a generic commentary. This forces the system to tie text to visuals.

- **Terminology (10%)**: Does it use correct football language? The judge verifies terms against `tactical_rules.py` (e.g., “Field Tilt,” “Progressive Passes,” “PPDA,” “Verticality”) to avoid generic concepts

- **Relevance (10%)**: Does it answer the user’s actual question? If someone asks about pressing strategy, then the response shouldn’t be about passing accuracy.

A report can be factually accurate (Faithfulness = 100%) but tactically shallow (Tactical Insight = 40%).

**Evaluation Result: 95.0%** ✅

#### Codifying "Vibes" into Rules

This question was also bugging me from the start: “How do you mathematically prove a report is tactically sound?”

Since what I’m trying to do there is translating stats and tactical dashboards from post match analyses into explainable text, I couldn't let the LLM guess what the stats meant.

I had to define a way of teaching the system the coordinates used in the WhoScored and Fotmob data, how they are calculated, and displayed in the field visualizations with the mplsoccer library.

So, I built a file called `tactical_rules.py` that reverse-engineers the visualizations into text logic.

For example, I defined **Verticality** thresholds explicitly:

```
def interpret_verticality(verticality: float) -> str:
    if verticality > 50:
        return "direct vertical passing - quick transitions"
    elif verticality > 35:
        return "balanced build-up"
    else:
        return "patient possession-based build-up"
```

- **Scenario:** Ajax has a verticality of **72%**.

- **Bad Output:** “Ajax played patiently.” (Judge fails this: 72% > 50%, so it _must_ be direct).

- **Good Output:** “Ajax played a direct game with quick transitions.” (Judge passes this).

If Ajax has 72% verticality and the report says "patient build-up," is a vague description. The judge verifies those numbers exist and it checks if the tactical language matches what `tactical_rules.py` says those numbers should mean.

Think of \`tactical\_rules.py\` as the rubric, and the judge as the grader applying it.

Of course, in the future this can change depending on what rules you want to add or readapt. This was a first attempt of contributing to the evaluation harness trustworthiness.

#### The Weighted Scoring Rubric

To bring it all together, I created a weighted rubric that scores every generated report on a 10-point scale.

```
Weighted Score = (Retrieval × 0.30) + (Faithfulness × 0.30) + (Specificity × 0.15) + (Visual Grounding × 0.15) + (Terminology × 0.15) + (Relevance × 0.15) + (Conciseness × 0.10)
```

**A report must score ≥ 7.0/10 to be considered production-ready.**

#### Scoring Examples: A Good Analysis But Wrong Retrieval

Here's where evaluation gets interesting. Sometimes the system produces excellent tactical analysis but for the wrong match.

**What I asked:** “Analyse Feyenoord vs Ajax match”

**What the system retrieved:** Feyenoord vs FC Volendam

**Report Generated:**

 Here's what the system actually returned (screenshot from the live demo).

That might be too small to read, here’s the answer:

“ **Match Overview**: Feyenoord demonstrated superior territorial dominance with a significantly higher average team position (62.4m vs 33.9m). The home team’s lower PPDA of 9.2 indicated more aggressive pressing compared to Volendam’s 15.36, suggesting consistent offensive pressure and a controlled possession strategy.

**xG & Shot Efficiency**: Feyenoord generated substantially higher shot volume and quality, with 37 shots generating 4.82 xG versus Volendam’s 9 shots and 0.83 xG. The significant xG differential suggests consistent high-quality chance creation, with each Feyenoord shot averaging approximately 0.13 xG compared to Volendam’s 0.09 xG per shot.

**Pressing & Progression**: Progressive passing metrics (156 vs 114) reinforced Feyenoord’s offensive control. High press events (5 vs 3) further illustrated their tactical superiority in disrupting opponent’s build-up play. The defensive line positioning (13.0m vs 8.6m) confirmed Feyenoord’s ability to maintain more advanced, proactive defensive structure.

**Key Tactical Insight**: Total pass volume (513 vs 429) combined with superior progressive passing demonstrates Feyenoord’s systematic approach to ball progression and territorial domination, directly translating into offensive efficiency and match control.“

**Judge Evaluation:**

- Retrieval: **0/10** (30%) - **Wrong match retrieved** (asked for Ajax, got Volendam)

- Faithfulness: 10/10 (30%) - All numbers verified for Feyenoord vs Volendam match

- Tactical Insight breakdown:

  - Specificity: 10/10 (15%) - Dense with exact metrics (62.4m, 9.2 PPDA, 4.82 xG, 156 progressive passes)

  - Visual Grounding: 9/10 (15%) - References positional data and tactical patterns

  - Terminology: 10/10 (15%) - Perfect use of PPDA, progressive passes, xG/shot, defensive line

  - Relevance: 10/10 (15%) - Excellent explanation of tactical dominance

Conciseness: 10/10 (10%) - 220 words, slightly over but acceptable

**Weighted Final Score: 6.7/10** ❌ **Failed**

This is a dangerous type of failure in production systems.

The analysis is **tactically excellent**. If you only read the commentary, you’d think the system nailed it.

But it’s analyzing the **wrong match**.

This islikely a vector database issue, either the embedding similarity between “Feyenoord vs Ajax” and “Feyenoord vs FC Volendam” was high enough to return the wrong match, or the metadata filtering didn’t catch it.

This example shows why without the retrieval check, this report would score **9.5/10** on analysis quality alone. But it’s completely useless because it’s not what the user asked for.

A coach asking about the Ajax match would make wrong decisions based on Volendam data.

**The fix:** Tighter metadata filtering + explicit team name verification in the retrieval step. This is why `matches_gold.json`exists, in order to verify we’re analyzing the exact match that was requested.

#### What Good Evaluation Looks Like and Common Failure Modes

When all three dimensions work correctly (right match retrieved, accurate numbers, insightful analysis) the system produces reports that score high ≥9.0/10:

- Retrieval: 10/10 - Correct match identified

- Faithfulness: 10/10 - Every number verified against `matches_gold.json`

- Tactical Insight: 9-10/10 across all four checks (Specificity, Visual Grounding, Terminology, Relevance)

- Conciseness: 10/10 - Under 200 words (it’s ok if slightly longer)

The judge validates this automatically across all 108 matches in the dataset, catching failures that manual review would miss.

That away the system surfaced three failure patterns:

1. Wrong retrieval: Feyenoord vs Volendam example above → fix with stricter metadata filtering.

2. Shallow analysis: generic commentary with no specific metrics or insights → tweaking prompt to emphasize specificity.

3. Hallucinated stats → catch errors early in the data engineering pipeline.

#### Takeaways from this Section

- Turn subjective quality ("does this sound good?") into objective metrics (“does this score ≥7.0/10?“)

- Numerical verification + tactical interpretation allows the system to move from "vibes-based development" to evaluation-driven development.

- A system can sound smart while being completely wrong. This helps you catch errors in an automatic way since the beginning.

### The Prompt Optimization Loop: From 1800 to 360 Tokens

With the evaluation harness in place, In parallel I could measure what was actually working.

I tested prompts in Anthropic Console before touching code.

Each iteration was scored against the 10-match eval dataset.

Claude Console with the winning System Prompt from V3.5.

The evolution of iteration was like this:

**V1.0**: 1800 tokens, 5.0/5.0 quality → Everything explicit, verbose

**V2.0**: 800 tokens, 3.2/5.0 quality → Removed too much, quality tanked

**V3.0**: 400 tokens, 3.8/5.0 quality → Added structured sections back

**V3.5**: 360 tokens, 4.9/5.0 quality → **Winner**

You can check how I stablished this prompt testing workflow in the repo: [⚽ Football RAG Intelligence](https://github.com/ricardoherediaj/football-rag-intelligence/tree/main/prompts)

The V3.5 version added explicit metric interpretations directly in the prompt like:

- “Lower PPDA = more aggressive pressing”

- “Higher position values = more advanced positioning”

Also adding the required section headers (Match Overview, xG & Shot Efficiency, Pressing & Progression, Key Tactical Insight).

And limited constraints in the amount of text generated: “180-220 words” instead of just “be concise.”

**Result:** 80% token reduction, dropping the cost per query from about $0.0018 to $0.0004.

### Wrapping Up

When building GenAI systems you need to stick to a set of best practices. I considered this ones:

**Evaluate first optimize later.** I built the judge before iterating with prompts and before creating the vector database, cause I wanted every change measured and every response in consonance with the data I had.

**Prompt-first design pays off.** I designed Prompt V3.5 before building the ChromaDB schema, in an attempt to reduce retrieval-generation mismatch. The ideal scenario is to align the metadata with what the prompt needs.

**Pre-calculate during ingestion.** 38 tactical metrics were computed during ingestion, this helps to make fast rebuilds if the logic changes, a simpler RAG pipeline, fewer tokens, and stable prompts.

Building systems requires evaluation in every step of the journey.

Using Evaluation-Driven Development to cut tokens, go from vibes to data-driven analyses, and automated validation is what helps you get more a trustworthy working product.

Thanks for reading until the end, hope this helps you think of a way to evaluate your own systems.

If so, I’d love to know what other approaches are you considering when evaluating your RAG/LLM/Agentic apps.

* * *

See you next time,

Ricardo.
