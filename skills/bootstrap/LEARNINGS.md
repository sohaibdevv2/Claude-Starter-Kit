# Bootstrap - Learnings

<!-- Lessons learned from running this skill. Read at start of every invocation. -->

- The #1 leverage point is minimal CLAUDE.md. Claude degrades fast with noisy context. 30-40 lines behavioral only.
- Parallel subagents for doc generation work well (one per module). Sequential subagents for implementation.
- Disable Explore agent in CLAUDE.md — it fills context with irrelevant code via grepping. Read docs first.
- `docs-synced-at` commit hash marker in CODEBASE.md enables tracking when docs were last updated.
- Third-party projects (family, clients) need isolation boundary in CLAUDE.md to prevent polluting ~/.claude/ state.
- For knowledge/personal projects, rules/ and sessions/ are more important than docs/. For code projects, docs/ and CODEBASE.md are the priority.
