"""Export test cases as CSV.

Writes a BOM so Excel opens the Korean text as UTF-8.

Usage:
    python3 export_csv.py test-cases.json > test-cases.csv
"""

import csv
import io
import json
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, dict):
        payload = payload.get("result", payload)
        cases = payload.get("testCases", [])
    else:
        cases = payload

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["제목", "기법", "우선순위", "부정", "사전조건", "단계", "기대 결과", "커버 항목", "근거"])

    for case in cases:
        steps = "\n".join(
            f"{i}. {s.get('action', '')}" + (f" [{s['data']}]" if s.get("data") else "")
            for i, s in enumerate(case.get("steps") or [], 1)
        )
        writer.writerow([
            case.get("title", ""),
            case.get("technique", ""),
            case.get("priority", ""),
            "Y" if case.get("isNegative") else "N",
            " / ".join(case.get("preconditions") or []),
            steps,
            case.get("expectedResult", ""),
            ", ".join(case.get("coversIds") or []),
            case.get("rationale", ""),
        ])

    sys.stdout.write("﻿" + buffer.getvalue())


if __name__ == "__main__":
    main()
