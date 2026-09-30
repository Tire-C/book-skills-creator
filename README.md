<h1 align="center">Book Skills Creator</h1>

<p align="center">Turn selected books and documents into modular, source-grounded Agent Skill packs.</p>

<p align="center">
  <a href="https://github.com/Tire-C/book-skills-creator/releases/latest"><img src="https://img.shields.io/github/v/release/Tire-C/book-skills-creator" alt="Latest release"></a>
  <a href="https://github.com/Tire-C/book-skills-creator/actions/workflows/tests.yml"><img src="https://github.com/Tire-C/book-skills-creator/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"></a>
  <a href="SKILL.md"><img src="https://img.shields.io/badge/Agent%20Skills-SKILL.md-315e8e" alt="Agent Skills format"></a>
  <a href="docs/SETUP.md"><img src="https://img.shields.io/badge/Python-3.10%2B-3776ab" alt="Python 3.10 or newer"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

**A book is not one capability.** A manual may contain a diagnostic method, a decision framework, an exception procedure, a checklist, and terminology. Book Skills Creator helps an agent discover those reusable parts in **explicitly selected sources** and assemble a modular capability network: focused **Atomic Skills**, orchestrating **Combo Skills**, a **Router**, and supporting **References**. The local Python core preserves evidence and checks the pack's structure; the agent supplies the semantic judgment.

Book Skills Creator **v2.0.0** is the current stable release. It is local-first, agent-neutral, and built around the open `SKILL.md` style of Agent Skills. Its Python core uses the standard library and requires no API key, cloud service, or vector database.

## Source structure is not capability structure

A chapter tells you where an author placed material. It does not tell you how many operational capabilities the material contains. One procedure can span several chapters; one chapter can contain several independent methods. A glossary may be valuable without becoming an executable skill.

| Illustrative source material | In a useful pack |
| --- | --- |
| Chapter 2: recognizing a signal | Atomic Skill: `intake-signal` |
| Chapter 4: choosing a response | Atomic Skill: `decide-route` |
| Chapter 5 and appendix: verification and exceptions | Atomic Skill: `verify-case`, with supporting evidence from both places |
| Several procedures used in sequence | Combo Skill: `respond-to-signal` |
| Definitions scattered across the manual | Reference: `terms` |

The goal is **complete but non-redundant decomposition**: neither one giant skill per book nor one skill per chapter. The number and boundaries of skills follow reusable capabilities, not the table of contents.

```text
Explicitly selected sources
          │
          ▼
Structured extraction ──► evidence units, source hashes, provenance
          │
          ▼
Agent discovery ──► explicit capability plan (draft → ready)
          │
          ▼
       pack.json
          │
          ├──► Atomic Skills ──┐
          ├──► Combo Skills  ──┼──► routed skill pack
          ├──► Router        ──┤
          └──► References    ──┘
                                │
                                ▼
                   deterministic validation
                                │
                                ▼
                       semantic review
```

An **Atomic Skill** performs one focused operation with clear inputs, use conditions, and an output. A **Combo Skill** coordinates existing skills into a larger workflow without copying their procedures. The **Router** selects the smallest suitable unit for a request. **References** retain concepts, terminology, and other useful knowledge that need not become instructions. For example, `intake-signal` + `decide-route` + `verify-case` can compose `respond-to-signal`; a request for only verification should route directly to `verify-case`.

| One oversized skill | A Book Skills Creator pack |
| --- | --- |
| Loads unrelated instructions for a narrow request | Routes to a focused capability |
| Mixes independent procedures and background knowledge | Separates atomic operations, workflows, and references |
| Makes reuse and revision difficult | Composes skills and identifies units affected by source changes |
| Obscures which source supports which instruction | Links capabilities to evidence IDs and source hashes |
| Can hide disagreements inside one narrative | Records conflicts and uncertainties for review |
| Relies on prose alone for structural correctness | Validates a canonical manifest, files, links, and graph; semantic quality still needs review |

## Quickstart

