# Decision Table Testing

## When it applies

**A combination of conditions produces different outcomes.** Looking at each
condition separately cannot express the requirement.

Sentences in the spec that call for this technique:

- "when A and also B, do C"
- "except when D"
- rules where tier, permission, or state combinations change the screen or the handling

If the checklist contains items starting with `DT-`, read this document.

## What the script did, and what you do

A decision table **cannot be generated in code**: extracting the conditions is
itself the act of reading the spec. When the analysis records `decisionTables`
in the Test Model, the checklist turns each rule row into one item, shaped
`DT-1:R3`.

You turn each rule row into an executable case.

## Structure

Conditions and resulting actions are the rows; **each column is one rule**, a
unique combination of condition values.

```
조건             R1    R2    R3
등급 VIP인가      T     T     F
카드 결제인가     T     F     –
─────────────────────────────────
할인 적용         X
수수료 부과             X     X
```

Notation: `T` the condition holds, `F` it does not, `–` the condition does not
affect this outcome, `N/A` the combination is infeasible. In the action rows,
`X` means the action must occur and a blank means it must not.

## Reducing the columns

With n conditions there are 2^n combinations; six conditions give 64 columns.
Reduce in two steps.

**Delete infeasible combinations.** "Not a member and also VIP tier" cannot occur.

**Merge columns with the same outcome where a condition is irrelevant.** Above,
a non-VIP pays the fee regardless of payment method, so R3 and R4 collapse into
one column with `–` for the payment condition.

If columns still remain beyond what is affordable, **cover the high-risk
combinations first**, and record both that the table is not fully covered and
which columns were dropped.

## Procedure

1. Take one `DT-` item. It carries the condition values and the expected action.
2. **Set up preconditions and inputs so that exact combination holds.** One
   condition set differently means a different rule is under test.
3. Write an expected result covering **both what must happen and what must not**.
   The blanks in the action rows are the "must not" part.
4. Put the rule's id in `coversIds`.

## Example

Checklist item:

```
DT-discount:R2   VIP=T / 카드결제=F → 수수료 부과
```

Test case:

```
제목      VIP 회원이 카드가 아닌 수단으로 결제하면 수수료가 부과된다
사전조건  등급이 VIP인 계정으로 로그인한다
단계      1. 장바구니에 10,000원 상품을 담는다
          2. 결제 수단으로 계좌이체를 선택한다
          3. 결제를 실행한다
기대 결과 결제 내역에 수수료 500원이 별도 항목으로 표시되고,
          할인 항목은 표시되지 않는다
기법      Decision Table Testing
coversIds DT-discount:R2
```

## Common mistakes

**Labelling a single-condition case as a decision table.** This has happened: a
case verifying sort order carried this technique name. One condition means
equivalence partitioning.

**Omitting what must not happen.** Checking that the discount applies, without
checking that the fee is not also charged, misses the defect where both fire.

**Setting up only part of the combination.** Claiming to test R2 without setting
the payment method leaves it unknown which rule actually ran.

## The side effect worth having

Filling in the table **exposes combinations the spec never defined**. That is the
greatest value of this technique. When a blank appears, do not write a case for
it — record an open question. Guessing the expected result produces cases that
are all wrong once the spec is settled.
