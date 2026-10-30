# Self-Check Before Reporting

Read this before reporting back, every run. These are the failure modes of a
model writing test cases, and each has occurred in this system's own history.

## What the scripts already settled

Do not re-judge these by eye. `scripts/testmodel.py coverage` computes them.

- whether any mandatory item lacks a case (`gaps`)
- whether a case references an id no checklist item defines (`danglingIds`)
- whether two cases verify the same thing (`duplicates`)

If the numbers are not what you expected, the model or the cases are wrong — not
the script.

## Hallucination checks

**Every business rule must quote the spec.** `scripts/verify.py` compares each
`source` against the spec's text. Anything it flags either cites an external
document the run never read, or was invented. Report these individually; do not
average them away in a summary.

One real instance: a line the spec marked `[제안 — §4.1]` was recorded as a
settled business rule. A proposal is not a requirement.

**A fact that appears in no cited source does not go in a case.** If the case
needs it, the fact is an open question.

## Judgeability of expected results

For each case, ask: **could two executors disagree about whether this passed?**
If yes, the expected result is not finished.

These fail the test:

- `정상적으로 동작한다`, `적절히 표시된다`, `올바르게 처리된다`
- `A 또는 B가 표시된다` — permitting either means there is no criterion
- `확인할 수 있다` with nothing named before it

These pass:

- an HTTP status code or a response field value
- named on-screen text, a badge value, a column value
- the name of a stored state
- what must **not** happen: `계정이 생성되지 않는다`

Where the spec never defined the behaviour, assert only the settled part and
move the rest to `openQuestions`. Inventing a message to make a case look
complete produces a case that fails for the wrong reason.

## One purpose per case

If a failure would leave the executor unsure which of two things broke, split it.
Two symptoms of this:

- an expected result with an unrelated extra clause bolted on
- steps that set two inputs to invalid values at once

## Technique labels

The `technique` field is a claim, and a wrong claim misleads the next reader.

- boundary value analysis requires an **ordered** range. Not for enums, not for
  sort order.
- a decision table requires **two or more** conditions combining.
- state transition testing requires the **order of events** to matter.

## Priority distribution

If nearly every case is P1, prioritization did not happen. P0 should be small —
the few ways this feature causes real damage. An executor with two days needs the
ordering to mean something.

## What to say about what was skipped

Name it. Combinations dropped as low-risk, a device matrix not enumerated, a
decision table covered partially — each with the reason. **A skip you can explain
is a decision; a skip you cannot explain is indistinguishable from an oversight.**

## The report itself

Korean, and in this order.

1. Open questions with `blocksTesting` true — sendable to the spec author now
2. Coverage numbers and any remaining gap
3. What verification flagged, listed individually
4. What was deliberately skipped, with reasons
5. Deliverable paths

Do not open with the case count. The number of cases is the least informative
thing about the run.
