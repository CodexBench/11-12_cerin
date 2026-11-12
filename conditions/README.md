# Week 4 condition operationalization

## WHEN: repository documentation × additional instructions

The code, issue, model, evaluator, and base commit remain fixed. Two factors change:

1. Repository documentation level: `full`, `partial`, or `sparse`.
2. Additional instructions: `off` or `on` (`instructions/combined/AGENTS.md`).

Documentation profiles are operationalized as follows for the selected SymPy tasks:

- `full`: keep the base checkout unchanged.
- `partial`: hide contribution and governance entry points (`CONTRIBUTING.md`, `PULL_REQUEST_TEMPLATE.md`, `CODE_OF_CONDUCT.md`).
- `sparse`: apply `partial`, then also hide `README.md`, `doc/README.rst`, and `.github`.

Hidden paths are removed from the agent workspace after the base commit is verified. They are excluded from the captured agent patch, so the evaluator receives only the agent's product-code changes. Missing paths are recorded rather than treated as an error.

This manipulation reduces discoverable repository guidance, but it is not equivalent to removing every docstring or code comment. It is therefore a practical documentation-availability proxy, not an absolute “no documentation” condition.

## WHAT: instruction information type

The `full` base repository state is held fixed while the injected root `AGENTS.md` varies:

- `none`: no additional instructions.
- `repo`: repository structure and editing rules only.
- `test`: testing and verification workflow only.
- `combined`: both information types.

`full_off` is reused as WHAT `none`, and `full_on` is reused as WHAT `combined`. This yields eight unique pilot runs rather than duplicating identical conditions.

