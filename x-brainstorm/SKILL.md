---
name: x-brainstorm
description: >-
  Turn an idea into a settled design through collaborative dialogue, then close what
  the dialogue left undecided by scanning a fixed topic list against the real code.
  Output is a settled design a spec can be written from, and it replaces
  superpowers:brainstorming for that job. Runs when something names it — the user, or
  a flow that calls it by name.
---

# Brainstorming Ideas Into Designs, Then Closing What Is Left Open

Help turn ideas into fully formed designs through natural collaborative dialogue, then find
what the dialogue left undecided and settle it before anything is written.

Start by understanding the current project context, then ask questions one at a time to
refine the idea. Once you understand what you're building, read the code the direction
touches, close the open decisions, and present the design for approval.

**Output: a short summary of settled decisions** — the input a spec is written from. This
skill produces decisions, not a document. The document is the spec, written next; there is no
separate implementation plan after it.

**This replaces `superpowers:brainstorming`.** Its exploring half is carried here verbatim.
Do not invoke that skill as well.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any
implementation action until you have presented a design and the user has approved it. This
applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config
change — all of them. "Simple" projects are where unexamined assumptions cause the most
wasted work. The design can be short (a few sentences for truly simple projects), but you
MUST present it and get approval.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Explore project context — the broad read** — files, docs, recent commits; how this part is built and which patterns it follows
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation; the user picks a direction
4. **Read current behaviour on the chosen path — the close read** — what happens today at every point the direction changes
5. **Scan the topic list** — mark each topic settled / half / untouched
6. **Close the open decisions** — up to five questions, one at a time, each with a recommendation
7. **Present the design** — in sections scaled to their complexity, get user approval
8. **Hand over** — a short summary of the decisions taken

## Why the order is what it is

The code is read twice, at different depths. The broad read comes first because approaches
proposed without it are guesses about a codebase you have not opened. The close read comes
**after** a direction is chosen — deep-reading all three candidate directions means throwing
most of it away — and **before** the design is presented, because most of the topic list
cannot be answered without knowing how the thing works today: what an empty state looks like
now, what already happens on failure, which of this is someone else's behaviour. Scan too
early and every answer is a guess dressed as a decision.

The design is presented and approved **once, at the end**. Approve it before the open
decisions are closed and the user is approving something five answers away from final: they
hold two versions, and the second gets approved by implication. The cheap early checkpoint is
the choice between approaches — enough direction to know which code to read, without
pretending the design is settled.

## The Process

**Understanding the idea:**

