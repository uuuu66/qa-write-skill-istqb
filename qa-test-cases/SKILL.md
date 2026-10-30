---
name: qa-test-cases
description: Turn a product spec (PRD) into test cases grounded in ISTQB test design techniques. Derives the list of things that must be tested in code so coverage gaps are counted rather than guessed, and records what the spec fails to answer instead of inventing an answer. Use for requests like "write test cases", "generate TCs from this spec", "QA scenarios from the PRD", "design tests for this screen", or the Korean equivalents ("테스트 케이스 만들어줘", "TC 뽑아줘", "기획서로 QA 시나리오").
---

# Test cases from a product spec

Work as a QA engineer with fifteen years behind them. That difference is not the
number of techniques known; it is three habits. Never assert without a source.
Never invent an answer to something the spec does not say — ask. Deliberately
skip the low-risk combinations, and be able to say what was skipped and why.

## Output language: Korean, always

Every deliverable is written in **Korean** — case titles, steps, expected
results, open questions, and the report back to the user. This holds regardless
of the language of the spec or of the request. Follow
`references/korean-style.md`.

Identifiers stay as they are: HTTP status codes, field and component names, file
paths, enum values, and text the product actually displays are never translated.

## Running the scripts

Every `scripts/...` path below is **relative to this skill's own directory**, not
to the working directory. That directory is given to you when the skill loads
("Base directory for this skill"). Prefix the commands with it:

```bash
SKILL_DIR="<the base directory printed when this skill loaded>"
python3 "$SKILL_DIR/scripts/testmodel.py" derive test-model.json
```

Write the intermediate and output files into the **working directory** (or a
subdirectory the user names), never into the skill directory.

## Pipeline

```
Spec document
   ↓  1. extract facts        you read
Test Model (JSON)
   ↓  2. derive               a script computes
Test Model with boundaries and partitions filled in
   ↓  3. checklist            a script computes
list of items that must be tested
   ↓  4. write cases          you write (after reading the technique docs)
Test cases
   ↓  5. coverage check       a script computes
gaps, duplicates, dangling references
   ↓  6. verify and export
Deliverables
```

**Who owns which step is the point of this skill.** Every counting and
arithmetic step runs in a script. Asking a model "is anything missing?" returns
a different answer each run. You only read and write.

## 1. Extract facts from the spec

Read the spec file **in full**. Do not summarize it or sample parts of it. If it
runs past roughly 200k characters and will not fit, split by feature and run the
pipeline per feature.

Extract in this order.

1. **Business rules first.** Quote the spec's own wording into `source` for each
   rule. If you cannot find wording to quote, do not record the rule.
2. **Inputs and their constraints**: `min`, `max`, `minLength`, `maxLength`,
   `enumValues`, `format`, `required`.
   **Do not enumerate boundary values.** Values like 13, 14, 15 are computed
   from the constraints by a script. Record the constraints precisely instead.
3. **States and transitions.** Include transitions that must *not* happen, not
   only the valid ones.
4. **Decision tables** where a combination of conditions decides the outcome.
5. **API aspects**, where an API is visible: auth and permissions, concurrency,
   idempotency, timeouts, payload size, rate limits.
6. **Risks**, scored by likelihood and impact into P0 through P3.
7. **Everything the spec does not answer** goes into `openQuestions`. An empty
   list here usually means the analysis was shallow, not that the spec was complete.

Follow `references/test-model.schema.json`. Id prefixes: partitions `EP-`,
boundaries `BV-`, business rules `BR-`, transitions `TR-`, decision tables `DT-`,
risks `RISK-`.

Read `references/techniques/acceptance-criteria.md` before this step: turning
prose requirements into acceptance criteria is what makes the rest extractable.

Save as `test-model.json`.

## 2. Derive

```bash
python3 "$SKILL_DIR/scripts/testmodel.py" derive test-model.json > test-model.derived.json
```

Computes boundary values and equivalence partitions from the constraints, and
merges duplicates where one field was captured under two names. `min=14` yields
13, 14 and 15; a required input always gets a missing-value partition.

## 3. Build the checklist

```bash
python3 "$SKILL_DIR/scripts/testmodel.py" coverage test-model.derived.json > checklist.json
```

Every item that must be tested, each with an id. **This list is the reference
for every later judgement.**

## 4. Write the cases

Read only the technique docs the checklist actually calls for. Paths are
relative to this skill's directory.

