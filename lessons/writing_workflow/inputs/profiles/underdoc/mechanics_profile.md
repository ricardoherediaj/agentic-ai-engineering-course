<!-- GENERATED FILE, do not edit by hand. Source: Underdoc harness repo (TheUnderdoc/harness). Files: skill/references/voice-mechanics.md, skill/references/ai-slop-blacklist.md. Regenerate with scripts/sync_underdoc_profiles.py. -->

Where the slop blacklist and the voice rules disagree, the voice rules in this file win. Only the blacklist's banned lists are included; its older style rules are superseded by the voice rules.

# Voice — Mechanics

Point of view, word choice, punctuation. Gates: `G-04` (pronouns), `G-05` (slop). Examples are real published sentences with the source post.

## First person singular. `G-04`

"I" carries the piece. "We" only when it genuinely means Ricardo plus named others, or the reader-and-writer together in a walkthrough moment — never as default narration. Evidence: the four posts where we-count ≥ I-count averaged 4.5 reactions; the corpus average is far above that. That figure is small-n (four posts) — treat it as directional, not precise. The rule stands on its own regardless: a solo author writing "we" for their own work is a voice distortion.

- Good: "I built this dashboard using: Python 3.10, Beautiful Soup..." (`building-your-own-football-analytics`, 204 reactions)
- Bad: "In previous articles we've covered..." (`shipping-a-rag-system-app-to-hf-spaces`, 5 reactions)
- Bad: "Now that we've tackled the data preparation, we need to talk to it." (`rag-is-a-data-engineering-heavy-problem`, 5 reactions)

Gate math: I-count per 1k words must exceed we-count per 1k words. On failure the harness stops and hands to Ricardo — a pronoun pass changes who the piece is about.

## Slop blacklist — words and structures. `G-05`

Canonical lists: `checks/blacklist-words.txt` (54 words/phrases) and `checks/blacklist-patterns.txt` (22 sentence-structure regexes). Both editable without code. The words tier caught 32 live hits in the published corpus; 19 of them are the `leverage`/`leveraging`/`harness` family — dropping that one habit removes 59% of the problem. (`harness` as a noun for a test/agent harness is legitimate; `harness the power of` is not.)

Real published hits, with rewrites:

- Bad: "you can leverage this data and flag specific players" (`how-to-use-fbref`) → Good: "you can use this data to flag specific players"
- Bad: "Leveraging AI to create systems or tools is one of the things that excites me the most." (`building-a-rag-system`) → Good: "Using AI to build systems is one of the things that excites me the most."
- Bad: "it's crucial to understand why that dataset exists" (`from-vibes-to-metrics`) → Good: "you need to know why that dataset exists"
- Bad: "Seamless Integration: it handles the Gradio environment out of the box" (`shipping-a-rag-system`) → Good: "It handles the Gradio environment out of the box."

The patterns tier catches LLM sentence signatures — "X is more than Y; it's Z", "It's not X, it's Y", "cut through the hype", "what separates X from Y", fake-profound endings. The corpus has **zero** structural hits across 26 posts: Ricardo does not write these. The tier exists so assisted drafting never introduces them.

**The inversion punch is slop even when the regexes miss it.** Any two-beat reversal — a setup line then a short line flipping it, or a "by X, not by Y" tail — reads as AI to Ricardo regardless of wording. State the fact once, flat, and let it sit. (Live correction, 2026-08-23 mentor draft:)

- Bad: "Nobody in that group was called my mentor. / All of them were. I learned... by working next to them, not by asking anyone for guidance in the abstract." (AI draft, rejected as "if not x then y")
- Good: "I learned how professionals handle real event data from StatsBomb, Tracab, and Opta by working next to them every week. Nobody there ever used the word mentor."

The same shape hides in **trailing tag sentences**: a short sentence appended to a finished line that restates it or labels it. It mirrors the inversion punch and reads exactly as slop. Delete the tag and end on the concrete sentence already there. (Live correction, same draft:)

