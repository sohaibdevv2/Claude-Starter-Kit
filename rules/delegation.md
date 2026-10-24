# Delegation Rules

Principles for orchestrating subagent (subprocess) work.

## Core Asymmetry

You (the main session) are persistent. Subagents are ephemeral. They run one task and terminate. All continuity, context, and knowledge consolidation is YOUR responsibility. Design every delegation around this fact.

## When to Delegate

- Tasks that are independent and can run in parallel
- Research that would flood the main context window
- Implementation work with clear acceptance criteria
- Code review or analysis that produces a discrete output

## Task Framing

1. **One task, one outcome.** Never bundle unrelated work. A subagent should finish in one run or report `blocked`.
2. **Acceptance criteria in the prompt.** Every task ends with "Done when: [specific deliverables]." The subagent shouldn't have to guess what success looks like.
3. **Context is cheap, ambiguity is expensive.** Include relevant file paths, project names, conventions. The subagent has no memory of previous tasks — over-specify rather than under-specify.
4. **Workspace preamble stays generic.** Task-specific context goes in the task, not the preamble. The preamble is "read CLAUDE.md, follow conventions."

## Authority Boundaries

| Action | Subagent can do? | Notes |
|--------|-----------------|-------|
| Read any file in workspace | Yes | |
| Write/edit code and docs | Yes | Core capability |
| Run tests, linters, builds | Yes | Should verify own work |
| Create new files | Yes | Within workspace only |
| Git commit | No | Report files changed, you review and commit |
| Git push | No | Never — you push after review |
| Install dependencies | Ask | Report as `blocked` with recommendation |
| Architectural decisions | No | Report options, you decide |
| Modify CI/CD or workflows | No | Report as `blocked` |
| Access external services | No | No API calls, no web requests |

Rule of thumb: if it's reversible and local, the subagent can do it. If it affects shared state or is hard to undo, escalate to the main session.

## Knowledge Flow

Dual-write pattern — this is how compound knowledge actually gets read:

1. **Subagent writes working docs in-workspace.** Architecture notes, code analysis, READMEs — these stay in the project so the NEXT subagent benefits too.
2. **Subagent reports key findings in structured output.** The summary and next_steps carry the essential information back to you.
3. **You consolidate into `~/claude-assistant/knowledge/`.** After reviewing subagent output, update your knowledge files. Subagents never write to your knowledge base directly.

This means project repos accumulate their own documentation (good for any collaborator), and your knowledge base stays curated (good for you).

## Quality Control

1. **Read the structured output first.** Status, summary, files changed, blocked reason, next steps.
2. **Spot-check 2-3 files from the changes.** Don't re-read everything. Look for: correctness, convention adherence, nothing dangerous.
3. **If status is `partial` or `blocked`, read stderr.** The subagent may have hit an error it couldn't recover from.
4. **Trust but verify.** If a subagent says "tests pass," run the tests yourself before committing.

## Error Handling

- `completed` — review output, commit if good, update knowledge
- `partial` — review what's done, create follow-up task for the rest
- `blocked` — read blocked reason, resolve the blocker, re-delegate
- `failed` — read stderr, diagnose, fix the task prompt or workspace issue, re-delegate

Never re-delegate the exact same task without changing something. If it failed once, something needs to be different.

## Sequencing

When a task needs multiple subagent passes:

1. **Knowledge first.** The subagent needs to understand the codebase before it can build or test.
2. **Infrastructure second.** Testing frameworks, CI, tooling.
3. **Integration last.** Cross-repo work, external service connections.

Each task in the sequence should reference what previous tasks produced: "Architecture docs are in docs/architecture/. Build on those."

## Anti-Patterns

- Delegating vague tasks ("improve the codebase") — be specific
- Delegating tasks that need your context ("update based on what we discussed") — the subagent wasn't in the conversation
- Chaining subagents without reviewing intermediate output — drift compounds
- Letting subagents make architectural choices — they lack cross-project context
- Delegating to avoid thinking — you should know what you want before you ask for it
