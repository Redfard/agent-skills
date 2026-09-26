# agent-skills

Personal skills for Claude Code (they work in Codex too): answer formats, demos and mockups of
changes, handing context between sessions, re-checking finished work, rules for writing skills.

## Install

Clone the repo and put the skill folders where the agent looks for them:

```bash
git clone https://github.com/Redfard/agent-skills.git
cp -r agent-skills/x-* ~/.claude/skills/
```

Skills with a `.env.example` read their settings from a `.env` next to it — copy the example and
fill it in.

## Skills

| Skill | What it does |
|---|---|
| `x-agent-bus` | Send and read messages between agents and sessions through a file bus |
| `x-brainstorm` | Idea → agreed design through dialogue, then a check of fixed topics against the live code; output is a summary of decisions for the spec |
| `x-check-and-fix` | Check the review findings you got and fix the confirmed ones; also called from `x-review-last` with flag `a` |
| `x-demo-guide` | A step-by-step guide to check finished changes by hand on a live test server: account, full URLs, real ids, expected result |
| `x-demo-run` | Walks the `x-demo-guide` steps in the browser and returns an HTML report: a screenshot per step, a "before" screenshot, the mockup, a status. Called by hand only |
| `x-explanation` | An explanation that keeps the technical details: clear, but with the code and the mechanism |
| `x-handoff` | Turn the current conversation into a handoff document for the next session. Called by hand only |
| `x-handout` | Files the person will open themselves (screenshots, reports, exports) go to a set folder, with the absolute path in the answer |
| `x-mem-top` | How memory is used on a Linux machine: a summary and processes ranked by memory |
| `x-nontech-answer` | An answer for a non-technical person: no code, no names of files, classes or tables. Called by hand only |
| `x-project-idiom` | Finds how the project usually does a similar thing, from several places in the live code. Read-only. Called by hand only |
| `x-review-last` | Re-check the work just done with fresh subagents and merge their findings into one list |
| `x-short-answer` | The answer in the first line, then only what changes the reader's decision. Argument `session` keeps it on for the whole session. Called by hand only |
| `x-simplify-answer` | The point in the first line, told through screens and actions, no jargon. Argument `session` keeps it on for the whole session |
| `x-starting-chrome-mcp` | Start a persistent Chrome for the chrome-devtools MCP (WSL setup) |
| `x-tech-simplify-answer` | A retelling in the `x-simplify-answer` form, but with the real names of endpoints, parameters and fields |
| `x-ui-mockups` | Mockups of a UI feature in the live interface on demo data: variants switched by a URL parameter, screenshots, steps to click through |
| `x-writing-skills` | Rules for skill files: invocation and description, completion criteria, prohibitions, pruning. Called by hand only |
