---
name: x-project-idiom
description: Scouts the project's style — finds similar places in the live code, walks through several cases and gives a "how this is done here" summary in the x-tech-simplify-answer form. Read-only, does not change code.
disable-model-invocation: true
---

# How it is done here (project idiom)

Based on the current context, finds places in the project where something similar is already done,
walks through several real cases and gives a summary: how this project does it. The skill
**only reads and reports** — the result is a summary, not a code change. No Edit, no Write.

Answer in the user's language; the examples below are only examples.

The point: before writing new code (or to answer "how is this done here?"), check the plan against
how the project already solves such tasks — names, where the logic lives, query patterns, error
handling, tests, config. Guesses about style are replaced by a sample of live examples.

## Steps

### 1. Define the goal of the scouting
Name in one line the specific construct/situation whose style we are looking for: for example "a
controller action in api v2", "a service with business logic", "an aggregating query to send_log in
ClickHouse", "a v2 React page with a table", "a migration that adds a column", "a Gearman worker",
"a cron job".

Done when the goal is worded so you can search by it. If the goal is ambiguous from the context
(both this and that fit) — ask **one** clarifying question and stop until the answer.

### 2. Collect real cases
Find existing places in the project that solve the same task (Grep/Glob; if they are widely spread —
an Explore subagent). Read each one enough to understand the pattern, not just the matching line.

Done when **at least 5 real occurrences** are analysed (target 5–8). Each is recorded as
`path:line` **with the real names of the entities** that appear in it (class, method, endpoint,
query parameter, response field, table, column, worker/cron name). If the project really has fewer
than 5 such places — analyse all there are and state clearly how many were found.

### 3. Derive the idiom from the cases
Go across the collected cases and pull out what they share: how things are named, where the logic
lives (thin controller vs service/component), how errors/empty cases are handled, what style the
queries are written in, how things are configured, whether there are tests nearby and of what kind.

Done when these are named: (a) the canonical/dominant approach, (b) deviations from it, if any were
found, (c) any case from step 2 that gave nothing on a specific aspect — named explicitly, not
silently dropped.

### 4. Give the summary via x-tech-simplify-answer
Shape the result **in the form of the x-tech-simplify-answer skill** (call it): direct answer first —
how it is done here and which pattern to follow; low cognitive load; but with the real technical
names (paths, classes, methods, endpoints, parameters, columns), so the programmer reading it sees
the under-the-hood part too and can get to the place on their own.

Done when the summary contains: the canonical pattern in one or two sentences, the list of analysed
cases as `path:line`, and — if it applies to the user's task — a short recommendation on which of
the found variants to follow here.