| Checklist contains | Read |
| --- | --- |
| `PARTITION` | `techniques/equivalence-partitioning.md` |
| `BOUNDARY` | `techniques/boundary-value.md` |
| `DECISION_RULE` | `techniques/decision-table.md` |
| `TRANSITION` | `techniques/state-transition.md` |
| `API_STATUS` | `techniques/api-technical.md` |
| `RISK` | `techniques/risk-based.md` |

Read these when the situation calls for them, whatever the checklist says.

| Situation | Read |
| --- | --- |
| Three or more inputs whose combinations could interact | `techniques/combinatorial.md` |
| Spec written as user stories or use cases | `techniques/use-case-and-user-story.md` |
| Business process spanning several screens or roles | `techniques/business-process.md` |
| Source code available, or coverage asked for | `techniques/white-box-coverage.md` |
| Authentication, authorization, or untrusted input | `techniques/security.md` |
| Response time, load, or failure-recovery requirements | `techniques/performance-reliability.md` |
| Browsers, devices, OS versions, or migrated data | `techniques/compatibility-and-data.md` |
| Spec is thin and the feature resembles a known one | `techniques/experience-based.md` |
| Always, before reporting | `techniques/self-check.md` |

**Work in slices of about 18 items, and dispatch the slices to subagents in
parallel.** Writing the whole list in one pass runs past the output limit and the
answer comes back truncated — a checklist over 100 items is normal. Fan-out is
also the only real lever on wall-clock time: the run is dominated by how many
output tokens have to be written, and parallel subagents are what divide it.

Each subagent gets exactly this brief, and nothing else:

- the full Test Model (identical for every slice — this is what makes the
  cached prefix pay off)
- **its own slice of the checklist**, and the instruction that it owns only
  those items
- the technique docs that slice calls for, per the routing tables above
- `references/korean-style.md`
- the rule that `coversIds` may only contain ids from its own slice

Tell each subagent to return the cases as JSON and nothing else. Collect the
slices, concatenate them into `{"testCases": [...]}`, and continue. Run six or so
at a time; more than that tends to hit provider rate limits rather than finish
sooner.

Only work through the slices yourself, in order, when subagents are genuinely
unavailable in the surface you are running on.

Every case carries:

- `coversIds` — the checklist ids it discharges. **Never an id absent from the list.**
- `technique` — the technique that produced it
- `rationale` — one sentence on why the case is needed

**An expected result must let the executor decide pass or fail.** Include at
least one of: an HTTP status code or response field value; specific on-screen
text, badge name or column value; the name of a stored state; or what must *not*
happen. "정상적으로 동작한다", "적절히 표시된다", and "A 또는 B가 표시된다" are
not expected results.

Where the spec never defined the behaviour, **do not guess.** State only the part
that is settled and add the rest to `openQuestions`.

Save as `test-cases.json`, shaped `{"testCases": [...]}`.

## 5. Check coverage

```bash
python3 "$SKILL_DIR/scripts/testmodel.py" coverage test-model.derived.json test-cases.json
```

Three fields matter.

- `gaps` — mandatory items no case covers. **Must be 0.**
- `danglingIds` — ids no checklist item defines. Must be 0.
- `duplicates` — cases whose steps and expected result are effectively identical

If `gaps` is not empty, rerun step 4 **for those items only**, in the same
sliced and parallel way. Never rewrite the whole list: regenerating cases that
were already correct costs the same tokens again and risks losing them.

## 6. Verify and export

```bash
python3 "$SKILL_DIR/scripts/verify.py" test-model.derived.json test-cases.json <spec path>
python3 "$SKILL_DIR/scripts/export_csv.py" test-cases.json > test-cases.csv
```

`verify.py` checks each business rule's `source` against the spec's actual text
and flags expected results that cannot be judged. Whatever it flags needs a human,
so include it in the report.

## Reporting back

In Korean. Do not lead with counts. Report in this order.

1. **Open questions** where `blocksTesting` is true. These can go to the spec
   author immediately, which makes them the first useful output of the run.
2. Coverage numbers and whether any gap remains.
3. What verification flagged — especially rules whose source is not in the spec.
4. Paths to the deliverables.

## Do not

- Build a case on a fact the spec does not contain. Record a question instead.
- Enumerate boundary values by hand. The script does it.
- Count coverage by eye. The script does it.
- Enumerate every combination. Drop the low-risk ones and say which, and why.
