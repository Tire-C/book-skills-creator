# Migration from v1

v1 packs were Markdown-only. Their basic layout still works as an Agent Skill collection, and `check_pack.py <pack> --legacy` checks required files and frontmatter. The validator returns a `legacy-pack` warning because no machine-readable graph or source evidence exists. A missing manifest without `--legacy` is an error.

To get full 2.0 validation, re-extract the **explicitly selected** original sources, create a draft plan, and map each existing atomic, combo, route, and reference entry to evidence IDs. Revisit decomposition and rejected candidates; do not infer grounding from the old Markdown alone. Mark the plan `ready`, build to a new output directory, then validate with the fresh `sources.json`. Compare behavior with the old pack before switching use.

Existing helper commands remain: `inspect_source.py`, `extract_text.py`, `preflight.py`, and `check_pack.py` forward to the unified CLI. Extraction now also writes structured `sources.json`; `full_text.txt` and `metadata.json` remain available. `create_pack_scaffold.py` is deliberately changed: it takes a ready plan and `--output`, and no longer makes `example-a` or `example-workflow` placeholders. The old static templates and example are retained under `examples/v1-*`.

The 2.0 renderer treats `pack.json` as authoritative. Edit the plan and rebuild to change generated files; validation flags hand-edited drift. If a source changes, run `update` against a fresh extraction to identify stale skills. The command reports impact but does not rewrite semantic instructions.
