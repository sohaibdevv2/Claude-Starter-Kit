#!/bin/bash
# session-save-reminder.sh — Stop hook
# Fires after every Claude response. Reminds ONCE per session (after 10+ min)
# to save state before ending.
# Must be extremely fast — runs on every response.

set -euo pipefail

WORKSPACE=$(cat "$HOME/.claude/workspace.conf" 2>/dev/null || echo "$HOME/claude-assistant")
MARKER="$HOME/.claude/state/.session-start"
REMINDED="$HOME/.claude/state/.session-reminded"

mkdir -p "$HOME/.claude/state"

# First call: record session start time
if [[ ! -f "$MARKER" ]]; then
  date +%s > "$MARKER"
  exit 0
fi

# Already reminded this session
if [[ -f "$REMINDED" ]]; then
  exit 0
fi

START=$(cat "$MARKER" 2>/dev/null || echo "0")
NOW=$(date +%s)
DURATION=$((NOW - START))

# Only remind after 10 minutes
if [[ $DURATION -lt 600 ]]; then
  exit 0
fi

# Check if a session note was already created recently
RECENT_NOTE=$(find "$WORKSPACE/state/sessions/" -name "*.md" -mmin -10 2>/dev/null | head -1)
if [[ -n "$RECENT_NOTE" ]]; then
  exit 0
fi

# One-time reminder
touch "$REMINDED"
cat >&2 << REMINDER
Session running >10min. Before ending or compacting:
1. UPDATE MEMORY.md — write current state and next steps
2. CREATE SESSION NOTE in state/sessions/ — summary, decisions, files changed, open items
3. COMMIT AND PUSH ~/claude-assistant if knowledge files changed
REMINDER
exit 2
