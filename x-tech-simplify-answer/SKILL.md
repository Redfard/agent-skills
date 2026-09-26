---
name: x-tech-simplify-answer
description: Retells the last answer in the x-simplify-answer form, but with the real names of things — endpoints, query parameters, response fields — so a programmer reading it also sees the under-the-hood part. Triggers on requests like "the same, but keep the technical terms".
---

# Simplify Answer — Tech

## Core idea

This is a **delta on top of `x-simplify-answer`**, not a style of its own.

As the first action, load `x-simplify-answer` via Skill and build the answer in its form: the answer
in the first line, effects through screens and actions, a click-path for each screen, one scenario
running through it in numbered steps, short. The form rules live there and are not repeated here.

Answer in the user's language; the examples below are only examples.

Below is only what this skill adds.

## What we add

The reader is a programmer. They need the same low cost of decoding, but they want to **go and
look**, and a descriptive phrase instead of a name takes that away: "an internal number nobody sees"
makes them first guess which field is meant.

Three additions, each tied to a place in the simple answer that is already written:

1. **The name next to the thing, once, at first mention, with an explanation in the same sentence.**
   "The list is loaded by `projectsApi.getEmployees()` — that is `GET /api/org-structure/profiles`
   with no parameters at all". After that, plain words; the name is not repeated.
2. **One sentence about the mechanism where it changes the picture.** Not "sorting works", but "the
   lift is done in the DB — as the leading term of `ORDER BY`, before the limit, not by sorting a page
   that was already fetched". Such a sentence goes where the conclusion depends on the mechanics, and
   nowhere else.
3. **What it was checked with or how it will show.** "Grep over `resources/js` finds no occurrences".
   "No error, no 422 — 200 and the usual alphabetical order". The reader sees not only the conclusion
   but also what it stands on.

## Which thing deserves a name

A name goes to what the reader can **open, call or find by search**: an endpoint, a query
parameter, a response field, a frontend function, a column, a query condition, a task number, an
HTTP code.

Architectural mechanics — layers, patterns, base classes, DTOs, directory paths — are not on this
list: you cannot call them, and no decision of the reader depends on them. Naming them brings back
exactly the density this skill removes.

Observed slip: on a request to "make it more technical" it is easy to slide into a full technical
breakdown with code blocks. Here the form stays simple: the same skeleton, plus names. If a code
block appeared, you went the wrong way.

## Done when

- Every screen has a click-path (inherited from `x-simplify-answer`).
- Every claim about behaviour has exactly one search key — the name of an endpoint, parameter, field
  or function. Go through the finished answer and for each claim ask: **how will the reader check
  this?** A claim without a key either gets one or is rewritten as an observable effect.
- Where no key is named, it is a thing the reader cannot open.
- Every name is explained in the same sentence where it first appears.
- There are no code blocks in the answer.

## The `session` argument

By default it fires **once** — it re-explains the last answer, then behaviour goes back to normal.

With the `session` argument — keep this style in every following answer until the end of the
session, until the user says to stop ("enough", "go back to normal") or asks for another format.
Confirm it is on in one line.

The stickiness lives in the context and in a long session it can fade — then the user calls the
skill again. Do not say this every turn.

## The goal — text like this

Fragments of a real answer that hit the target. All three additions are visible, and so is what is
not in it.

> **Where this is bad.** `Project → Members → "Add member"` and the "Share" button. These are
> `getAccessCandidates()` and `accessApi.searchRecipients()` — **the very same**
> `GET /api/org-structure/profiles`, just with `search`/`limit`. There you pick **who else** to
> invite. You will not invite yourself — you are already inside. But your own row still sits at the top.
>
> **The reviewer's finding.** For these two forms the server got a query parameter `exclude_self=1` —
> "remove my row from the results" (`WHERE id != :currentProfileId`). But nobody on the frontend sends
> it: grep over `resources/js` finds no occurrences. So the parameter exists, but nobody presses it.
>
> 3. And the frontend could not have fixed this: the spec has only `exclude_self`, not a word about
>    `current_first`. Nobody would ever send it, and "me first" would just quietly not work. No error,
>    no 422 — 200 and the usual alphabetical order.

The screens kept their click-path, the effects are told through what the person sees and does. Names
appeared where the reader would go looking: two frontend calls, an endpoint, two parameters, a `WHERE`
condition, code 422. Not a single layer, pattern or code block.
