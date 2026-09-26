---
name: x-demo-guide
description: A step-by-step guide for a person to look at and check finished changes by hand on a live stand — with an account, full URLs, real ids and the expected result at each step. Triggers on "how do I test this by hand", "write a guide to check it", "show what we got", "give me a demo".
---

# Demo guide for finished changes

A guide for a person who will sit at the browser and walk through it step by step. It both
**shows** what was done — the reader sees what changed and why — and **checks** it: each step
ends with something to observe, and from it the reader sees "matches" or "does not match".

The reader may not know the spec, the task, or how the work cycle is set up. They know the product.

## Main rule: every fact is taken from the live system at the time of writing

Every id, name, URL, count and text on the screen is checked right now — with a query to the
database, by opening the page, by reading the localization file. Not from the spec, not from the
test report, not from your memory of what was there an hour ago.

The spec describes the intent, not what is on the stand. The test report describes a moment
that has already passed: test data gets cleaned up, and the entity everything was checked on is
deleted by the time the guide is written.

**The observed failure this rule was written for.** The guide sent the reader to
`/projects/16/phases/3/tasks/46` — the id came from a snapshot taken before the cleanup. Task 46
had been soft-deleted four hours earlier. The query used to check it did not look at
`deleted_at`, and the row in the database looked alive. The reader would have got an empty page
on a step that checks nothing by itself.

From this come two habits, not one:

- **Check that entities are alive, explicitly.** Soft delete — the row is still there, the object
  is gone from the screen. `WHERE deleted_at IS NULL` in every query you use to collect data for
  the guide.
- **Open every URL you wrote in.** A response code, not a guess. A link the author never opened
  is a link they made up.

## Where each kind of fact comes from

| What | From where, and only from there |
|---|---|
| ids, names of projects, entities, files | the live database or the stand itself |
| address, port, SPA base path | the router config and the page actually opened |
| routes and URL parameters | the routes file |
| expected texts on the screen — labels, hints, empty states | the project's localization files |
| what exactly changed and how it was before | the branch diff, the code and localization of the base branch |
| what must be checked | the task's acceptance criteria |
| why the change was needed | an exact quote from the task, and if it is not there — from the project docs |
| login, password, rebuild commands | the stand config or project notes |

A hint text taken from the spec and not from the localization file will differ from the screen
on exactly the day the wording was fixed during the work. The reader will then think they found
a bug.

## What the guide is made of

**Section zero — the entry.** Stand address, login and password, and what to do if the front
end looks old (the rebuild and restart command). Then — the project and entities that the whole
check runs on, named once.

**Then one section for each visible change and for each acceptance criterion.** A section
opens with the full URL it starts from, then numbered steps follow.

**A step is one action and one observation.** "Tick only 'Payment' → 'Apply'. Three rows will
remain, and a 'Source type' column appears with the value 'Payment' _(earlier: there was no
filter, all 12 rows were shown)_." Action, arrow, expected result, and if the behavior changed
here — a short note on how it was before the changes.

**The expectation must be checkable.** A row count, an exact line of text, the number of
checkmarks, a specific badge. The reader cannot check "should work correctly" — they will
confirm it whatever they see.

**Say how it was before — as a note in brackets at the end of the step.** This is the demo
half: without it the guide says the system works, but does not say what changed.

- One format for the whole guide: `_(earlier: …)_` at the end of the step, one line. Not a
  separate section and not a "before/after" table — the reader sees the old behavior in the same
  place where they check the new one.
- The note is only on steps where the behavior changed. Navigation steps, "what should stay the
  same" checks and repeat steps about the same change have none — one per change.
- Describe the old behavior in the same observable words as the new one: "earlier: 403", "earlier:
  there was no button", "earlier: the list also had other people's documents". Not "before it
  worked incorrectly".
- No longer than one line. If it does not fit — the step checks two changes and must be split.
- The source is the base branch code and its localization (`git diff`, `git show <base>:<file>`),
  not a guess. If the new behavior is a whole new screen, a note on the first step of the section
  is enough.

**Say why this change was made — with an exact quote and a note on where it is from.** Every
step with an "earlier" note gets a separate line below it: `Reason: "…" — task MBD-666` or
`Reason: "…" — BUSRD §6.6`. The reader sees not only what changed, but who asked for it, and can
compare the requirement with the screen themselves.

- **The task first**, the ticket text in the tracker. Only if the task says nothing about this
  change — the project docs, with the section number. Where the docs live and how to check their
  wording — the section of that skill that says where the project docs live; the skill is named
  in `.env` next to this file, key `XDEMO_GUIDE_REQUIREMENTS_SKILL`
  (`grep -E '^XDEMO_GUIDE_REQUIREMENTS_SKILL=' ~/.claude/skills/x-demo-guide/.env | cut -d= -f2-`).
  The key is empty, there is no `.env`, or there is no such skill among the available ones — ask
  where the project docs are.
