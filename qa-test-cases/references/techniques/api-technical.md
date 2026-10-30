# API and Technical Testing

## When it applies

The spec exposes an API, or the feature calls one. Read this whenever the
checklist contains `API_STATUS` items — and read it even when it does not, if the
feature talks to anything over a network.

**This is the technique that finds what the spec never mentions.** A product spec
describes the successful path in the user's language. The failures below are
almost never written down, and they are what breaks in production.

## What a spec omits, nearly always

Work through this list against every endpoint the feature uses.

**Authentication and authorization**
- no credentials → 401
- valid credentials, insufficient role → 403
- another tenant's or another user's record id → 403 or 404, never the record
- token expired mid-session
- permission checked on the UI but not on the API (test the API directly)

**Existence and conflict**
- id that does not exist → 404
- duplicate create where a uniqueness rule exists → 409
- record deleted after the screen loaded, then acted on → 404 or 409
- **a referenced record deleted while still referenced** — the single most common
  crash source. A membership whose group is gone, an order whose product is gone.

**Validation**
- required field missing → 400 or 422
- type mismatch: string where a number belongs
- payload far above expected size
- `Content-Type` wrong or absent

**Concurrency and repetition**
- the same request sent twice in quick succession — does it create two records?
- two users editing the same record at once
- retry after a timeout where the first request actually succeeded (idempotency)

**Degradation**
- an upstream service returns 500
- an upstream service times out
- an upstream service returns a partial result: 10 requested, 3 failed

That last one deserves its own case. **Partial failure is where products lie
most** — they show a clean result and silently drop the failures.

## Procedure

1. For each endpoint in `apiAspects`, take the status codes listed and write one
   case per code.
2. For each entry in `technicalRisks`, write a case that forces the condition —
   mock the upstream failure, send the duplicate, delete the referenced record.
3. Expected results at this level should name the **status code and the response
   body's shape**, plus what the UI does with it.
4. Where the spec does not define the behaviour for a failure, state only what is
   certain and record an open question. This is the most frequent gap: specs say
   what happens on success and stay silent on the rest.

## Example

```
제목      ERP 마스터 조회가 실패하면 미등록으로 단정하지 않는다
사전조건  ERP 마스터에 등록된 병원이 존재한다
단계      1. ERP 마스터 조회 API가 HTTP 500을 반환하도록 구성한다
          2. 해당 병원명으로 조회를 실행한다
기대 결과 「ERP 등록」 컬럼에 「미등록」 배지가 표시되지 않고, 조회 실패를
          알리는 표기가 나타난다
기법      API Testing (upstream failure)
coversIds GET:/erp/master:500
rationale 확인 실패를 미등록으로 단정하면 담당자가 거래 가능 여부를 오판한다
```

Note what the expected result does **not** claim: it does not invent the exact
failure wording, because the spec never defined it. It asserts the part that is
certain — the misleading badge must not appear.

## Common mistakes

**Testing permissions only through the UI.** A hidden button is not access
control. Call the endpoint directly with the lower-privileged token.

**Treating an upstream failure as equivalent to an empty result.** "No data" and
"could not check" must display differently, or the operator cannot tell them
apart.

**Writing one case for "error handling".** Each status code is its own case;
they fail independently.
