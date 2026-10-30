"""Derive test items from a Test Model and compute coverage.

Everything in this file is deterministic: the same Test Model always yields the
same items. Asking a model "is anything missing?" returns a different answer
each run, which is why none of this is left to one.

Usage:
    python3 testmodel.py derive   model.json   > model.derived.json
    python3 testmodel.py coverage model.json [cases.json]
"""

import json
import re
import sys

# ---------------------------------------------------------------- shared

INT_TYPES = re.compile(r"^(number|integer|int|long|numeric|decimal|float|double)$", re.I)
# One field often gets captured twice under two names ("sim-check" and
# "「심평원도 함께 조회」 체크박스"). Compare with whitespace and punctuation
# stripped so those fold into a single item.
NAME_NOISE = re.compile(r"[\s_\-·「」\"'()\[\]]")


def name_key(name):
    return NAME_NOISE.sub("", (name or "").lower())


def arr(value):
    return value if isinstance(value, list) else []


def find_by_input(rows, name):
    key = name_key(name)
    for row in rows:
        if name_key(row.get("input")) == key:
            return row
    return None


# ---------------------------------------------------------------- derivation

def three_value(boundary, below, on, above):
    return [
        {"value": str(boundary - 1), "kind": "below", "expectation": below},
        {"value": str(boundary), "kind": "on", "expectation": on},
        {"value": str(boundary + 1), "kind": "above", "expectation": above},
    ]


def boundaries_for(field):
    """Boundary values from the constraints. Arithmetic, so never delegated."""
    out = []
    c = field.get("constraints") or {}
    numeric = bool(INT_TYPES.match((field.get("type") or "").strip()))

    if numeric and isinstance(c.get("min"), (int, float)):
        out += three_value(int(c["min"]), "거부 (하한 미만)", "허용 (하한)", "허용")

    if numeric and isinstance(c.get("max"), (int, float)):
        out += three_value(int(c["max"]), "허용", "허용 (상한)", "거부 (상한 초과)")

    for key, below, on, above in (
        ("minLength", "거부 (하한 미만)", "허용 (하한)", "허용"),
        ("maxLength", "허용", "허용 (상한)", "거부 (상한 초과)"),
    ):
        if isinstance(c.get(key), (int, float)):
            n = int(c[key])
            out += [
                {**v, "value": f"길이 {v['value']}"}
                for v in three_value(n, below, on, above)
            ]

    return out


def partition_for(field):
    valid, invalid = [], []
    c = field.get("constraints") or {}

    if isinstance(c.get("min"), (int, float)) or isinstance(c.get("max"), (int, float)):
        lower = c.get("min", "하한 없음")
        upper = c.get("max", "상한 없음")
        valid.append(f"{lower} ~ {upper}")
        if isinstance(c.get("min"), (int, float)):
            invalid.append(f"{c['min']} 미만")
        if isinstance(c.get("max"), (int, float)):
            invalid.append(f"{c['max']} 초과")
        invalid.append("숫자가 아닌 값")

    if arr(c.get("enumValues")):
        valid += list(c["enumValues"])
        invalid.append("정의되지 않은 값")

    fmt = c.get("format") or c.get("pattern")
    if fmt:
        valid.append(f"형식에 맞는 값 ({fmt})")
        invalid.append(f"형식에 맞지 않는 값 ({fmt})")

    # A missing required value is the most commonly omitted case in practice.
    if field.get("required"):
        invalid.append("값 누락 / 빈 값")

    return valid, invalid


def dedupe(values):
    seen, out = set(), []
    for v in values:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def derive(spec):
    """Merge what the model produced with what the constraints imply."""
    boundaries, partitions = [], []

    for b in arr(spec.get("boundaries")):
        existing = find_by_input(boundaries, b.get("input"))
        if existing:
            seen = {v["value"].strip() for v in existing["values"]}
            existing["values"] += [v for v in arr(b.get("values")) if v["value"].strip() not in seen]
        else:
            boundaries.append({**b, "values": list(arr(b.get("values")))})

    for p in arr(spec.get("partitions")):
        existing = find_by_input(partitions, p.get("input"))
        if existing:
            existing["valid"] = dedupe(existing["valid"] + arr(p.get("valid")))
            existing["invalid"] = dedupe(existing["invalid"] + arr(p.get("invalid")))
        else:
            partitions.append({**p, "valid": arr(p.get("valid")), "invalid": arr(p.get("invalid"))})

    for i, field in enumerate(arr(spec.get("inputs"))):
        name = field.get("name") or str(i + 1)

        values = boundaries_for(field)
        if values:
            existing = find_by_input(boundaries, name)
            if existing:
                seen = {v["value"].strip() for v in existing["values"]}
                existing["values"] += [v for v in values if v["value"].strip() not in seen]
            else:
                boundaries.append({"id": f"BV-{name}", "input": name, "values": values})

        valid, invalid = partition_for(field)
        if valid or invalid:
            existing = find_by_input(partitions, name)
            if existing:
                existing["valid"] = dedupe(existing["valid"] + valid)
                existing["invalid"] = dedupe(existing["invalid"] + invalid)
            else:
                partitions.append(
                    {"id": f"EP-{name}", "input": name, "valid": dedupe(valid), "invalid": dedupe(invalid)}
                )

    return {**spec, "boundaries": boundaries, "partitions": partitions}


