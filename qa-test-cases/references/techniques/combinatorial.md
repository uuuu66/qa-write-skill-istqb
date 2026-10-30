# Combinatorial Testing

## When it applies

**Three or more inputs whose combinations could interact**, where testing every
combination is unaffordable.

- a search screen with six optional filters
- a settings page where several toggles affect one output
- a configuration matrix: browser × OS × locale × plan tier

Not every multi-input feature needs this. Reach for it when a defect could live
in the *interaction* rather than in any single value.

## Why not all combinations

Five inputs with four values each is 1,024 combinations. Most interaction defects
involve only two parameters, so covering every **pair** finds most of them at a
fraction of the cost.

## Two ways to reduce

**Base choice coverage.** Pick the most typical value for every input — that
combination is the base case. Then, for each input in turn, swap only that input
to each of its other values, holding the rest at base. With five inputs of four
values: 1 + 5×3 = **16 cases** instead of 1,024.

Use this when one combination is clearly the normal usage and the others are
variations. It reads well to a human executor and each failure points at one
input.

**Pairwise coverage.** Every pair of values from every two inputs appears in at
least one case. Stronger at finding interaction defects, but the cases look
arbitrary and a failure takes more work to localize. Generating a minimal set
requires a tool; do not hand-optimize it.

Prefer base choice unless the spec actually describes interacting conditions.

## Reduce the input space first

Apply equivalence partitioning **before** combining. An input with a 1–100 range
has three partitions, not 100 values. Combining raw values instead of partitions
is what makes combinatorial testing look impossible.

Then remove combinations that cannot occur. "비회원 + VIP 등급" is infeasible and
should never enter the count.

## Procedure

1. List the inputs and, for each, its partitions (not its raw values).
2. Remove infeasible combinations.
3. Pick base choice or pairwise, and say in `rationale` which and why.
4. Write the cases. Each case sets every input explicitly — an unset input makes
   the result unattributable.
5. Add back, by hand, any combination known to be problematic from past defects.

## Example

```
검색 조건   병원명(입력/미입력) · 지역(선택/미선택) · 심평원 동시조회(ON/OFF)

base        병원명 입력, 지역 미선택, 심평원 ON        ← 가장 흔한 사용
변형 1      병원명 미입력, 지역 미선택, 심평원 ON
변형 2      병원명 입력, 지역 선택, 심평원 ON
변형 3      병원명 입력, 지역 미선택, 심평원 OFF
```

Four cases instead of eight, and each variant differs from base in exactly one
input, so a failure names its own cause.

## Common mistakes

**Combining before partitioning.** The combination count explodes and the
technique gets abandoned as impractical.

**Leaving inputs unset.** "지역은 아무 값" means the case is not reproducible and
a failure cannot be attributed.

**Using pairwise where the spec states explicit condition rules.** If the spec
says which combinations produce which outcome, that is a decision table — it has
defined expected results, and combinatorial testing does not.

## When not to use it

**Two inputs only.** Equivalence partitioning with Each Choice coverage already
handles it.

**The combination is the requirement.** Use a decision table.
