---
name: x-simplify-answer
description: Use when the user invokes /x-simplify-answer, or asks you to explain something more simply, in plain language, or "what does this mean for the user" — typically right after an answer that was too dense, too technical, jargon-heavy, or buried its point. The reader needs the takeaway restated with low cognitive load — direct answer first, grounded in the app's UI (screens, buttons, what the user sees and does), with breadcrumbs to locate any screen. Keywords — simplify, plain language, explain simply, in plain terms, too technical, "didn't get it", "simpler", "explain more clearly", cognitive load, ELI5.
---

# Simplify Answer

## Overview

The reader should not have to decode your answer to find the point. Re-express the content the way they actually experience the product — **what they see on screen and what they do** — lead with a direct answer to the exact question asked, and cut the jargon.

**Core principle:** explain through the user's lived experience of the app, not the machinery behind it. Same facts, near-zero decoding effort.

This is *clarity, not dumbing down* — keep every fact that changes what the reader decides or does; drop only the plumbing they can't act on.

Write the answer in the language of the conversation.

## Argument: `session`

By default this skill acts **once** — it re-expresses the last answer and then behavior returns to normal.

If the skill is invoked with the argument `session` (e.g. `/x-simplify-answer session`), then in addition to simplifying the current answer, **adopt this simplified style for all subsequent responses for the rest of the session**, until the user says to stop (e.g. "enough", "go back to normal", "stop simplifying") or explicitly asks for a detailed/technical answer.

When invoked with `session`:
- Confirm in one short line that sticky mode is on (e.g. "OK, from now on I answer in the simple style — say 'go back to normal' to turn it off.").
- Apply the shape rules below to every following answer, not just this one.

Caveat to keep in mind (not something to announce every turn): this stickiness lives in the conversation context, so in a very long session or after a context summary it may fade — if the user notices the style slipping, they can re-invoke `/x-simplify-answer session`.

## When to use

- The user invokes `/x-simplify-answer`.
- They say "didn't get it", "simpler", "explain more clearly", "what does this mean for the user", "too technical", "ELI5".
- A previous answer was dense, jargon-heavy, table/diff-heavy, or buried its conclusion.
- You're about to explain product behavior and want it to land on the first read.

## The shape of a simplified answer

Build the answer in this order. This is a recipe, not a menu.

1. **Answer first, in one line.** The very first sentence answers the exact question asked — yes/no plus the single thing that matters. No "let me look first", no setup, no restating the question.
2. **Ground every effect in the UI.** Describe what the *user sees and does*: screens, buttons, fields, dropdowns, lists, error messages. Not functions, DB columns, flags, layers, or patterns.
3. **Locate each screen with breadcrumbs.** The first time you mention a screen, give the click-path so the reader knows instantly which one and how they'd reach it: `Admin (Nova) → Document types → "Create"`.
4. **Show one concrete scenario.** Walk a single realistic "user does X → sees Y" story in numbered steps. One concrete path beats any abstract description.
5. **Spend almost no jargon.** If a technical word is truly unavoidable, gloss it in plain words in the same breath — "in the trash (deleted, but not fully erased)".
6. **Keep it short and scannable.** The point must be findable in ~5 seconds. Drop tables, code, and diffs unless a *tiny* before/after scenario genuinely lowers effort.

## Translate machinery → experience

When you catch yourself writing the left column, say the right column instead.

| Instead of (machinery) | Say (what the user experiences) |
|---|---|
| soft delete / `withTrashed` / "in the trash" as a mechanism | "the type is gone from the list, but not erased — it is in the trash" |
| validation returns "name taken" | "when you create it, you get the error 'this name already exists'" |
| repository / Action / Application layer / DTO | *don't mention* — describe the visible result |
| throws 500 / exception / stack trace | "the page crashes with an error" |
| migration / partial index / `LOWER(name)` | *don't mention unless explicitly asked* |
| endpoint returns only non-deleted rows | "deleted ones do not show in the dropdown" |

Rule of thumb: if the reader can't click it, see it, or decide something from it, it probably doesn't belong in a simplified answer.

## Example — before → after

**Question:** "With the current approach, will anything look wrong in the UI?"

**Before (too much):**
> Short answer: no more crashes and 500s... Where the UI behaves fine ✅ — the dropdown (read-only API) returns only live types (getList excludes deleted ones)... Where the UX is confusing ⚠️ — validation (now withTrashed) finds the soft-deleted record... forceDelete is blocked by the policy... [several screens later — the point].

Problems: leads with caveats, names internals (`getList`, `withTrashed`, `forceDelete`, "the policy"), the actual problem is buried.

**After (target):**
> **Yes — one confusing moment in the admin panel. Everything else is fine.**
>
> Where: `Admin (Nova) → Document types`.
> 1. You delete the type "Contract" → it is gone from the list.
> 2. You try to create a new "Contract" → error "this name is already taken".
>
> The odd part: "Contract" is not in the list, but you cannot create it — as if an invisible record holds the name. In fact the old "Contract" is in the trash and just hidden. You cannot free the name by deleting — you can only go to the trash and restore it.
>
> Everything else is fine: deleted types do not show in the dropdown on the site, old documents move to "Undefined", and a new deploy does not bring a deleted type back.

Same facts as "before", but: the answer is line one, every effect is a screen/click/message, the screen has a breadcrumb, and there's one concrete walk-through.

## Common mistakes

- **Burying the answer** under "let me look first" / setup / restating the question. Answer on line one.
- **Leading with the mechanism** ("added withTrashed to the repository") instead of the effect the user sees.
- **Naming a screen without a breadcrumb** — the reader then has to figure out which screen you mean.
- **Keeping jargon "because it's precise."** Precision the reader can't parse is just noise; gloss it or drop it.
- **Re-introducing load** with big tables, code blocks, or diffs. A small numbered scenario is the heaviest tool you usually need.
- **Dumbing down instead of simplifying** — don't drop facts that change the reader's decision; drop only the plumbing.

## Not always literally the UI

The deepest rule is *speak in the reader's concrete terms with low decoding cost.* For product behavior that means UI screens and actions (the usual case). If the question is genuinely about code internals with no UI surface, still lead with the answer, still kill jargon, still use one concrete example — just in the simplest concrete terms that fit, not forced screens.