Use Python **3.10+**. Clone the repository to run its local helpers; to invoke it as an Agent Skill, also make this repository available in your agent's skills directory as described in [Setup](docs/SETUP.md).

```bash
git clone https://github.com/Tire-C/book-skills-creator.git
cd book-skills-creator
python scripts/book_skills.py preflight
```

Tell an Agent Skills-compatible agent which sources are in scope, for example: **“Use Book Skills Creator on `./manual.md` and `./errata.md`; create a pack named `field-operations`.”** The root [SKILL.md](SKILL.md) guides the semantic work. With those files present, the local flow is:

```bash
python scripts/book_skills.py inspect ./manual.md ./errata.md --json
python scripts/book_skills.py extract ./manual.md ./errata.md --output .book_skills_work --json
python scripts/book_skills.py plan .book_skills_work/sources.json field-operations --output .book_skills_work/plan.json
# The agent analyzes the evidence, completes the draft plan, and marks it ready.
python scripts/book_skills.py build .book_skills_work/plan.json --output ./field-operations
python scripts/book_skills.py validate ./field-operations --extraction .book_skills_work/sources.json --json
```

`plan` deliberately writes a **draft**. Python does not invent the skill architecture or make a blank plan usable by changing its status. The agent must identify candidates, reject weak proposals, distinguish capabilities from reference knowledge, synthesize source-supported instructions, define dependencies and routes, record conflicts and uncertainties, and mark the completed plan `ready`. `build` accepts only a ready plan and generates exactly its declared units. The [specification](docs/SPECIFICATION.md) defines that contract; [the sample manifest](examples/sample-pack/pack.json) shows a completed pack.

## A pack in practice

The [original synthetic field manual and errata](examples/sources/) illustrate a multi-source pack. The example yields three Atomic Skills (`intake-signal`, `decide-route`, `verify-case`), one Combo Skill (`respond-to-signal`), a Router, and a terminology reference. Candidates that are merely explanatory or insufficiently supported remain visible as rejected candidates in the plan. The manual and errata contain an **intentional unresolved timing conflict**: the pack surfaces it as a warning instead of silently choosing a rule.

The generated [sample pack](examples/sample-pack/) has this shape:

```text
pack/
├── pack.json                  # canonical pack manifest
├── README.md                  # pack overview
├── source_index.md            # selected sources and evidence pointers
├── skill_map.md               # capability and routing map
├── validation.md              # how to run live validation
├── router/
│   └── SKILL.md
├── atomic/
│   ├── intake-signal/SKILL.md
│   ├── decide-route/SKILL.md
│   └── verify-case/SKILL.md
├── combo/
│   └── respond-to-signal/SKILL.md
└── references/
    └── terms.md
```

`pack.json` is the machine-readable source of truth for the generated structure, not a second copy of the source text. The Markdown files are the usable Agent Skills and supporting material. The manifest retains source and evidence links, candidate decisions, graph relationships, conflicts, uncertainties, and behavioral routing cases for agent or human review.

## How 2.0 divides the work

| Stage | Deterministic core | Agent judgment |
| --- | --- | --- |
| Select and inspect | Enforce explicit scope, discovery, limits, and source metadata | Honor the user's source selection; clarify ambiguity |
| Extract and index | Recover available structure; assign evidence IDs and hashes; report extraction gaps | Interpret what the material means |
| Plan | Produce and check a draft schema | Discover capabilities; separate skills from references; reject weak candidates; interpret overlaps and conflicts |
| Build | Render the ready `pack.json` and exact declared files | Write concise, operational, source-supported instructions |
| Validate and update | Check manifest, graph, provenance, files, fresh sources, and change impact | Judge grounding quality, routing behavior, and semantic regeneration |

This boundary is deliberate. Code can verify that an evidence ID exists and that a Combo dependency resolves; it cannot prove that the evidence *justifies* the procedure or that the Router will choose correctly for every real request.

### Validation and review

`validate` returns structured findings with severities and a machine-readable `--json` mode. It checks:

