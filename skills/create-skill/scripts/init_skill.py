#!/usr/bin/env python3
"""Scaffold a new skill directory with template files.

Usage:
    python init_skill.py <skill-name> --path <output-directory>
    python init_skill.py bootstrap --path ~/.claude/skills
"""

import argparse
import sys
from pathlib import Path


def to_title(name: str) -> str:
    return " ".join(w.capitalize() for w in name.split("-"))


def create_skill(name: str, output: Path) -> None:
    skill_dir = output / name
    if skill_dir.exists():
        print(f"Error: {skill_dir} already exists")
        sys.exit(1)

    skill_dir.mkdir(parents=True)
    title = to_title(name)

    # SKILL.md
    (skill_dir / "SKILL.md").write_text(f"""---
name: {name}
description: >
  TODO — What this skill does and when to use it. Be specific: Claude uses this
  to decide when to activate. Include trigger phrases and contexts.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "[args]"
---

# /{name} — {title}

**First:** Read `LEARNINGS.md` in this skill's directory.

**Arguments:** `$ARGUMENTS`

## Step 1: TODO

TODO: First step of the workflow.

## Step 2: TODO

TODO: Next step.

## Rules

- TODO: Constraints, gotchas, things to never do.
""")

    # LEARNINGS.md
    (skill_dir / "LEARNINGS.md").write_text(f"""# {title} - Learnings

<!-- Lessons learned from running this skill. Read at start of every invocation. -->
""")

    print(f"Created: {skill_dir}/")
    print(f"  SKILL.md      — fill in description, steps, rules")
    print(f"  LEARNINGS.md  — accumulates as skill runs")
    print()
    print("Optional dirs (create only if needed):")
    print("  scripts/     — deterministic code")
    print("  references/  — on-demand docs")
    print("  assets/      — templates, files used in output")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new skill")
    parser.add_argument("skill_name", help="kebab-case name (e.g., 'my-skill')")
    parser.add_argument(
        "--path",
        default=".claude/skills",
        help="Parent directory (default: .claude/skills in current workspace)",
    )
    args = parser.parse_args()

    name = args.skill_name.lower()
    if not name.replace("-", "").isalnum():
        print("Error: name must be lowercase alphanumeric + hyphens")
        sys.exit(1)
    if name.startswith("-") or name.endswith("-") or "--" in name:
        print("Error: no leading/trailing/consecutive hyphens")
        sys.exit(1)

    output = Path(args.path).resolve()
    if not output.exists():
        output.mkdir(parents=True)

    create_skill(name, output)


if __name__ == "__main__":
    main()
