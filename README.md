<h1 align="center">Book Skills Creator</h1>

<p align="center">
  <strong>Turn a selected book or document into a modular Agent Skill pack—not one oversized skill.</strong>
</p>

<p align="center">
  <a href="https://github.com/Tire-C/book-skills-creator/releases"><img src="https://img.shields.io/github/v/release/Tire-C/book-skills-creator?color=blue" alt="Latest release"></a>
  <a href="https://github.com/Tire-C/book-skills-creator/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/Tire-C/book-skills-creator/tests.yml?label=tests" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Agent%20Skills-open%20standard-blueviolet" alt="Agent Skills open standard">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-standard%20library-green" alt="Python standard library">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
</p>

## A book is not one capability

A good book is a decision framework in one chapter, a checklist in another, a vocabulary that
spans the whole text, and a handful of workflows hiding in between. Flatten all of that into a
single skill and every instruction competes for the same context: the agent gets one blunt
instrument instead of a toolbox.

Book Skills Creator converts explicitly selected source material into a **structured,
source-grounded skill pack**:

```text
selected source -> extraction -> analysis -> planning -> skill map
                -> atomic skills -> combo skills -> router -> validation
```

- **Atomic skills** do one job each, with one mission and one procedure.
- **Combo skills** orchestrate atomic skills into explicit multi-step workflows.
- **A router** sends each request to the smallest useful unit.
- **References** preserve source context without overloading the active skill.
- **A validation record** documents what was built, what was rejected, and why.

The result behaves like a well-organized team extracted from the book, not like the book pasted
into a prompt.

## Quickstart

**1. Install** into a skills directory your agent environment recognizes:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Tire-C/book-skills-creator.git \
  ~/.agents/skills/book-skills-creator
```

Other environments may use locations such as `.agents/skills/`, `.github/skills/`,
`~/.claude/skills/`, or `~/.copilot/skills/`. Reload the agent session after installation; see
[Setup](docs/SETUP.md) for verification and manual installation.

**2. Invoke** the skill on an explicitly selected source:

```text
Use Book Skills Creator on ./books/my-book.docx and create a pack named leadership-toolkit.
```

```text
Use Book Skills Creator on ./sources/research-notes/ and propose the skill map before writing files.
```

Only the file, directory, or glob you select is in scope. Passing a directory intentionally
authorizes recursive processing of that directory; nothing else is scanned.

**3. Validate** the generated pack:

```bash
python scripts/check_pack.py leadership-toolkit
```

## What a generated pack contains

```text
my-book-skill-pack/
  README.md            # scope, entry point, limitations
  source_index.md      # selected sources, extraction methods, known gaps
  skill_map.md         # every skill, route, dependency, and rejected candidate
  validation.md        # structural, routing, overlap, and grounding checks
  router/
    SKILL.md           # entry point: picks the smallest useful unit
  atomic/
    decision-framework/SKILL.md
    risk-analysis/SKILL.md
  combo/
    strategy-workflow/SKILL.md
  references/
    concepts.md  glossary.md  examples.md  anti_patterns.md  chapters/