- Bad: "Pick one channel and take one action on it this week. That's the whole method."
- Good: "Pick one channel and take one action on it this week."

Related shapes to avoid, all the same two-beat family: mirrored halves ("The event is half of it. The follow-up is the other half."), concession flips ("It's the slowest. It's also the only one that..."), X/not-Y tails ("...in production, not in tutorials"), and the **Everyone/Nobody hook**, which is the highest-risk instance because it sits in the first line. (Live correction, same draft:)

- Bad: "Everyone tells you to get a mentor. Nobody tells you where mentors actually are."
- Good: "I got told to find a mentor for years before anyone explained where you actually find one."

Note this Bad example passed `G-05` cleanly — the regex tier only lists the literal "what nobody tells you". **The two-beat family is not machine-checkable and never will be.** Sweep for it by hand on every draft: read each pair of adjacent short sentences and ask whether the second one exists to reverse, mirror, or label the first. If it does, merge them into one flat statement or delete the second.

Three more AI tells from the same family, also not machine-checkable, swept alongside the two-beat family: **weasel attribution** ("experts agree", "studies show", "which suggests that" — cite a real name or number, or state it flat), **synonym cycling** (renaming the same object for variety: "The agent handles your email. The assistant drafts replies." — call it one name), and **"This is where X comes in"** (a dead transition — show X instead of announcing it).

## Punctuation: no em-dashes, no semicolons `[advisory, measured]`

Corpus median is zero for both, in every performance band. Use a comma, a period, or a new sentence. This describes existing practice, not a new constraint.

- Good: "Specialization isn't bad. But betting your entire identity on a single skill, in a world that's moving this fast, is the riskiest thing you can do." (`embrace-your-weirdness`)
- Bad: "Specialization isn't bad — but betting your entire identity on a single skill; that's the risk."

## Active voice, verbs over nominalizations `[advisory]`

- Good: "I scraped data from Championship, League One, and League Two to find a hypothetical signing for Sheffield United." (`how-to-use-fbref`, 36 reactions)
- Bad: "Data was scraped from three leagues and an analysis was performed."

## Small rules `[advisory]`

- Acronyms: expand on first use (RAG, MCP, xG), then use freely.
- Emoji: none in body text. Corpus practice.
- Bold: sparing. Corpus bolds an occasional key term or main-point statement; a post with zero bold is fine. Never general emphasis — when in doubt, don't.
- Capitalization: sentence case in prose; headings may title-case tool names only because the tools are names.

## Slop blacklist (banned openings, structures, vocabulary)

### Banned opening moves
- "In this era of...", "In today's fast-paced world...", "As we navigate the complexities..."
- "In this post, I'll cover..." (throat-clearing — Cole's rule)
- Rhetorical question immediately answered as a hook. **[R]** Exception: the Eyebrow Raise pattern — external skepticism quoted in italics ("*Why tech? You are a doctor.*") is allowed; it's someone else's question, not a self-answered hook.
- "Imagine...", "Think of it like this..." analogy openers.

### Banned sentence structures
- "It isn't just X, it's Y." / "X is more than just Y; it's Z."
- "It wasn't X, it was Y."
- "This is where X comes in."
- Meta transitions: "Now that we've explored X, let's move on to Y."
- Compulsive rule-of-three (three parallel clauses in every other sentence).

### Banned vocabulary (unless quoting or technically required)
amazing, fascinating, mind-blowing, must-read, game-changer, groundbreaking, paradigm-shifting, transformative, pivotal, paramount, outstanding, a significant leap, delve, dive into, embark, endeavour, realm, tapestry, vibrant, leverage, harness, seamlessly, seamlessly integrates, effortlessly, robust, supercharge, elevate, unlock, "unlock the real power", "the best part is", "real magic happens", "recipe for disaster", thrive, cut through the noise/hype, crucial, critical, invaluable, significant/significantly, surprisingly, simply, neatly, "Whether you're X or Y".
