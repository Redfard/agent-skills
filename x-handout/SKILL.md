---
name: x-handout
description: Use when producing a file the user will open themselves — a screenshot, a before/after pair, an exported report, a dump, a sample file, anything they asked to be shown — or when they say to put it in the handout folder. Such files go to a subfolder of the directory configured in this skill's .env, and their absolute path is named back. Keywords — handout, give it to me as a file, screenshot, before/after, report as a file, export, dump.
---

# Handout — files the person opens themselves

## Where

The base directory is set **not here but in `.env` next to this file**, key `XHANDOUT_DIR`:

```bash
XHANDOUT_DIR=$(grep -E '^XHANDOUT_DIR=' ~/.claude/skills/x-handout/.env | cut -d= -f2-)
```

Files go to `$XHANDOUT_DIR/<subfolder>/`. The path from `.env` is absolute; put it into commands
as is, without adding `~` and without expanding it through the shell.

No `.env` → `cp ~/.claude/skills/x-handout/.env.example ~/.claude/skills/x-handout/.env`,
and say so in the answer: from then on the directory comes from there, and the person must know
the value was set by default, not chosen by them.

The directory stays outside working trees: the artifact does not show up in `git status`, does not
ask to be committed and survives a branch switch — and for "before/after" screenshots you have to
switch the branch exactly when the file already exists.

## What goes there and what does not

| File | Where |
|---|---|
| The person will open it themselves: a screenshot, a "before/after" pair, an export, a dump, a sample file, a report they asked for as a file | `$XHANDOUT_DIR/<subfolder>/` |
| Intermediate, for you: raw command output, a draft, parsed json, a run log | the session scratchpad directory |
| A work result that lives in the project: code, a test, docs, a spec, a flow artifact | its own place in the repository |

A file the person asked to see, but which you left only in the session scratchpad, does not exist
for them: they do not read the scratchpad path.

## Subfolder name

One task — one subfolder, kebab-case, `<task-key>-<topic>`; no key — just `<topic>`.
Drawer screenshots for MBD-620 → `mbd-620-drawer-before-after`.

When you come back to the same task, put files in the **same** subfolder, do not create a sibling
with a date. Otherwise in a week there are a dozen directories, and the person does not know which
one is fresh.

File names say what is in them: `drawer-BEFORE-develop.png` reads well, `screenshot-2.png` does not.

## After putting files there

In the answer name the **full absolute path**: the subfolder if there are several files, and the
path of each file if there are two or three. Without this the person sees only "done" and does not
know what to open.

## Done when

- the directory is taken from `XHANDOUT_DIR` in `.env`, not typed into the command by hand;
- every file the person will open themselves is in one subfolder of this directory;
- its absolute path is named in the answer;
- nothing appeared in the working tree because of this — `git status` is as clean as it was.
