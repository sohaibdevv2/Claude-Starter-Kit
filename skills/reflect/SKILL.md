---
name: reflect
description: Analyze the current or recent session(s) for corrections, preferences, and implicit feedback. Extracts learnings and routes them to the right knowledge/rules file. Run when you want to capture what was learned this session.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, AskUserQuestion
argument-hint: "[--since YYYY-MM-DD] [--file path.jsonl]"
---

# /reflect — Session Learning System

**First:** Read `LEARNINGS.md` (in this skill's directory) before proceeding.

You are running a 4-phase reflection workflow. Follow each phase in order.

**Arguments:** `$ARGUMENTS`

---

## Phase 1: Extract

Run the extraction script to get candidate learnings from session JSONL.

```bash
python3 ~/claude-assistant/scripts/extract-learnings.py $ARGUMENTS
```

If `$ARGUMENTS` is empty, it analyzes the latest session. Pass `--since YYYY-MM-DD` or `--file <path>` to customize scope.

- If no pairs found -- tell user "Nothing to reflect on" and stop
- If pairs found -- capture the output and proceed to Phase 2

---

## Phase 2: Analyze

For each candidate pair from Phase 1, determine:

1. **Is this a real learning?** ~40% are normal conversation — skip those. Look for:
   - Corrections ("no, do X instead", "actually...", "wrong")
   - Preferences ("always use...", "I prefer...", "from now on...")
   - Tool rejections with feedback (user denied + said why)
   - Workflow patterns (user repeatedly does something a specific way)
   - Implicit feedback (user rephrases, asks again, provides what Claude should have known)

2. **Check rejections** — Read `~/claude-assistant/knowledge/self/rejections.md`. For each candidate:
   - If it matches a previously rejected learning (same topic + target file): **skip silently**. Note in output: "Skipped: matches rejected learning from [date]"
   - If it *contradicts* a previously rejected learning (opposite of what was rejected): flag as **potential reversal** — present to user with context from the rejection log

3. **Classify and route** each real learning using the routing table below.

4. **Check for duplicates** — Read the target file and verify the learning isn't already captured.

5. **Scan for contradictions** — For each proposed change with a target file:
   a. Read the target file
   b. Read up to 5 related files: same directory + shared tags (YAML `tags` field) + wiki-linked files
   c. Scan for statements that **directly contradict** the proposed change
   d. If contradiction found, flag it for Phase 3 conflict resolution:
      ```
      CONFLICT with [file.md:line]:
        Existing: "[quoted text]"
        Proposed: "[new learning]"
      ```
   e. **Update feedback counters** — If the contradiction traces to a specific existing rule/learning entry, increment its `harmful` counter in `~/claude-assistant/state/rule-feedback.json`

6. **Update feedback counters** — Read `~/claude-assistant/state/rule-feedback.json` (create if missing). For each finding:

   a. If a correction **contradicts** an existing rule -- increment `harmful` for that rule:
      - Key format: `"<relative-path>::<section or first 60 chars of rule>"`

   b. If the session had **no corrections** in an area covered by a rule, and the rule was relevant to work done this session -- increment `helpful`

   c. Write updated counters back to `~/claude-assistant/state/rule-feedback.json`

   d. **Flag unhealthy rules** for Phase 3:
      - `harmful >= 3` -- flag: "This rule has been contradicted 3 times. Review or remove?"
      - `harmful / (helpful + harmful) > 0.5` with 4+ total signals -- flag as unreliable
      - `helpful >= 5` with `harmful == 0` -- mark as "stable" (note in output, no action needed)

7. **For multi-session scans** (`--since`): Track if the same learning appears across 2+ sessions. Flag for promotion:
   - 2+ occurrences -- suggest knowledge file if not already there
   - 3+ occurrences -- flag for promotion to rule
   - **Exception:** if the learning contradicts a rejected entry (Claude keeps making the same mistake), promote immediately to rule on 2nd occurrence

### Routing Table

| Category | Target File |
|---|---|
| Task/operational correction | `~/.claude/rules/tasks.md` |
| Communication preference | `~/.claude/rules/communication.md` |
| Session management | `~/.claude/rules/sessions.md` |
| Security/git correction | `~/.claude/rules/security.md` |
| Delegation pattern | `~/.claude/rules/delegation.md` |
| Development standard | `~/.claude/rules/development.md` |
| Research convention | `~/.claude/rules/research.md` |
| User profile update | `~/claude-assistant/knowledge/user/profile.md` |
| User goals update | `~/claude-assistant/knowledge/user/goals.md` |
| Self-knowledge | `~/claude-assistant/knowledge/self/identity.md` |
| Problem insight | `~/claude-assistant/knowledge/problems/NN-*.md` Insights Log |
| Project state change | `~/claude-assistant/knowledge/projects/<project>.md` |
| Global convention | `~/.claude/CLAUDE.md` |
| Recurring pattern (3+ sessions) | `~/.claude/rules/` (new file or existing) |
| Actionable work identified | SQLite via `sqlite3 ~/claude-assistant/tasks.db` then `python3 ~/claude-assistant/scripts/db.py export` |
| MEMORY.md state change | MEMORY.md (sparingly) |

**Routing priority:** Rules files > Knowledge files > MEMORY.md > CLAUDE.md

**Problem routing:** Read `~/claude-assistant/knowledge/problems/00-overview.md` to match findings against the user's problems.

---

## Phase 3: Present

Show each finding to the user in this format:

```
## Finding N: [short title]
- **Evidence:** "[what user said]" (in response to "[what Claude said]")
- **Category:** [from routing table]
- **Target:** `path/to/file.md`
- **Proposed change:** [exact text to add/edit]
- **Already captured?** Yes/No
```

### Conflict Resolution

If Phase 2 flagged contradictions:

```
CONFLICT with [file.md:line]:
  Existing: "[quoted text from file]"
  Proposed: "[the new learning]"
  Resolve: keep existing (k), replace (r), or note both (b)
```

### Flagged Rules

If feedback counters flagged unhealthy rules:

```
## Flagged Rules

### [rule key]
- Counters: helpful=N, harmful=N
- Recommendation: review / remove / keep with caveat
```

Ask: **"Action on flagged rules? (r)emove, (e)dit, (k)eep, or (s)kip"**

### User Decision

After listing all findings, ask:

> **Apply all (a), select by number (e.g. 1,3,5), or discard (d)?**

If no real learnings found: tell user "Analyzed N pairs, no actionable learnings found" and stop.

### Rejection Logging

When user discards findings:

1. Ask: **"Brief reason? (or Enter to skip)"**
2. Append to `~/claude-assistant/knowledge/self/rejections.md`:
   ```markdown
   ### YYYY-MM-DD — Rejected
   - **Proposed:** [the learning]
   - **Target:** `path/to/file.md`
   - **Reason:** [user's reason, or "(not provided)"]
   ```

---

## Phase 4: Apply

For each approved finding:

1. **Read** the target file
2. **Edit** with the proposed change (use Edit tool, not Write)
3. **Update** YAML frontmatter `last_reviewed` to today's date (if present)
4. If adding to a problem file's Insights Log, use format: `### YYYY-MM-DD — Session Reflection`

After all edits:

1. Summarize what was changed: `| File | Change |` table
2. Stage `~/claude-assistant/state/rule-feedback.json` if counters were updated
3. Commit with message `reflect: capture session learnings`
