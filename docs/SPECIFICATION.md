# Pack and validation specification (2.0)

## Plan and pack contract

`book-skills plan <sources.json> <name> --output plan.json` creates a draft containing these top-level keys:

| Key | Meaning |
|---|---|
| `schema_version`, `status` | `2.0`; `draft` until an agent completes the architecture, then `ready` |
| `pack` | `name` (ASCII lowercase slug), `title`, `description` |
| `sources` | Selected source IDs, paths, formats, byte counts, hashes, extraction methods, versions, and warnings |
| `evidence` | Unit ID, source ID, kind, heading path, order, optional line range, length, hash; no raw text |
| `extraction_gaps` | Skipped inputs and source extraction warnings |
| `candidates` | Accepted, reference-only, or rejected proposals; rejected entries need reasons |
| `atomic` | Focused capabilities |
| `combo` | Orchestrated workflows and dependencies |
| `routes` | Activation condition and target node |
| `references` | Supporting knowledge and evidence IDs |
| `conflicts`, `uncertainties` | Explicit unresolved source issues and limitations |
| `overlaps`, `validation_risks` | Suspected overlap and risks requiring agent/human review |
| `behavior_tests` | Inspectable routing cases for semantic review |

An atomic entry needs `id`, `title`, `description`, `mission`, `use_when`, nonempty `inputs`, `steps`, `output`, `constraints` (possibly empty), nonempty `evidence`, and `grounding` (`grounded` or `review`). A combo needs the same descriptive fields, at least two `dependencies`, a nonempty high-level `flow`, `output`, `evidence`, and `grounding`. A reference needs `id`, `title`, `content`, and `evidence`. The complete synthetic manifest at [`examples/sample-pack/pack.json`](../examples/sample-pack/pack.json) is an executable example.

Every generated atomic, combo, or reference unit must be linked from a candidate decision. Accepted candidates map to atomic/combo nodes, reference-only candidates map to reference nodes, and rejected candidates retain a reason. Each candidate cites evidence. This makes the decomposition decision inspectable without requiring an arbitrary skill count.

IDs and generated names use ASCII lowercase letters, digits, and single hyphens, with a 64-character maximum. Unit IDs are unique across atomic, combo, and reference categories. Generated frontmatter names are `<pack-name>-<unit-id>`; router is `<pack-name>-router`. A generated pack needs at least one selected source and one atomic skill.

Routes use `atomic:<id>`, `combo:<id>`, or `reference:<id>`. Combo dependencies use atomic or combo targets. Nested combos are permitted; cycles and self-dependencies are errors. The renderer writes exactly the declared units. References do not become skills.

Behavioral cases have `type` (`positive`, `negative`, `combo`, `reference`, `ambiguous`, or `unsupported`) and `request`. The first four also name a `target`: atomic for positive/negative, combo for combo, and reference for reference. Validation verifies case shape and target category; an agent or human judges the expected behavior.

## Deterministic validation

`validate` reports `PASS`, `PASS_WITH_WARNINGS`, or `FAIL`, plus independent `ERROR` and `WARNING` findings in `--json` mode. Errors include missing/invalid schema fields, invalid names or hashes, duplicate IDs, bad evidence/source references, broken dependencies or routes, cycles, orphan units, missing generated files, unlisted files, file/manifest drift, invalid frontmatter, and broken local links. With `--extraction`, changed or removed planned source/unit hashes and extraction methods are errors; a newly selected source yields `new-source-unreviewed`, and a new unit in an existing source yields `new-evidence-unreviewed`. Invalid fresh snapshots yield `invalid-extraction`. The new-source finding covers its units without one error per unit. Warnings include unresolved source conflicts, units marked for grounding review, suspicious mission overlap, copied atomic procedure text inside a combo, and 30-word contiguous verbatim reuse from extracted text. The overlap and copying checks are screening tools, not semantic verdicts. The JSON report gives counts for sources, skills, routes, grounding declarations, unresolved conflicts, graph issues, and copying/overlap warnings without combining them into a quality score.

Passing validation does not certify factual grounding, complete capability discovery, absence of all copying, or correct routing by every agent. Keep rejected candidates, conflicts, and uncertainties visible in the plan. Review the source evidence for each capability.

## Legacy packs

A v1 pack without `pack.json` can still be checked with the explicit `validate --legacy` option for its basic file structure and frontmatter. It receives a `legacy-pack` warning because graph and provenance checks are unavailable. Without `--legacy`, a missing manifest is an error. Rebuild from a ready 2.0 plan for full validation.
