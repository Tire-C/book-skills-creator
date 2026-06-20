# Generated pack file guide

This guide describes the public files expected in a generated skill pack.

| Path | Purpose |
|---|---|
| `README.md` | Explains the pack's scope, installation, entry point, and limitations |
| `source_index.md` | Records selected sources, extraction methods, and known gaps |
| `skill_map.md` | Lists every skill, route, dependency, and rejected candidate |
| `validation.md` | Records structural, routing, overlap, and grounding checks |
| `router/SKILL.md` | Selects the smallest appropriate atomic or combo skill |
| `atomic/<name>/SKILL.md` | Implements one focused, reusable capability |
| `combo/<name>/SKILL.md` | Orchestrates multiple atomic skills into a workflow |
| `references/concepts.md` | Stores supporting concepts that do not need active instructions |
| `references/glossary.md` | Defines source-specific terminology |
| `references/examples.md` | Contains short synthesized examples |
| `references/anti_patterns.md` | Records failure modes and misuse patterns |
| `references/chapters/` | Holds optional source-structure notes |

## Design rules

- Split broad capabilities into atomic skills.
- Use combo skills for orchestration, not duplicated instructions.
- Keep explanatory material in references when it is not an executable workflow.
- Ensure the router and skill map can reach every generated skill.
- Keep source provenance and extraction limitations visible.
