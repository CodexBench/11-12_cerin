# Repository and test guide

## Repository guide

- This is an established Python project. Inspect nearby implementation and existing tests before editing.
- Preserve compatibility with the checked-out version and keep unrelated behavior unchanged.
- Prefer a small root-cause correction over an issue-specific workaround.
- Do not commit, rewrite history, update dependencies, or perform broad formatting changes.

## Test guide

- Start with the narrowest existing test that reproduces or covers the reported behavior.
- Use the repository test runner under `bin/`; expand to nearby regression coverage only when useful.
- Add or update a focused regression test when it materially improves confidence.
- If a host dependency is unavailable, report it precisely and continue with static checks.
- Run `git diff --check`, inspect the final diff, and leave only the intended change.

