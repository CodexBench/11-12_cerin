# Test guide

- Start with the narrowest existing test that reproduces or covers the reported behavior.
- Use the repository test runner under `bin/`; expand to nearby regression coverage only when useful.
- Add a focused regression test when it materially improves confidence.
- If a host dependency is unavailable, report the limitation and continue with static checks.
- Run `git diff --check`, inspect the final diff, and do not claim tests passed unless they ran.

