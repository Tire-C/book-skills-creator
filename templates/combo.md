# Combo template

Purpose: one workflow that combines several focused units.

Use when: the request needs more than one unit.

Units:
- unit-a
- unit-b
- unit-c

Flow:
1. Run unit-a.
2. Use its result as input for unit-b.
3. Use the next result for unit-c.
4. Return one final answer.

Checks:
- each unit has a role
- order is clear
- no duplicated work
