# Experience-Based Testing

## When it applies

The spec is thin, or the feature resembles one that has broken before. These
techniques do not derive cases from a model — they draw on **what tends to go
wrong**. Use them to fill the space the spec-based checklist cannot reach.

Never use them as a substitute for the checklist. They add; they do not replace.

## Error guessing

Anticipate defects from three sources: how this product has failed before, the
mistakes this team's developers tend to make, and how similar features fail
elsewhere.

A working checklist of the categories, with what to try in each:

**Input** — correct input rejected; a required parameter missing; a parameter
present but empty; leading or trailing whitespace; a value pasted from Excel with
an invisible character; a very long value; a name containing quotes or emoji.

**Output** — wrong format or unit; a number rendered with the wrong precision;
a date shown in the wrong timezone; truncation in a narrow column; a value that
is correct but stale.

**Logic** — an off-by-one in a boundary; an inverted condition; a missing `else`;
"and" implemented where "or" was meant; a case the developer did not consider
because the spec did not mention it.

**Computation** — rounding at the wrong step; integer division; a percentage
applied twice; a total that does not equal the sum of its parts.

**Interface** — a parameter mismatch between caller and callee; a type that
happens to coerce; a field renamed on one side only.

**Data** — an uninitialized value; a null where the type says required; **a
referenced record that has been deleted**; a duplicate that the uniqueness rule
was supposed to prevent.

The last one in the Data row is the highest-yield single case in most features.
A record whose referenced parent is gone crashes screens that otherwise work.

## Fault attacks

Build the list of plausible defects first, then design one case per entry.
Working from a written list rather than intuition makes the coverage reviewable —
someone else can see what was considered and what was not.

## Checklist-based testing

Reuse a standing list across features: the categories above, plus product-specific
entries accumulated from past defects. Where a past defect exists, its case
belongs in the suite permanently — that is regression coverage earned the hard way.

## Exploratory testing

Design, execute, and evaluate at the same time while learning the feature. It
belongs in a session with a written charter — an objective and a time box — and a
record of what was covered and found, or it cannot be reviewed or repeated.

Exploratory findings that matter should be **written back as ordinary cases**.
An exploratory session is a way to discover cases, not a substitute for having them.

## Procedure

1. Run the spec-based checklist first. This technique fills gaps; it does not
   define scope.
2. Walk the categories above against the feature. For each plausible defect,
   write one case with a concrete input and an observable expected result.
3. Add any case corresponding to a past defect in this area.
4. Record what you tried and found nothing on. An explicit negative is useful to
   the next person.

## Common mistakes

**Vague cases.** "이상한 값을 넣어 본다" is not a case. Name the value.

**Letting it replace the model.** Experience-based cases feel productive because
they find defects quickly, but they leave no way to say what fraction of the
requirement is covered. The checklist provides that; keep both.

**Expected results taken from current behaviour.** When the spec is silent, the
answer is an open question, not a certification of what the code does today.
