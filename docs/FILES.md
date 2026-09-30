# Generated pack files

| Path | Purpose |
|---|---|
| `pack.json` | Canonical 2.0 IR: source/evidence metadata, capability graph, candidate decisions, routes, references, conflicts, uncertainties, and behavioral cases |
| `README.md` | Scope and router entry point |
| `source_index.md` | Source hashes, extraction methods, and warnings |
| `skill_map.md` | Atomic/combo inventory, dependencies, rejected proposals, and unresolved issues |
| `validation.md` | How to run the current validator; the live report comes from the CLI |
| `router/SKILL.md` | Smallest suitable route, explanation, clarification, and unsupported behavior |
| `atomic/<id>/SKILL.md` | One focused capability with inputs, procedure, output, constraints, evidence |
| `combo/<id>/SKILL.md` | Workflow orchestration and handoffs |
| `references/<id>.md` | Supporting knowledge, linked to evidence |

The file tree is rendered from a `ready` plan. There are no production placeholders. Markdown content is checked against `pack.json`; edit the plan and rebuild to change a generated pack. Behavioral cases live in the manifest for agent/human evaluation.
