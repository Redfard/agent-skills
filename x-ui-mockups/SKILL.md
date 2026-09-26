---
name: x-ui-mockups
description: Mockups of a UI feature right inside the project's live interface on demo data — several layout variants, each turned on by a URL parameter, with screenshots and steps to click through them yourself. Triggers on "make mockups", "show options for how this will look in the interface".
---

# Mockups in the live interface

The person needs to see how a feature fits into the product and pick a layout. ASCII diagrams
and descriptions in words do not work for this: you cannot understand them quickly. So each variant
is built in code in the real screen, on demo data, and shown with screenshots and a live link.
After the choice, the variants stay in the code: the person clicks through them, and the chosen
one becomes the base of the implementation.

Answer in the user's language; the examples below are only examples.

## 1. Variants

Read the component the feature goes into and find the flow it will live in: where the user comes
from, what is already on the screen, how the action ends.

If the person did not name the variants, come up with 3–5 that **differ in substance**: where the
entry point is, how the mode switches, how much space it takes. Colour and spacing do not count as
differences. Describe them briefly in the answer (what it is, plus, minus, which one you recommend)
and build all of them right away: the choice is made from pictures, not descriptions. If the person
narrowed the list, build only that list.

An iteration on one variant ("tabs under tabs look bad, what else is there?") gives sub-variants
of the same one: `b2`, `b3`, … The old `b` stays for comparison.

## 2. Mock code

- **Off by default.** Turned on by the parameter `?<feature>mock=<variant>`. Without the parameter
  the screen works as before, so the mock can safely sit in the working tree while the choice is made.
- **Edge states** (no data, error, "empty") are turned on by extra parameters
  (`&<feature>mock_empty=1`), not by separate variants.
- **Isolated in two new files next to the screen:** a data module (`.ts`: demo data, reading the
  parameter, a fake call with a 1–1.5 s delay so loading is visible) and a mock components module
  (`.tsx`). Data and components are split because the fast refresh rule
  (`react-refresh/only-export-components`) rejects a file that exports both. Existing components
  get only conditional inserts `mock.variant === "…"`.
- **Ends in the real flow.** Only what does not exist yet is fake (an endpoint, a generation). The
  result goes into the UI that already exists (a list, a form, saving), and the report says clearly
  that it is saved for real.
- **Demo data is realistic and passes the project's validation:** required placeholders, length,
  no duplicates. Otherwise the real save fails on the first click.
- **The project's frontend gates** (types, linter on the touched files) pass with no new errors.

## 3. Deploy to the test server

Build the frontend the way the test server serves it: take the command and its quirks from CLAUDE.md and
the project memory. Then **check that the built bundle contains the mock parameter name** (grep over
the assets). If it is not there, the build went to the wrong place, and the screenshots will capture
the old interface.

## 4. Screenshots

Browser — via `x-starting-chrome-mcp`. Folder `.forge/stage/<feature>-mockups/` in the project
root, files `<variant>-<n>-<state>.png`.

For each variant: the initial state, the state after the main action (if it differs between
variants) and each edge state. Pick a window height so the dialog or panel fits fully.

**Open each screenshot and check it against what it should show.** Check the first screenshot of
the first variant before taking the rest: if the mock did not turn on, you see it right away, not
after a dozen files.

Tricks for repeated actions:
- Pass the function that opens the needed screen to `navigate_page` via `initScript` and call it
  with one line of `evaluate_script` on each variant.
- Radix tabs switch from a script only with the chain `pointerdown` → `mousedown` → `click`.
  A Radix Select dropdown opens only with a real MCP click on the `uid` from the snapshot.

## 5. Report

- **Steps "how to see it yourself":** the test server address the person will open from their own
  machine (from the project memory, not `localhost`), logins, the full link to each variant, the
  click path to the screen, what to press and what should appear, the edge state parameters.
- **What is real and what is demo:** which actions really write to the database, which data is made up.
- **List of screenshots** with paths.
- **Changed files**, gate results, build status. Commit — only on request.

Done when every variant has a link and screenshots that you opened and checked, and the steps
contain no step without a full URL or a button name.
