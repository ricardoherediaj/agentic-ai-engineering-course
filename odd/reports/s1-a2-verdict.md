# S1 verdict: does the unified voice make Brown better? (A2)

Date: 2026-10-04 · Slice: S1 (`odd/tasks/s1-unified-voice.md`) · Branch: `feat/s1-unified-voice`

## Verdict

**A2 holds on VoiceAdherence and UserIntent and is inconclusive on FollowsGT.** Under the plan's strict definition, which requires all three metrics to beat noise, A2 is **not fully proven**. The FollowsGT miss is a floor effect of the metric, not evidence against the voice (see "FollowsGT").

The new voice clearly reduces AI-slop structures (0.34 to 0.67 of sections clean), but one third of sections still contain two-beat slop ("it's X, not Y"). Both arms invent biographical claims in about half of their sections. These two problems are the next actions.

## Setup

| Item | Value |
| --- | --- |
| Baseline arm | Unchanged Brown: course profiles plus `paul_iusztin.md` (`configs/course-fallback.yaml`) |
| New arm | Brown with the harness voice (`configs/underdoc-fallback.yaml`) |
| Generator (both arms) | `opencode_go:deepseek-v4.1-flash`. Gemini free tier is capped at 20 requests per day, so the fallback rule applied, with Ricardo's approval. |
| Judge (all metrics) | `opencode_go:gpt-6-luna` |
| Test set | 7 paired test posts: 2 builds, 2 explainers, 2 bridge, 1 field-notes |
| Noise | 3 posts × 2 repeats per arm; std per metric averaged over posts and arms |
| Decision rule | The new voice improves a metric only if delta > noise std |

**Scope cut:** Ricardo stopped the runs at 21:53 to save OpenCode Go budget. At that point the runs had reached 8/10 (baseline) and 7/10 (new) test posts, and 2/3 noise repeats. The cut was decided before any result was inspected. The analysis uses the 7 posts that both arms completed, and the 2 complete noise repeats per arm.

## Results (paired subset)

| Metric | Baseline | New | Delta | Noise std | Verdict |
| --- | --- | --- | --- | --- | --- |
| FollowsGT | 0.083 | 0.125 | +0.042 | 0.079 | within noise |
| UserIntent | 0.387 | 0.604 | +0.217 | 0.062 | **beats noise** |
| VoiceAdherence | 0.531 | 0.740 | +0.209 | 0.061 | **beats noise** |

Per criterion:

| Criterion | Baseline | New | Delta | Noise std |
| --- | --- | --- | --- | --- |
| follows_gt.content | 0.250 | 0.339 | +0.089 | 0.236 |
| follows_gt.flow | 0.000 | 0.000 | +0.000 | 0.000 |
| follows_gt.structure | 0.000 | 0.036 | +0.036 | 0.000 |
| user_intent.guideline_adherence | 0.525 | 0.875 | +0.350 | 0.094 |
| user_intent.research_anchoring | 0.250 | 0.333 | +0.083 | 0.088 |
| voice.first_person_voice | 0.290 | 0.871 | +0.581 | 0.103 |
| voice.concrete_specifics | 0.588 | 0.906 | +0.318 | 0.074 |
| voice.no_slop_structures | 0.344 | 0.671 | +0.327 | 0.133 |
| voice.spoken_rhythm_and_punctuation | 0.465 | 0.544 | +0.079 | 0.222 |
| voice.no_slop_vocabulary | 0.984 | 0.976 | -0.008 | 0.062 |
| voice.no_invented_biography | 0.514 | 0.474 | -0.040 | 0.130 |

Opik (project `underdoc-s1`, dataset `underdoc_dataset`): `s1v2-baseline-r1`, `s1v2-new-r1` (7 paired posts each), and `s1v2-noise-baseline-r1/r2`, `s1v2-noise-new-r1/r2`. Raw scores are in `lessons/writing_workflow/outputs/s1/s1v2-*` (gitignored) and the summary is in `outputs/s1/s1v2-summary.json`.

## Judge alignment (T6)

