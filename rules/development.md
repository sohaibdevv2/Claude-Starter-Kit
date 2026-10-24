# Development Standards

Code quality and testing conventions for working with Claude.

## Code Quality

### Limits

- Functions: 100 lines max, cyclomatic complexity 8 max
- Parameters: 5 positional max
- Line length: 100 characters

### Zero Warnings

Fix every warning from linters, type checkers, and tests. If a warning truly can't be fixed, add an inline ignore with a justification comment. A clean output is the baseline, not the goal.

### Comments

Code should be self-documenting. No commented-out code — delete it. If you need a comment to explain WHAT the code does, refactor instead. Comments explain WHY, not WHAT.

### Error Handling

- Fail fast with clear, actionable messages
- Never swallow exceptions silently
- Include context: what operation, what input, what to do about it

## Testing

**Test behavior, not implementation.** Tests verify what code does, not how. If a refactor breaks your tests but not your code, the tests were wrong.

**Test edges and errors.** Empty inputs, boundaries, malformed data, missing files. Bugs live in edges. Every error path should have a test that triggers it.

**Mock boundaries, not logic.** Only mock things that are slow (network, filesystem), non-deterministic (time, randomness), or external services you don't control.

**Verify tests catch failures.** Break the code, confirm the test fails, then fix.

## Reviewing Code

Evaluate in order: architecture, code quality, tests, performance. Before reviewing, sync to latest remote.

For each issue: describe concretely with file:line references, present options with tradeoffs when the fix isn't obvious, recommend one, and ask before proceeding.

## Before Committing

1. Re-read your changes for unnecessary complexity, redundant code, unclear naming
2. Run relevant tests — not the full suite
3. Run linters and type checker — fix everything before committing

## Commits

- Imperative mood, 72 char subject line max, one logical change per commit
- Never amend or rebase commits already pushed to shared branches
- Prefer feature branches over direct commits to main
