# S1.1: Pre-S0 hardening

Status: **approved 2026-10-17; executing.** Design: `capstone/s1-1-hardening-design` (#45, Engram). Evidence: `capstone/s1-1-pre-s0-findings` (#44).
Plan: `~/Documents/TheUnderdoc/capstone-plan.md` (rev 2, sections 4, 5, 7, 8). Engram: `course/capstone-plan` (#35).
Branch: `feat/s1-unified-voice` (course repo) and `~/Documents/TheUnderdoc/harness`.
Predecessor: `odd/tasks/s1-unified-voice.md` (S1 closed T1 to T9; T10 open there).

## Goal

Fix the measurement first, then measure, then improve. One S1.1 run that can move the two dead criteria from S1 (`no_slop_structures` 0.67 with two-beat slop left, `no_invented_biography` about 0.5 with a judge bug), and a verdict that discriminates, before the S0 monorepo.

## Scope

In:
- W0 measurement fixes: cache keys, biography judge evidence, FollowsGT admission rule.
- W1 slop gate: harness patterns in two tiers plus one config-gated gate inside Brown's review loop.
- W2 experience notes in the guideline brief and a harness rule for first person.
- W3 terminology reference file regenerated into the terminology profile.
- W4 runtime pinning and resolved-config logging.
- One S1.1 run on OpenCode Go plus a written verdict.

Out (deferred to S0 or later): monorepo (S0), hermetic `tests/brown/nodes` (S0 CI entry), Python 3.14 spike (S0), hybrid profiles (dropped, see Corrections), Gemini transfer check (only if production goes to Gemini), Nova build-reading tool (S2), deployment (S4).

## Cuts applied to the design (#45) on 2026-10-17

- **No `DraftGate` port.** It would have a single adapter, so it buys nothing now. Brown gets one config-gated code path that runs the harness `check.py` on each draft. At S0 the import switches to the `voice/` package; that is the whole migration.
- **No `gates.json`.** The hits are fed to the reviewer and logged; a report file has no consumer yet.
- Everything else stands: FAIL/WARN tiers, hits injected as `Review(profile="mechanics", location=<H2>)`, early stop only when both the LLM reviews and the gate hits are empty.

## Corrections carried from S1

- There is no hybrid-profiles variant. Ricardo wants only his own voice; Paul's six-profile format is a template already filled from Ricardo's corpus. The row was removed from `odd/reports/s1-a2-verdict.md` (commit `bbbb5b6`).
- T6 labels and prefill snapshot committed (commit `7dee0cf`).
- Plan rev 2, section 7 needs the amendments below (W0c, W4) plus the two already recorded in the verdict's "Plan corrections" (Gemini free tier is 20 req/day; the judge makes one call per article per metric).

## Tasks

Each task closes with one work-unit commit (conventional commits, no AI attribution) in the repo it touches. Evidence = the exact command run and its observed result.

- [x] **H0. Branch hygiene.** Commit Ricardo's T6 labels and inputs, and remove the hybrid-profiles row from the verdict report.
  Evidence (2026-10-17): `7dee0cf` (`odd/labels/t6/` plus `odd/labels/t6-validation-sheet.md`), `bbbb5b6` (`odd/reports/s1-a2-verdict.md`). The unrelated modification in `lessons/research_agent_part_2/mcp_server/src/routers/tools.py` stays out of every commit.

- [x] **W0. Measurement fixes.** Three parts.
  (a) Cache keys. In `scripts/underdoc_run_eval.py` the generation key is `_config_fingerprint(config)` plus sample and repeat (line 190), so a profile, example, workflow or node-code change does not change it; the judge key (line 203) is judge model plus metric plus metric version plus article sha, so a voice-rules change does not change it. Extend the generation fingerprint with hashes of the profile files, the examples, the workflow and node code, and the sample's `article_guideline.md` plus `research.md`; extend the judge key with a hash of the voice-rules content. Test: changing a profile changes the generation key; changing the voice rules changes the judge key.
  (b) Biography judge. `src/brown/evals/metrics/voice_adherence/prompts.py:23` loads only tonality, mechanics and terminology, so `no_invented_biography` cannot tell a true author fact from an invention. Add `character_profiles/ricardo_heredia.md` as evidence.
  (c) FollowsGT admission rule. Report FollowsGT but exclude it from the A2 decision rule: a metric that cannot move cannot decide (flow and structure noise 0.000 in both arms; content noise 0.236). Structure is owned by the HITL 1 outline, `guideline_adherence` and online section survival. The course metric stays untouched; the change goes in as an amendment to plan section 7, with a note that it is not because of the result.
  Evidence (2026-10-17): `s1.generator_code_version` now hashes `models/get_model.py` plus every `.py` under `workflows/` and `nodes/`; `s1.corpus_version(profiles_uri, examples_uri)` and `s1.input_version(guideline, research)` join the generation key, and `s1.voice_rules_version(profiles_dir)` joins the judge key for `voice_adherence`. `prompts.VOICE_PROFILE_FILES` now includes `character_profiles/ricardo_heredia.md`. Tests: 5 in `tests/brown/evals/test_s1.py` plus the character-profile assertion in `tests/brown/evals/metrics/voice_adherence/test_voice_adherence_metric.py`; all 7 were seen failing with the old code (stashed source, 7 failed / 32 passed) and pass after (39 passed). Full suite: 278 passed, 27 failed, the same 27 known baseline failures in `tests/brown/nodes/`. Plan section 7 amendment written: "Amendment: metric admission rule (2026-10-17, S1.1)".

- [ ] **W1. Slop gate.** Two parts.
  (a) Harness. New patterns in two tiers in `checks/blacklist-patterns.txt` plus `checks/check.py`: FAIL (0 hits over the 26-post corpus): `not X. It is Y` and `what separates` in any form; WARN: the `, not Y` tail. A calibration test requires FAIL = 0 hits on the corpus. Amend `skill/references/voice-mechanics.md:43`: part of the two-beat family is machine-checkable (the file currently claims it is not, and never will be). Corpus rates for the record: `, not Y` tail 0.12 per post in Ricardo's corpus, 1.57 in the S1 new arm, 3.75 in baseline; `what separates` 0 in corpus, 0.29 in the new arm.
  (b) Brown, config-gated and off by default: run the harness `check.py` patterns on each draft, append every hit to the reviewer's input as `Review(profile="mechanics", location=<H2>, comment=<hit>)` in `src/brown/nodes/article_reviewer.py`, and make the review loop's early stop require both the LLM reviews and the gate hits to be empty. One builder used by both `src/brown/workflows/generate_article.py` and `edit_article.py`. Hits are logged; no port, no `gates.json`.
  Evidence: calibration test output; one Brown run where gate hits appear as reviews and in the log; final-draft hits near the corpus rate.

- [ ] **W2. Experience notes (inputs only).** Add an `## Experience notes` section to the guideline template; Ricardo fills it at HITL 1. Harness rule: first person comes only from the author profile, the notes, or the research; otherwise write `[EXPERIENCE: what would go here]`, the same pattern as `[SCREENSHOT: ...]`. The dataset does not change (leakage).
  Evidence: template diff, harness rule diff, one generated section using the marker.

- [ ] **W3. Terminology.** New `skill/references/voice-terminology.md` in the format of the other reference files (word choice, descriptive language, emphasis, naming), filled from the 26-post corpus: a deterministic frequency pass, then rules drafted citing the posts that support each rule, approved by Ricardo, then `scripts/sync_underdoc_profiles.py` regenerates `inputs/profiles/underdoc/terminology_profile.md`. Descriptive, never quotas.
  Evidence: the frequency pass output, the rules with citations, Ricardo's approval, the regenerated profile.

- [ ] **W4. Runtime.** Pin `CONFIG_FILE` for the Brown MCP server in `.mcp.json` (repo root), because `config.py` defaults to `configs/course-gemini-flash.yaml` (Paul's voice, Gemini) when the environment does not override it, and log the resolved config plus the loaded model ids at startup. Evals and T10 run on OpenCode Go; the production provider is an ADR in S4.
  Evidence: `.mcp.json` diff; a startup log line naming the Underdoc config and the Go models.

- [ ] **S1.1 run and verdict (one run, OpenCode Go).** Re-judge the S1 baseline without regenerating it, then run the new arm with W1 + W2 + W3 on the same 7 paired test posts plus noise 3 posts x 2 repeats (about half the cost of S1 run 2). Passes if `no_slop_structures` beats 0.67 by more than noise, regex hits end close to the corpus rate, `no_invented_biography` (fixed judge) improves by more than noise, and VoiceAdherence and UserIntent do not regress beyond noise. Verdict in `odd/reports/s1-1-verdict.md` plus Engram.
  Evidence: Opik experiment names; the delta-versus-noise table; the verdict.

- [ ] **T10. Real post (open from S1, human).** Draft the next Notion idea with the new Brown voice on OpenCode Go; Ricardo edits and publishes by hand. Record section survival and editing time as the first online baseline point.

## Order

1. H0 hygiene (done).
2. W0 to W3.
3. W4.
4. S1.1 run and verdict.
5. T10 real post.
6. PRs in both repos, plan rev 3, then S0.

## Done when

W0 to W4 are checked with evidence, the S1.1 run is done and `odd/reports/s1-1-verdict.md` states a verdict backed by named Opik experiments, and T10 is published by hand.

## Next step

W0 done (2026-10-17). Next: W1, the slop gate in the harness (two tiers plus the calibration test).
