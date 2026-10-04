<!-- GENERATED FILE, do not edit by hand. Source: Underdoc harness repo (TheUnderdoc/harness). Files: skill/references/voice-structure.md, skill/SKILL.md, skill/references/build-story-structure.md, skill/references/explainer-post-structure.md, skill/references/conceptual-post-structure.md. Regenerate with scripts/sync_underdoc_profiles.py. -->

# Voice — Structure

Rhythm, headings, length, sign-off. Gates: `G-01`, `G-02`, `G-03`, `G-06`, `G-07`. All numbers are medians measured from the 26-post corpus (`checks/calibration.md`) — descriptive, never quotas.

## The one-to-two-sentence paragraph is the default unit `[advisory, measured]`

The signature rhythm of this voice, and the finding no earlier document recorded: ≈32 one-sentence paragraphs per post, mean 1.4 sentences per paragraph, observed hard cap of 4 sentences (~45 words). Skill v1 said fragments were "for emphasis, max ~3 per post" — wrong by an order of magnitude. Do not merge short paragraphs into "proper" ones; the white space is doing work.

- Good (four consecutive paragraphs, `embrace-your-weirdness`):
  > So I started exploring other things on the side: bartending, mobile app development, whatever I could get my hands on.
  >
  > Then the pandemic hit, and I stumbled upon Python.
  >
  > Something clicked.
  >
  > I started applying it to football analytics and got immediately hooked.
- Bad: the same four beats fused into one six-sentence block paragraph.

The reverse failure is the ladder: every sentence isolated on its own line, the whole page a staircase of stop dots. That shape is the current visual signature of AI-generated posts, and it reads as slop no matter what the sentences say. The singles in the Good example land because they sit between two-sentence paragraphs. **Workhorse paragraphs run two to three sentences; one-sentence paragraphs are rationed to structural moments — the hook, a turn, the payoff — rarely more than two singles in a row, never a full ladder. A standalone line that functions as a section label is a heading — set it as H4, don't leave it floating.** [advisory, corrected 2026-09-05 after the long-form draft read as slop; refined same day from Ricardo's own section-label lines]

One idea per paragraph. A paragraph reaching its fourth sentence is almost always two paragraphs.

## Sentence length `[advisory, measured]`

Mean 15–22 words; the occasional 30-word story sentence is normal, but keep the long tail rare (corpus p90 ≈ 32). Alternate short and long — the one-liner lands because the sentence before it ran long.

## Headings: flat and functional. `G-02` (warn-only)

Style is the signal, not count. Calibration killed the 3–8 rule: the best post (204 reactions) has 12 headings, the second and third best have one each.

- Plain functional labels, often questions: "What's a match dashboard?", "Where to get the data from?", "What's Next?", "Key Takeaways".
- Never dramatic two-part titles with `:` or `—` ("The Hidden Cost: Why Your Pipeline Is Lying to You").
- Write at H3/H4 (corpus practice), never deeper than H4.
- The gate warns outside 3–8 and past 14; it never fails. The two 19–20-heading posts earned 5 and 4 reactions — past ~14, sections have stopped being sections.

## Word count. `G-01` (warn-only)

Guidance band 900–1,400 (top-performer median 1,029). Field notes run 400–900. Past 1,600 the gate warns again. Nothing about length blocks a draft — the second-best post ever is 641 words.

## Standalone rule: no series openers. `G-06`

Every post lands with zero prior posts read. Series context, if any, is one linked line placed after the hook — never the opening.

- Bad: "In my last post, I shared the big picture of the Football RAG system I've launched... and today, I want to talk about..." (`rag-is-a-data-engineering-heavy-problem`, 5 reactions — the whole five-part series opened this way, median 5)
- Good: open on the problem, then later: "I also integrated the FBRef data with the Transfermarkt data, a process I described in my last post: [link]" (`how-to-use-fbref`, 36 reactions — reference sits mid-post, after the hook did its job)

Gate fails on series-opener phrases in the first three paragraphs. Auto-revise up to twice, then hand over.

## Sign-off. `G-03`

