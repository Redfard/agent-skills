---
name: x-writing-skills
description: House rules for skill files — invocation and description, completion criteria, prohibitions, pruning, and when a change earns a subagent test. Use when writing a new skill or editing an existing one.
---

# Writing skills

A skill exists to make the agent take the **same process** every run. Every rule below serves
that, and nothing here is style.

## Invocation and description

A description sits in the context window every turn, whether the skill fires or not. It is
invocation machinery, not documentation.

- **A skill only a human ever types is user-invoked.** Set `disable-model-invocation: true`
  and write the description for a person: one line, no trigger phrasing. It then costs
  nothing per turn, and the cost moves to the human, who becomes the index that has to
  remember it exists.
- **A skill the agent must reach on its own stays model-invoked**, and earns its per-turn cost
  with a tight description: one trigger per branch. Two phrasings of the same trigger are one
  branch written twice — keep the clearer one.
- **Prose telling the model not to fire the skill is the expensive way to write
  `disable-model-invocation: true`.** Use the flag; the description then has nothing to
  defend against.

## Completion criteria

Every unit of work in a skill ends on a condition the agent can check against. Two properties,
independent of each other:

- **Checkable** — can the agent tell done from not-done? A vague bound lets attention slide to
  the next thing while the current one is half-finished.
- **Demanding** — how much it requires. "Every reader of the old value accounted for" produces
  different work than "consider the impact."

The demand axis binds flat reference, not only ordered steps: a checklist that says *account
for every row, and name the rows that yielded nothing* comes back with coverage; one that says
*among other things* comes back with whatever the agent happened to notice. Most skills here
are reference rather than steps, which makes this the lever that actually moves them.

## Prohibitions

Naming a banned behaviour puts it in the context window and makes it more available, not less
— *don't think of an elephant* is all elephant, and the ban half-reads as an instruction.
State the target behaviour instead, so the banned one is never spoken.

One real exception: **a rationalization you have actually watched an agent produce.** An
argument cannot be pre-empted without stating it. There, name the excuse, answer it, and pair
it with what to do instead.

The test between the two: is this steering style, or closing a hole something fell through?
Style goes positive; an observed hole gets named.

## Pruning

- **One meaning, one place.** Two copies drift apart, and the copy quietly carries more weight
  than the meaning deserves.
- **A line that changes nothing is worth deleting even when it reads well.** The test: does the
  agent behave differently with the line than without it? This measures the model's default,
  not the reader's taste — so a disagreement about a line is settled by running the skill, not
  by discussing it.
- **A sentence saying why a rule exists is not such a line.** It is what holds the rule when
  following it is inconvenient. Keep it.
- **Prune what you are already editing.** A sweep through working skills spends real risk for
  a gain nobody can measure.

## When a change earns a subagent test

**Subagents run on the user's explicit go-ahead, every time.** The skill judges when a test is
worth proposing; the user decides whether it runs.

Default: no test. Most edits are wording, structure, or reference material, and their effect
is visible on the page — proposing a run for those trains the user to decline on reflex.

Three cases are worth proposing:

1. **A fix for something that went wrong in a real run** — recommend running it. The failed
   run is already the baseline, so the test is one replay of a scenario that exists, against
   the edited skill. Cheapest of the three and the only one with a known answer to check.
2. **A rule that has to hold under pressure** — one the agent would skip or argue around by
   default. Worth proposing: a rule nobody has watched hold is a hope.
3. **A new skill** — offer it, and say what it would cost. This is the most speculative of the
   three: there is no observed failure yet, so the scenarios are invented.

**Ask once, when the change is complete, and ask it as a recommendation.** Name what the test
would check, roughly what it costs in subagent runs, and which way you lean. "Should I test
this?" reads as a detour and gets declined; "this rule is the kind an agent argues around —
one baseline plus one pressure run, two subagent calls, I'd run it" gets a decision.

Where a skill for testing skills with subagents is installed — `superpowers:writing-skills`
carries one — follow its procedure once the go-ahead lands, rather than improvising: the
baseline without the skill first, then pressure scenarios, then close whatever holes the
scenarios opened.