# ---------------------------------------------------------------- checklist

def checklist(spec):
    items = []

    for p in arr(spec.get("partitions")):
        for i, label in enumerate(arr(p.get("valid"))):
            items.append({"id": f"{p['id']}:valid:{i}", "kind": "PARTITION",
                          "description": f"{p.get('input')} — 유효: {label}", "mandatory": True})
        for i, label in enumerate(arr(p.get("invalid"))):
            items.append({"id": f"{p['id']}:invalid:{i}", "kind": "PARTITION",
                          "description": f"{p.get('input')} — 무효: {label}", "mandatory": True})

    for b in arr(spec.get("boundaries")):
        for i, v in enumerate(arr(b.get("values"))):
            items.append({"id": f"{b['id']}:{i}", "kind": "BOUNDARY",
                          "description": f"{b.get('input')} = {v.get('value')} ({v.get('kind')}) → {v.get('expectation')}",
                          "mandatory": True})

    for t in arr(spec.get("transitions")):
        items.append({"id": t.get("id"), "kind": "TRANSITION",
                      "description": f"{t.get('from')} --{t.get('event')}--> {t.get('to')}", "mandatory": True})

    for r in arr(spec.get("businessRules")):
        items.append({"id": r.get("id"), "kind": "BUSINESS_RULE",
                      "description": r.get("rule"), "mandatory": True})

    for table in arr(spec.get("decisionTables")):
        for i, rule in enumerate(arr(table.get("rules"))):
            items.append({"id": f"{table['id']}:R{i + 1}", "kind": "DECISION_RULE",
                          "description": f"{' / '.join(arr(rule.get('conditionValues')))} → {rule.get('action')}",
                          "mandatory": True})

    for a in arr(spec.get("apiAspects")):
        for code in arr(a.get("statusCodes")):
            items.append({"id": f"{a.get('method')}:{a.get('endpoint')}:{code}", "kind": "API_STATUS",
                          "description": f"{a.get('method')} {a.get('endpoint')} → {code}", "mandatory": False})

    for r in arr(spec.get("risks")):
        # Leaving low-risk items uncovered is intended, not an omission.
        items.append({"id": r.get("id"), "kind": "RISK", "description": r.get("description"),
                      "mandatory": r.get("priority") in ("P0", "P1")})

    return items


def analyze(items, cases):
    claimed = {cid for c in cases for cid in arr(c.get("coversIds"))}
    known = {i["id"] for i in items}

    signatures = {}
    for c in cases:
        steps = ">".join(f"{s.get('action')}|{s.get('data', '')}" for s in arr(c.get("steps")))
        sig = re.sub(r"\s+", " ", f"{steps}#{c.get('expectedResult')}").strip().lower()
        signatures.setdefault(sig, []).append(c.get("title"))

    return {
        "total": len(items),
        "covered": sum(1 for i in items if i["id"] in claimed),
        "gaps": [i for i in items if i["mandatory"] and i["id"] not in claimed],
        "danglingIds": sorted(claimed - known),
        "duplicates": [t for t in signatures.values() if len(t) > 1],
    }


# ---------------------------------------------------------------- entry point

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command, model_path = sys.argv[1], sys.argv[2]
    with open(model_path, encoding="utf-8") as f:
        loaded = json.load(f)
    # Accept a full job payload as well as a bare Test Model.
    spec = loaded.get("result", loaded)
    spec = spec.get("spec", spec)

    if command == "derive":
        print(json.dumps(derive(spec), ensure_ascii=False, indent=2))
        return

    if command == "coverage":
        items = checklist(spec)
        cases = []
        if len(sys.argv) > 3:
            with open(sys.argv[3], encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, dict):
                payload = payload.get("result", payload)
                cases = payload.get("testCases", [])
            else:
                cases = payload

        report = analyze(items, cases)
        print(json.dumps({"checklist": items, "coverage": report}, ensure_ascii=False, indent=2))
        return

    print(f"unknown command: {command}")
    sys.exit(1)


if __name__ == "__main__":
    main()
