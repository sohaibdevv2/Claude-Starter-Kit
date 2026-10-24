# Security Rules

NON-NEGOTIABLE. These apply globally.

## Hard Blocks (enforced by ~/.claude/scripts/global-guard.py)
1. Cannot read/write `.env`, `.env.*`, `*.key`, `*.pem`, `*.secret`, `*.keystore`
2. Cannot read secrets via shell commands (cat, head, tail, etc.)
3. Cannot `git add` secrets files
4. Cannot `git push --force` or `git push -f`
5. Cannot write outside `$HOME/` or `/tmp/`
6. Cannot read outside `$HOME/`, `/tmp/`, `/usr/local/`, `/opt/homebrew/`

## Git Discipline
- Always commit and push before starting new features
- `git status` then stage relevant files, then commit, then push. Verify no sensitive files staged.
- Commit proactively after batching edits.
- PRs: only touch files in scope. Update PR description when pushing changes.
- Prefer feature branches over direct commits to main.

## Secrets Management
- Store API tokens as exports in `~/.zshrc` — don't create separate token files
- Read tokens from environment variables via `source ~/.zshrc` in Bash commands
- Never echo, log, or display token values — only verify length or first few chars

## Security-First Building
- When building security-sensitive infrastructure, establish and get approval on the security rules BEFORE writing any code

## Project Isolation
- **Third-party projects** (family, clients): own repo, CLAUDE.md boundary rule ("Do NOT update ~/claude-assistant/knowledge/, MEMORY.md, or task backlog"), session notes local.
- **Work projects**: protect with `global-guard.py` rules. Add company-specific blocks as needed (e.g., read-only repos, no autonomous push).
