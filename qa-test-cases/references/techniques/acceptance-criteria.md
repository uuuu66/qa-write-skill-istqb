# Acceptance Criteria and Acceptance Tests

## When it applies

**Read this before extracting the Test Model.** Product specs are written as
prose and screen descriptions, not as testable statements. Converting prose into
acceptance criteria is the step that makes everything downstream extractable.

This is the chain:

```
Spec prose
   ↓  acceptance criteria      testable statements
   ↓  business rules           what must always hold
   ↓  partitions, boundaries, states
   ↓  test conditions
   ↓  test cases
```

## What makes a criterion testable

A criterion is testable when two people reading it would agree on whether a given
run passed. Three properties:

- **An observable subject.** A field, a badge, a status, a response.
- **A definite outcome.** One outcome, not "or".
- **Stated conditions.** Under what circumstances this holds.

```
not testable   조회가 빠르게 동작한다
testable       조회 결과가 3초 이내에 표시된다

not testable   권한이 없으면 적절히 처리한다
testable       권한이 없는 계정이 조회를 요청하면 HTTP 403을 반환하고
               "조회 권한이 없습니다"가 표시된다
```

## The Given-When-Then shape

Structuring a criterion this way makes the extraction mechanical.

```
Given  시스템이 어떤 상태인가        → 사전조건, 그리고 상태 전이의 from
When   사용자가 무엇을 하는가        → 단계, 그리고 전이를 일으키는 event
Then   무엇이 관찰되는가             → 기대 결과, 그리고 전이의 to
```

The value is not the syntax. It is that **each block maps onto a part of the
Test Model**. A criterion that cannot be written in this shape is usually not a
criterion yet — it is a wish.

Write these in the product's own vocabulary, describing user actions rather than
UI mechanics ("조회를 실행한다", not "조회 버튼을 클릭한다") so the criterion
survives a UI change.

## Extracting from prose

Work through the spec looking for these patterns.

| Spec says | Extract as |
| --- | --- |
| "~해야 한다", "~할 수 없다" | a business rule, with the sentence quoted as `source` |
| "최대 N개", "N일 이내", "N자 이상" | an input constraint — the script derives the boundaries |
| "A인 경우 ~, B인 경우 ~" | a decision table |
| "~한 뒤에는 ~할 수 있다" | a state and a transition |
| "관리자만", "담당자는" | an actor and a permission, plus a negative case for others |
| "~를 제안한다", "~를 검토 중" | **not a rule.** An open question |

That last row matters. A spec marked "제안" or "검토" is not settled, and
recording it as a rule produces cases that will all be wrong. This has happened
in practice: a line labelled `[제안 — §4.1]` became a business rule.

## What to do with what is missing

Every acceptance criterion you cannot complete becomes an `openQuestions` entry,
and the `why` field states **which case cannot be written without the answer**.

```
question       한 번에 조회 가능한 최대 건수 상한은 몇 건인가?
why            복수 조회 건수의 경계값(상한, 상한+1)을 확정할 수 없어
               BV-multiQueryLimit 항목을 실행할 수 없다
blocksTesting  true
```

Phrased this way, the question is actionable for the spec author: it says what is
blocked, not merely that something is unclear. **This list is the first useful
output of the whole run** — it can be sent before any case is reviewed.

## Common mistakes

**Treating a screen description as a criterion.** "부가정보 섹션에 최종 검증일,
과거 변경이력, 촉탁처를 표시한다" describes layout. The criterion needs the
condition and the observable state: when is it collapsed, when expanded, what
happens when a value is absent.

**Inferring an unstated criterion from good intentions.** If the spec does not
say what happens when the upstream check fails, the answer is a question, not a
reasonable guess.

**Dropping the source quote.** Without it, nobody can later tell a real rule from
an invented one. `scripts/verify.py` checks these quotes against the spec text;
a rule with no quotable source will be flagged.