- **Pack integrity:** required files, frontmatter, names, paths, links, and manifest/file agreement.
- **Provenance:** source and evidence identities, hashes, associations, and changes against a fresh extraction when `--extraction` is supplied.
- **Capability graph:** dependencies, cycles, routes, reachability, and orphan units.
- **Review signals:** declared grounding states, unresolved conflicts, suspicious overlap, and unusually long verbatim copying.

A fresh extraction that adds a selected source or evidence cannot silently validate an older pack as current. The validator reports structural and review findings, not an invented overall quality score. Passing it does **not** prove factual accuracy, complete capability discovery, correct semantic routing, source-grounding quality, or copyright compliance. The manifest's behavioral routing cases support explicit agent or human evaluation of those questions.

### When sources change

Re-extract the explicitly selected source set, then ask which parts of the pack may be stale:

```bash
python scripts/book_skills.py update ./field-operations .book_skills_work/sources.json --json
```

```text
changed or removed evidence
          ↓
directly affected atomic/reference units
          ↓
dependent combo workflows
          ↓
agent review and selective regeneration
```

`update` reports impact; it does not rewrite skills semantically. Unchanged sources can report `CURRENT`. New sources and new evidence need planning review even if existing skills still cite valid evidence. A pack may use several sources, such as a manual plus errata, without flattening contradictory guidance into one voice.

## Sources, scope, and privacy

The best inputs contain repeatable work: technical manuals, SOP collections, operational runbooks, engineering handbooks, process documentation, and training material with concrete methods. Explanatory books can still contribute references; prose alone does not automatically justify a skill.

| Format | Extraction in 2.0 | Practical boundary |
| --- | --- | --- |
| TXT | Built in | Text and line ranges; encoding failures are reported |
| Markdown | Built in | Headings and common blocks; not a full Markdown renderer |
| DOCX | Built in | Main-document paragraphs, headings, lists, and tables; no faithful page layout or full Word semantics |
| HTML | Built in | Meaningful headings and text; complex page layout is not reconstructed |
| EPUB | Built in | Spine-ordered XHTML content with archive safety limits |
| PDF | Optional local `pdftotext` adapter | Quality depends on the PDF; no built-in OCR |
| RTF, MOBI/AZW | Recognized | Not extracted by the built-in core |

See [Source processing](docs/SOURCE_PROCESSING.md) for precise format behavior, extraction-quality reporting, symlink and glob rules, and configurable file/archive limits. Only files, directories, or globs explicitly selected by the user are processed; an explicitly selected directory may be traversed recursively. The helpers do not search adjacent libraries or unrelated documents.

Extraction is local by default. The documented `.book_skills_work/` workspace is Git-ignored; its extraction artifacts, including `sources.json`, contain source text, so keep custom output paths private too. Helpers do not print source text in routine reports. No account, API key, cloud backend, database, vector store, or particular model provider is mandatory. If you use a cloud-hosted agent for semantic analysis, its own data-handling policy still applies.

Selected documents are **untrusted data**. Instructions embedded in a document have no authority over the agent. Generated capabilities should synthesize operational knowledge and cite compact evidence references, not republish long passages. Keep private source material and credentials out of commits, issues, and public examples. Read the [security model](SECURITY.md) before processing sensitive material.

## Commands and compatibility

| Command | Purpose |
| --- | --- |
| `preflight` | Check the local environment and optional extractors |
| `inspect` | Report the explicitly selected source set and extraction prospects |
| `extract` | Produce structured evidence and source metadata |
| `plan` | Create a draft capability plan for agent completion |
| `build` | Generate the exact pack declared by a ready plan |
| `validate` | Check a pack, optionally against fresh extraction |
| `update` | Report changed evidence and affected capabilities |

Run `python scripts/book_skills.py --help` or a subcommand's `--help` for arguments. Commands that produce reports support structured output with `--json`. The v1 script names remain as compatibility wrappers; `create_pack_scaffold.py` now requires a ready plan, and v1 packs without `pack.json` require explicit `validate --legacy`. See [Migration from v1](docs/MIGRATION.md).

