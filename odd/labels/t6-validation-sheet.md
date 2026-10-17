# T6 judge-alignment sheet

Ricardo, this sheet is a pre-filled grading of two generated Underdoc articles, written by Claude before it saw any LLM-judge output.
`[x]` means the section meets the criterion (score 1). `[ ]` means it does not (score 0).
Read each line, and flip any box you disagree with. Your flips are the most valuable signal, because your final sheet is compared against the LLM judges to measure judge alignment.
Optionally append `<- me: reason` to a line you flipped.
When you are done, say "done" in chat.
Rubrics are the ones the judges use: strict, binary, one section at a time, whole section must be clean for a 1.

## 2025-08-12-using-agentic-ides-for-football-analytics · explainers

- Generated article: [article.md](../../lessons/writing_workflow/outputs/s1/s1-t6-validation-r1/2025-08-12-using-agentic-ides-for-football-analytics/article.md)
- Ground truth: [article_ground_truth.md](../../lessons/writing_workflow/inputs/evals/underdoc_dataset/data/2025-08-12-using-agentic-ides-for-football-analytics/article_ground_truth.md)

Anchor choice: the ground truth has no H2s (it uses H4 headings), so FollowsGT sections are the Introduction plus the seven H4 headings of the ground truth. UserIntent sections are the six "Section intents" of the guideline, matched to the generated H2s (intent 6 maps to two generated H2s, listed together). VoiceAdherence sections are the generated H2s plus "Introduction"; H3s stay inside their H2.

### FollowsGT

#### "Introduction"

- [x] follows_gt.content: both open on the shift in how code gets written and cite Karpathy's "Software Is Changing (Again)" talk with the same claim (more thinking, planning, reviewing than writing from scratch).
- [x] follows_gt.flow: generated opens with an invented anecdote ("it renamed a column that three of my plots depended on") and adds "I don't work that way on everything"; ground truth goes ChatGPT era, Karpathy quote, tools rising.
- [x] follows_gt.structure: ground truth sets Karpathy's words as a bold blockquote with a footnote; generated paraphrases inline with a plain link and no blockquote.

#### "What are Agentic IDEs?"

- [x] follows_gt.content: both define agentic IDEs and list the same capabilities (several LLM providers, indexing codebase and docs, MCP, autonomous edits, completions) and mention Claude Code and Gemini CLI.
- [x] follows_gt.flow: generated adds a "friend finishing your sentence" analogy and drops the planning-to-execution and workflow-adaptation points; ground truth ends on those.
- [x] follows_gt.structure: ground truth uses a bulleted capabilities list; generated packs them into one sentence, "You get several LLM providers inside one window, indexing over your codebase...".

#### "What are their main challenges?"

- [x] follows_gt.content: ground truth challenges are about using the tools (which LLM for which task, rate limits, prompt formats, context window, agent leash, MCPs); generated lists code failures ("Invented columns", "Repeated code"), which the ground truth puts under Example 1.
- [x] follows_gt.flow: ground truth has personal Cursor/Trae intro, the Uncle Ben quote, then six challenges; generated has four failures and an explanation paragraph, "The fourth bullet belongs to a different category."
- [x] follows_gt.structure: ground truth has a callout quote and plain bullets; generated uses bold-lead bullets ("**Invented columns.**") and no quote.

#### "How can you leverage them for Football Analytics?"

- [x] follows_gt.content: both give the three-file setup (rules.mdc, project_context.md, task log), Git before accepting suggestions, and indexing only necessary folders and docs.
- [ ] follows_gt.flow: generated adds a long caveat that "`rules.mdc` is a Cursor convention" and a paragraph on version accuracy; ground truth has none of that and ends with a one-line flow summary, generated has a mermaid diagram instead.
- [x] follows_gt.structure: ground truth is a numbered list with nested numbered files; generated uses H3 per file ("### rules.mdc") plus a mermaid block.

#### "Football Examples"

