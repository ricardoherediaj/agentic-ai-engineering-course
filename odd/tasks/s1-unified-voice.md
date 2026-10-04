# S1: Unified voice in Brown (A2)

Status: ready to start
Plan: `~/Documents/TheUnderdoc/capstone-plan.md` (rev 2, sections 3, 5, 7, 8). Engram: `course/capstone-plan` (#35).
Branch: `feat/s1-unified-voice` (course repo) and the same branch name in `~/Documents/TheUnderdoc/harness`.
Engram copy: `odd/s1-unified-voice/tasks`.

## Goal

Prove or disprove A2: Brown fed with the canonical Underdoc voice (the harness) beats unchanged Brown on VoiceAdherence, FollowsGT and UserIntent by more than measured noise, on the 10-post test split of a 26-post Underdoc dataset, with every number traceable to an Opik experiment.

## Scope

In:
- Brown reads the harness voice through config and profile files only. Nova and Brown are extended, never rewritten (plan section 4 invariant).
- `explainers` bucket rules in the harness, written before labeling.
- Underdoc eval dataset: 26 samples, 4 bucket labels, splits 2 few-shot / 2 validation / 22 test.
- New `VoiceAdherence` metric that uses the same base class and pattern as `follows_gt` and `user_intent`.
- Baseline vs. new runs in Opik, noise measured on a 5-post subset, written verdict.

Out: monorepo (S0), Nova build-reading tool (S2), Underdoc MCP (S3), deployment (S4), Claude Code sessions as input, any database.

## Decisions taken for this file

- Baseline = unchanged Brown: course profiles plus `paul_iusztin.md`, run through the same pipeline. Using the same generator isolates the voice variable. Ricardo can override this before T6.
- In S1 the canonical voice stays in the harness repo; `voice/` exists only after S0. Brown points at harness files through a new config (`configs/underdoc-gemini-flash.yaml`). The course configs stay unchanged.
- Model: everything runs on the existing Gemini key, free tier. The generator and the judge both use `gemini-3.7-flash`, exactly as in the course (judge at temperature 0, thinking high). There is no new provider. The judge can be swapped later (GPT 6 Luna or DeepSeek) if self-preference bias shows up in T6.
- Fallback: OpenCode Go (key in `.env` as `OPENCODE_API_KEY`), wired in T3b. It is used only if Gemini blocks a run (quota exhausted for the day, repeated 429/5xx after retries, or the model is unavailable). Comparability rule: the baseline and the new voice always use the same generator and judge. If the fallback triggers, the whole experiment (baseline, noise and every new-voice iteration) reruns on the fallback models; Gemini and fallback scores are never mixed in one comparison. The switch is recorded in the verdict. Requests identify themselves with their own user agent (`underdoc-evals/0.1`), never as OpenCode, because Go's terms target coding-agent traffic.
- Scoped run so S1 fits the free-tier quota: 10 test posts (balanced by bucket) instead of 22, noise on 3 posts × 3 runs instead of 5 × 5. All 26 samples still go into the dataset; the other 12 stay as an extended set for later. The course judge makes one call per article per metric, so judging is cheap; most of the volume is Brown generation.

## Tasks

Each task closes with one work-unit commit (conventional commits, no AI attribution) in the repo it touches. Evidence = the exact command run and its observed result.

- [x] **T1. Branches and green base.** Create `feat/s1-unified-voice` in both repos. Run the Brown test suite and the harness `tests/test_check.py`, and record which tests already fail on the base. Leave the pre-existing unrelated change in `research_agent_part_2/.../tools.py` out of every commit.
  Evidence (2026-10-04, base `bffead9`):
  - `git switch -c feat/s1-unified-voice` in the course repo and in the harness: both branches created.
  - `OPIK_TRACK_DISABLE=true uv run pytest -q` in `lessons/writing_workflow`: 195 passed, 35 failed. All 35 failures in `tests/brown/nodes/` (`test_article_reviewer`, `test_article_writer`, `test_base`, `test_media_generator`) raise `ValueError: Required environment variable GOOGLE_API_KEY is not set`; there is no `.env` in `lessons/writing_workflow` (only `.env.example`).
  - `uv run --with pytest pytest -q tests` in the harness: 28 passed.
  Known environmental failures: the 35 `tests/brown/nodes/` tests above, until `GOOGLE_API_KEY` is set. Any other failure is a regression.
  Update (17:17, after Ricardo created `.env`): the base gives 211 passed and 27 failed, all in `tests/brown/nodes/`. 24 fail with `ValueError: "ChatGoogleGenerativeAI" object has no field "responses"` (the test helper sets mocked responses on a real model once a key is present) and 3 fail on model-equality assertions. The T3 writer checked these against a stashed base, so they are not caused by S1. These 27 are the new known baseline failures.

## Blockers

- **B1 resolved.** A live Gemini call (`gemini-3.7-flash`) returns "ok"; both OpenCode Go smoke calls pass; `OPIK_API_KEY` is set in settings. `OPIK_WORKSPACE` is unset, so the default workspace for the key applies, which T7 confirms. Original note: `lessons/writing_workflow/.env` was missing. It needs `GOOGLE_API_KEY` and the Opik keys (see `.env.example`), plus `OPENCODE_API_KEY` (a rotated key) for the fallback. T1 to T6 can proceed without it (offline work and fake-model tests). T3 sample generation, the T3b smoke calls, T7 and T8 cannot.

- [x] **T2. `explainers` bucket rules.** Add `skill/references/explainer-post-structure.md` to the harness and register the bucket in `SKILL.md`. The taxonomy becomes builds / explainers / bridge / field-notes. Ground the rules in the ~6 explainer posts of the corpus, citing the posts that support each rule.
  Evidence: file diff; each rule linked to at least one corpus post.
  Done (harness commit `0f5291a`): `skill/references/explainer-post-structure.md` with 10 rules, each citing corpus posts; the bucket registered in `SKILL.md` (table, frontmatter enum, structure pointer); `explainers` added to `VALID_BUCKETS` in `checks/check.py` with `test_explainers_bucket_passes`, which was seen failing before the change. `uv run --with pytest pytest -q tests` gives 29 passed. Explainers: 2025-06-27 and 2025-07-06 (football data scouting I and II), 2025-08-31 (uv), 2025-09-29 (MCP), 2026-03-09 (football framework). 2025-06-08 (data-driven strategies) is an event recap, so it is relabeled field-notes. Open item: G-01 keeps the default 900 to 1400 word band, so the 702-word explainer gets a WARN; a per-bucket band is a later ratchet item.

- [x] **T3. Brown reads the Underdoc voice.** Done: harness commit `6c2ebc3` (`author-profile.md`), course commit `407cbb2`. It adds `scripts/sync_underdoc_profiles.py`, which generates `inputs/profiles/underdoc/` with GENERATED headers; `inputs/examples/underdoc/` holds the RESERVED posts 2026-07-12 (personal finance) and 2025-08-31 (uv), which must not go in test or validation; `configs/underdoc-gemini-flash.yaml` changes only the profiles, character and examples URIs. `tests/brown/test_underdoc_config.py` has 8 tests (seen failing first). Full suite: 211 passed, 27 failed, the same 27 as the stashed base. Brown source untouched. Gaps: the terminology profile is thin (the harness has no glossary), and the slop-blacklist style quotas conflict with the voice files (voice wins). The sample generation moves to T7's first smoke run.
  Original scope: Add `configs/underdoc-gemini-flash.yaml`. Map the Brown profile slots to harness sources: mechanics, structure and tonality to `voice-*.md`; article and terminology to the matching harness rules; character to a new Ricardo profile written from `analysis.json` and the corpus, with first person singular and no invented biography. Extend the loader only if it cannot point at external files. Add a test that loads this config and checks that no course "we/team" mandate leaks in.
  Evidence: test passes; one generated sample article in `outputs/` for a single post.

- [x] **T3b. Fallback provider (OpenCode Go).** Done: commit `facdea9`. `opencode_go:` branch in `get_model.py` (`ChatOpenAI`, base URL `https://opencode.ai/zen/go/v1`, `underdoc-evals/0.1` user agent, Responses API only for `gpt-6-luna`, temperature dropped for it); optional `OPENCODE_API_KEY` setting; `configs/course-fallback.yaml` and `configs/underdoc-fallback.yaml`; `--judge-model` option in `scripts/brown_run_eval.py`. `tests/brown/models/test_opencode_go.py`: 9 passed, 2 smoke tests skipped (no `OPENCODE_API_KEY` in settings). Full suite: 220 passed, 2 skipped, the known 27 failures. Live-verified in commit `bb7b94d`: Go rejected requests without `x-opencode-session` (400 `MissingSessionID`), so a stable per-process session header was added; `gpt-6-luna` also rejected `n` on `Responses.parse()`, so it is dropped. `tests/brown/models/test_opencode_go.py`: 11 passed, including both live smoke calls with structured output. Full suite: 222 passed, the known 27 failures.
  Original scope: Add `langchain-openai` and new `SupportedModels` values for `gpt-6-luna` (judge, `https://opencode.ai/zen/go/v1`, Responses API) and `deepseek-v4-flash` (generator, chat completions), reading `OPENCODE_API_KEY` from the environment and sending the `underdoc-evals/0.1` user agent. Add `configs/underdoc-fallback.yaml` and `configs/course-fallback.yaml` (the same profiles as their Gemini twins, only the model ids change). This is an extension of the enum and configs; Gemini stays the default. Add a test that builds both models without network, plus one live smoke call per model, skipped when the key is missing.
  Evidence: tests pass; smoke call output, or "skipped: no key".

- [x] **T4. Underdoc dataset.** Done: commit `a7eddbe`. 26 samples; buckets: builds 12, explainers 6 (2025-08-12 agentic IDEs added as an explainer), bridge 5, field-notes 3. Splits: few-shot (2026-01-12 RAG data engineering, builds; 2025-12-31 thank-you, bridge); validation (2025-12-26 RAG system, builds; 2025-08-12 agentic IDEs, explainers); test 10 (4 builds, 2 explainers, 2 bridge, 2 field-notes); extended 12, including both RESERVED posts. Noise subset: 2026-03-03 wordalisation (builds), 2026-03-09 football framework (explainers), 2026-02-21 embrace your weirdness (bridge). `uv run python scripts/check_underdoc_leakage.py`: 26 samples, 0 failures (guidelines of 95 to 172 words). 9 research dossiers for builds and explainers outside extended; the rest are placeholders, so research_anchoring is not scored for them. The loader ignores extra metadata keys. Tests: 7 new; full suite 229 passed, the known 27 failures. Caveat: the dossiers are reconstructed from the posts (an upper bound, the same for both arms).
  Original scope: Create `inputs/evals/underdoc_dataset/` with the same layout as `inputs/evals/dataset/` (one folder per post: `article_guideline.md`, `article_ground_truth.md`, and `research.md` only for builds and explainers). Set `metadata.json` with bucket and split per post: 2 few-shot, 2 validation, 10 test, 12 extended. The 3-post noise subset is taken from the test split and covers at least 3 buckets. Guidelines are short briefs (angle, audience, 3 to 6 section intents, sources), at most ~300 words, with no phrasing copied from the published post. Add a leakage check script with a test: word count, plus n-gram overlap against ground truth.
  Evidence: 26 samples, leakage check output with 0 failures, bucket counts.

- [ ] **T5. VoiceAdherence metric.** `src/brown/evals/metrics/voice_adherence/`. Binary criteria per H2 section, derived from harness rules and `check.py` gates. Pydantic outputs; all criteria of one section are batched into one judge call. Use the 2 few-shot posts as examples. Unit tests mirror the existing metric tests.
  Evidence: tests pass; one judged sample printed.

- [ ] **T6. Validation labels (human, Ricardo).** Generate a labeling sheet for the 2 validation posts (per section, per criterion, 0/1). Ricardo fills it in. Measure judge vs. Ricardo agreement per metric. This task does not block T7; T9 does need it.
  Evidence: filled sheet plus agreement % per metric.

- [ ] **T7. Baseline + noise.** Add an Underdoc eval script, or extend `brown_run_eval.py` through config only, so it runs all three metrics in Opik. Run the baseline on the 10 test posts once, then the 3-post noise subset 3 times, recording the standard deviation per metric. Cache outputs so a quota hit resumes instead of restarting.
  Evidence: Opik experiment names/links; table of baseline mean and std per metric.

- [ ] **T8. New voice runs.** Run the same protocol with `underdoc-gemini-flash.yaml`. Stop rule: if the new voice does not beat the baseline by more than the noise after 2 iterations, change the mechanism (for example, from rules to corpus examples in context) and rerun. Hard cap: 4 iterations in total.
  Evidence: Opik experiments per iteration; delta vs. noise table.

- [ ] **T9. Verdict.** Write `odd/reports/s1-a2-verdict.md` with: the metric table (baseline, new, delta, noise), judge alignment from T6, the A2 verdict (holds / fails / inconclusive), and the next action routed by the plan's feedback ratchet. Update the Engram copy and `course/capstone-plan` status.
  Evidence: report file; Engram updated.

- [ ] **T10. Real post (human, after the goal).** Draft the next Notion idea with the new Brown voice; Ricardo edits and publishes it by hand. Record section survival and editing time as the first online baseline point.

## Done when

T1 to T9 (including T3b) are checked with evidence, and `odd/reports/s1-a2-verdict.md` states a verdict backed by Opik experiments. If T6 labels are still missing when T9 is reached, the verdict is written as "provisional: judge not aligned", and that blocker is the next step.

## Next step

T2. Ricardo: create `lessons/writing_workflow/.env` (B1) before T7.
