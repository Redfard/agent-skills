---
name: x-short-answer
disable-model-invocation: true
description: Answer short — the answer on the first line, then only what changes the reader's decision; flag s keeps it on for the whole session.
---

# Short answer

Cut the volume, keep the answer. The reader asked one thing; give them that, and stop.

## The shape

1. **The answer is the first line.** Not a preamble, not what you checked, not a restatement of
   the question. If the question was yes/no, the first word is yes or no.
2. **Then only what changes what the reader does or decides** — a number, a file, a status, a
   risk, a name they need. Everything else is cut, however true it is.
3. **Three to five lines by default.** Longer only when the content is a list the reader will act on
   item by item.
4. **One structure, not three.** A table or a list, not both, and never a list of full sentences
   where one line does.
5. **Details on request, in one short line** — "tell me if you need details". A paragraph
   offering the details is the details.

Write the answer in the language of the conversation.

## What stays even when short

Brevity is a cut of volume, never of accuracy.

- Something is **not** done, failed, or was skipped → it is said, in the first three lines. A short
  answer that reads cleaner than the truth is the one failure mode worth watching for.
- A question you need answered to continue stays, as one line at the end.
- A number or a name the reader will look for stays. Shortening `fixes-3.md` to "the report" makes the
  answer shorter and the reader's next question longer.

## The observed excuse

*"He asked for short, but these details matter — I will keep them and just make the wording tighter."* That produces
the same volume in denser prose, which is harder to read, not easier. Cutting means whole
paragraphs leave: the options you did not take, the reasoning behind a decision nobody questioned,
the recap of what you already said above, the process narration.

## Argument: `s` (same as `session`)

Without it — this answer only, then back to normal.

With `s` (`/x-short-answer s`, `-s` and `session` mean the same thing) — hold the style for the rest
of the session: **every** subsequent answer in this conversation is short, whatever the topic,
until the user asks to stop or asks for detail.
Confirm in one line, then just do it.

Being asked a follow-up question is not a request for detail. Answer it short too. Nor is a long or
multi-part task: the work is done in full, only the report stays short.

## Related

`x-simplify-answer` cuts decoding cost — jargon out, screens and actions in. This one cuts volume.
Both at once when the answer is long *and* dense.

## Done when

- The first line answers the question asked.
- Every line left would change what the reader does. A line that only shows work done is gone.
- Anything unfinished or failed is stated, not omitted.
