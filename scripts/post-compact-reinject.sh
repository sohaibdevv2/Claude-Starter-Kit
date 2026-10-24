#!/bin/bash
# post-compact-reinject.sh — Re-inject critical rules after context compaction.
#
# CLAUDE.md content fades after compaction (GitHub #22309, #21119).
# This hook fires on SessionStart:compact and re-outputs key behavioral rules
# as system-reminder content that survives compaction.

WORKSPACE=$(cat "$HOME/.claude/workspace.conf" 2>/dev/null || echo "$HOME/claude-assistant")

echo "=== CRITICAL RULES (re-injected after compaction) ==="
echo ""
echo "SECURITY: Cannot read/write secrets (.env, .key, .pem). Cannot write outside \$HOME. Cannot force-push. Cannot rm -rf."
echo "GIT: Commit and push before new features. Stage specific files, never git add -A. Verify no secrets staged."
echo "TASKS: Check active tasks before substantive work. Never claim done without verification."
echo "COMMUNICATION: No hype, no flattery. Specific praise only. Lead with problems."
echo "SESSIONS: Update MEMORY.md and create session note before exit."
echo "WORKSPACE: Your assistant workspace is $WORKSPACE. All knowledge, tasks, and state live there."
echo ""

# Also output the pre-compact state if available
if [ -f "$WORKSPACE/state/pre-compact-state.md" ]; then
    echo "=== PRE-COMPACTION STATE ==="
    cat "$WORKSPACE/state/pre-compact-state.md"
fi