- [x] follows_gt.content: both cover the six-plot dashboard (coordinate confusion 0-100 vs 120x80, fixed by documenting dimensions) and the GPT-5 on-ball sequences with Dean Huijsen and about 39-43 m.
- [x] follows_gt.flow: ground truth walks the framework steps per example and the 3 prompting steps; generated skips them and adds a long distance-formula explanation ("take the difference on x, take the difference on y, square both").
- [x] follows_gt.structure: ground truth uses H5 per example, bulleted steps, and bold "challenges" and "takeaway"; generated uses H3 and plain prose with no bold callouts.

#### "How to get reliable results from the models"

- [x] follows_gt.content: both advise specific inputs and data specs, indexing context, and getting a plan or explanation before running (generated "Ask for a plan first").
- [x] follows_gt.flow: ground truth has 4 items in the order specific inputs, paste snippets, index, explain logic; generated has 5 in a different order and adds "Commit before you accept a suggestion".
- [x] follows_gt.structure: both are a plain bulleted list of short guidance items with no sub-headings or bold.

#### "Quick comparison between Cursor vs Trae based on my experience"

- [x] follows_gt.content: same facts per tool (Cursor Agent mode with Claude Sonnet 4, MCP, $20 Pro and quiet rate-limit change; Trae $3 then $10, 600 requests, Builder modes, SOLO waitlist).
- [x] follows_gt.flow: ground truth has one bulleted block per tool; generated uses a combined table plus two opinion paragraphs and a "verified in November 2025" note.
- [x] follows_gt.structure: ground truth uses H5 per tool with bullets; generated uses a markdown table, "| | Cursor | Trae |".

#### "Final thoughts"

- [x] follows_gt.content: ground truth closes on guardrails (index docs, sanity checks after every iteration, simple tests, state assumptions before coding); generated closes with one tip, "write `project_context.md`".
- [x] follows_gt.flow: ground truth goes summary, start small, guardrails, repeat the flow line; generated is a single short call to action.
- [x] follows_gt.structure: generated ends the section with a "* * *" separator and sign-off, "Till next time, Ricardo."; the ground truth section has neither.

### UserIntent

#### "Introduction"

- [x] user_intent.guideline_adherence: intent 1 wants a framing of the shift with a credible reference; generated adds an unrequested incident ("it renamed a column that three of my plots depended on") and "When I want to understand a piece of a project properly, I still write it by hand".
- [ ] user_intent.research_anchoring: the column-rename incident and "twenty minutes debugging a chart" are not in the research; only the Karpathy claim is.

#### "What is an agentic IDE?"

- [x] user_intent.guideline_adherence: defines agentic IDEs in plain terms and lists what they offer (LLM providers, indexing, MCP, edits), as intent 2 asks.
- [x] user_intent.research_anchoring: "read your files, run commands and edit the code" adds "run commands", which the research does not mention; the sentence-finishing friend analogy is invented framing.

#### "Where it breaks in practice"

- [x] user_intent.guideline_adherence: lists the practical difficulties day to day (invented columns, coordinate systems, repeated code, changing model and plan terms).
- [x] user_intent.research_anchoring: "It rewrote the same matplotlib function four times in one file" and "picked the wrong one for a shot chart" add a count and a chart type the research does not give.

#### "The setup I use on every project now"

- [x] user_intent.guideline_adherence: intent 4 wants a lightweight setup that works across tools; generated adds a Cursor-only caveat paragraph, a mermaid diagram and a version-accuracy digression.
- [x] user_intent.research_anchoring: "Trae, Claude Code and Gemini CLI each read their own file, with a different name" and the library list "pandas, matplotlib, seaborn" (seaborn) are not in the research.

#### "Two football tasks"

- [x] user_intent.guideline_adherence: both tasks plus errors and the context fix are there, but a long distance-gain derivation ("square both, add them, take the square root") and a grid-comparison paragraph go well beyond the intent.
- [x] user_intent.research_anchoring: "The first run gave me a number I had no way to check", the scaling-to-metres derivation and "The endpoint pairs live in the event data" are not in the research.

#### "How do I get reliable output? + Cursor vs Trae, honestly"

- [x] user_intent.guideline_adherence: guidance then comparison are both present, but generated adds a closing "Where to start" section and a recommendation paragraph not in intent 6.
- [x] user_intent.research_anchoring: "I verified the prices, request limits and model availability in November 2025" and "I pay for Cursor" are not in the research.