- **The quote is exact**: the phrase from which the need for exactly this change follows. You
  may cut with an ellipsis, you may not change words: retelling is exactly where a requirement
  changes shape.
- **The phrase is about something nearby, and the change follows from it** — mark it that way:
  `Reason (follows from): "…" — task MBD-666`. Something that follows, shown as something that
  was said, hides a decision nobody made.
- **Neither the task nor the docs talk about the change** — write that, and name where it came
  from: `Reason: not said in the task or BUSRD — only the mockup <full link>` (or "decision at
  review", "decision during the work"). This is not a hole in the guide but a finding: the
  reader sees which changes stand on no requirement.
- One line per change, on the same step as the "earlier" note. If a change comes from two
  requirements in different places — two quotes separated by ";", each with its own note.

**Negative checks — on equal terms with positive ones.** What must not appear, what must not be
available, where the list must stay empty.

**An empty result by itself proves nothing.** When a step checks that something is not shown,
the guide must say in the same step what should be shown at that moment: "the list is not empty
at this point" — otherwise the step passes on broken output, on an empty page, and on a failed
request alike.

**The last section — what should stay the same.** Shared components, nearby screens, tables
that reuse the touched code. A quick look, but a look.

## Route: as few reader actions as possible

A busy person walks through the guide, and every extra step is a chance the check is dropped
halfway. Build the route so what is checked lies along the way: pick the entities where several
acceptance criteria meet at once, order the sections the way the reader moves through the
screens anyway, and do the login, project choice and filter setup once in section zero — later
sections refer to it ("on the same screen", "from the same place").

A step that observes nothing and only moves the reader is not a step: navigation steps in a row
merge into one. Aim for 10–15 steps for the whole walk; if you get more, look for sections that
share one screen and join them.

The path gets shorter, not the coverage. An acceptance criterion is not dropped for a short
route: it is either checked along the way or keeps its own section. Same with creating data —
an entity that has to be created anyway is created once at the start and then reused by all
sections.

## Data that is not on the stand

The guide needs an entity and it does not exist — two ways out, and the first is better:

1. **Make creating it a step of the guide.** Creating a task, a member, a document checks the
   product by itself, and after the walk the reader understands where everything came from.
2. **Create the data in advance** — then name it in the guide by its names, say it was created
   on purpose, and say what to do with it afterwards.

The second way leaves junk on someone else's stand. If you choose it, say so openly, not
quietly.

## Scenarios that need a second user

The permissions check is usually the most valuable section of the guide and the most skipped:
as an admin you see everything, and access control looks like it works without ever being
checked.

Give the full path to create the second user — screen, button, role, switch positions — and
say how to log in as them without losing the first session: another browser or a private
window.

## Mobile view — its own section when the behavior differs

A hover hint does not exist on a phone. If a narrow screen has its own layout, its own rows or
a hint that opens on tap — this is a separate section with its own URL and a note on what width
to shrink the window to.

## Language and words

The guide is written in the user's working language and in product words: screens, buttons,
fields, messages. Internal ideas — layers, repositories, class names, run numbers, names of
process artifacts — the reader does not need, and they do not go into the text.

The task name and its acceptance criteria do go in: from them the reader understands what
exactly they are accepting.

## How to hand it over

The whole guide goes into the reply, not as a link to a file: people read it from the screen
and follow it right away. It ends with one line on what is left for the reader to decide — what
to finish, what to file as a separate task, what to remove after the walk.

## Done when

- Every URL in the text was opened and returned a working page; every id was checked for being
  alive, with soft delete in mind.
- Every expected text on the screen was compared with the localization file, not with the spec.
- Every acceptance criterion is covered by at least one section; a criterion that cannot be
  checked is named as not checkable, not skipped in silence.
- Every step ends with an observation from which the reader sees "matches" or "does not match".
- Every step where the behavior changed has a one-line `_(earlier: …)_` note taken from the base
  branch; the other steps have no note.
- Every such step has a "Reason" line: an exact quote with a "task" or "BUSRD §…" note, and the
  docs are used only where the task says nothing; something that follows is marked as following,
  and a change with no requirement is named as such, with where it came from.
- There is a permissions section with a second user — or it says why this task has none.
- There is a "what should stay the same" section.
- Data created for the guide is named, and it says what to do with it next.
- The login, project choice and other repeated setup are done once, not again in every section;
  the whole walk is about 10–15 steps, and each of them observes something.
