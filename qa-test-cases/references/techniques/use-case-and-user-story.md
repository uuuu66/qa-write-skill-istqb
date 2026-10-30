# Use Case and User Story Testing

## When it applies

The spec is written as user stories ("~로서 ~할 수 있다") or as use cases with a
main flow and alternatives. These describe **a sequence a person performs**, so
the cases derive from flows rather than from individual inputs.

## Use case testing

A use case has a main success scenario plus alternative and exception flows. Each
flow is a coverage item: **one case per flow**, minimum.

```
main        조회 조건 입력 → 조회 → 결과 1건 → 현황 표시
alt-1       결과 여러 건 → 선택 단계 → 현황 표시
alt-2       결과 0건 → 결과 없음 안내
exc-1       조회 중 세션 만료 → 로그인 화면으로 이동
exc-2       상위 시스템 오류 → 오류 안내, 이전 결과 유지되지 않음
```

The alternatives and exceptions are where the defects are, and they are the ones
spec authors write last or not at all. If the spec lists only a main flow, the
alternatives become open questions.

Cases at this level are **end to end**: several screens, the real sequence a
person follows. They catch integration defects that per-field cases cannot — a
value entered on screen one that does not arrive on screen three.

## User story testing

A story is testable only through its acceptance criteria. The story itself is too
coarse.

```
story      담당자로서 병원의 거래 가능 여부를 조회 화면에서 바로 확인할 수 있다
criteria   1. ERP 등록 병원은 「거래가능」으로 표시된다
           2. ERP 미등록 병원은 「미등록」으로 표시된다
           3. ERP 조회에 실패하면 미등록으로 단정하지 않는다
```

Each criterion becomes at least one case. See
`acceptance-criteria.md` for turning prose into criteria.

**A story with no criteria is not ready to test.** Say so rather than inventing
them: the invented criteria will differ from what the team eventually agrees, and
every case built on them will be wrong.

## Checking the INVEST properties, briefly

Two of them affect testability directly, and noticing the failure early is worth
more than any case.

- **Testable** — can a pass be observed? If not, it is a question.
- **Small** — a story covering four screens and three roles usually hides several
  stories. Cases built on it are unfocused; ask for a split.

## Procedure

1. List the flows, or the criteria. This list is the coverage target.
2. Write one case per flow or per criterion, end to end.
3. For each flow, ask what happens if the actor **abandons it midway** — closes
   the screen, navigates away, loses the session. Specs rarely say.
4. For each role in the story, write the case for the roles that must *not* be
   able to do it. See `security.md`.
5. Missing alternatives and exceptions become open questions with the blocked
   case named.

## Example

```
제목      결과가 여러 건인 경우 선택 단계를 거쳐 현황이 표시된다
사전조건  ERP 어드민 담당자 계정으로 로그인한 상태다
단계      1. 병원명에 여러 병원이 조회되는 값을 입력한다
          2. 조회를 실행한다
          3. 결과 목록에서 두 번째 병원을 선택한다
기대 결과 결과 목록에 2건 이상이 표시되고, 선택 전에는 하단 현황 영역이
          비어 있으며, 선택 후 해당 병원의 현황이 표시된다
기법      Use Case Testing (alternative flow)
```

Note the expected result asserts the **intermediate state** — empty before
selection. A flow case that only checks the final screen misses the defect where
a previous hospital's data lingers.

## Common mistakes

**One case for the whole story.** A story has several criteria; a single case
cannot fail informatively.

**Only the main flow.** The main flow is the one the developer tested manually.

**Skipping the intermediate observations.** In an end-to-end case, what is on
screen between steps is often the requirement.

## When not to use it

For per-field validation, use equivalence partitioning and boundary values.
Driving a full flow to test one input's range is slow and fails for many reasons
at once.
