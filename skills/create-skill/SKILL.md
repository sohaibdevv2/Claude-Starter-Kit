---
name: create-skill
description: >
  Create a new Claude Code skill. Use when the user wants to build a new slash-command
  skill, extend Claude with a specialized workflow, or asks to create/add a skill.
  Handles scaffolding, SKILL.md authoring, and validation.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: "[skill-name] [--description 'what it does']"
---

# /create-skill — Skill Builder

**First:** Read `LEARNINGS.md` in this skill's directory.

**Arguments:** `$ARGUMENTS`

## Process

### Step 1: Understand

If `$ARGUMENTS` provides a skill name and description, proceed. Otherwise ask:

1. What should this skill do? (one sentence)
2. When should it trigger? (what would the user say/do?)
3. What resources does it need? (scripts, reference docs, templates?)

Keep questions to one message. Don't over-interview.

### Step 2: Scaffold

Run the init script:

```bash
python3 .claude/skills/create-skill/scripts/init_skill.py <skill-name> --path .claude/skills
```

This creates the directory with template files. If `--path` is omitted, defaults to `.claude/skills` in the current workspace.

### Step 3: Write SKILL.md

Replace the template content. Follow these rules:

**Frontmatter (required):**
- `name`: kebab-case, max 64 chars. Becomes the `/slash-command`.
- `description`: Comprehensive. This is how Claude decides when to activate. Include trigger phrases, contexts, use cases.

**Frontmatter (optional, add only when needed):**
- `allowed-tools`: Restrict tool access (e.g., `Read, Grep, Glob, Bash`)
- `argument-hint`: Autocomplete hint (e.g., `[filename]`, `[--dry-run]`)
- `fork: true`: Run as sub-agent (use for data-heavy skills that would bloat main context)
- `disable-model-invocation: true`: Manual `/name` only, no auto-trigger

**Body rules:**
- Start with "Read LEARNINGS.md" instruction
- Use `$ARGUMENTS` placeholder for user input
- Imperative form ("Run the script", not "You should run the script")
- Keep under 500 lines. Split longer content into `references/` files.
- Reference bundled resources with relative paths + describe when to read them
- Match freedom to fragility: exact scripts for brittle ops, text guidance for flexible tasks

**Body structure (adapt as needed):**
```markdown
# /name -- One-Line Summary

**First:** Read `LEARNINGS.md` in this skill's directory.
**Arguments:** `$ARGUMENTS`

## Step 1: [Name]
[What to do, expected outcome]

## Step 2: [Name]
[What to do, expected outcome]

## Rules
[Constraints, gotchas, things to never do]
```

### Step 4: Write LEARNINGS.md

Start with an empty learnings file. It will accumulate as the skill runs.

```markdown
# <Skill Name> - Learnings

<!-- Lessons learned from running this skill. Read at start of every invocation. -->
```

### Step 5: Write Supporting Files (if needed)

- **`scripts/`** — For operations that need deterministic reliability or get rewritten repeatedly. Python preferred.
- **`references/`** — On-demand docs SKILL.md tells Claude when to read. For detailed workflows, schemas, examples that would bloat SKILL.md.
- **`assets/`** — Templates, images, boilerplate used in output (not loaded into context).

Delete any empty dirs the init script created that aren't needed.

### Step 6: Validate

Check the result:

```bash
python3 .claude/skills/create-skill/scripts/validate_skill.py .claude/skills/<skill-name>
```

Fix any issues reported.

### Step 7: Update Index

Add the new skill to the `CLAUDE.md` Available Skills section.

## Rules

- One skill = one concern. Don't bundle unrelated workflows.
- Description is the trigger — if it's vague, the skill won't activate when needed.
- SKILL.md is for another Claude instance. Include what's non-obvious, skip what any model already knows.
- No hardcoded absolute paths except `~/claude-assistant/` and `~/`. Use relative paths within the skill dir.
- Test the skill by running it once before reporting done.
