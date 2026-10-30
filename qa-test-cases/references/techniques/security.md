# Security Testing

## When it applies

The feature involves authentication, authorization, or accepts input that reaches
a query, a file path, or a rendered page. Practically every feature with a login
qualifies.

**Scope note.** This covers the test cases a QA engineer writes for a feature. It
is not penetration testing and does not replace a security review.

## Authorization: the cases specs never contain

A spec says who *can* do something. It almost never says what happens to
everyone else, and that silence is where the defects are.

For every action in the feature, write these:

- **no credentials** → 401, and no data in the response body
- **authenticated, wrong role** → 403
- **authenticated, right role, another owner's record id** → 403 or 404, never
  the record. Test this by taking a real id from account A and requesting it as
  account B.
- **permission enforced in the UI only** → call the endpoint directly with the
  lower-privileged token. A hidden button is not access control.
- **privilege escalation through the payload** → send `role: "ADMIN"` on a
  self-service signup or profile update and confirm it is ignored, not applied.

That last one has a checklist item in this skill's own history: a signup feature
where an ordinary user could set their own role.

## Session and token handling

- expired token → 401, and the UI returns to login rather than showing a blank screen
- token from a deleted or suspended account → rejected
- logout, then reuse of the previous token → rejected
- **an active session whose permissions were revoked mid-session** — is the
  change picked up, or does the old permission persist until expiry?

## Input reaching a sensitive sink

Where input reaches a database query, a file path, a shell, or rendered HTML, add
a case per sink with a payload characteristic of that sink. The expected result is
always the same shape: **the input is treated as data, not as instruction.**

```
기대 결과  입력한 문자열이 화면에 그대로 텍스트로 표시되고,
           스크립트로 실행되지 않는다
```

Do not write these as "check for SQL injection". Name the field, the payload, and
what must be observed.

## What must not leak

- an error page or API error that contains a stack trace, query text, or internal
  host name
- a "wrong password" message that differs from "no such account", which lets an
  attacker enumerate accounts
- a list endpoint that returns other tenants' fields even though the UI hides them
- personal data in application logs

## Procedure

1. Enumerate every action and every endpoint in the feature.
2. For each, write the 401, 403, and cross-owner cases. These are mandatory and
   independent of what the spec says.
3. For each input that reaches a sensitive sink, write one case per sink.
4. For each error path, add the leakage check to the expected result.
5. Score these risks for impact honestly — a permission boundary is HIGH impact
   even when the path is rare.

## Common mistakes

**Testing authorization only at the happy boundary.** Verifying an admin can
access admin functions says nothing about whether a regular user cannot.

**Accepting a 200 with an empty body as correct for cross-owner access.** It is
inconsistent with a 403 elsewhere and often means the check landed in the view
layer, not in the query.

**Treating security cases as optional extras.** They fail independently of
functional cases and belong in the same suite.
