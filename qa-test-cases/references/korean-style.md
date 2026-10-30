# Writing the Deliverables in Korean

Every deliverable is written in Korean: case titles, steps, expected results,
open questions, and the report. The readers are QA engineers and PMs who will
execute the cases, so an ambiguous sentence blocks the execution itself.

## Sentence rules

1. **End sentences completely.** Do not stop at a noun phrase or a connective.
   - bad: `중복 시 오류`
   - good: `이미 가입된 이메일이면 409 오류를 반환한다`

2. **Use the `~한다` register throughout.** Never mix `~합니다` into the same
   deliverable.

3. **Do not drop particles or endings.**
   - bad: `계정 상태 변경 확인`
   - good: `계정 상태가 EMAIL_PENDING으로 변경되었는지 확인한다`

4. **No em dash (—).** Use a comma, a conjunction, or a colon to carry the relation.

5. **Do not chain words with the interpunct (·).** List with `와`, `과`, or commas.
   - bad: `로딩·에러·재시도 확인`
   - good: `로딩과 에러, 재시도를 확인한다`

6. **No figurative wording.**
   - bad: `케이스가 물린다`
   - good: `케이스가 해당 항목을 검증한다`

7. **Call the same thing by the same name.** Screen and field names follow the
   spec's own wording. If the spec writes 「병의원 현황」, do not render it as
   「병원 현황」.

8. **Leave identifiers alone.** HTTP status codes, field and component names,
   enum values, file paths, and text the product actually displays are never
   translated or tidied.

## Step sentences

One action per sentence. Input values go in the `data` field, not inside the
sentence.

```
good   action: "가입 폼을 제출한다"           data: "age=13"
bad    action: "age를 13으로 해서 가입 폼 제출"
```

## Expected result sentences

Include at least one observable subject:

- an HTTP status code or a response field value
- on-screen text, a badge name, or a column value
- the name of a stored state
- what must **not** happen

Never use these. The executor cannot decide pass or fail from them.

- `정상적으로 동작한다`, `적절히 표시된다`, `올바르게 처리된다`
- `A 또는 B가 표시된다` — allowing either is the same as having no criterion
