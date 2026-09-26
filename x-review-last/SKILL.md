---
name: x-review-last
description: Re-check the work just done with fresh subagents and merge their findings into one list; with flag a the findings go straight to x-check-and-fix, if it is installed. Called when asked to re-check or review what was done in this session — "review what you just did".
argument-hint: "[N] [a]"
---

# Review last

You need to re-check the work you just did. To do this, create subagents (with no name), give each one context on what you did and any data that helps it find its way around faster, and ask it to look for flaws of any kind.

Wait for the reports and show the findings. Write them in the language of the conversation.

## Number of reviewers

The number in the call is how many subagents check the work. No number — **2**.

Spawn them all at once, in one message. Each one searches on its own and changes nothing.

## Merging the reports

Wait for all of them and merge the findings into one list:

- the same flaw from several reviewers — one item; note that they found it independently, and take the wording with the more concrete reasoning;
- a finding from only one reviewer stays in the list: it is a different angle, not a disagreement;
- do not drop findings that directly contradict each other — show both and name the contradiction.

## Flag a

If the call had flag `a`, then right after the report, in this same session, call the skill `x-check-and-fix` and pass it the merged list of findings. If that skill is not among the available ones, say so in one line and stop at the report.
