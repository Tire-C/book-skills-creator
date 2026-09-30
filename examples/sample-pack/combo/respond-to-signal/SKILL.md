---
name: lantern-field-desk-respond-to-signal
description: "Orchestrate intake, routing, and any needed verification for a field report."
---

# Respond to a signal

## Mission

Carry a report through the smallest complete response path.

## Use when

The user asks to handle a report from arrival through its next disposition.

## Dependencies

- atomic:intake-signal
- atomic:decide-route
- atomic:verify-case

## Flow

1. Run intake and pass the case ID with decision-relevant facts to routing.
2. Run routing and branch on its selected path.
3. For escalation, run verification; for a watch note, schedule review; for a duplicate, link the existing case.

## Output

A case record with its chosen route and current disposition.

## Evidence

- src-1a0a594410af81c1-fc8d7cdc3c81
- src-1a0a594410af81c1-c3edaa2cf8d7
- src-1a0a594410af81c1-0ae8874e4bd4
- src-1a0a594410af81c1-6b984f51f0fe
- src-1a0a594410af81c1-19512bb71bd7
- src-1a0a594410af81c1-92a3339d4067
- src-1a0a594410af81c1-f222f3881b1a
- src-1a0a594410af81c1-6f5e034784ae
- src-1a0a594410af81c1-34e1f929478c
- src-1a0a594410af81c1-61466bf98140
- src-cb165ae4cf6701fc-ad56fdaec1b8
- src-cb165ae4cf6701fc-4471191b7180