### VoiceAdherence

#### "Introduction"

- [x] voice.first_person_voice: "I caught it in the diff", "how I write code now" keep the narrator as I.
- [x] voice.concrete_specifics: names Andrej Karpathy, the talk title, "three of my plots", "twenty minutes".
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned opener or inversion structure found.
- [x] voice.spoken_rhythm_and_punctuation: "That failure is the price of how I write code now. Planning what I want ... Andrej Karpathy made the same point ..." is a three-sentence paragraph of about 70 words.
- [ ] voice.no_invented_biography: the opening incident ("it renamed a column that three of my plots depended on and told me the code was cleaner that way") is not in the research and looks invented; flip if it truly happened.

#### "What is an agentic IDE?"

- [x] voice.first_person_voice: "Across the tools I've tried", "the two I've used the most".
- [x] voice.concrete_specifics: names Cursor, Trae, Claude Code, Gemini CLI and Model Context Protocol (MCP).
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: none found; the analogy is a plain comparison.
- [x] voice.spoken_rhythm_and_punctuation: "Across the tools I've tried, the feature list is roughly the same. You get several LLM providers inside one window, ..." runs about 53 words in one paragraph.
- [x] voice.no_invented_biography: only tool usage that the research supports.

#### "Where it breaks in practice"

- [x] voice.first_person_voice: "There are like four failures I hit over and over", "my dataframe".
- [x] voice.concrete_specifics: "120x80", "0-100", GPT-5, Cursor, Trae, matplotlib.
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [x] voice.spoken_rhythm_and_punctuation: short bullets, short paragraphs, no em dash or semicolon.
- [x] voice.no_invented_biography: the failures are supported by the research (misnamed columns, coordinate confusion, repeated functions); the "shot chart" and "four times" details are embellishment, flip if you object.

#### "The setup I use on every project now"

- [x] voice.first_person_voice: "Mine says", "I adapted the structure", "I initialise Git".
- [x] voice.concrete_specifics: rules.mdc, project_context.md, tasks.md, project_log2025.md, pandas, matplotlib.
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [ ] voice.spoken_rhythm_and_punctuation: "The two habits are simple. I initialise Git ... Indexing by itself does not guarantee that: the version accuracy comes from ..." is one paragraph of well over 100 words.
- [x] voice.no_invented_biography: habits match the research; "so I don't re-explain the project every morning" is small color.

#### "Two football tasks"

- [x] voice.first_person_voice: "I asked the agent", "For this one I used GPT-5 inside Cursor".
- [x] voice.concrete_specifics: Salzburg vs Real Madrid, Dean Huijsen, "about 39 m", "43 m", 120x80, 0-100.
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [ ] voice.spoken_rhythm_and_punctuation: "At 120x80 the pass start sits at one pair of coordinates ... take the square root." is a single paragraph of roughly 100 words.
- [ ] voice.no_invented_biography: "I still checked the first result by hand before using it" and "The first run gave me a number I had no way to check" are not in the research; flip if true.

#### "How do I get reliable output?"

- [x] voice.first_person_voice: imperative advice to the reader, no default "we".
- [x] voice.concrete_specifics: "Column names, coordinate ranges, date formats", "more than two files".
- [x] voice.no_slop_vocabulary: no banned words found.
- [ ] voice.no_slop_structures: "Write the rules file before your first prompt, not after your first broken chart." is an "X, not Y" tail.
- [x] voice.spoken_rhythm_and_punctuation: short bullets, no em dash or semicolon.
- [x] voice.no_invented_biography: advice only, no claimed history.

#### "Cursor vs Trae, honestly"

- [x] voice.first_person_voice: "I pay for Cursor", "what I hit while using both".
- [x] voice.concrete_specifics: "$20/month", "$3 for the first month, then $10", "600 requests per month", Claude Sonnet 4, Supabase.
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found; the closing trade-off sentence is a plain contrast.
- [ ] voice.spoken_rhythm_and_punctuation: "Everything in this table comes from DataCamp's ... tutorials and from what I hit while using both. I verified ..." is a two-sentence paragraph of about 75 words.
- [ ] voice.no_invented_biography: "I verified the prices, request limits and model availability in November 2025" is a dated verification event not in the research.

