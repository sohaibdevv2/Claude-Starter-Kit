---
name: plan
description: Structured workflow for planning and implementing new features, skills, scripts, or major changes. Use when the user asks to build something new, add a skill, create infrastructure, or make architectural changes. Guides through explore, plan, approve, implement, verify, update.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, WebSearch, WebFetch, AskUserQuestion
argument-hint: "[feature description]"
---

# Plan & Implement Workflow

**First:** Read `LEARNINGS.md` (in this skill's directory) before proceeding.

You are executing a structured 6-phase workflow for building or changing project features. Follow each phase in order. Do NOT skip phases or start implementing before approval.

The user's request: `$ARGUMENTS`

---

## Phase 1: Explore

Understand the current project state before designing anything.

1. Read `CLAUDE.md` for project conventions, key paths, and existing skills
2. Look for a file map or project structure documentation
3. Read any existing skills, scripts, or files that relate to what's being built
4. Identify reusable patterns, utilities, or templates from existing code

Do NOT propose anything yet — just gather context.

---

## Phase 1.5: Tool Discovery (autonomy-first)

Before designing a custom solution, search for existing tools that do the job.

1. **Search for MCP servers** — WebSearch for `"<service-name> MCP server"` on GitHub/npm/PyPI
2. **Search for official SDKs** — Check if the service has an official Python/Node SDK
3. **Check existing MCP servers** — Read `.mcp.json` for already-connected servers
4. **Evaluate options**: MCP server > official SDK > custom wrapper
5. **If an MCP server exists**: configure it in `.mcp.json` instead of writing custom code
6. **If no MCP server**: proceed with custom implementation but note it as a future improvement target

---

## Phase 2: Design

Classify what's being built and design the implementation.

1. **Classify** the change type: skill / script / database / config / structure / other
2. **List files** to create (with paths) and files to modify
3. **Define dependencies** between files (what must be created first)
4. **Detail the design** based on type
5. **Ask clarifying questions** via AskUserQuestion if requirements are ambiguous — do NOT guess

---

## Phase 3: Approve

Present the plan and wait for explicit approval.

Format the plan as:

### What
- Files to create (path + one-line description each)
- Files to modify (path + what changes)

### Why
- What problem this solves or capability it adds

### How
- Implementation order with dependencies noted
- Key design decisions and rationale

### Verify
- Specific steps to confirm it works after implementation

Then ask: **"Approve this plan, or suggest changes?"**

Do NOT proceed to Phase 4 until the user approves.

---

## Phase 4: Implement

Execute the approved plan step by step.

1. Create directories first, then files in dependency order
2. For each file: write it, verify it exists and is well-formed
3. For each modification: read current file, make edit, verify change
4. Follow all project conventions from CLAUDE.md

---

## Phase 5: Verify

Run the verification steps defined in the approved plan. Report results. If anything fails, fix it before proceeding.

---

## Phase 6: Update Project Files

Update all project metadata to reflect the changes.

1. Update any file map or structure documentation
2. Update `CLAUDE.md` if the change affects skills, paths, or workflows
3. Update settings files if new permissions or hooks are needed
4. Confirm all updates are done, then summarize what was built
