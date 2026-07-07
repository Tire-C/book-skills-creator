# Roadmap

Book Skills Creator prioritizes reliable, source-grounded skill-pack generation over broad
format coverage. v1.0.0 shipped the modular pack workflow, the standard-library helpers, the
automated tests, and the public documentation.

## Next

- Configurable source and archive safety limits (size caps, file-count caps).
- Lightweight EPUB extraction with synthetic fixtures.
- Stricter `check_pack.py` validation of generated `SKILL.md` frontmatter and router coverage.

## Later

- Extraction-quality reporting for richer document structures.
- Optional adapters for external extraction tools (PDF, OCR) without mandatory dependencies.

## Principles for new work

Items may change based on user feedback. New formats are added independently, each with
synthetic fixtures, explicit limitations, and no mandatory third-party dependencies unless
clearly justified.
