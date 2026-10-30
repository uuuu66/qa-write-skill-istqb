# State Transition Testing

## When it applies

The feature has **states**, and the same input produces different results
depending on which state the system is in.

- an order that is 접수 → 결제완료 → 배송중 → 완료
- an account that is 미인증 → 인증대기 → 활성 → 정지
- a screen that is 초기 → 조회중 → 결과표시 → 선택됨

If the checklist contains items starting with `TR-`, read this document.

## Notation

A transition is `event [guard condition] / action`. The guard is a condition
that must hold for the event to cause the transition; the action is what the
system does on the way. Either may be absent.

A state table has states as rows and events as columns. Its cells hold the target
state. **Empty cells are the invalid transitions** — the events that must do
nothing in that state. A state diagram hides these; the table makes them visible,
which is why invalid transitions are so often untested.

## Coverage levels

Three levels, in increasing strength.

**All states.** Every state is reached at least once. Weak: it says nothing about
how you got there.

**Valid transitions (0-switch).** Every valid transition is exercised once. **This
is the default target for this skill** — one case per `TR-` item.

**All transitions.** Every cell of the state table including the empty ones, so
invalid transitions are attempted and confirmed to do nothing. Use this where a
wrong transition would corrupt data or money.

## Procedure

1. Take one `TR-` item: `from --event--> to`, possibly with a guard.
2. **Drive the system into the `from` state through the product's own flow**, not
   by editing the database. A state reached by a shortcut may not carry the same
   side conditions.
3. Fire the event, satisfying the guard if there is one.
4. The expected result names **the new state and how it is observable** — which
   badge, which button becomes enabled, which status field value.
5. One case may legitimately walk several transitions; list every id it covers.

## Invalid transitions

For an empty cell, the expected result is the interesting part:

```
기대 결과  상태가 배송중에서 바뀌지 않고, 취소 버튼이 비활성 상태로 유지되며,
           취소 요청에 대해 HTTP 409를 반환한다
```

Three things at once: the state did not change, the UI did not offer the action,
and the API refused it. A product often gets two of the three right.

## Example

Checklist item:

```
TR-02   EMAIL_PENDING --24시간 경과--> EXPIRED   guard: 미인증 상태
```

Test case:

```
제목      인증 메일을 24시간 내 인증하지 않으면 계정이 만료 상태로 전이한다
사전조건  가입을 완료해 계정 상태가 EMAIL_PENDING이다
단계      1. 인증 링크를 클릭하지 않고 24시간이 지난 시점으로 시간을 이동한다
          2. 계정 상태를 조회한다
          3. 만료된 인증 링크를 클릭한다
기대 결과 계정 상태가 EXPIRED로 표시되고, 만료된 링크 클릭 시
          "인증 유효 기간이 지났습니다"가 표시되며 계정이 활성화되지 않는다
기법      State Transition Testing (valid transitions coverage)
coversIds TR-02
```

## Common mistakes

**Reaching the starting state by direct data manipulation.** The state is set,
but the accompanying data is not, so the transition runs against a state the
product can never actually be in.

**Testing only the happy path chain.** 접수 → 결제 → 배송 gets covered while
"cancel while shipping" never does. The invalid transitions are where the money
defects live.

**Not observing the new state.** "전이한다" is not an expected result. Name the
field, badge, or button that shows it.

## When not to use it

If the outcome depends on **a combination of conditions rather than on history**,
that is a decision table. State transition testing is for when *the order of
events* matters.