Ricardo reviewed validation post 1 (`2025-08-12-using-agentic-ides-for-football-analytics`), 63 matched items:

| Metric | Agreement, judge v1 | Agreement, after the bounded correction |
| --- | --- | --- |
| FollowsGT | 0/3 | 0/3 |
| UserIntent | 75.0% | 75.0% |
| VoiceAdherence | 79.2% | 83.3% |
| Overall | 74.6% | 77.8% |

All of Ricardo's 27 flips went from 0 to 1, so he is more lenient than Claude on structure and research anchoring. On `no_invented_biography` the corrected judge is stricter than Ricardo on 2 sections and still lenient on 1 (5/8). The sample is one post, so alignment is indicative only.

## Caveats

- **Generator transfer.** A2 was tested with DeepSeek, not Gemini (production Brown). Confirming that the result holds on Gemini needs a paid or reset quota.
- **Small sample.** 7 paired posts and 2 noise repeats on 3 posts. The two winning deltas are about 3.5× the noise std, which is robust to that; FollowsGT is not.
- **Partial circularity.** VoiceAdherence criteria come from the same harness rules that the new arm is prompted with, so part of that gain is "following the rules it was given". UserIntent (+0.217) does not depend on the voice rules and still beats noise. Ricardo's own read also counts: both arms "did a good job", with residual two-beat slop.
- **FollowsGT floor.** Flow and structure are 0.000 in both arms with zero noise. By design (leakage control), guidelines are briefs of 95 to 172 words, so no generator can reproduce the published post's flow and structure from them. On explainers, the judge collapses a ground truth without H2s into one section. The metric does not discriminate in this setup, and Ricardo disagrees with it on structure.
- **Research dossiers** are reconstructed from the published posts, which makes `research_anchoring` an upper bound. The same applies to both arms.
- **Run 1 was invalid** (DeepSeek rejected json_schema structured output, so no diagrams were generated and two runs crashed). It was excluded entirely; the fixes are in `e39c491` and `49bd101`.

## Next actions (feedback ratchet)

| Signal | Owner layer | Action | Verification | Retirement |
| --- | --- | --- | --- | --- |
| `no_slop_structures` 0.67: one third of sections keep two-beat slop, as Ricardo also observed | Runtime control in Brown's loop | Deterministic gate: run the `check.py` blacklist patterns on every draft and feed each hit to Brown's reviewer as a mandatory review (plan section 4, flow step 4) | `no_slop_structures` beats its current value by more than noise; 0 regex hits in the final drafts | When 0 hits hold across 3 real posts |
| `no_invented_biography` around 0.5 in both arms | Inputs (guideline) and Nova sourcing | Add a "real experience notes" field to the guideline brief, and make Brown's reviewer flag unsupported first-person claims | The criterion beats noise; Ricardo finds no invented facts in the next real post | When 3 real posts ship with no invented claim |
| FollowsGT at the floor | Metric review | Decide whether flow and structure stay. Options: score only `content`, or give the judge the approved outline instead of the ground truth | The metric discriminates (noise std > 0, deltas measurable) | When it is replaced |
| Hybrid profiles (Ricardo's idea) | Inputs (profiles) | Variant: Paul's structure, article and terminology profiles plus Ricardo's mechanics, tonality and character, with no team "we" | Measured against the same baseline | If it does not beat the harness-only voice |
| Generator transfer | Runtime | Rerun the paired subset on Gemini when quota allows | Same directional result | Once confirmed |
| Real post (T10) | Ricardo | Draft the next Notion idea with the new voice, then edit and publish by hand; record section survival and editing time | First online baseline point | Not applicable |

## Plan corrections

- Plan rev 2, section 7: the Gemini free tier is **20 requests per day** for `gemini-3.7-flash`, not about 1,500. It cannot carry the evals. The working setup is OpenCode Go (DeepSeek V4.1 Flash plus GPT 6 Luna), and S1 cost a fraction of its monthly cap, including the invalid run 1.
- Plan rev 2, section 7, judge cost: the course judge makes one call per article per metric, not one per section, so the per-section count in the plan overestimates by about 6×.
