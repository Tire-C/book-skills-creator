# Combo template

Purpose: one workflow that combines several focused units.

Use when: the request needs a sequence and one atomic unit is not enough.

Units:
- unit-a
- unit-b
- unit-c

Flow:
1. Run the first unit.
2. Pass its result to the next unit.
3. Continue until the final unit.
4. Return one final answer.

Handoff rules:
- each unit receives only what it needs
- each unit has a clear role
- the combo does not repeat the atomic content

Checks:
- workflow has a clear goal
- order is clear
- no duplicated work
- final output is useful
