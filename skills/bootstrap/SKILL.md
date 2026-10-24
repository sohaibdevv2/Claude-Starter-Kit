---
name: bootstrap
description: >
  Bootstrap a new project with a proper .claude/ setup for agentic development.
  Use when: setting up a new codebase for Claude Code, user says "set up this project",
  "bootstrap", "add Claude to this repo", or when .claude/ is missing in a project.
  Creates CLAUDE.md, CODEBASE.md, docs/, knowledge/, and optionally skills and hooks.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent
argument-hint: "[project-path] [--type code|knowledge]"
---

# /bootstrap — Set Up a Project for Claude Code

**First:** Read `LEARNINGS.md` in this skill's directory.

**Arguments:** `$ARGUMENTS`

If no project path given, use the current working directory.
If `--type` not specified, infer from context (has `src/`, `package.json`, `Cargo.toml` -> code; otherwise -> knowledge).

## Step 1: Reconnaissance

Before creating anything, understand what exists.

1. Read the project's existing README, package.json/Cargo.toml/pyproject.toml, or equivalent
2. `ls` the top-level directory structure
3. Check if `.claude/` already exists — if so, audit what's there and fill gaps instead of overwriting
4. Identify:
   - **Tech stack** (languages, frameworks, package manager)
   - **Build/lint/test commands** (from package.json scripts, Makefile, etc.)
   - **Major modules** (top-level dirs that represent distinct concerns)
   - **Project type**: `code` (has source code, build system) or `knowledge` (notes, docs, automation)

Present findings to the user in a table. Confirm before proceeding.

## Step 2: Create Directory Structure

```
.claude/
  CLAUDE.md              # Behavioral core (always created)
  CODEBASE.md            # Project overview + module index (code projects only)
  docs/                  # Module documentation (code projects only)
    <module>.md          # One per major module
  knowledge/             # On-demand context
    <framework>.md       # Language/framework conventions
  settings.local.json    # Project-scoped settings (if hooks needed)
```

For **knowledge projects**, skip `CODEBASE.md` and `docs/`. Add instead:
```
.claude/
  rules/                 # Domain rules (always loaded)
  knowledge/sessions/    # Session logs
```

Create the directories. Do NOT create empty placeholder files.

## Step 3: Write CLAUDE.md

Target: **30-40 lines max.** This burns context tokens every session.

Structure — adapt sections to the project:

```markdown
# <Project Name>

## Commands
- `<build command>` -- build the project
- `<test command>` -- run tests
- `<lint command>` -- lint/typecheck

## Process
- Before starting, read `.claude/CODEBASE.md` and relevant `.claude/docs/` files
- Do NOT use the Explore agent by default -- read documentation first
- After code changes, update documentation if interfaces or behavior changed
- When fetching context, state which documents you loaded

## Available Documentation
- `.claude/CODEBASE.md` -- project overview and module index
- `.claude/docs/<module>.md` -- <one-line description>

## Available Knowledge
- `.claude/knowledge/<topic>.md` -- <one-line description>
```

**What goes in CLAUDE.md:** commands, process instructions, file listings.
**What does NOT go in CLAUDE.md:** architecture details (-> CODEBASE.md), code conventions (-> knowledge/), module descriptions (-> docs/).

## Step 4: Write CODEBASE.md (Code Projects Only)

The entry point Claude reads first. Include:

1. What the project does (2-3 sentences)
2. Tech stack summary
3. Module index — one line per module linking to its doc file
4. `<!-- docs-synced-at: <commit-hash> -->` marker on line 1

```markdown
<!-- docs-synced-at: abc1234 -->
# <Project Name> — Codebase Overview

<What this project does. 2-3 sentences.>

## Tech Stack
<Language, framework, database, key libraries>

## Modules
| Module | Description | Docs |
|--------|-------------|------|
| `src/api/` | REST API routes and handlers | [docs/api.md](docs/api.md) |
| `src/web/` | Frontend application | [docs/web.md](docs/web.md) |
```

## Step 5: Write Module Docs (Code Projects Only)

One file per major module in `docs/`. Each file:

- What the module does (2-3 sentences)
- Key interfaces and type signatures (actual code, not prose)
- Links to source files
- Important design decisions and why
- Behavioral description (what happens when X is called)

These describe **behavior and intent** for an agent, not auto-generated API docs.

Use an Agent subagent per module (parallel) to scan source code and produce the doc.

## Step 6: Write Knowledge Files

Create `knowledge/<topic>.md` for each relevant framework/language convention.
Only create files for technologies actually used — don't speculate.

For **knowledge projects**, also create any needed `rules/*.md` files.

**Knowledge file design principles:**
- YAML frontmatter on every file (tags, created, last_reviewed, type)
- Imperative phrasing ("Use X for Y" not "X is used for Y")
- Tables over prose for structured data
- 40-80 lines per file, no redundancy — each fact lives in ONE place
- Actionable: "what do I need to know to act", not complete documentation

For **knowledge projects**, also set up MEMORY.md:
- Under 200 lines always (silently truncated beyond)
- Structure: Active State table, Key Decisions, Next Up, File Map
- Concise index pointing to topic files — not a comprehensive document
- "Next Up" section is mandatory — next session reads this first

## Step 7: Configure Hooks (If Needed)

Only add hooks when the project has specific needs:

| Need | Hook | Example |
|------|------|---------|
| Security boundaries | PreToolUse guard | Block writes outside project dir |
| Session continuity | PreCompact state dump | Save critical context before compaction |
| Reminders | Stop hook | "Update docs before ending" |

Write hooks to `scripts/` and register in `.claude/settings.local.json`.

## Step 8: Verify

Run through the checklist:

| # | Item | Check |
|---|------|-------|
| 1 | CLAUDE.md exists and is under 40 lines | |
| 2 | CLAUDE.md lists all doc and knowledge files | |
| 3 | CLAUDE.md has build/lint/test commands | |
| 4 | CODEBASE.md exists with module index (code projects) | |
| 5 | Each major module has a docs/ file (code projects) | |
| 6 | knowledge/ files exist for each framework used | |
| 7 | No placeholder/empty files | |
| 8 | CLAUDE.md disables Explore agent by default | |

Present the completed checklist to the user.

## Step 9: Initial Commit

Stage all `.claude/` files. Commit message: `feat: bootstrap .claude/ for agentic development`

Do NOT push without user approval.

## Rules

- **Minimal CLAUDE.md is non-negotiable.** 30-40 lines. Minimize noise, maximize signal — it gets very bad, very fast if you give information that you might not use.
- **Never dump architecture into CLAUDE.md.** That's what CODEBASE.md and docs/ are for.
- **Docs describe behavior, not API surface.** Write for an agent that needs to understand the codebase without reading every file.
- **Only create files for things that exist.** Don't create `knowledge/react.md` if the project doesn't use React.
- **Third-party projects get isolation.** Add to CLAUDE.md: `Do NOT update ~/claude-assistant/knowledge/, MEMORY.md, or task backlog for this project.`
- **Don't over-document.** Start lean. Fill gaps over time as you learn what's actually needed.
- **Adapt, don't template.** Every project is different. The structure above is a guide, not a rigid template. A 3-file Python script doesn't need module docs.
