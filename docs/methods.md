# Study design and interpretation

## Decision being audited

The classification task was whether feedback related to any of seven rubric areas. Topic relevance and answer specificity are distinct: a brief, general response can still be relevant. The audit did not evaluate individual teachers or infer teacher effectiveness.

Of 12,628 source records, 97 were handled in an earlier audit. The main study reconstructed baseline labels for the remaining 12,531 records using the existing classification method. These are newly generated baseline labels, not recovered historical labels or trusted reference annotations. Identical inputs sometimes shared model requests; rows are not all independent experimental units.

Claude was pinned to `claude-haiku-4-5-20251001`; the Jev response resolved to `jev-1.14.0`. The initial audit was blind to the Claude label. The original Claude path used cleaned, masked text truncated to 800 characters; Jev received full masked text. This asymmetry affected 308 rows, so the initial comparison is not a pure model-only comparison.

## Sequential experiments

### Audit triage

The Jev audit policy marked 10,105 labels supported, 2,224 held and 202 contradicted. Of the contradictions, 201 suggested off-topic→on-topic and one suggested the reverse. Agreement and confidence identify where to investigate; neither establishes correctness. Holds are policy outcomes, not necessarily missing API responses.

### Prompt intervention

On the 201 selected off→on disagreements, a fresh original-prompt control classified 21 responses on-topic; a revised prompt separating relevance from specificity classified 49 on-topic. Paired counts were 144 off/off, 36 off/on, 8 on/off and 13 on/on. Net inclusion increased by 28, but no trusted labels establish which changes were correct. The fresh control avoids attributing every historical difference to the intervention.

### Input grouping

The 152 cases still excluded under the revised prompt were tested in batch and singleton calls, twice per condition. Model, prompt and target text were held fixed. There were 150 complete cases and two unavailable after bounded format retries. A state of Off or On means both repetitions agree; Mixed means they differ.

Rows are batch states; columns are singleton states:

| | Off | Mixed | On |
|---|---:|---:|---:|
| Off | 44 | 7 | 79 |
| Mixed | 1 | 0 | 16 |
| On | 1 | 0 | 2 |

Batch on-topic counts were 11 and 12; singleton counts were 98 and 103, each out of 150. This is selected-cohort sensitivity, not a population estimate. Repetition connectors in the plot are visual aids; two repetitions do not justify inferential error bars.

### Output-design comparison

160 real responses were evaluated twice under each design. These were adaptively selected, and 40 development responses informed the evidence-based design. The table reports the real-response subset, including retries where specified.

| Design | First-pass full-contract validity | Final valid calls | Stable binary outcomes / 160 | Other paired outcomes | Estimated total cost | Median first-call latency |
|---|---:|---:|---:|---|---:|---:|
| A: singleton binary | 308/320 | 319/320 | 157 | 2 flips; 1 unavailable | $0.167463 | 0.521 s |
| B: schema-constrained binary | 320/320 | 320/320 | 150 | 10 flips | $0.226605 | 0.616 s |
| C: rubric areas + generated evidence | 273/320 | 291/320 | 116 | 22 stable holds; 3 flips; 19 unavailable | $1.287601 | 1.809 s |

All 320 first-pass C outputs satisfied the JSON schema, but only 273 passed the full contract. Generated quotes sometimes came from rubric instructions rather than response text: 18 such quote spans were observed across real and synthetic tests. Structural validity does not establish evidence validity. B also changed the output envelope and instruction placement, so this is a package comparison rather than an isolated test of schema constraints.

A is a promising candidate for shadow validation based on this observed cost/stability trade-off, not demonstrated accuracy superiority. A later post-hoc parser recovered all 320 A first-pass real outputs; that retrospective adaptation had 157 stable pairs and 3 flips. It is not an independently validated saving.

A small follow-up replaced generated quotes with enumerated source-span IDs: 19/20 full-contract-valid calls versus 12/20 for C on five real and five synthetic inputs, each repeated twice. All 20 source pointers were valid. Valid pointers still do not prove semantic support; this pilot is too small to establish general performance.

### Preprocessing intervention

The school dictionary used by the evaluation harness contained an aggregate value, `ALL`. Case-insensitive masking replaced the ordinary word “all.” The repair excludes only that exact aggregate dictionary value while retaining genuine multiword names containing “All.” This is an evaluation-preprocessing defect, not a proven historical production defect.

Among 1,171 affected rows, 1,148 had a change inside their own 800-character model input; 23 changed only beyond the cutoff. Original prompt, model, batch IDs, order and grouping were preserved. A fresh original-input arm and a repaired arm produced 18 off→on and 4 on→off changes; 1,149 labels were unchanged. The historical baseline differed from the fresh control on 10 rows, illustrating why a fresh control matters.

Conditional follow-up calls reproduced 15 of the 18 off→on changes and all 4 reverse changes. The remaining 3 were unstable. Repeats were selected after observing a change. Repairs may also change neighboring batch context and how much trailing text fits inside the character limit. These are part of the intervention, not separately isolated effects.

## Limits and next validation

There is no independent ground truth, accuracy estimate, F1 estimate or verified number of corrected errors. Do not sum changes across overlapping cohorts. Stability can reflect a consistently wrong rule. The corpus was used adaptively; a fresh prospective reference set is preferable to relabeling an explored subset as a held-out test.

Freeze preprocessing, prompt, model, parser and audit thresholds before the next comparison. Group duplicates and responses from the same respondent when splitting. Compare the proposed pipeline with the baseline in shadow mode on a trusted reference set. Track:

- Relevant responses among automatically excluded responses: risk faced by someone relying on an exclusion.
- Automatically excluded responses among all relevant responses: relevant-response loss.
- Irrelevant responses among retained responses: retained noise.
- Coverage, hold reasons, final availability, retries, latency and estimated cost.

Automated regression and metamorphic tests can run continuously without new annotation. They test invariants and contract compliance; they cannot alone certify classification correctness.

## Reproducibility boundary

`results/aggregates.json` is a minimal release of aggregate study counts. Its values reproduce the figures; the private corpus, prompts containing original rubric content, per-row outputs and run ledgers are withheld. The public utilities are an extracted, offline companion rather than the original experiment runner. No API evaluation is triggered by a public command.
