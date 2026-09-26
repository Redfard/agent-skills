---
name: x-agent-bus
description: Use when you need to pass information to or pull it from another agent or another Claude Code session that you cannot talk to directly — leaving a note/handoff/finding for another agent, reading the latest message left by other agents, or coordinating between parallel sessions and worktrees. Keywords — share between agents, leave a note for another agent, message another session, inter-agent, handoff, mailbox, agent bus, read latest from agents.
---

# Agent Bus

## Overview

Independent agents and Claude Code sessions can't talk to each other directly. The agent bus is a shared, file-based mailbox: any agent **posts** a message as a file, and any agent **reads** the latest message — without knowing where it was written or who is online.

**Core idea:** each message is one Markdown file in a shared directory, named with a UTC timestamp. Lexical sort = chronological order, so "the latest message" is just the last file. No index, no locking, no read-state.

## When to use

- You finished something another agent/session needs to know (a finding, a decision, a handoff).
- You're starting work and want to see the most recent note left by other agents.
- You're coordinating parallel sessions or worktrees that share a machine but not a conversation.

Not for: talking to a subagent you spawned yourself (it already returns its result to you), or durable project knowledge (use your memory / the repo for that). The channel lives in `/tmp` and does not survive a machine reboot.

## The script

`bus.sh` (next to this file) does everything. Channel dir defaults to `/tmp/claude-agent-bus` (override with `AGENT_BUS_DIR`).

| Goal | Command |
|------|---------|
| Leave a message | `bus.sh post --from NAME --title SLUG [--re REF]` (body via stdin/heredoc) |
| Read the latest | `bus.sh latest` |
| Read latest from a specific agent | `bus.sh latest --from NAME` |
| Browse recent | `bus.sh list -n 5` |

Run `bus.sh help` for all flags.

`bus.sh` lies next to this file; `<skill dir>` in the commands below is this skill's directory.

## Posting

Pass the body on stdin (a heredoc avoids quoting pain). Use a short, recognizable `--from` so readers can tell who wrote it.

```bash
<skill dir>/bus.sh post --from reviewer --title idor-finding --re MBD-297 <<'MSG'
Documents of a soft-deleted phase are still resolvable. Check the cascade listeners.
MSG
```

It prints the path of the file it wrote.

## Reading

```bash
<skill dir>/bus.sh latest
```

Returns only the single newest message (filename header + frontmatter + body). This is intentional — there is no "unread since last time" tracking. To target one author, add `--from NAME`; to see what else is around, use `list`.

## Notes

- A message filename is `<UTC-timestamp>__<from>__<slug>.md`; `from`/`slug` are lowercased and hyphenated.
- Each message is its own file, so parallel posts never clobber each other — no locks needed.
- Empty channel is not an error: `latest`/`list` say "No messages yet" and exit 0.