#### "Where to start"

- [x] voice.first_person_voice: direct advice with no "we" as default narration.
- [x] voice.concrete_specifics: "project_context.md", "Pitch dimensions, the columns you actually have", "about ten minutes".
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [ ] voice.spoken_rhythm_and_punctuation: the three-sentence paragraph "Before your first prompt ... it costs about ten minutes." is about 55 words.
- [x] voice.no_invented_biography: nothing beyond the article's own two tasks.

## 2025-12-26-building-a-rag-system-that-generates · builds

- Generated article: [article.md](../../lessons/writing_workflow/outputs/s1/s1-t6-validation-r1/2025-12-26-building-a-rag-system-that-generates/article.md)
- Ground truth: [article_ground_truth.md](../../lessons/writing_workflow/inputs/evals/underdoc_dataset/data/2025-12-26-building-a-rag-system-that-generates/article_ground_truth.md)

Anchor choice: FollowsGT sections are the ground truth's eight H2s ("Long time no see" is the first, there is no text before it). Two ground-truth sections have no counterpart in the generated article ("Why This Matters" and "Bottom Line"), so they are scored 0 on every criterion. UserIntent sections are the six "Section intents" of the guideline, matched to generated H2s (intents 5 and 6 each map to two H2s, listed together). VoiceAdherence sections are the generated H2s plus "Introduction"; the H3 stays inside its H2.

### FollowsGT

#### "Long time no see"

- [x] follows_gt.content: generated intro plus "What was annoying me" cover the seasonal check-in, why he is back, the pain of gathering free match data, and the ideal natural-language interaction.
- [x] follows_gt.flow: ground truth goes greeting, return note, problem, ideal question in one section; generated adds an invented anecdote ("started working ... at 9pm and looked up at 3am") and splits the problem into its own H2.
- [x] follows_gt.structure: ground truth sets the problem and the ideal question as bold callouts; generated has no bold and adds a separate H2, "What was annoying me".

#### "What I Built"

- [x] follows_gt.content: both present the live demo on Hugging Face Spaces, the RAG definition, Eredivisie data from WhoScored and Fotmob, 108 matches, ~1,355 events, three providers, $0.50, and dual-mode.
- [x] follows_gt.flow: ground truth ends with a bulleted feature list and the dashboard article link; generated adds a validation-limitation paragraph ("It does not verify yet that a number belongs to the match") and screenshot placeholders.
- [x] follows_gt.structure: ground truth uses a bold-label bullet list ("**108 Eredivisie matches indexed**"); generated uses prose paragraphs and "[SCREENSHOT: ...]" placeholders.

#### "Why This Matters"

- [x] follows_gt.content: no generated section covers who benefits (coaches, scouts, analysts, fans, developers) or the value of one place for data; section missing.
- [x] follows_gt.flow: section missing from the generated article.
- [x] follows_gt.structure: section missing from the generated article. (dont understand why)

#### "How It Works"

- [x] follows_gt.content: both give the flow (route, retrieve, generate, validate, deliver) and the same decisions (2-chunk design, 38 pre-calculated features, metadata filtering, bypassing the LLM for plots, Pydantic golden dataset).
- [x] follows_gt.flow: generated adds scrape and compute-features steps (six steps vs five) and adds trade-off commentary ("a question that never names a team gives the filter nothing to grab").
- [x] follows_gt.structure: ground truth has an ASCII diagram, bold numbered steps and a bold-label bullet list; generated uses a plain numbered list, a mermaid diagram and an H3, "### The decisions behind it".

#### "The Results"

- [x] follows_gt.content: both report retrieval accuracy 100% vs 70%, faithfulness 99.4%, tactical insight 95.0%, about $0.0001 per query and the wrong-name limitation.
- [x] follows_gt.flow: generated adds a long judge-scoring methodology ("The match score is the share of that match's criteria the judge marked as met") and a chart; ground truth is a short metric-by-metric list.
- [x] follows_gt.structure: ground truth uses bold metric lines ("**Retrieval Accuracy: 100%**") with one-line explanations; generated uses prose and an xychart block.

