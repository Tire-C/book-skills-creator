# Architecture

Book Skills Creator 2.0 is an Agent Skill plus a local, standard-library Python core. Its pipeline is:

```text
explicit selection → shared discovery → structured extraction → sources.json
→ agent capability analysis → ready plan.json → deterministic build → pack.json + SKILL.md files
→ deterministic validation → semantic and behavioral review
```

`book_skills/discovery.py` owns scope, symlinks, deduplication, output exclusion, and limits. `extraction.py` converts each source into ordered evidence units. `pack.py` defines the canonical plan/pack representation and renders Markdown. `validation.py` checks structural contracts and the capability graph. `cli.py` exposes the commands; `scripts/` contains the CLI entry point and compatibility wrappers.

## Responsibility boundary

Code owns path selection, bytes and archive limits, source and unit hashes, stable IDs, serialization, names, file agreement, evidence references, routes, dependencies, cycles, orphans, and reports. The agent owns capability discovery, distinctions between knowledge and procedure, overlap decisions, synthesis, conflict interpretation, and routing behavior. Similarity and verbatim checks produce review warnings; neither decides semantic truth.

## Source model

The ignored `sources.json` contains `sources[]`, each with a logical ID, selected path, format, byte count, source SHA-256, extraction method/version, extraction timestamp, extracted SHA-256, warnings, and `units[]`. Units carry stable IDs derived from source identity and heading context, kind, heading path, order, optional line range, length, hash, and local text. Line ranges are emitted for Markdown and plain text; DOCX/HTML/EPUB do not claim page or line precision. IDs remain stable for edits within a unit, though inserting an earlier unit of the same kind in a section can shift later IDs. The hash detects changed content.

## Pack graph and provenance

`pack.json` is the canonical IR. It retains source metadata and an evidence index **without source text**, candidate decisions, atomic and combo units, dependencies, routes, references, conflicts, uncertainties, and behavioral cases. Router routes point to `atomic:<id>`, `combo:<id>`, or `reference:<id>`. Combo dependencies point to atomic or combo nodes. Every unit must be reachable from a route and every cited evidence ID must exist. Validation detects dependency cycles and missing targets. Generated Markdown is reproducible from `pack.json`, so manual drift is detectable.

The pack records source and unit hashes. `validate --extraction` compares both directions: removed or changed planned material is stale, while a newly selected source or a new unit in an existing source is unreviewed. The plan's evidence index includes all extracted units, even those unused by capabilities, so ordinary unused evidence does not cause an error. `update` reports changed, new, and removed units plus affected skills, including dependent combos; reference nodes use the same `reference:<id>` prefix as routes. An agent must revise impacted synthesis and inspect new evidence for additional capabilities before rebuilding. Changes to unreferenced evidence still mark the source changed, but may affect no existing skill.

## Validation limits

The validator can prove structural consistency, not that a source truly teaches a procedure or that a router will behave correctly in every agent. Agent/human review must inspect evidence, resolve conflicts, evaluate suggested overlap, and run the behavioral cases. See [Specification](SPECIFICATION.md).
