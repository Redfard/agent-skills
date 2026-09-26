---
name: x-demo-run
description: Walk the x-demo-guide steps in the browser and get an HTML report with a screenshot and a status for each step.
disable-model-invocation: true
---

# Demo run with screenshots

The same demo guide that `x-demo-guide` writes, but the agent walks the steps and the person gets
a report: for each step a screenshot with a frame on what is being checked, the old code's
screenshot next to it, the mockup, and under them the step text and a status. The person scrolls
the report instead of sitting at the browser.

This skill is a wrapper. **What to check, on which data and what to expect is decided by
`x-demo-guide`**, with all its rules about live data and full URLs. This skill only says how to
walk the steps and how to show the result.

## Argument `--no-before`

By default the run goes twice: first on the code before the task (the "Before" run, section 7),
then on the task's code (the "After" run). `--no-before` runs only "After".

## 1. Steps come from x-demo-guide, as they are

If the conversation already holds the `x-demo-guide` guide for this task, use it. If not, call
`x-demo-guide` as a real skill call first and wait for the whole guide.

Every step of the guide is one card of the report, with the same number, and the card's text is
the guide's text: the report reader gets what the guide reader would get, plus pictures. Copied
word for word: the action, the expected result, the "earlier" note (how it worked before the
task, in brackets at the end of the step), the "Reason" line with its quote and source mark, the
note about a mockup mismatch, the section titles, the logins, the data, what was not checked and
what is left. The agent writes only two fields of its own: `look_at` (what to look at in the
screenshot) and `actual` (what the screen shows, for ✗/⚠).

`actual` is a separate field, not an edit of `expected`: an expectation changed to fit the
screen turns a ✗ into a false ✓.

## 2. Report language

All text the agent puts into the report is in one language: every text value in the JSON,
including the agent's own fields and the screenshot captions. The language is set in `.env`
next to this file, key `XDEMO_RUN_REPORT_LANG`:

```bash
XDEMO_RUN_REPORT_LANG=$(grep -E '^XDEMO_RUN_REPORT_LANG=' ~/.claude/skills/x-demo-run/.env | cut -d= -f2-)
```

Empty or no key — the language of the conversation.

A guide written in another language is translated into the report language: sentence by
sentence, with the same facts, numbers and order, nothing added and nothing dropped. Screen texts
in quotes are copied as they are, and so are URLs, ids and emails.

The fixed labels in the HTML (step, status, box titles) come from `build-report.py` and are
always in English, whatever the report language.

## 3. Where the report goes

The folder is set in `.env` next to this file, key `XDEMO_RUN_DIR`:

```bash
XDEMO_RUN_DIR=$(grep -E '^XDEMO_RUN_DIR=' ~/.claude/skills/x-demo-run/.env | cut -d= -f2-)
```

No `.env` → `cp ~/.claude/skills/x-demo-run/.env.example ~/.claude/skills/x-demo-run/.env`, and
say so in the answer.

- A relative path is counted from the working-tree root (`git rev-parse --show-toplevel`); an
  absolute path is used as it is.
- Inside it — the task folder. The task key comes from the branch name (`MBD-666`). A folder
  `<KEY>-*` exists → use it; none → create `<KEY>`. No key in the branch → ask for the key in
  one line.
- File name `demo-run.html`; already there → `demo-run-2.html`, `-3` and so on. An earlier run is
  never overwritten: two reports get compared.
- Working screenshots and the run JSON go to the session scratchpad, not to the task folder:
  they reach the report inside the HTML.

## 4. Browser

- Start Chrome per `x-starting-chrome-mcp` and work only in your own tabs, by `pageId`.
- **Each user of the guide gets an isolated context** (`new_page` with `isolatedContext` named
  after the role). Sessions do not affect each other, and nobody has to log out.
- **The interface is in the report language.** Find in the app's code where it takes the
  language from (a `localStorage` key, a profile setting, a switch in the UI), set the report
  language and reload. Check: the first screen shows a heading in that language. Without this,
  the screenshots do not match the step texts.
- Screens between login and the app (an offer to install the app, a welcome screen) are passed
  on the way and do not go into the report.
- Window width — desktop (1440 px or more); for a step about the mobile view — the width the
  step names.

## 5. One step

1. **Do the step's action** — click, type, pick a filter, open the address.
2. **Frame on what is checked.** Before the screenshot, outline the element that the expected
   result talks about: `evaluate_script` sets `outline: 3px solid #e53935; outline-offset: 2px`
   on the element (a table row, a button, a window). Several elements — a frame on each. Remove
   the frames before the next step.
3. **Hints and dropdowns** are captured open: hover or open them, and take the screenshot while
   they are visible.
4. **Screenshot** — `take_screenshot` with `filePath` in the scratchpad, not inline.
5. **Check by the page text, not by the picture.** `take_snapshot` or `evaluate_script`: number
   of rows, exact text, `disabled` on a button. Status:
   - `pass` — everything in the expected result matched;
   - `fail` — at least one thing did not match; `actual` says what the screen shows;
   - `blocked` — the step cannot be done (the page did not open, an earlier step broke the
     state); `actual` says why.
6. **`look_at`** — one line for the screenshot: which element is in the frame and what matters
   in it.

A failed step goes into the report as `fail`, and the route goes on. No code changes during the
run: the run shows how the system works right now.

## 6. Steps that change data

