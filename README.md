# Book Skills Creator

**A book is not one capability.** Book Skills Creator turns explicitly selected books, manuals, SOPs, or other documents into modular, source-grounded Agent Skill packs. An agent discovers the procedures and decisions in the source; local Python code preserves evidence and validates the resulting structure.

The output separates focused **Atomic Skills**, orchestrating **Combo Skills**, a **Router** that chooses the smallest suitable unit, and **References** for knowledge that does not need to be a skill. Chapter boundaries never determine the number of skills.

This keeps a request for one procedure from loading an entire book's instructions, while still allowing a larger workflow to combine the procedures it needs. Typical sources include an operations manual plus errata, a collection of SOPs, or course notes with several independent methods.

```text
selected sources → structured evidence → agent capability plan → pack.json
→ atomic + combo + router + references → validation and review
```

## Quickstart

Install this repository in an Agent Skills-compatible skills directory, or use its helpers directly with Python 3.10+:

```bash
git clone https://github.com/Tire-C/book-skills-creator.git
cd book-skills-creator
python scripts/book_skills.py preflight
```

Tell your agent which sources to process, for example: “Use Book Skills Creator on `./manual.md` and `./errata.md`; create a pack named `field-operations`.” The Agent Skill in [SKILL.md](SKILL.md) directs semantic analysis and planning. The local commands are:

```bash
python scripts/book_skills.py inspect ./manual.md ./errata.md --json
python scripts/book_skills.py extract ./manual.md ./errata.md --output .book_skills_work --json
python scripts/book_skills.py plan .book_skills_work/sources.json field-operations --output .book_skills_work/plan.json
# The agent completes the draft plan from evidence and sets status to ready.
python scripts/book_skills.py build .book_skills_work/plan.json --output ./field-operations
python scripts/book_skills.py validate ./field-operations --extraction .book_skills_work/sources.json --json
```

The `plan` command deliberately creates a **draft**, not guessed skills. An agent must classify candidates, synthesize source-supported instructions, record rejected proposals and conflicts, design routes, and mark the plan `ready` before `build` accepts it. See the [pack contract](docs/SPECIFICATION.md) and the original [synthetic example](examples/sample-pack/pack.json).

## What 2.0 verifies

The standard-library core shares one explicit source discovery policy between inspection and extraction. It emits ordered evidence units with source and content hashes, structure and line ranges where recoverable, methods, versions, and warnings. A canonical `pack.json` drives exact Markdown generation. Validation checks names, metadata, manifest/file agreement, evidence IDs, routes, dependencies, cycles, orphans, changed or newly selected sources and evidence when a fresh extraction is provided, and suspicious overlap or long verbatim copying.

Semantic judgments remain the agent's responsibility: whether a procedure is truly supported, how to split overlapping capabilities, how to interpret conflicting sources, and how the router behaves on real requests. The manifest holds explicit behavioral cases for review. Reports use findings and severity, not a fabricated quality score.

## Local formats and privacy

Built-in extraction covers TXT, Markdown, lightweight DOCX, HTML, and EPUB. A local `pdftotext` executable is an optional PDF adapter; OCR is not built in. RTF and MOBI/AZW can be identified but not extracted. See [source processing](docs/SOURCE_PROCESSING.md) for structure and limits.

No account, cloud service, database, or API key is required. Source text stays in the Git-ignored `.book_skills_work/` directory and is not printed by helpers. Documents are treated as untrusted data, including any instructions embedded in them. Generated packs synthesize procedures and retain compact evidence references instead of reproducing long source passages.

## Updating and compatibility

After a selected source changes, extract it again and run:

```bash
python scripts/book_skills.py update ./field-operations .book_skills_work/sources.json --json
```

The report identifies changed evidence and affected skills, including dependent combos. Review and regenerate those units before rebuilding. Automatic semantic rewriting is not claimed.

[`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) is a historical inspiration for the book-to-skill idea. Book Skills Creator follows a different architecture: it plans and validates a routed pack of atomic and combo capabilities rather than treating one document as one skill.

The v1 helper names (`inspect_source.py`, `extract_text.py`, `preflight.py`, and `check_pack.py`) remain as wrappers. `create_pack_scaffold.py` now requires a ready plan and writes exactly its units. Validate a v1 pack without `pack.json` using the explicit `--legacy` flag; the former synthetic pack and templates are preserved under `examples/v1-*`. See [migration](docs/MIGRATION.md).

## Verify the repository

```bash
python -m unittest discover -s tests
python -m compileall -q book_skills scripts tests examples/build_sample.py
python scripts/book_skills.py validate examples/sample-pack --json
```

The sample pack is generated from [two original synthetic sources](examples/sources/). Its unresolved timing conflict produces an intentional warning. The tests exercise explicit scope, archive limits, format structure, graph failures, copying detection, and incremental impact. Python 3.10 and 3.12 are checked in CI on Linux and Windows.

Read [architecture](docs/ARCHITECTURE.md), [specification](docs/SPECIFICATION.md), [security](SECURITY.md), [roadmap](ROADMAP.md), and [changelog](CHANGELOG.md) for the exact implemented boundary. The tool is MIT-licensed; selected source material retains its own rights.