- Check out the current project state first (files, docs, recent commits)
- Before asking detailed questions, assess scope: if the request describes multiple
  independent subsystems (e.g., "build a platform with chat, file storage, billing, and
  analytics"), flag this immediately. Don't spend questions refining details of a project
  that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose into sub-projects:
  what are the independent pieces, how do they relate, what order should they be built? Then
  brainstorm the first sub-project through the normal design flow. Each sub-project gets its
  own spec → implementation cycle.
- For appropriately-scoped projects, ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why
- YAGNI ruthlessly - remove unnecessary features from every approach and design

**Presenting the design:**

- Once the open decisions are closed, present the design
- Write the design and the summary in the language of the conversation
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose, communicate through
  well-defined interfaces, and can be understood and tested independently
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you change the
  internals without breaking consumers? If not, the boundaries need work.
- Smaller, well-bounded units are also easier for you to work with - you reason better about
  code you can hold in context at once, and your edits are more reliable when files are
  focused. When a file grows large, that's often a signal that it's doing too much.

**Working in existing codebases:**

- Follow the patterns already there. The broad read in step 1 is what tells you which ones
  they are — the close read that comes later answers a different question and does not
  substitute for it.
- Where existing code has problems that affect the work (e.g., a file that's grown too large,
  unclear boundaries, tangled responsibilities), include targeted improvements as part of the
  design - the way a good developer improves code they're working in.
- Don't propose unrelated refactoring. Stay focused on what serves the current goal.

## The close read

**Scale it to the topic list, not to the module.** Enough to answer what the topics ask about
the path you are changing — never an audit.

What the screen shows today while it loads, when it is empty, when it fails; what the current
call does on error; what else already depends on the thing being changed.

This is not a repeat of step 1. The broad read asks *how is this built and what patterns does
it follow* — it is what makes the approaches in step 3 sane, and without it you cannot even
name the alternatives. The close read asks *what exactly happens here today*, on one path, and
it is only possible once that path is chosen.

## Topic list

Walk all of them; most will be settled or irrelevant in seconds. Mark each **settled** /
**half** / **untouched**.

**Report the walk before you ask anything.** Two lines: the topics that came back *half* or
*untouched* — these are what the questions come from — and, names only with no explanation,
the ones that came back settled or irrelevant. A scan that reports only what it found reads
exactly like a scan that stopped after three topics. Everything else stays working notes;
nothing is written to disk.

- **Boundaries** — what is in, and what is explicitly not. An unstated "not this" becomes
  scope creep or a review argument later.
- **Who it is for** — roles, permissions, who sees this and who may act on it.
- **Data and state** — entities involved, the states they move between, what happens to data
  that already exists.
- **Screens and flows** — the main path, plus what the user sees while it loads, when the
  result is empty, and when it fails.
- **Failure and edge cases** — what happens on error, on a slow response, on two people doing
  it at once, on the boundary value.
- **External dependencies** — other services or modules involved, and what this does when
  they are unavailable or answer differently than expected.
- **Compatibility** — does anything users rely on today behave differently after this, and is
  that intended.
- **Non-functional** — speed, volume, and what has to be observable when it misbehaves in
  production. Only where the change plausibly moves them.
- **Terminology** — one thing, one name. Fix the name now; renaming it after the spec is
  written is three edits and a stale test.
- **Test seams** — where the tests will hook in: what each test drives, and what it
  substitutes. Prefer a seam that already has tests to a new one; take the highest seam that
  still reaches the behaviour, so tests assert what users get rather than how it is built;
  keep the count down, because every seam is another set of substitutions that can go green
  for the wrong reason. Creating a new seam is real work — name it as a cost, not a detail.
- **Done-ness** — how anyone will confirm this works. If the criteria live in a ticket or a
  requirements doc, they belong here, agreed, before the spec starts.
- **Placeholders** — anything still carrying TODO, "later", or an adjective with no number
  behind it: "fast", "robust", "convenient".

## What to ask, and what to skip

Ask only when the answer changes **the architecture, the tests, or what the user sees**.

Skip:

- anything answerable by reading the code — read it instead of asking,
- decisions better made with the compiler and the tests in hand (internal decomposition,
  helper boundaries, naming of local variables),
- stylistic preference,
- a question whose every answer leads to the same implementation.

Between asking and reading sits a third case, and it comes up often: the code answers what
happens **by default**, but whether that default is right for this change is not the code's
call. A counter that goes stale after an inline edit; a guard that fires on a path this
feature now reaches; an aggregate that nobody refreshes. The precedent tells you the
behaviour — it does not tell you whether to keep it here.

Settle those in the design rather than in a question: one line naming the precedent you
followed and stating that you are accepting its behaviour for this change. The user reads the
design and can overturn it there; a default that was never written down cannot be overturned,
because nobody knows it was chosen.

If more than five survive, take the five with the largest blast radius and say plainly which
ones you dropped. If the scan finds nothing unsettled, say so and move to the design.

## Question shape

One question per message, in the user's working language:

```
**Question:** <a full question, ending in a question mark, that makes sense on its own>
**Why it matters:** <one sentence — what this decides downstream>
**Recommend:** <option> — <one or two sentences of why>

| A | <recommended option> |
| B | <alternative> |
| C | <alternative> |

Answer with a letter, "yes" if you agree with the recommendation, or your own option.
```

Rules that make this cheap for the user:

- **Never a bare label as the question.** "Error handling (FR-3)" is a heading, not a
  question. The line before the `?` must be answerable on its own.
- **Always recommend.** A question without a proposed answer converts your uncertainty into
  the user's homework. Pick the option you would pick, and say why in one breath.
- **Two to five options**, mutually exclusive, plus the user's own answer.
- **One at a time.** Later questions often change based on earlier answers; a batch of five
  wastes the ones that turn out moot.
- **Order by dependency, not by topic.** Walk the decision tree: a question whose answer
  changes what the next question even means goes first. Asking in the order the topics happen
  to sit in the list makes the user answer the same thing twice.

## Handing over to the spec

The summary of decisions is the input to the spec. Pass the decisions, not the
transcript — the spec's decisions section restates them in its own words, with the reasoning
that survived, not the conversation that produced it.

A decision the user deliberately left open goes over as an open question, named. The spec
skill stops rather than guessing at it.
