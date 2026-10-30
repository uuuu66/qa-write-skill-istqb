# Risk-Based Prioritization

## When it applies

Always, at two moments: when scoring risks into the Test Model, and when
assigning `priority` to each case. Read this whenever the checklist contains
`RISK-` items.

**This is what separates a test suite from a list.** Anyone can enumerate
combinations. Deciding what not to test, and being able to defend it, is the
senior judgement.

## Scoring a risk

A risk is scored on two axes, each LOW / MEDIUM / HIGH.

**Likelihood** — how probable is it that this goes wrong? Raise it for: new
code, unfamiliar technology, time pressure on the team, complex logic, many
hands on the same area, a history of defects here.

**Impact** — what happens if it does? Raise it for: money, legally binding
records, data that cannot be recovered, decisions other people make from this
output, loss of trust with an external party.

The product of the two gives priority.

```
impact\likelihood   LOW     MEDIUM   HIGH
HIGH                P1      P0       P0
MEDIUM              P2      P1       P1
LOW                 P3      P2       P2
```

Only **P0 and P1** become mandatory checklist items. P2 and P3 risks may go
uncovered, and that is the intended behaviour, not an omission.

## Impact is about consequence, not visibility

The most commonly mis-scored risks:

**Under-scored: a wrong value shown confidently.** A screen that says
「ERP 미등록」 when it simply failed to check is worse than a screen that errors
out, because the operator acts on it. Silent wrongness beats loud failure in
impact.

**Under-scored: anything touching money or a permission boundary.** Even if the
path is rare, the impact is high. Rarity belongs in likelihood, not impact.

**Over-scored: cosmetic layout issues.** A misaligned label is LOW impact
however visible it is.

## Assigning priority to cases

Each case inherits the priority of the risk it addresses. Where a case covers
several items, take the highest.

A rough shape for a healthy suite: P0 is small (the handful of ways this feature
can cause real damage), P1 is the largest group (the core behaviour), P2 and P3
taper off. If nearly every case is P1, the prioritization was not actually done,
and the suite gives the executor no order to work in.

## What to deliberately skip

Write these down rather than silently dropping them.

- combinations of two low-risk optional inputs
- every browser in a matrix when the feature has no browser-specific code
- exhaustive enumeration of a decision table's low-risk columns
- duplicate coverage of a partition already exercised by a boundary case

In the report, say what was skipped and why. **A skip you can explain is a
decision; a skip you cannot explain is an omission.**

## Example

```
RISK-01  중복 가입으로 계정이 중복 생성된다
         likelihood HIGH (이메일 유일성 검사가 신규 코드다)
         impact     HIGH (정산 데이터가 두 계정으로 갈린다)
         priority   P0
```

The resulting case carries `priority: P0`, and the checklist marks `RISK-01`
mandatory.

## Common mistakes

**Scoring impact by how noticeable the failure is.** A crash is noticeable and
gets fixed. A quietly wrong number is not, and gets acted upon.

**Making everything P0 or P1.** Priority that does not discriminate is not
priority. If the executor has two days, the ordering has to mean something.

**Skipping without recording.** An unexplained absence looks identical to a
mistake when someone reviews the suite later.