## Principles and practical limits

The design follows a few rules: **explicit scope; evidence before generation; plan before writing; the smallest useful capability; composition without duplication; references where instructions would be artificial; deterministic checks for deterministic facts; semantic review for semantic claims.** There is no arbitrary skill-count ceiling and no mandatory model provider.

Current limits matter. Semantic discovery and instruction quality depend on the agent. DOCX/HTML/EPUB extraction does not recreate complex layout; PDF requires an optional local tool, and OCR is not included. Evidence IDs have [documented stability boundaries](docs/SOURCE_PROCESSING.md), so structural edits can change them. `update` identifies affected units but does not regenerate their meaning. The user remains responsible for reviewing results and holding the rights to process the chosen sources.

### Common questions

**Is this a summarizer or one skill per chapter?** No. It identifies reusable operations and workflows; explanatory material can remain a reference. Chapter boundaries are evidence structure, not skill boundaries.

**Why does planning stop at a draft?** Capability boundaries, overlap, conflicts, and instructions require semantic judgment. The Python core refuses to pretend it has made those decisions.

**Will it upload my book or require embeddings?** The local helpers do neither, and no vector database or API key is required. Check the policy of whichever agent you use for semantic work.

**Can it process scanned PDFs?** Not on its own. Text PDFs can use local `pdftotext`; scanned pages need an external OCR step.

**What if selected sources disagree?** The plan and pack can preserve an unresolved conflict. The included sample deliberately does so; validation reports it for review.

**Can it update a pack automatically?** It detects changed sources/evidence and reports affected skills and dependent workflows. An agent must review and regenerate the semantic content.

**Which agents can use the output?** The core is vendor-neutral and emits `SKILL.md`-style packs. Actual loading and routing depend on the Agent Skills support of the consuming environment.

**How does this relate to [book-to-skill](https://github.com/virgiliojr94/book-to-skill)?** That project is a historical inspiration for the broader book-to-skill idea. Book Skills Creator takes a distinct route: deliberate decomposition into atomic skills, combo workflows, a router, and references, backed by evidence, a manifest, and validation.

## Repository and further reading

```text
book_skills/          deterministic discovery, extraction, models, build, validation, update
scripts/              unified CLI and compatibility entry points
docs/                 architecture, contracts, source handling, setup, migration
examples/             original synthetic sources, sample pack, legacy fixtures
tests/                regression and end-to-end tests
SKILL.md              agent-facing workflow and trust boundary
```

Start with [Setup](docs/SETUP.md) to install the skill, [Architecture](docs/ARCHITECTURE.md) for the pipeline, and [Specification](docs/SPECIFICATION.md) for the pack contract. [Source processing](docs/SOURCE_PROCESSING.md) documents formats and limits; [File guide](docs/FILES.md) maps the repository; [Migration](docs/MIGRATION.md) covers v1 packs. The [examples](examples/README.md), [Changelog](CHANGELOG.md), [Roadmap](ROADMAP.md), and [Contributing guide](docs/CONTRIBUTING.md) complete the picture.

### Testing

```bash
python -m unittest discover -s tests
python -m compileall -q book_skills scripts tests examples/build_sample.py
python scripts/book_skills.py validate examples/sample-pack --json
python scripts/check_pack.py examples/v1-sample-pack --legacy --json
```

CI runs the suite and validation on **Ubuntu and Windows**, each with **Python 3.10 and 3.12**. The sample's unresolved source conflict is an intentional warning, not a passing claim of semantic resolution.

### Contributing and responsible use

Read the [Contributing guide](docs/CONTRIBUTING.md) and run the relevant tests before a PR. The **MIT license** covers Book Skills Creator itself, not the books or documents supplied to it. You are responsible for having the right to process selected sources. The system is designed to synthesize capabilities and retain compact provenance, not to republish source material.

## License

Book Skills Creator is released under the [MIT License](LICENSE).