#### "What's Next: The Series Roadmap"

- [x] follows_gt.content: both list the same five upcoming posts (ETL, prompt engineering, evaluation-driven development, deployment, production scaling).
- [x] follows_gt.flow: ground truth elaborates each post (what RAG is, V1.0 to V3.5 iterations, three-metric framework, CI/CD); generated gives one short line each and drops most of that detail.
- [x] follows_gt.structure: ground truth uses bold post titles followed by descriptions; generated uses plain one-line bullets with no bold.

#### "Try It Yourself"

- [x] follows_gt.content: both invite readers to try the demo with their own API key and to clone the open-source repo.
- [x] follows_gt.flow: ground truth includes six example queries and "Clone it. Run it locally."; generated has no example queries and adds "open an issue on GitHub".
- [x] follows_gt.structure: ground truth has bold links and bold-labelled quote lists; generated uses plain "The demo:" and "The repo:" lines.

#### "Bottom Line"

- [x] follows_gt.content: no generated section closes with the project goal and the "idea to working system" reflection; section missing.
- [x] follows_gt.flow: section missing from the generated article.
- [x] follows_gt.structure: section missing from the generated article.

### UserIntent

#### "Introduction"

- [x] user_intent.guideline_adherence: opens with the new-season check-in and gives reasons for writing again, as intent 1 asks.
- [x] user_intent.research_anchoring: "One Saturday I started working on the football RAG system at 9pm and looked up at 3am" is not in the research.

#### "What was annoying me"

- [x] user_intent.guideline_adherence: states the pain across WhoScored and Fotmob and the ideal "type a question, get the numbers and the chart" interaction.
- [x] user_intent.research_anchoring: "remind yourself what PPDA (passes allowed per defensive action) actually measures" and the Ajax vs Heracles example question are not in the research.

#### "What the app does"

- [x] user_intent.guideline_adherence: demo, modes, 108 matches and $0.50 are there, but it adds a validation limitation ("It only checks that the number appears somewhere in the dataset") that belongs to the failure-modes section.
- [x] user_intent.research_anchoring: "so a real number attached to the wrong match can still get through" goes beyond the research, which only says occasional wrong team names or statistics.

#### "How it works at a high level"

- [x] user_intent.guideline_adherence: intent 4 says without deep detail; generated adds per-decision trade-off paragraphs and a very large mermaid diagram that includes evaluation and roadmap nodes.
- [x] user_intent.research_anchoring: "a question that never names a team gives the filter nothing to grab, and I do not have a clean answer for those queries yet" is not in the research.

#### "First evaluation results + Where it still fails"

- [x] user_intent.guideline_adherence: all the figures and failure modes are present, but a long scoring-method explanation ("the average of the 10 match scores, and every match carries the same weight") and "I am not publishing the per-criterion breakdown yet" are extra.
- [x] user_intent.research_anchoring: "Each match has one rubric with a set of criteria", "I wrote the questions and the rubrics" and "Index a match under the wrong team name and retrieval will confidently hand it back" are not in the research.

#### "What comes next in this series + Try it, then break it"

- [x] user_intent.guideline_adherence: five upcoming posts in the planned order, then an invite to try the demo and clone the repo; the GitHub-issues ask is a small flourish on the invite.
- [x] user_intent.research_anchoring: "and the smaller one gives better answers" and "how I turned that rubric into something I run every time I touch the prompt" are not in the research.

### VoiceAdherence

#### "Introduction"

- [x] voice.first_person_voice: "I want to use this one to write more", "I lost track of time".
- [x] voice.concrete_specifics: "9pm", "3am", "the football RAG system".
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [x] voice.spoken_rhythm_and_punctuation: "I lost track of time on this project more than once. One Saturday ... So this post is partly a launch, partly a self-check." is a four-sentence paragraph of about 85 words.
- [x] voice.no_invented_biography: "One Saturday I started working on the football RAG system at 9pm and looked up at 3am" and "writing it down is the only way I have to check that I actually understand it" are not supported by the research; flip if true.

