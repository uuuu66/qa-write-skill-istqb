# Code Coverage Techniques

## When it applies

Source code is available, or someone asked for a coverage level. Unlike the other
techniques here, these derive cases from **the code's structure**, not from the
spec — so they answer "is this code exercised", never "is this behaviour correct".

Use them to find what spec-based testing missed, not as a replacement for it.

## The levels, in increasing strength

**Statement coverage.** Every executable statement runs at least once. 100% here
still misses plenty: a `divide(a, b)` runs fine until `b` is 0, and an `if`
without an `else` reaches full statement coverage while the false branch never
executes.

**Branch coverage.** Every transfer of control is taken, so both outcomes of each
decision are exercised. This is the useful minimum for most code.

**Modified Condition/Decision Coverage (MC/DC).** For a decision made of several
conditions, each condition is shown to **independently** change the outcome. For
`if (a && b)`, branch coverage is satisfied by `a=T,b=T` and `a=F,b=F` — but that
never shows `b` mattering. MC/DC forces the cases that isolate each condition.

Required in safety-critical domains (avionics, medical, automotive). Elsewhere,
apply it to the decisions that gate money, permissions, or irreversible actions.

**Multiple condition coverage.** Every combination of condition values. Grows as
2^n and is rarely worth it beyond three conditions.

## Turning coverage into cases

Coverage levels are measured on the code, but cases still need spec-level
expected results. The procedure:

1. Find the decision or branch that is not exercised.
2. Work out the input that reaches it.
3. **Look up what the spec says should happen for that input.** If the spec says
   nothing, you have found either dead code or an undocumented rule — record an
   open question rather than asserting the code's current behaviour is correct.
4. Write the case with the spec's expected result, not the code's actual output.

Step 3 is the whole discipline. Writing "the expected result is what the code
does" converts a test suite into a change detector that certifies bugs.

## Example

```
if (hospital.erpCode != null && hospital.status == 'ACTIVE') { 거래가능 = true }
```

MC/DC on this decision needs:

```
erpCode 있음, status ACTIVE      → 거래가능
erpCode 없음, status ACTIVE      → 거래불가   (erpCode 가 결과를 바꿈)
erpCode 있음, status INACTIVE    → 거래불가   (status 가 결과를 바꿈)
```

Three cases, and each shows one condition independently deciding the outcome.

## Common mistakes

**Chasing a coverage percentage.** 100% statement coverage with assertions that
check nothing is worse than 60% with real expected results, because the number
creates false confidence.

**Deriving expected results from the implementation.** The test then passes
forever, including over the bug it was supposed to catch.

**Applying MC/DC everywhere.** Cost grows fast. Reserve it for decisions whose
wrong outcome causes real damage.

## When not to use it

**No access to the code.** Then this is not available, and spec-based techniques
plus experience-based testing are the coverage you have.

**As the primary technique.** Code coverage cannot find a missing requirement:
code that was never written has no statements to exercise. Requirements coverage
comes from the checklist, not from here.
