# Business Process-Based Testing

## When it applies

The feature is one step inside a **process that spans several screens, roles, or
systems** — an approval chain, an order-to-delivery flow, a case that passes from
one team to another.

Per-screen cases can all pass while the process is broken. This technique tests
the handover points, which is where the work actually falls through.

## What to model

Write the process as a sequence of steps, each with three things:

```
step        누가            무엇을 한다                   그 결과 무엇이 남는가
1           담당자          병의원 현황을 조회한다         조회 이력
2           담당자          가능 여부를 판단해 기록한다     판단 결과
3           CS 담당자       CS 접수로 이어받는다           접수 건
```

The third column matters most. **A handover is only real if something persists**
between the steps. If step 2's result is not stored anywhere, step 3 cannot pick
it up, and that is a requirement gap rather than a test case.

## The cases this produces

**The happy path, end to end.** One case walking the whole process with one
piece of data, verifying it arrives intact at the end. Slow to run, and worth it:
it catches the field that is dropped in the handover.

**Each handover in isolation.** Given the state left by the previous step,
does the next step pick it up correctly? Tested separately so a failure names the
handover rather than the whole process.

**Abandonment at each step.** The process is started and left unfinished. What
does the queue show? Does the record stay locked? Can someone else pick it up?
Specs almost never describe this, and real users do it constantly.

**Role boundaries at each step.** Can the step-3 actor perform step 2? Should
they be able to? See `security.md`.

**Concurrent actors on the same case.** Two people process the same item at once.
Which one wins, and does the loser get told?

## Procedure

1. Write out the steps with actor, action, and persisted result.
2. Mark every point where the data changes hands. Those are your primary cases.
3. Write the end-to-end case first, then one case per handover.
4. For each step, write the abandonment case.
5. Where a step's result has nowhere to be stored, record an open question. This
   is a design gap that will otherwise surface after release.

## Example

```
제목      판단 결과를 기록하면 CS 접수 화면에서 해당 내용을 확인할 수 있다
사전조건  담당자 계정으로 병의원 현황 조회를 완료한 상태다
단계      1. 조회 결과에서 가능 여부를 「가능」으로 기록한다
          2. 로그아웃한 뒤 CS 담당자 계정으로 로그인한다
          3. CS 접수 화면에서 해당 병원의 건을 연다
기대 결과 CS 접수 화면에 1단계에서 기록한 「가능」 판단과 판단 일시,
          판단한 담당자가 표시된다
기법      Business Process-Based Testing (handover)
```

The role switch in step 2 is the point of the case. Running both steps as the
same account would pass while the real handover is broken.

## Common mistakes

**Only the end-to-end case.** When it fails, the whole process is suspect and
nobody knows which step broke. Pair it with per-handover cases.

**Staying in one session.** A handover between roles has to switch accounts, or
the permission and visibility defects stay hidden.

**Ignoring what the previous step left behind.** Setting up step 3 by inserting
data directly skips the very thing under test.

**Assuming the process as described is the process performed.** Where the spec
says a step is optional or "보통 함께 진행한다", ask what happens when it is
skipped. That ambiguity is an open question, not a detail.
