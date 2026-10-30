# Boundary Value Analysis

## When it applies

An input in the Test Model carries an **ordered range constraint**.

- a number with `min` or `max`
- a string with `minLength` or `maxLength`
- a date range, a record-count ceiling, an amount limit

`scripts/testmodel.py derive` detects these and computes the boundary values.
If the checklist contains items starting with `BV-`, read this document.

## What the script did, and what you do

Turning a constraint into values is arithmetic, and it is already done.

```
min=14, max=100  →  13(below) 14(on) 15(above)   99(below) 100(on) 101(above)
```

**Do not recompute the values.** Use the ones in the checklist and write one
executable case per item. Inventing a value produces a `coversIds` entry no
checklist item defines, which breaks traceability.

## Why boundaries

The most common implementation mistake is placing a boundary one position off,
or omitting it — writing `x < 10` where `x <= 10` was meant.

This skill uses 3-value BVA: the boundary and **both** neighbours. 2-value BVA
looks only at the boundary and its outside neighbour, which cannot catch
`x <= 10` implemented as `x == 10`; the inside neighbour, 9, is what exposes it.

## Procedure

1. Take one `BV-` item. It carries the value, its position (below / on / above)
   and the expected behaviour.
2. Put **only that one input** at its boundary value. Fill every other input
   with an ordinary valid value.
3. Write an expected result that names what to observe: on acceptance, what gets
   created or which state is reached; on rejection, which error code and which
   message appears.
4. Put the item's id in `coversIds`.

## Example

Checklist item:

```
BV-age:0   age = 13 (below) → 거부 (하한 미만)
```

Test case (written in Korean, as all deliverables are):

```
제목      만 13세는 가입이 거부된다
사전조건  미가입 이메일을 보유한다
단계      1. 가입 폼에 age=13, 나머지 필드는 유효값으로 입력한다
          2. 제출한다
기대 결과 HTTP 400을 반환하고 "만 14세 이상만 가입할 수 있습니다"가 표시되며,
          계정이 생성되지 않는다
기법      Boundary Value Analysis (3-value)
coversIds BV-age:0
```

## Common mistakes

**Several boundaries in one case.** With `age=13` and `length=256` together, a
failure does not say which one caused it. One boundary per case.

**Reading "below" and "above" as pass and fail.** They mark position relative to
the boundary, nothing else. 101, the "above" of an upper bound of 100, must be
rejected; 15, the "above" of a lower bound of 14, must be accepted. Take the
expected behaviour from the checklist.

**An expected result that only says "거부된다".** The executor has nothing to
observe. Name a status code, a message, or the absence of created data.

## When not to use it

**Unordered values have no boundaries.** If `role` is `USER` or `ADMIN`, there is
no boundary to test — use equivalence partitioning. This has gone wrong in
practice: a case verifying sort order was labelled boundary value analysis. Sort
order involves sequence, but not the boundary of an input partition.

**Do not invent a limit the spec does not state.** If "how many records can be
queried at once" is absent, record an open question instead of guessing a number.
