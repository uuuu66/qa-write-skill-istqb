# Compatibility, Usability and Data Quality

## When it applies

The feature runs across browsers, devices or OS versions; it displays data
migrated from elsewhere; or it exchanges files with another system. These are
quality characteristics rather than functions, and specs describe them least.

Keep these cases few and targeted. Enumerating a full device matrix produces
dozens of cases that all pass and find nothing.

## Compatibility

**Only test the variation the feature is actually sensitive to.** A screen built
from the standard component library does not need a per-browser case; one using a
file download, a date picker, clipboard access, or a fixed layout does.

Worth a case when present:

- **clipboard and paste** — pasting several cells from Excel. Line breaks, tabs
  and invisible characters arrive differently per browser and per OS.
- **file download and upload** — filename encoding with Korean characters is the
  classic failure
- **date and number formatting** where the OS locale differs from the app's
- **narrow viewport** if the screen has a table. A table at 1024px is a different
  layout problem than at 1920px.

## Data quality and migration

When existing data is displayed, the defects come from data that predates the
current rules.

- a required field that is empty in old records
- a referenced record that no longer exists — **the highest-yield case in this
  category**
- a value outside the current enum, stored before the enum existed
- text longer than the current maximum length
- duplicates that the current uniqueness rule would reject
- an encoding difference in imported text

Each of these becomes a case with the same shape: the screen must render without
crashing and must show a defined fallback rather than a blank or an error.

```
기대 결과  연결된 그룹이 삭제된 회원의 상세 화면이 오류 없이 열리고,
           그룹 항목에 "-"가 표시된다
```

## File exchange

- an empty file, a file with only a header row, and a file at the size limit
- a required column missing, and columns in a different order
- a row whose type is wrong — text where a number belongs
- a partially valid file: 100 rows, 3 invalid. Are all 100 rejected, or the 97
  accepted? **The spec must say**, and usually does not — record the question.

## Usability, at case level

Full usability testing needs users. What belongs in a case suite:

- every action's result is visible: a spinner during a long operation, a message
  after a save
- an error message says what to do next, not only that something failed
- the keyboard path works: tab order, Enter to submit, Esc to close
- an empty state explains what to do rather than showing a blank area

## Procedure

1. List only the variations the feature is genuinely sensitive to. Justify each.
2. For every displayed data field, write the case where the underlying data is
   missing or dangling.
3. For every file exchange, write the empty, malformed, and partially valid cases.
4. Add the visible-feedback and empty-state cases.
5. Where the handling of partial or legacy data is undefined, record an open
   question rather than assuming.

## Common mistakes

**A full browser matrix by default.** Many cases, no findings, and the real
compatibility risk — the clipboard, the download — gets no attention.

**Assuming existing data satisfies current rules.** It does not. That assumption
is the most common cause of a crash on a screen that worked in testing.

**Writing "화면이 깨지지 않는다" as an expected result.** Name the fallback value,
the message, or the layout property being observed.
