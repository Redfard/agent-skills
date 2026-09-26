#!/usr/bin/env bash
# Ensure the Chrome instance used by the chrome-devtools MCP server is running.
#
# The MCP server is configured with --browserUrl=http://127.0.0.1:9333, so it
# connects to THIS Chrome instead of launching its own. Run this before using
# any chrome-devtools tool. Idempotent: if Chrome is already up on :9333 it does
# nothing, so it is safe to run any number of times.
set -u

PORT=9333
PROFILE="$HOME/chrome-mcp-profile"
LOG="/tmp/chrome-mcp-${PORT}.log"
URL="http://127.0.0.1:${PORT}/json/version"

ver="$(curl -s --max-time 2 "$URL" | grep -o '"Browser": *"[^"]*"' || true)"
if [ -n "$ver" ]; then
  echo "OK: Chrome already running on :${PORT}  (${ver})"
  exit 0
fi

echo "Starting Chrome on :${PORT}  (profile: ${PROFILE}) ..."
setsid google-chrome \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${PROFILE}" \
  --no-first-run --no-default-browser-check \
  --window-position=100,100 --window-size=1400,900 \
  </dev/null >"$LOG" 2>&1 &
disown

# Wait for the debug port using curl's own retry (no blind sleep).
ver="$(curl -s --retry 15 --retry-delay 1 --retry-connrefused --max-time 5 "$URL" \
        | grep -o '"Browser": *"[^"]*"' || true)"
if [ -n "$ver" ]; then
  echo "OK: Chrome is up on :${PORT}  (${ver})"
  echo "Note: 'Failed to connect to the bus ... dbus' lines in ${LOG} are harmless WSL noise."
  exit 0
fi

echo "FAIL: Chrome did not come up on :${PORT}. See ${LOG}." >&2
echo "Common cause on WSL: no GUI display. Check: echo \$DISPLAY (expect :0)." >&2
exit 1
