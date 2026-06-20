<h1 align="center">Book Skills Creator</h1>

<p align="center">
  <strong>Turn a selected book or document into a modular Agent Skill pack—not one oversized skill.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Agent%20Skills-open%20standard-blueviolet" alt="Agent Skills open standard">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-standard%20library-green" alt="Python standard library">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
</p>

Book Skills Creator is an agent-neutral workflow for converting explicitly selected source
material into a structured, source-grounded skill pack:

```text
selected source -> extraction -> analysis -> planning -> skill map
                -> atomic skills -> combo skills -> router -> validation
```

The generated pack separates focused capabilities from multi-step workflows and routes each
request to the smallest useful unit. References preserve source context without overloading
every skill.

## Why a skill pack?

| Single-skill conversion | Book Skills Creator |
|---|---|
| One document becomes one large skill | One document becomes a modular skill pack |
| Reference and procedure are mixed | Skills and supporting references are separated |
| Broad instructions compete for context | Atomic skills stay focused |
| Multi-step behavior is implicit | Combo skills define explicit workflows |
| One entry point does everything | A router selects the appropriate unit |
| Quality depends on manual review | The output includes a validation record |

The project is inspired by the broader book-to-skill concept, including
[`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill), while using an
original multi-skill architecture centered on planning, routing, composition, and validation.

## Requirements

- An environment that supports the open Agent Skills `SKILL.md` format.
- Python 3.10 or newer to run the helper scripts.
- No third-party Python packages for the included extraction and validation helpers.

## Installation

Clone the repository into a skills directory recognized by your agent environment:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Tire-C/book-skills-creator.git \
  ~/.agents/skills/book-skills-creator
```

Other environments may use locations such as:

```text
.agents/skills/book-skills-creator
.github/skills/book-skills-creator
~/.claude/skills/book-skills-creator
~/.copilot/skills/book-skills-creator
```

Reload the agent session after installation. See [Setup](docs/SETUP.md) for verification and
manual-installation options.

## Usage

Invoke the installed skill with a specific source:

```text
Use Book Skills Creator on ./books/my-book.docx and create a pack named leadership-toolkit.
```

```text
Use Book Skills Creator on ./sources/research-notes/ and propose the skill map before writing files.
```

Only the file, directory, or glob explicitly selected by the user is in scope. Passing a
directory intentionally authorizes recursive processing of that directory; unrelated library
locations are not scanned.

The workflow:

1. validates the selected source scope;
2. inspects available formats and extraction quality;
3. extracts readable text with an appropriate local method;
4. analyzes reusable concepts, procedures, examples, and anti-patterns;
5. plans the pack, including rejected candidates and uncertainties;
6. generates atomic skills, combo skills, references, and a router;
7. validates naming, coverage, overlap, routing, and source grounding.

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

## Generated output

```text
my-book-skill-pack/
  README.md
  source_index.md
  skill_map.md
  validation.md
  router/
    SKILL.md
  atomic/
    decision-framework/
      SKILL.md
    risk-analysis/
      SKILL.md
  combo/
    strategy-workflow/
      SKILL.md
  references/
    concepts.md
    glossary.md
    examples.md
    anti_patterns.md
    chapters/
```

Each generated `SKILL.md` uses YAML frontmatter with a lowercase, hyphenated `name`, a specific
`description`, and an operational Markdown body.

## Helper scripts

Run helpers from the repository root:

```bash
python scripts/preflight.py
python scripts/inspect_source.py ./books/my-book.docx
python scripts/extract_text.py ./books/my-book.docx
python scripts/create_pack_scaffold.py my-book-skill-pack
python scripts/check_pack.py my-book-skill-pack
```

`extract_text.py` writes local working files to `.book_skills_work/`:

- `full_text.txt` — combined extracted text with source boundaries;
- `metadata.json` — formats, counts, skipped sources, sizes, and extraction methods.

The workspace is ignored by Git. Helpers print summaries and metadata, never extracted source
content.

## Documentation

- [Specification](docs/SPECIFICATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Source processing](docs/SOURCE_PROCESSING.md)
- [Setup](docs/SETUP.md)
- [File guide](docs/FILES.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Example output tree](examples/output-tree.md)
- [Sample pack](examples/sample-pack)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)

## Tests

```bash
python -m unittest discover -s tests
python -m compileall -q scripts tests
python scripts/check_pack.py examples/sample-pack
```

Tests use synthetic temporary fixtures. No books, private documents, or extracted workspace
outputs are committed.

## Limitations

- The included extractor supports TXT, Markdown, and lightweight DOCX only.
- Complex layout, OCR, tables, images, and rich document semantics are outside the current
  extraction layer.
- Generated skills still require source-aware review; extraction quality limits generation
  quality.
- Users are responsible for having the right to process their selected sources.

## Security and responsible use

Keep private documents, credentials, and extracted source text out of issues and pull requests.
Report vulnerabilities according to [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](docs/CONTRIBUTING.md) and run the complete test
suite before opening a pull request.

## License

[MIT](LICENSE)
