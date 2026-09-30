# Synthetic examples

`sources/field-manual.md` and `sources/field-errata.md` are original fixtures for the actual product concept. They contain several independent procedures, a combined workflow, pure terminology, a rejected overlapping candidate, an ambiguity, an anti-pattern, an exception, a visible contradiction, and source-level prompt injection text that must stay inert.

`sample-pack/` is a 2.0 pack built from those selected sources by `build_sample.py`. Inspect `pack.json` first, then `router/SKILL.md`, the atomic/combo files, and the references. The manifest includes rejected candidates and behavioral routing cases. Validation reports an unresolved conflict on purpose.

`v1-sample-pack/` and `v1-templates/` preserve the original structural example and templates for migration review. They are not the 2.0 generation source of truth. See [output tree](output-tree.md).
