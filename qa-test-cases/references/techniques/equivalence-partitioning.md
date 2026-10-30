# Equivalence Partitioning

## When it applies

An input divides into **groups the system treats the same way**. That covers
almost every input, which is why this technique produces the largest share of
cases.

- ranged values: inside the range, below the minimum, above the maximum
- enumerated values: each value, plus a value not in the set
- format constraints: matching, not matching
- required inputs: present, missing

If the checklist contains items starting with `EP-`, read this document.

## What the script did, and what you do

`scripts/testmodel.py derive` builds the partitions from the constraints. Valid
and invalid groups are separated, and every required input already carries a
missing-value partition.

**Do not re-partition.** Pick one representative value per group and write the case.

## The principle

Values inside one partition are assumed to be processed identically, so testing
one value from a partition stands for all of them. **One case per partition is
enough.** Adding a second value from the same partition does not raise coverage.

Partitions must not overlap and must not be empty. Overlapping partitions mean
the partitioning itself is wrong.

**Never skip the invalid partitions.** Testing only valid values is the single
most common omission in practice.

## Procedure

1. Take one `EP-` item. It says `유효` or `무효` and describes the group.
2. Pick **one representative value**. Use an example from the spec if there is
   one; otherwise take the most ordinary value in the group. Avoid values sitting
   on a boundary — boundary value analysis owns those.
3. Fill the other inputs with valid values.
4. Write an expected result that names what to observe.

## With several inputs

Each partition of each input needs to appear **at least once**. This is Each
Choice coverage. Three inputs with four partitions apiece need **four** cases,
not twelve, because one case can carry a partition from every input at once.

But **only one invalid partition per case**. With two invalid values present, the
system's filtering order decides which error surfaces, and the other value goes
unverified.

```
good   age=13(invalid), email=valid, role=USER     → verifies the age partition
bad    age=13(invalid), email=malformed(invalid)   → the email check is masked
```

When the combination itself decides the outcome, this is not equivalence
partitioning — use a decision table.

## Example

Checklist item:

```
EP-role:invalid:0   role — 무효: 정의되지 않은 값
```

Test case:

```
제목      정의되지 않은 role 값은 거부된다
단계      1. 가입 요청 본문에 role="SUPERUSER"를 넣고, 나머지 필드는 유효값으로 채운다
          2. 요청을 전송한다
기대 결과 HTTP 400을 반환하고 role 필드의 유효성 오류가 응답에 포함되며,
          계정이 생성되지 않는다
기법      Equivalence Partitioning
coversIds EP-role:invalid:0
```

## Common mistakes

**Verifying the same partition twice under different names.** This happens when
the partition itself was captured twice. Different checklist ids with identical
verification content should be merged into one case.

**Choosing a boundary as the representative.** Picking 14 for the `14~100` group
makes the case indistinguishable from the boundary case. Pick 30 or 45.

**Checking incidental things in a valid-partition case.** Two purposes in one
case means a failure does not narrow to one cause. Keep one thing under test.

## When not to use it

**Combinations of conditions decide the outcome** — use a decision table. A rule
like "VIP tier paying by card gets a discount" cannot be handled by looking at
each partition separately.

**The same input behaves differently depending on state** — use state transition
testing.
