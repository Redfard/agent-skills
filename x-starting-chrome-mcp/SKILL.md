---
name: x-starting-chrome-mcp
description: Use when the chrome-devtools MCP browser must be running before browser work in this WSL setup, or when chrome-devtools tools fail with "cannot connect to browser" / "No connected page" / list_pages returns nothing. Covers launching the persistent Chrome on port 9333 and the multi-agent pageId rule.
---

# Starting Chrome for chrome-devtools MCP

## Overview

The `chrome-devtools` MCP server is configured with `--browserUrl=http://127.0.0.1:9333` and `--experimentalPageIdRouting`. It does **not** launch its own browser — it connects to a user-launched Chrome on port 9333 that holds the persistent, logged-in profile. If that Chrome isn't running, every chrome-devtools tool fails to connect.

## When to use

- Before driving any `chrome-devtools` tool in a session.
- A tool errors with "cannot connect to browser", the connection is refused, or `list_pages` returns nothing.
- Starting a multi-agent browser session.

## How — run the launcher (idempotent)

```bash
bash ~/.claude/skills/x-starting-chrome-mcp/start-chrome.sh
```

If it prints `OK: Chrome ... on :9333`, the browser is ready. The script is safe to run repeatedly — if Chrome is already up it does nothing. Best run **before** starting Claude Code, but it also works mid-session (the MCP server connects lazily).

## Rules — do NOT

- **Don't launch a browser through MCP** or with a second `--remote-debugging-port`. There is exactly one Chrome (port 9333); reuse it.
- **Don't start a second instance on the same profile** (`~/chrome-mcp-profile`) — it conflicts. The script already guards against this.
- **Don't panic at `dbus ... ERROR` lines** in the log — harmless WSL noise, not a failure. Verify success by the port, not the log.
- **Assume the user is logged in.** If a site needs login, tell the user — don't try to log in yourself. Cookies live in `~/chrome-mcp-profile` and persist across restarts.
- **Don't close the browser when done.** Leave it open for the next task and to keep the logged-in session alive.

## Working with tabs & pageId

This is the core rule that lets several agents share one Chrome without clobbering each other.

- **Open as many tabs as you need** with `new_page` — no hard cap. It returns that tab's **`pageId`**.
- **Get a `pageId`** from `new_page` (the tab you just opened) or `list_pages` (existing tabs). Keep track of the `pageId` of every tab you open.
- **Pass the target `pageId` on every page-scoped call** — `navigate_page`, `click`, `fill`, `take_snapshot`, `take_screenshot`, `upload_file`, etc. Do **not** rely on a "current/selected" tab: page choice is by `pageId`, and when multiple agents share the browser the global selection moves under you. `select_page` is not needed.
- **Touch only your own tabs** — the ones you opened. Never act on another agent's or the user's `pageId`.
- **Fan-out:** each subagent opens its own tab(s) via `new_page` and works only with its own `pageId`(s). No central ID registry.
- Snapshot `uid`s go stale after navigation or many page switches — refresh with `take_snapshot` (same `pageId`).

### Slow page navigation

Job sites often keep long-lived network requests open. In that case `new_page` or
`navigate_page` can report a navigation timeout (or a client-side cancellation)
even though Chrome has already created and loaded the tab. This is **not** by
itself a browser/MCP outage.

- After such an error, call `list_pages`, find the tab you just opened by its
  target URL, and call `take_snapshot` with that exact `pageId`.
- If the snapshot contains the expected page, continue using that `pageId`; do
  not retry blindly and do not report the source as browser-blocked.
- Only call the browser unavailable after the launcher fails or both
  `list_pages` and a snapshot fail. Close only the tab you created if it is
  unusable.

For job sites, **MUST use this deterministic variant** so the `pageId` is known
even when navigation does not settle: call `new_page` for `about:blank`, retain
its returned `pageId`, then call `navigate_page` for the destination with a
short timeout. **Do not call `new_page` with an external job-site URL.** If that
navigation times out, wait briefly and take a snapshot of the same known
`pageId`. Never open a replacement tab while the first one may still be
loading.

## Screenshots

Save screenshots to a file with `take_screenshot filePath=…` — **don't return them inline**. Inline images linger in context and bloat it fast. Read the file back only if you genuinely need to see pixels; for filling forms / clicking, the text `take_snapshot` is enough. (In the job-applications repo, save to `temp/`.)

## Common mistakes

| Symptom | Fix |
|---|---|
| Tools "cannot connect" / `list_pages` empty | Run the launcher script; Chrome wasn't up. |
| Saw `dbus` ERRORs, assumed crash, closed terminal | Ignore dbus noise; the script detaches Chrome so the terminal is free. |
| `FAIL: did not come up` | Check `echo $DISPLAY` (expect `:0`); see `/tmp/chrome-mcp-9333.log`. |
| Two agents land on the same/wrong tab | Each agent must pass its own `pageId` on every call. |
| Context ballooned with images | Save screenshots with `filePath=…`; don't return them inline. |
