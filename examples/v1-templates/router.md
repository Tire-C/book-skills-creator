# Router template

Purpose: choose the best unit for the user request.

Inputs:
- user request
- available atomic units
- available combo units
- reference files

Decision rules:

1. Use one atomic unit when one focused capability is enough.
2. Use one combo unit when the task needs a sequence.
3. Use references when the user asks for explanation only.
4. Ask one short question when the request is unclear.
5. Say the pack does not support the request when no unit applies.

Routing table:

| Need | Route |
|---|---|
| one capability | atomic unit |
| multi-step task | combo unit |
| explanation | references |
| unclear | clarify |
| unsupported | limitation |
