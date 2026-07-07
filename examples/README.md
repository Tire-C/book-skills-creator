# Examples

This folder shows what Book Skills Creator produces, without shipping any real book text.

| Path | What it shows |
|---|---|
| [`sample-pack/`](sample-pack) | A complete synthetic pack: router, atomic skills, a combo workflow, references, skill map, source index, and validation record |
| [`output-tree.md`](output-tree.md) | The recommended layout of a generated pack at a glance |

## Reading the sample pack

The sample pack uses intentionally generic names so the structure stays in focus. A useful
reading order:

1. [`sample-pack/README.md`](sample-pack/README.md) — the pack's own scope and entry point.
2. [`sample-pack/router/SKILL.md`](sample-pack/router/SKILL.md) — how requests are dispatched to
   the smallest useful unit.
3. [`sample-pack/atomic/`](sample-pack/atomic) — two focused skills with one mission each.
4. [`sample-pack/combo/example-workflow/SKILL.md`](sample-pack/combo/example-workflow/SKILL.md) —
   a workflow that orchestrates the atomic skills without duplicating them.
5. [`sample-pack/references/`](sample-pack/references) — supporting context kept out of the
   active skills.
6. [`sample-pack/skill_map.md`](sample-pack/skill_map.md) and
   [`sample-pack/validation.md`](sample-pack/validation.md) — the audit trail: routes,
   dependencies, rejected candidates, and validation checks.

## Validation

The sample pack doubles as a test fixture. It must always pass:

```bash
python scripts/check_pack.py examples/sample-pack
```

The automated test suite exercises the same structure, so the example and the validator cannot
drift apart.