#### "What was annoying me"

- [x] voice.first_person_voice: "which is what I did", "What I wanted".
- [x] voice.concrete_specifics: WhoScored, Fotmob, matplotlib, PPDA, "how did Ajax press in the second half against Heracles?".
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [x] voice.spoken_rhythm_and_punctuation: "WhoScored has one set of events. Fotmob has another. ... remind yourself what PPDA ... repeat." is a five-sentence paragraph of about 85 words.
- [x] voice.no_invented_biography: the dashboard reference is supported by the research.

#### "What the app does"

- [x] voice.first_person_voice: "testing everything across all three providers cost me about $0.50".
- [x] voice.concrete_specifics: Hugging Face Spaces, Anthropic Claude, OpenAI, Gemini, 108 matches, 1,355 events.
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [x] voice.spoken_rhythm_and_punctuation: "The model still writes the sentence, but ... so a real number attached to the wrong match can still get through." is a three-sentence paragraph of about 65 words.
- [x] voice.no_invented_biography: facts match the research.

#### "How it works at a high level"

- [x] voice.first_person_voice: "give me the raw Eredivisie event data", "I do not have a clean answer".
- [x] voice.concrete_specifics: PPDA, "38 tactical features", "two chunks per match", "70% to 100%", ChromaDB, Pydantic.
- [x] voice.no_slop_vocabulary: no banned words found.
- [ ] voice.no_slop_structures: "It is an existence check, not a correctness check, so a real number attached to the wrong team still gets through." is an "X, not Y" tail.
- [ ] voice.spoken_rhythm_and_punctuation: "Metadata filtering instead of pure semantic search. Retrieval filters on ... so it stays." is a four-sentence block of about 75 words.
- [x] voice.no_invented_biography: nothing beyond the research.

#### "First evaluation results"

- [x] voice.first_person_voice: "I evaluated on 10 diverse matches", "I am not publishing".
- [x] voice.concrete_specifics: "99.4%", "95.0%", "$0.0001", "Claude Haiku 4.5", "6 to 7 seconds".
- [x] voice.no_slop_vocabulary: no banned words found.
- [ ] voice.no_slop_structures: "So 99.4% is the mean of 10 per-match shares, not a single pooled count across every criterion in the set." is an "X, not Y" tail.
- [ ] voice.spoken_rhythm_and_punctuation: "The judge worked criterion by criterion. For each match it read the answer ... So 99.4% is the mean ..." is a long paragraph of about 100 words.
- [x] voice.no_invented_biography: matches the research (LLM judge, rubrics, reference answers).

#### "Where it still fails"

- [x] voice.first_person_voice: "I wrote the questions and the rubrics", "The failure I see most".
- [x] voice.concrete_specifics: "Ten matches", "wrong team name", "golden dataset".
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [x] voice.spoken_rhythm_and_punctuation: short two- and three-sentence paragraphs under about 45 words, no em dash or semicolon.
- [x] voice.no_invented_biography: "I wrote the questions and the rubrics" is a reasonable first-person fact for this project; flip if the questions came from elsewhere.

#### "What comes next in this series"

- [x] voice.first_person_voice: "My prompt went from 1,800 tokens ... down to 360".
- [x] voice.concrete_specifics: "1,800 tokens in V1.0", "360 in V3.5", Hugging Face Spaces.
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [x] voice.spoken_rhythm_and_punctuation: short bullets and one-line paragraphs, no em dash or semicolon.
- [ ] voice.no_invented_biography: "how I turned that rubric into something I run every time I touch the prompt" claims a deliberate method the research does not support.

#### "Try it, then break it"

- [x] voice.first_person_voice: "I would rather collect those cases in public".
- [x] voice.concrete_specifics: full demo and repo URLs, "open an issue on GitHub".
- [x] voice.no_slop_vocabulary: no banned words found.
- [x] voice.no_slop_structures: no banned structure found.
- [ ] voice.spoken_rhythm_and_punctuation: "Paste your own API key and ask it something ... than after the series is done." is a five-sentence paragraph of about 90 words.
- [x] voice.no_invented_biography: no claimed history.
