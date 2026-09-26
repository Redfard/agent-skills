---
name: x-explanation
description: Use when the user asks for a clear, simple explanation of how something works that still keeps the technical details — real code and config shown, explained step by step on one example. The reader knows code but wants clarity, not a wall of jargon.
---

# Explanation

## Core idea

The reader understands code but does not want to decode a wall of pseudocode, layers and formulas. The job is to explain the **mechanism** so it lands on the first read: the real details (config, code, schema, data) stay, but they come as a **plain story, step by step, on one example that runs through the whole answer**, not as a symbolic derivation.

**Main rule:** do not throw technical details away — *explain* them. This is not "simplify down to the product" (that is `x-simplify-answer`); it is "make the internals clear to a technical person".

How it differs from the neighbouring skills:
- `x-simplify-answer` — no code, told through screens and user actions. The reader is not always technical.
- `x-nontech-answer` — the reader is non-technical, no code and no terms at all.
- **`x-explanation`** — the reader is technical, code and config are **shown**, but explained in simple words and on an example.

Answer in the user's language; the examples below are only examples.

## The `session` argument

By default the skill fires **once** — it re-explains the last answer, then behaviour goes back to normal.

If called with the `session` argument (`/x-explanation session`), **keep this style in every following answer until the end of the session**, until the user says to stop ("enough", "go back to normal", "stop") or clearly asks for another format.

With `session`:
- Confirm in one line that the mode is on ("OK, I'll keep explaining in this style — say 'go back to normal' to turn it off.").
- Apply the form rules below to every following answer.

Note (do not repeat it every turn): the stickiness lives in the context, and in a very long session it can fade — then the user just calls `/x-explanation session` again.

## Answer form

Build it in this order. This is a recipe, not a menu.

1. **The idea in one sentence.** The first sentence is the whole mental model: how the thing works, in one sentence. No "let me look first", no restating the question.
2. **Name the details in simple words and show the real artifact.** Do not hide the code/config/schema — show it. But next to it explain in one line what it is and why ("this is the table 'role → what is allowed by default'").
3. **One example with concrete data that runs through everything.** Set up real characters and data (Peter is a member, task #55, he was given edit access) and **carry them through the whole explanation**. Do not start a new example for each point.
4. **Trace the mechanism in numbered steps, in prose.** "The action needs the 'edit' level. We look at the config row `member → task` → it says `view`. We look at personal grants in the database → task #55 has `edit`. We take the maximum → `edit`. That is enough → access allowed." Exactly like this, NOT `effective = max(roleBase(...), grant(...))`.
5. **Show a contrast case.** Right after "allowed", give "and here it is denied" on the same data — so the fork and the boundary become visible.
6. **End with the consequence.** One section "and here is what matters / here is where it hurts": what this leads to, where the catch is, what to change. This is why the whole thing was explained.

## Turn derivation → story

When you catch yourself writing the left column, say the right one.

| Instead of (derivation) | Say (story) |
|---|---|
| `effective = max(roleBase, grant, ownership, inherited)` | "we take the highest level of four: role, personal grant, authorship, inheritance" |
| `roleBase(role, entity, dim)` with no explanation | "we look at the config row `member → task` → it says `view`" |
| a wall of "layer 2 / layer 3 / short circuit / resolver" | name it once in simple words, show the value, then refer to it by name |
| a symbolic formula, arrows `→`, `≤` in the text | a sentence: "it needs 'edit', but there is only 'view' → no button" |
| abstract `user` / `entity` / `subject` | concrete Peter / task #55 / stage "Finishing" |
| "the config takes part in computing the level" | "the config is read in exactly one step — this one: …" (show where) |

Rule: details stay, but each one is **tied to a step of the example or to a line of the code shown**, not left hanging in the abstract.

## Example — before → after

**Question:** "Explain clearly, with technical details, how the permission check works."

**Before (too much):**
> effectiveLevel(profile, S, dim) = max(roleBase(profile, type(S), dim), grant(profile, S, dim), ownership(profile, S), inherited(parent(S), dim)). Layer 2 reads the role_base_levels config, layer 3 reads the access_entity_grant table, for viewer min(level, view) is applied…

Problems: a symbolic formula in the first line, layers with no anchor, the reader has to decode it.

**After (the goal):**
> **Every action needs a level, and the system takes the person's highest level from four sources and compares.** One of the sources is the role, and here it is in the config:
>
> ```php
> 'member' => ['content' => ['task' => 'view'], 'budget' => ['phase' => 'none']],
> ```
> It reads: "a member can see tasks by default, but not money".
>
> Peter is a member. The database records that task #55 was opened to him personally for editing.
>
> Peter deletes task #55:
> 1. Deleting needs "edit".
> 2. For the role we look at the config, row `member → task` → "view".
> 3. Personal grants in the database → #55 has "edit".
> 4. Take the maximum → "edit". That is enough → **it is deleted.**
>
> The same button on task #56, which was not opened to him: by role "view", no grant → maximum "view" → **no button.**
>
> The main point is visible: **the config is read in exactly step 2** — to turn the role into a level. Everything else does not come from the config.

The same facts and the same technical content, but: the model is in the first line, the real config is shown and explained, the mechanism is prose in steps, there is a contrast denial, and at the end — where exactly the config takes part.

## Common mistakes

- **Hiding code because you think "simple" = "no code".** That is `x-simplify-answer`. Here code/config is **shown** — just explained.
- **Putting a formula or pseudocode before the idea.** First the mental model in words, then (if needed) the artifact.
- **A wall of layer/resolver jargon** with no link to a step or a value.
- **A new example for each point.** One example, carried through everything.
- **Abstract `user`/`entity`.** Concrete names and numbers.
- **Forgetting the contrast case.** Without "and here it is denied", the boundary of the rule is not visible.
- **Stopping without the consequence.** The last section is why all this matters and where the catch is.
