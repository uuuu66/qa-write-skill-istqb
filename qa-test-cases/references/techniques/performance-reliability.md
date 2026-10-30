# Performance and Reliability Testing

## When it applies

The spec states a response time, a volume, or a recovery expectation — or the
feature fans out to several upstream calls, loads a list that grows without
bound, or is used concurrently by many people.

**A performance case needs a number.** If the spec has none, the correct output
is an open question, not a case with a guessed threshold.

## Performance: what to ask for

Turn vague wording into a measurable criterion before writing a case.

```
spec says     조회가 빠르게 동작한다
ask           어떤 조건에서 몇 초 이내인가? 동시 사용자 몇 명 기준인가?
criterion     담당자 10명이 동시에 조회할 때, 100건 결과가 3초 이내에 표시된다
```

A usable criterion carries three parts: **the load** (how many users, how much
data), **the operation**, and **the threshold**.

Distinguish the kinds, because they fail differently:

- **Load** — the expected peak. Does it meet the threshold at normal busy times?
- **Stress** — beyond the peak. Does it degrade gracefully or collapse?
- **Volume** — a large data set rather than many users. A list of 100,000 rows.
- **Endurance** — sustained over hours. Reveals leaks and connection exhaustion.

For a feature-level suite, load and volume cases are usually enough.

## Volume cases specs forget

- a list with zero rows, one row, and a very large number of rows
- a field at its maximum length rendered in a narrow column
- an export of the full data set rather than one page
- pagination at the last page and one past it

These often surface layout and timeout defects that no functional case touches.

## Reliability: behaviour when something fails

The questions that matter more than throughput:

- an upstream call times out — does the user see a clear message, or a spinner
  forever?
- **a partial failure**: 10 items requested, 3 fail. Are the 3 distinguished from
  the 7, or does the screen present a clean result that is quietly incomplete?
- the process restarts mid-operation — is the record left half-written?
- a retry after an apparent failure that actually succeeded — does it duplicate?

Partial failure deserves its own case in almost every feature that calls an
upstream service. It is the failure mode products hide best.

## Procedure

1. Find every stated number in the spec. Each becomes a case with that number as
   the threshold.
2. For every unstated but implied number, write an open question naming which
   case is blocked.
3. Write the volume cases: empty, one, many.
4. For each upstream dependency, write timeout, error, and partial-failure cases.
5. The expected result names **what is measured and where it is observed** — the
   elapsed time as seen by the user, the message shown, the state left behind.

## Example

```
제목      복수 조회 중 일부 건만 실패하면 실패한 건을 구분해 표시한다
사전조건  병원 10건을 조회 대상으로 입력한다
단계      1. 심평원 조회 API가 3건에 대해서만 500을 반환하도록 구성한다
          2. 조회를 실행한다
기대 결과 실패한 3건의 「심평원 확인」 배지가 「미검증」으로 표시되고,
          성공한 7건과 시각적으로 구분되며, 전체 조회가 실패로 처리되지 않는다
기법      Reliability (partial failure)
```

## Common mistakes

**Writing a performance case without a number.** "빠르게 표시된다" cannot pass or
fail. Ask, or record the question.

**Measuring the server and calling it the user's experience.** The threshold the
spec promises is usually what the user sees, which includes rendering.

**Testing only the empty and the typical volume.** The large-volume case is where
timeouts and layout breaks live.

**Treating an upstream failure as an empty result.** "데이터 없음" and
"확인하지 못함" must be distinguishable, or the operator acts on a false negative.
