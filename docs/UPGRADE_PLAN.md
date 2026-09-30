# Book Skills Creator 2.0 implementation plan

This plan records the decisions made after auditing v1.0.0 (`fdf35bd`) and `main` at `300e544`. The last published v1 workflow run inspected during the audit had succeeded. No 2.0 release or tag is part of this change.

## Baseline audit

| Area | v1 finding | 2.0 decision |
|---|---|---|
| Product | `SKILL.md` and `docs/SPECIFICATION.md` correctly insist on selected scope, capability-based decomposition, planning, rejection, and a router. | Preserve these as the agent-facing contract. |
| Selection | `inspect_source.py` recursively inspected symlinks and repeated overlapping paths; `extract_text.py` skipped symlinks, deduplicated, and excluded output. | One shared discovery implementation and one limit policy. |
| Extraction | TXT/Markdown text was flattened, and DOCX read only `word/document.xml` without checking archive expansion. `full_text.txt` was the main artifact. | Structured evidence units, retained compatibility text, bounded archive access. |
| Planning | The skill describes a plan, but no machine contract records decisions before generation. | Draft/ready JSON plan with candidates, rejections, gaps, overlap, conflicts, and risks. |
| Generation | `create_pack_scaffold.py` always writes `example-a` and `example-workflow`; `templates/` are not consumed by it. | Exact rendering from the ready plan; preserve old templates only as migration examples. |
| Validation | `check_pack.py` only tests required paths and whether `name:` and `description:` appear anywhere. It cannot verify YAML frontmatter, routes, dependencies, evidence, or file drift. | Manifest-based graph and file validator, with severity and JSON report. |
| Provenance | No stable source hashes or evidence links, so a changed source cannot mark a skill stale. | Source/unit hashes, evidence references, and impact analysis. |
| Safety | Local processing and Git ignore are good; archive bombs, unbounded traversal, prompt injection instructions, and copied passages were not enforced or documented sufficiently. | Configurable limits, archive checks, explicit source trust rule, privacy tests, and copying warnings. |
| Tests/CI | Synthetic helper tests and a Linux 3.10/3.12 workflow exist, but the generic sample has no actual selected source and does not prove decomposition. | Original multi-source fixture, failure tests, and Windows matrix. |
| Release | `v1.0.0` is published; post-release presentation work is in `[Unreleased]`. | Keep history intact and document 2.0 work under `[Unreleased]`; do not publish a release or tag. |

## Preserve

The root Agent Skill, explicit source selection, planning before generation, atomic/combo/router/reference roles, local standard-library helpers, and synthetic tests remain the foundation. The v1 sample pack remains readable through a legacy validation path during migration.

## Correct

Inspection and extraction currently disagree about selection and symlinks. DOCX reading lacks archive limits. Extraction flattens structure. The scaffold writes example skills, while validation checks mostly file existence and substring metadata. The README describes source-grounding and routing checks that code cannot enforce.

## Architecture

1. One discovery module applies explicit paths/globs, symlink rules, deduplication, output exclusion, and configurable size/count limits.
2. Extractors emit a local `sources.json` with source metadata and ordered evidence units. `full_text.txt` and `metadata.json` remain compatibility artifacts. Archive readers enforce limits before decompression.
3. An agent fills a draft `plan.json` with capability decisions and concise synthesized instructions. The CLI creates only the draft structure; it never guesses capabilities.
4. A versioned `pack.json` is the canonical pack IR. The builder deterministically renders exactly its atomic, combo, router, and reference entries. Each skill cites evidence IDs.
5. Validation checks schema, identities, paths, graph reachability/cycles, evidence references, generated file agreement, suspected overlap, and optional verbatim reuse. Semantic quality and conflict resolution remain explicit review work.
6. Update compares old and fresh source/evidence hashes and reports affected skills for deliberate regeneration.

## Sequence and verification

Implement discovery and extraction, then IR/build/validation, then CLI and compatibility wrappers, then a synthetic manual and failure tests. Run unit tests, compilation, pack validation, and a real CLI flow. Update the root skill, security model, README, docs, roadmap, changelog, and CI to match tested behavior.

## Risks and deferred work

Heading recovery from DOCX/EPUB is approximate; page layout and footnotes remain unsupported. PDF extraction uses an optional local `pdftotext` adapter, and OCR remains external. No deterministic rule can prove a synthesized procedure is semantically faithful, decide whether two capabilities truly overlap, or reconcile conflicting sources. Behavioral routing cases are review artifacts, not automatically judged by the CLI.
