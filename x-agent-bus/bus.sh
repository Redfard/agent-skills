#!/usr/bin/env bash
# x-agent-bus: a tiny file-based mailbox so independent agents/sessions can
# exchange notes. Each message is one Markdown file in a shared tmp directory.
# The timestamp-prefixed filename carries chronological order, so "the latest
# message" is just the last file in a lexical sort — no index, no locking.
#
# Subcommands: post | latest | list | help
# Channel dir: $AGENT_BUS_DIR (default /tmp/claude-agent-bus)

set -euo pipefail

BUS_DIR="${AGENT_BUS_DIR:-/tmp/claude-agent-bus}"

# Lowercase, collapse anything non-alphanumeric to single hyphens, trim hyphens.
sanitize() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
}

usage() {
  cat <<'EOF'
x-agent-bus — file-based mailbox for exchanging notes between agents/sessions.

USAGE
  bus.sh post   [--from NAME] [--title SLUG] [--re REF] [--body TEXT]
                 (body is read from stdin if --body is omitted)
  bus.sh latest [--from NAME]
  bus.sh list   [-n N]
  bus.sh help

EXAMPLES
  bus.sh post --from reviewer --title idor-finding <<'MSG'
  Documents of a soft-deleted phase are still resolvable. See MBD-297.
  MSG

  bus.sh latest                 # newest message from anyone
  bus.sh latest --from reviewer # newest message authored by "reviewer"
  bus.sh list -n 5              # 5 most recent messages (headers only)

Channel directory: ${AGENT_BUS_DIR:-/tmp/claude-agent-bus}
EOF
}

cmd_post() {
  local from="agent" slug="" ref="" body=""
  local have_body=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --from)  from="$2"; shift 2 ;;
      --title) slug="$2"; shift 2 ;;
      --re)    ref="$2"; shift 2 ;;
      --body)  body="$2"; have_body=1; shift 2 ;;
      *) echo "post: unknown argument '$1'" >&2; exit 2 ;;
    esac
  done

  if [ "$have_body" -eq 0 ]; then
    if [ -t 0 ]; then
      echo "post: no body. Pipe it via stdin (heredoc) or pass --body TEXT." >&2
      exit 2
    fi
    body="$(cat)"
  fi

  from="$(sanitize "$from")"; [ -n "$from" ] || from="agent"
  slug="$(sanitize "$slug")"; [ -n "$slug" ] || slug="note"

  mkdir -p "$BUS_DIR"

  local stamp iso file
  stamp="$(date -u +%Y%m%dT%H%M%S.%NZ)"
  iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  file="$BUS_DIR/${stamp}__${from}__${slug}.md"

  {
    echo "---"
    echo "from: $from"
    echo "time: $iso"
    [ -n "$ref" ] && echo "re: $ref"
    echo "---"
    printf '%s\n' "$body"
  } > "$file"

  echo "$file"
}

# Newest message file, optionally filtered by author. Empty if none.
newest_file() {
  local from_filter="${1:-}" pattern
  if [ -n "$from_filter" ]; then
    pattern="$BUS_DIR/*__${from_filter}__*.md"
  else
    pattern="$BUS_DIR/*.md"
  fi
  # shellcheck disable=SC2086
  { ls -1 $pattern 2>/dev/null || true; } | sort | tail -n 1
}

cmd_latest() {
  local from=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --from) from="$(sanitize "$2")"; shift 2 ;;
      *) echo "latest: unknown argument '$1'" >&2; exit 2 ;;
    esac
  done

  local file
  file="$(newest_file "$from")"
  if [ -z "$file" ]; then
    if [ -n "$from" ]; then
      echo "No messages from '$from' yet (channel: $BUS_DIR)."
    else
      echo "No messages yet (channel: $BUS_DIR)."
    fi
    return 0
  fi

  echo "# latest: $(basename "$file")"
  echo
  cat "$file"
}

cmd_list() {
  local n=10
  while [ $# -gt 0 ]; do
    case "$1" in
      -n) n="$2"; shift 2 ;;
      *) echo "list: unknown argument '$1'" >&2; exit 2 ;;
    esac
  done

  local files
  files="$({ ls -1 "$BUS_DIR"/*.md 2>/dev/null || true; } | sort -r | head -n "$n")"
  if [ -z "$files" ]; then
    echo "No messages yet (channel: $BUS_DIR)."
    return 0
  fi

  echo "Recent messages (newest first) in $BUS_DIR:"
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    local time from
    time="$(sed -n 's/^time: //p' "$f" | head -n 1)"
    from="$(sed -n 's/^from: //p' "$f" | head -n 1)"
    printf '  %s  from=%-12s  %s\n' "${time:-?}" "${from:-?}" "$(basename "$f")"
  done <<< "$files"
}

main() {
  local sub="${1:-help}"
  [ $# -gt 0 ] && shift || true
  case "$sub" in
    post)   cmd_post "$@" ;;
    latest) cmd_latest "$@" ;;
    list)   cmd_list "$@" ;;
    help|-h|--help) usage ;;
    *) echo "Unknown subcommand '$sub'." >&2; echo >&2; usage >&2; exit 2 ;;
  esac
}

main "$@"
