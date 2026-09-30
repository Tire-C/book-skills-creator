---
name: sample-pack-example-workflow
description: "Use this sample combo workflow when the task needs both sample atomic units in sequence."
---

# Example workflow

Purpose: demonstrate how a combo unit orchestrates atomic units.

Units:
- sample-pack-example-a
- sample-pack-example-b

Flow:
1. Run Example A.
2. Pass its result to Example B.
3. Return one final result.

Output: one combined result.
