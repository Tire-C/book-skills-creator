---
name: lantern-field-desk-router
description: "Route requests to the smallest supported capability in Lantern Field Desk."
---

# Lantern Field Desk router

Choose one atomic skill when it suffices. Use a combo for a multi-step request. Use a reference for explanation. Ask for clarification when ambiguous; state limits for unsupported requests.

## Routes
- Record a new report → `atomic:intake-signal`
- Choose an action for an intake record → `atomic:decide-route`
- Confirm an escalated case → `atomic:verify-case`
- Handle a report end to end → `combo:respond-to-signal`
- Explain desk terminology → `reference:terms`
