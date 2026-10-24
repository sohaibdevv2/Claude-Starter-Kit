#!/usr/bin/env python3
"""Validate a skill directory meets conventions.

Usage:
    python validate_skill.py <path/to/skill-dir>
"""

import re
import sys
from pathlib import Path


def validate(skill_dir: Path) -> list[str]:
    errors = []

    # SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing SKILL.md")
        return errors

    content = skill_md.read_text()

    # Frontmatter
    fm_match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
    if not fm_match:
        errors.append("SKILL.md: missing YAML frontmatter")
    else:
        fm = fm_match.group(1)
        if "name:" not in fm:
            errors.append("SKILL.md: frontmatter missing 'name' field")
        if "description:" not in fm:
            errors.append("SKILL.md: frontmatter missing 'description' field")
        if "TODO" in fm:
            errors.append("SKILL.md: frontmatter still has TODO placeholders")

    # Body checks
    body = content.split("---", 2)[-1] if "---" in content else content
    if "TODO" in body:
        errors.append("SKILL.md: body still has TODO placeholders")

    lines = content.count("\n") + 1
    if lines > 500:
        errors.append(f"SKILL.md: {lines} lines (target: <500). Split into references/")

    # LEARNINGS.md
    if not (skill_dir / "LEARNINGS.md").exists():
        errors.append("Missing LEARNINGS.md")

    # Check for extraneous files
    bad_files = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md"}
    for f in skill_dir.iterdir():
        if f.name in bad_files:
            errors.append(f"Extraneous file: {f.name} (not needed in skills)")

    # Check referenced files exist (only relative paths, not absolute like ~/... or /...)
    for match in re.finditer(r"(?<![~/\w])references/[\w.-]+", content):
        ref = skill_dir / match.group()
        if not ref.exists():
            errors.append(f"Referenced file missing: {match.group()}")
    for match in re.finditer(r"(?<![~/\w])scripts/[\w.-]+", content):
        script = skill_dir / match.group()
        if not script.exists():
            errors.append(f"Referenced script missing: {match.group()}")

    return errors


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <skill-directory>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.is_dir():
        print(f"Error: {skill_dir} is not a directory")
        sys.exit(1)

    errors = validate(skill_dir)
    if errors:
        print(f"FAIL: {len(errors)} issue(s) in {skill_dir.name}/\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"OK: {skill_dir.name}/ passes validation")


if __name__ == "__main__":
    main()