Exactly: `Till next time, Ricardo.` The corpus has four spellings (Till/Til/Til'/See you); the gate passes the canonical form, warns on variants, fails on absence and auto-fixes.

## Images. `G-07` (warn-only)

Evidence-driven screenshots, marked `[SCREENSHOT: what to capture]` in layout and draft — median 7 per Builds post; the gate warns under 3 for Builds only. Bridge and Field notes carry slots only where evidence demands one (gate reports INFO). Ricardo captures them manually; never generate body images. Cover slot marked `[COVER]`.

## Lists `[advisory]`

Bullets for genuine enumerations (tools used, metrics available) — corpus uses them freely. Never bullet-point prose that should be sentences, and never a bulleted argument: reasoning happens in paragraphs.

## Bucket routing (which structure to follow)

Pick the bucket first (see the bucket table in the article profile), then follow its structure. Structure templates are advisory;
the voice rules win on any conflict.

| Bucket | Structure to follow |
|---|---|
| Builds (`builds`) | Build story structure: pain, manual process, build, what broke, takeaway |
| Explainers (`explainers`) | Explainer post structure: friction, definition plus analogy, worked example, takeaway |
| Bridge (`bridge`) | Conceptual post structure: idea, framework, story as evidence, reader's mirror |
| Field notes (`field-notes`) | Short (400-900 words); open on the take, no template; end on the reader's next action or a flat note |

## Build Story Structure

For posts about automating a personal or business workflow ("I built X so I don't have to do Y manually"). Distinct from both Technical Deep-Dive (leads with a system/metric) and Conceptual/Career (leads with an idea). This one leads with a tedious, relatable process.

### Shape

1. **The manual process** — Concrete, specific, mildly tedious. Named tools, real cadence ("every month," "twenty to thirty entries"). End on the honest admission that it worked but was annoying.
2. **The discovery** — Where the better tool/approach came from (a community, a coworker, a doc someone shared). One or two sentences. Don't dramatize it.
3. **The build** — What you actually built, named tools included (MCP, Claude Code skill, specific APIs). Explain the mechanism in plain terms, not a feature list.
4. **The real problems, named** — Every build like this has at least one non-obvious design problem (idempotency, a mapping/classification step, a race condition, a trust boundary). Name it, explain the trade-off you made, and admit the honest limitation. This section is where technical credibility lives — skip it and the post reads as a product pitch.
5. **The first real run** — Concrete numbers from an actual run: how much had piled up, what got processed, how long it took versus before.
6. **What to steal** — Generalize the pattern one level up so it's not just "use my exact tools." End forward: an open question, a known rough edge, or what happens next. Not a summary of what was covered.

### Anti-patterns specific to this structure

- Turning step 3 into a feature list ("it does X, Y, and Z"). Explain the mechanism, not the spec sheet.
- Skipping step 4. A build post with no acknowledged trade-off reads as marketing.
- Ending on enthusiasm ("this changed how I think about automation!") instead of the concrete next question.
- Screenshots or data that reveal real personal information — use fictional-but-realistic placeholder data instead (see workflow note below).

### Workflow note

When the post needs screenshots of tools with real personal data (finance trackers, private dashboards), populate a throwaway or duplicate view with fictional-but-realistic data before capturing — not obviously-fake placeholders ("Expense 1 - $100"), but data that reads like a real row without being one.

## Explainer Post Structure

For posts that teach a concept, tool, or method ("what X is and how to use it"). No repo is the subject: the sources are URLs, docs, a course, or a spec, and Ricardo is the guide, not the builder. Distinct from Build Story (a thing Ricardo made) and Conceptual (an idea argued from his own story).

Every rule below is observed in the corpus, cited by filename. Numbers are descriptive, not quotas.

### Shape

1. **Open on the reader's friction or the old assumption.** First lines name a frustration the reader has had, or a mistaken habit Ricardo used to have. Not a definition. (`2025-08-31-uv-the-tool-that-helps-you-manage`: "conflicting package versions, virtual environment headaches"; `2025-09-29-understanding-model-context-protocol`: copy-pasting data into a model; `2026-03-09-how-a-football-framework-for-measuring`: "I used to think starting a data project was about jumping straight to the data.")
2. **Define the thing in one bolded sentence, then an analogy.** One plain definition, then a single everyday comparison. (`2025-09-29-understanding-model-context-protocol`: MCP as a USB-C port; `2025-08-31-uv-the-tool-that-helps-you-manage`: Swiss Army knife; `2025-06-27-the-art-of-football-data-scouting`: Moneyball as the entry point.)
3. **Name the source of the knowledge.** A docs site, a course, a spec, a quote from the person who built it. Link it. (`2026-03-09-how-a-football-framework-for-measuring`: the Twelve course and its quoted line; `2025-09-29-understanding-model-context-protocol`: spec, Anthropic docs, GitHub org listed under resources; `2025-06-27-the-art-of-football-data-scouting`: Rasmus Ankersen quote.)
4. **Flat headings that read like the questions the reader would ask.** "What is X?", "Why X beats Y", "How to use it", "Key takeaways". No clever section names. (`2025-08-31-uv-the-tool-that-helps-you-manage`, `2025-09-29-understanding-model-context-protocol`: 7 to 10 `##`/`###` headings each.)
5. **Break the concept into named parts, one short block each.** Three files, three primitives, five metrics: enumerate, give each one or two sentences. (`2025-08-31-uv-the-tool-that-helps-you-manage`: `pyproject.toml` / `uv.lock` / `.venv`; `2025-09-29-understanding-model-context-protocol`: host / client / server, then resources / tools / prompts.)
6. **Compare against what the reader already uses.** Place the thing next to the incumbents, with one honest line per rival. (`2025-08-31-uv-the-tool-that-helps-you-manage`: pip, Poetry, Conda, including Ricardo's own Conda history.)
7. **Show the concept working on one concrete example, then transfer it.** One worked example carries the abstraction; a second domain proves it travels. (`2025-06-27-the-art-of-football-data-scouting`: Como 1907 case study; `2026-03-09-how-a-football-framework-for-measuring`: Passing Quality score with its weights, then diabetic patient monitoring; `2025-08-31-uv-the-tool-that-helps-you-manage`: step-by-step setup of his tutorials repo.)
8. **Put commands, weights, or numbers in the example, not adjectives.** "30%, 20%, 20%, 20%, 10%"; `uv sync`; "66.5% of possessions". (`2026-03-09-how-a-football-framework-for-measuring`, `2025-08-31-uv-the-tool-that-helps-you-manage`, `2025-06-27-the-art-of-football-data-scouting`.)
9. **Close on what the reader takes away, as a short list or one rule.** Key Takeaways or a stated principle, or a "do this next" list with the docs link. Not a recap of every section. (`2026-03-09-how-a-football-framework-for-measuring`: "Start with the human question"; `2025-08-31-uv-the-tool-that-helps-you-manage`: "Getting Started Today" steps; `2025-09-29-understanding-model-context-protocol`: resources and takeaways.)
10. **Part two assumes part one and does not re-explain.** A follow-up opens with one recap list, then goes straight to the new step. (`2025-07-06-the-art-of-football-data-scouting-d2a`: three-step recap, then steps 2 and 3.)

### Length observed

About 700 to 1,450 words across the five posts: `2026-03-09-how-a-football-framework-for-measuring` (702), `2025-07-06-the-art-of-football-data-scouting-d2a` (936), `2025-08-31-uv-the-tool-that-helps-you-manage` (1,137), `2025-06-27-the-art-of-football-data-scouting` (1,172), `2025-09-29-understanding-model-context-protocol` (1,452). The shortest carried the single-idea framework; the longest carried a tool plus a code walkthrough.

### Anti-patterns specific to this structure

- Opening on a definition or "In this post I will explain". Open on the friction (rule 1).
- A feature list with no worked example. `2025-09-29-understanding-model-context-protocol` leans toward this in its tool inventory; the example must carry the weight.
- Treating one tool's repo as the subject. If the repo is what you built, it is a Build, not an Explainer.
- Re-explaining a concept covered in an earlier post (rule 10).
- Unattributed claims. Explainers borrow authority from sources, so link them (rule 3).

### Checklist before publishing

- [ ] Opens on a reader's friction or an old assumption
- [ ] One bolded definition and one analogy
- [ ] Sources named and linked (docs, course, spec)
- [ ] One worked example with real commands or numbers
- [ ] Compared against what the reader already uses
- [ ] Ends on a takeaway or next step, not a recap
- [ ] Gate zero: the reader can do something specific tomorrow

## Conceptual Post Structure
### For idea-led, career, and mindset posts

This reference covers a second writing mode not present in the technical deep-dive templates.
Use this when the post is about a concept, not a system.

---

### When to Use This Mode

- Career transitions and identity
- Mindset, career capital, learning philosophy
- "Why I build what I build" meta posts
- Any post where the thesis is an idea, not a metric

**Examples from The Underdoc**:
- "Embrace Your Weirdness" (weird skill combination as advantage)
- A future post about why you share publicly
- A post about what building teaches you that studying doesn't

---

### The Conceptual Post Structure

#### 1. Opener: Idea or Provocation (not a story)

Start with the concept, a tension, or a challenge to conventional thinking.
The reader needs to know immediately what they're reading about.

**Pattern**: State the idea → name the opposing pressure people feel

```
A concept I believe is really important nowadays — when AI is closing the gap
of what you can create and where you come from — is: weirdness. The strange
combination of skills that make you a valuable individual.

At some point of our lives, someone tells you to pick a lane.
```

#### 2. The Opposing View (Briefly)

Give the counterargument its due — one quote, one line, one beat.
Don't knock it down yet. Let it land.

```
"Pick one thing, go deep enough and become an expert at that for the rest of your life."
```

#### 3. Your Reframe

One or two sentences that flip the premise.

```
Although the most interesting people I've come across didn't get there by picking a lane — but by refusing to.
```

#### 4. The Framework (External Source)

Bring in a book, thinker, or framework that supports your argument.
Name it specifically. Don't paraphrase so heavily it disappears.

```
I've been recently reading Dan Koe's Purpose & Profit where he says the education
system was never designed to help you reach your potential but to produce useful workers.
```

**Note**: If this framework was already covered in a previous post (e.g., Cal Newport's career capital), reference it in one sentence and move on. Don't re-explain it.

#### 5. Your Story as Evidence

This is the personal section. Fast, factual, no drama.
You're proving the concept with your lived experience — not narrating a saga.

See `ricardo-voice-patterns.md` → Story-Mode Patterns for execution rules.

**Structural beats** (from "Embrace Your Weirdness"):
- Starting point (where you came from)
- The pivot or stumble (what changed)
- What you accumulated (the weird stack)
- The honest self-check (gap you filled)
- The intersection (what you now have)
- The craft moment (behavior that proves alignment)

#### 6. The Reader's Mirror

Turn the lens outward. Give the reader a framework to apply to themselves.
Concrete questions or prompts, not abstract advice.

```
Some self-awareness is necessary here. Start by asking yourself these three questions:

- Is there something you know that most people in your field don't?
- Where do your interests converge?
- What can you build to work at the intersection of it?
```

**Note on format**: Questions can use bullets here — they're a list by nature and the reader needs to pause on each one.

#### 7. The Closer: Return to the Stakes

Return to the original tension. Why does this matter now? What happens to people who don't do this?
End with a sentence that's about the reader, not about you.

```
Your weirdness is your moat.
```

---

### Pacing Rules for Conceptual Posts

- **No section should be longer than ~4 short paragraphs**
- **Alternate between short and long paragraphs** (Cole rhythm applies here too)
- **The story section is NOT the longest section** — it's evidence, not the centerpiece
- **The practical section (reader's mirror) earns its length** — be specific

---

### External Inspiration Protocol

Sometimes a post is inspired by someone else's writing (a LinkedIn post, an article, a friend's story).

**Rules**:
- Never copy structure or language — absorb the spirit, write your own version
- Credit the person if you reference them directly ("a friend from LinkedIn, Anas Riad, shared a story that...")
- If you're just inspired, no need to credit — the post becomes your own
- Ask: what is the *lesson* in their story, and how does *your* story illustrate the same lesson differently?

---

### What Conceptual Posts Are NOT

- ❌ A recap of a book (you're adding your experience, not summarizing)
- ❌ A listicle of advice (structure around an idea, not bullet points)
- ❌ A therapy session (emotion serves the idea, not the other way around)
- ❌ A repeat of a previous post's framework (reference it, move on)

---

### Checklist Before Publishing

- [ ] Opener states the idea, not a story
- [ ] External framework named specifically (book title, author)
- [ ] Personal story is fast and factual — no drama between beats
- [ ] Story section positions you as example, not hero
- [ ] Reader gets a concrete tool or question to apply
- [ ] Closer is about the reader
- [ ] No framework repeated from a previous post without referencing that post
- [ ] Professional discretion rules followed (no employer references)
