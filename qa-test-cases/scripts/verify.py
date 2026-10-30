"""Check a generated result against the spec's own text.

Every judgement here rests on one question only: does this wording actually
appear in the spec? That keeps the check meaningful to someone who knows nothing
about the pipeline's internals.

Usage:
    python3 verify.py test-model.json test-cases.json spec.md [spec2.md ...]
"""

import json
import re
import sys

NOISE = re.compile(r"[\s\"'`.,·:()\[\]{}「」]")

# Wording that defers the judgement itself. An ending like "확인할 수 있다" is
# fine when an observable subject precedes it, so only these phrases count as a
# problem, not the ending.
# This heuristic is advisory: it flags candidates for a human to read, and it
# both misses cases and produces false positives. Treat its count as a hint,
# never as a verdict.
UNJUDGEABLE = re.compile(r"정상적으로|적절히|올바르게|필요에 따라|또는 .{0,20}(표시|노출|안내)된다")
OBSERVABLE = re.compile(r"\d|[A-Z]{2,}|「.+?」|배지|컬럼|상태가|표시되지 않|생성되지 않|반환|저장|이동|비활성|차단|거부")


def squash(text):
    return NOISE.sub("", (text or "").lower())


def appears_in(corpus, probe):
    """Accept a quote whose particles or endings were adjusted."""
    q = squash(probe)

    if len(q) < 6:
        return False
    if q in corpus:
        return True

    for i in range(0, len(q) - 11, 6):
        if q[i:i + 12] in corpus:
            return True

    return False


def load_cases(path):
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, dict):
        payload = payload.get("result", payload)
        return payload.get("testCases", [])

    return payload


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        loaded = json.load(f)
    spec = loaded.get("result", loaded)
    spec = spec.get("spec", spec)

    cases = load_cases(sys.argv[2])

    corpus = ""
    for path in sys.argv[3:]:
        with open(path, encoding="utf-8") as f:
            corpus += squash(f.read())

    print("=== 1. 출처 대조 (기획서에 실제로 있는 문구인지) ===")
    unverified = []

    rules = spec.get("businessRules") or []
    for rule in rules:
        quoted = re.findall(r"[\"'“”](.{6,}?)[\"'“”]", str(rule.get("source") or ""))
        probes = quoted or [rule.get("rule") or ""]

        if not any(appears_in(corpus, p) for p in probes):
            unverified.append(rule)

    print(f"비즈니스 규칙 {len(rules)}건 중 {len(rules) - len(unverified)}건을 기획서에서 확인했습니다.")

    if unverified:
        print(f"\n기획서에서 찾지 못한 규칙 {len(unverified)}건입니다. 사람이 확인해야 합니다.")
        for rule in unverified:
            print(f"  - {rule.get('id')}: {str(rule.get('rule'))[:60]}")
            print(f"      출처: {str(rule.get('source'))[:70]}")

    no_source = [r for r in rules if len(str(r.get("source") or "")) < 4]
    if no_source:
        print(f"\n출처가 비어 있는 규칙 {len(no_source)}건입니다.")

    print("\n=== 2. 검증 가능성 (기대 결과로 합격을 가를 수 있는지) ===")
    vague = [
        c for c in cases
        if len(c.get("expectedResult") or "") < 12
        or UNJUDGEABLE.search(c.get("expectedResult") or "")
        or not OBSERVABLE.search(c.get("expectedResult") or "")
    ]
    print(f"판정할 수 없는 기대 결과 {len(vague)}건 / 전체 {len(cases)}건")
    for case in vague[:5]:
        print(f"  - {case.get('title')}")
        print(f"      기대: {case.get('expectedResult')}")

    print("\n=== 3. 사람이 직접 볼 항목 ===")
    questions = spec.get("openQuestions") or []
    blocking = [q for q in questions if q.get("blocksTesting")]
    print(f"미해결 질문 {len(questions)}건, 그중 테스트 불가 {len(blocking)}건")
    for q in blocking[:5]:
        print(f"  - {q.get('question')}")


if __name__ == "__main__":
    main()