Create, edit and delete are done for real. Such a step gets **two screenshots, before and after
the change**, with the frame on the same place: the row that appeared, disappeared or changed its
value. Each caption starts with "before the change" or "after the change" (in the report
language) and names what changed. A toast message, if one appears, is in the "after" shot too.

## 7. "Before" — a run on the code before the task

Skipped with `--no-before`. Goal: every step with an "earlier" note gets a pair of screenshots,
"Before" and "After", with the frame on the same place. Steps without the note did not change and
get no "Before" shot.

**When switching is allowed.** The "Before" run is skipped — and the answer says why — when:

- the working tree has uncommitted changes outside `.forge/`;
- the diff `<base>..HEAD` touches migrations or dependency lock files (`package-lock.json`,
  `composer.lock` and the like): the old code then does not match the database or the installed
  packages.

**Base** — `base` from the task's `state.md` when the task runs the `forge` cycle; otherwise
`git merge-base HEAD <parent branch>`.

**Order.**

1. First line of the answer, in the report language: screenshots are being taken — do not work
   on the stand until the run ends.
2. Remember the current branch. `git switch --detach <base>`, rebuild the stand with the command
   from the guide's entry section.
3. Walk the steps that have an "earlier" note and take the "Before" shots. **This run changes no
   data:** in a step that creates or deletes, go as far as the confirm window, capture it, and
   press cancel. Otherwise the "After" run will not find what it has to delete or create.
4. `git switch <branch>`, rebuild the stand. Switch back also when the "Before" run failed in the
   middle: at the end the stand always stands on the task branch.
5. Walk all the steps and take the "After" shots — sections 5 and 6.

**The element did not exist before** (a filter, a window, a button) — the "Before" shot has no
frame, and its caption says the element was not there. A "Before" screen that differs from the
guide's "earlier" note is a finding too: it goes into the `before_actual` field; it does not
change the step's status, and the answer names it separately.

## 8. Mockup next to it

A step with a Figma link gets the mockup frame (`get_screenshot` by the `node-id` from the link,
downloaded to the scratchpad) next to the screenshot. A mockup mismatch named in the step goes
into the mockup note.

Figma is not authorized, or the frame cannot be captured — keep the link on the step and say so
in the answer.

## 9. Run description and building the report

Put together the JSON and pass it to the script:

```bash
python3 ~/.claude/skills/x-demo-run/build-report.py <scratchpad>/run.json <task folder>/demo-run.html
```

```json
{
  "title": "Demo: MBD-666 — the \"Documents\" screen",
  "lang": "en",
  "task": "task name and its acceptance criteria in one line",
  "stand": "https://…", "branch": "branch @ short hash", "date": "25.09.2026",
  "before_note": "Before — commit <base> (before the task), After — commit <HEAD>; or why \"Before\" was skipped",
  "password_note": "Password for everyone — password",
  "logins": [{"who": "Member 1", "email": "…", "role": "member"}],
  "data": ["Project \"…\" (id 393)", "…"],
  "sections": [{
    "title": "1. Member 1 on the \"Documents\" screen",
    "who": "Member 1", "url": "https://…",
    "steps": [{
      "n": 1, "status": "pass",
      "action": "…", "expected": "word for word from the guide",
      "look_at": "…", "before": "the \"earlier\" note text, if any",
      "basis": [{"quote": "word for word", "source": "task MBD-666 | BUSRD §6.6", "inferred": false},
                {"missing": "not in the task or BUSRD — only the mockup", "url": "https://www.figma.com/…"}],
      "actual": "only for fail/blocked",
      "shots": [{"path": "/…/s1.png", "caption": "…"}],
      "before_shots": [{"path": "/…/s1-before.png", "caption": "…"}],
      "before_actual": "only when \"Before\" differs from the \"earlier\" note",
      "mockup": {"path": "/…/m1.png", "url": "https://www.figma.com/…", "note": "…"}
    }]
  }],
  "not_checked": ["what the guide named as not checkable"],
  "leftover": ["data left on the stand"]
}
```

Text values are in the report language (section 2); `lang` is its code (`ru`, `en`).

## 10. Answer in the console

- The full path to the report.
- Counts: ✓ / ✗ / ⚠.
- Each ✗ and ⚠ in one line: step number, what was expected, what the screen shows.
- The "Before" run: done, or why it was skipped; each "Before" screen that differs from its
  "earlier" note.
- What is left on the stand after the run and what to do with it — as in `x-demo-guide`.

## Done when

- The steps come from the `x-demo-guide` guide; every guide step has a card with the same
  number, and the expected result is word for word (or a sentence-by-sentence translation into
  the report language).
- Every text value in the report is in the report language.
- Every card has a screenshot with a frame on what is checked; a step that changes data has a
  before/after pair.
- Every step's status is set by the page text; every ✗ and ⚠ has `actual` filled in.
- The screenshots were taken with the interface in the report language.
- Without `--no-before`: every step with an "earlier" note has a "Before" / "After" pair, or the
  answer says why the "Before" run was skipped; the "Before" run changed no data; at the end the
  stand stands on the task branch and is rebuilt.
- A step with a mockup link has the mockup frame next to it, or the answer says why not.
- The report is in the task folder under `XDEMO_RUN_DIR`, and no earlier report was overwritten.
- The answer names the path, the counts and every ✗/⚠.