```

Each generated `SKILL.md` uses YAML frontmatter with a lowercase, hyphenated `name`, a specific
`description`, and an operational Markdown body. A browsable synthetic example lives in
[`examples/sample-pack`](examples/sample-pack), with a short guide in
[`examples/README.md`](examples/README.md).

## Why a pack instead of one skill?

| Single-skill conversion | Book Skills Creator |
|---|---|
| One document becomes one large skill | One document becomes a modular skill pack |
| Reference and procedure are mixed | Skills and supporting references are separated |
| Broad instructions compete for context | Atomic skills stay focused |
| Multi-step behavior is implicit | Combo skills define explicit workflows |
| One entry point does everything | A router selects the appropriate unit |
| Quality depends on manual review | The output includes a validation record |

## How it works

1. **Scope** — validates that every selected path was explicitly chosen by the user.
2. **Inspect** — identifies formats, sizes, unsupported files, and likely extraction quality.
3. **Extract** — pulls readable text with the least complex local method that preserves structure.
4. **Analyze** — finds reusable concepts, procedures, decision rules, examples, and anti-patterns.
5. **Plan** — presents the pack architecture *before writing files*, including rejected
   candidates and uncertainties.
6. **Generate** — writes atomic skills, combo skills, references, the router, and the maps.
7. **Validate** — checks naming, coverage, overlap, routing, and source grounding, and records
   the result in `validation.md`.

Planning is a hard requirement, not a suggestion: material ambiguity is resolved before any pack
file is written, and candidates without a repeatable procedure are kept as references or
rejected with a reason.

## Use cases

- **Technical books** — a toolbox of procedures and decision frameworks instead of one summary.
- **Internal runbooks and SOPs** — routed operational skills your agent can apply step by step.
- **Course and training notes** — atomic study skills plus combo workflows for practice.
- **Research note collections** — concept references with explicit synthesis workflows on top.
- **Product and process manuals** — task-focused skills that answer "how do I do X here?"

Anything you are allowed to process and that contains repeatable capability is a candidate—the
pipeline is about structure, not genre.

## Built-in format support

The repository distinguishes source inspection from built-in extraction:

| Format | Inspection | Built-in extraction | Notes |
|---|---:|---:|---|
| `.txt` | Yes | Yes | UTF-8 with a safe replacement fallback |
| `.md`, `.markdown` | Yes | Yes | Preserved as text |
| `.docx` | Yes | Yes | Reads `word/document.xml` |
| PDF, EPUB, HTML, RTF, MOBI/AZW | Yes | No | Requires a suitable tool available in the agent environment |
| Scanned documents | File only | No | Requires OCR outside this repository |

DOCX extraction preserves main-document paragraphs, tabs, and line breaks. It does not extract
headers, footers, comments, footnotes, embedded objects, tracked-change semantics, or page
layout. See [Source processing](docs/SOURCE_PROCESSING.md) for details.

## Helper scripts

All helpers use only the Python standard library and run from the repository root:

| Command | What it does |
|---|---|
| `python scripts/preflight.py` | Reports the Python runtime and optional external tools |
| `python scripts/inspect_source.py <path>` | Deterministic inventory of a selected source |
| `python scripts/extract_text.py <path>` | Extracts TXT/Markdown/DOCX into a local workspace |
| `python scripts/create_pack_scaffold.py <name>` | Creates an empty pack skeleton |
| `python scripts/check_pack.py <pack-path>` | Validates the structure of a generated pack |

`extract_text.py` writes to a Git-ignored `.book_skills_work/` workspace: `full_text.txt`
(combined text with source boundaries) and `metadata.json` (formats, counts, skipped sources,
sizes, extraction methods). Helpers print summaries and metadata, never extracted source
content.

## Design principles

- **Explicit scope only.** Nothing outside the user-selected paths is ever read.
- **Plan before writing.** The architecture—including what gets rejected—is agreed first.
- **Smallest useful unit.** The router prefers one focused skill over one giant one.
- **Validation is an artifact.** Every pack ships its own auditable `validation.md`.
- **Local and network-free.** No helper requires network access; nothing leaves the machine.
- **Standard library only.** No mandatory third-party dependencies for included helpers.
- **Agent-neutral.** Packs target the open Agent Skills `SKILL.md` format, not one vendor.
- **Honest about limits.** Weak extraction and uncertainty are reported, never papered over.

## FAQ

**Is the pack just a summary of the book?**
No. A summary tells you what the book says; a pack gives the agent things it can *do*. Skills
synthesize procedures, decision rules, and workflows—references carry the supporting context.

**Why does the pack need a router?**
Without one, every request activates the entire converted document. The router reads the request
and dispatches the single atomic skill, combo workflow, or reference that fits, keeping context
small and behavior predictable.

**Does anything get uploaded anywhere?**
No. Inspection, extraction, and validation are local and network-free. The workspace is
Git-ignored, and helpers never print extracted source text.

**My source is a PDF—can I still use this?**
Inspection recognizes it, but built-in extraction covers TXT, Markdown, and lightweight DOCX
only. If your agent environment provides a PDF tool (such as `pdftotext`), the workflow can use
it; `scripts/preflight.py` reports what is available. Wider built-in coverage is on the
[roadmap](ROADMAP.md).

**How does this relate to `book-to-skill`?**
[`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) helped popularize
the book-to-skill concept and inspired this project. Book Skills Creator explores a different
architecture for the same idea: instead of producing one skill per document, it decomposes the
document into a routed pack of atomic and combo skills with planning and validation as
first-class steps. Pick whichever model fits how you want your agent to work.

**Which agents can use the generated packs?**
Any environment that supports the open Agent Skills `SKILL.md` format. The generator itself is
also an Agent Skill, so the same compatibility applies to running it.

## Repository structure

```text
book-skills-creator/
  SKILL.md          # the Agent Skill that drives the workflow
  scripts/          # standard-library helpers (inspect, extract, scaffold, validate)
  templates/        # atomic, combo, and router SKILL.md templates
  docs/             # specification, architecture, setup, source processing, contributing
  examples/         # synthetic sample pack and expected output tree
  tests/            # automated tests with synthetic fixtures
```

## Documentation

- [Specification](docs/SPECIFICATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Source processing](docs/SOURCE_PROCESSING.md)
- [Setup](docs/SETUP.md)
- [File guide](docs/FILES.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Examples guide](examples/README.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)

## Tests

```bash
python -m unittest discover -s tests
python -m compileall -q scripts tests
python scripts/check_pack.py examples/sample-pack
```

The same commands run in continuous integration on every push and pull request. Tests use
synthetic temporary fixtures; no books, private documents, or extracted workspace outputs are
committed.

## Limitations

- The included extractor supports TXT, Markdown, and lightweight DOCX only.
- Complex layout, OCR, tables, images, and rich document semantics are outside the current
  extraction layer.
- Generated skills still require source-aware review; extraction quality limits generation
  quality.
- Users are responsible for having the right to process their selected sources.

## Copyright and responsible use

The MIT license covers this tool, not the documents you process with it. Generated packs derive
from your selected sources: you are responsible for having the right to process them, and packs
are designed to synthesize procedures rather than reproduce source text. Keep private documents,
credentials, and extracted source content out of issues and pull requests, and report
vulnerabilities according to [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](docs/CONTRIBUTING.md) and run the complete test
suite before opening a pull request.

## License

[MIT](LICENSE)
