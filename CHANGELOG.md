# Changelog

All notable changes to Book Skills Creator are documented here.

Public releases follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.0.0] - 2026-09-30

### Added

- 2.0 architecture: shared explicit source discovery; structured evidence units and
  source hashes; built-in HTML/EPUB extraction; optional local PDF text adapter; configurable
  source/archive limits; canonical `pack.json`; exact generation; graph, provenance, and file
  validation; behavioral case artifacts; and incremental impact reporting.
- Original multi-source synthetic manual, errata, and generated 2.0 pack with a preserved conflict,
  rejected candidates, and prompt-injection regression coverage.
- CLI, architecture/specification/security/migration documentation, and targeted safety and graph
  tests.
- Continuous integration workflow running the unit tests, bytecode compilation, and sample-pack
  validation on every push and pull request.
- Examples guide describing the sample pack, its reading order, and its role as a test fixture.

### Changed

- Hardened fresh-extraction validation for added sources and evidence, canonicalized affected reference IDs,
  and rejected malformed snapshots, source changes during extraction, and undeclared pack files.
- Legacy helpers now forward to one CLI and share source discovery. `create_pack_scaffold.py` now
  builds from a ready plan without placeholders. The v1 sample and templates are retained under
  `examples/v1-*`.
- Rewrote the README around the problem the project solves, the 2.0 workflow, supported formats,
  verification, and migration.
- Refreshed the roadmap for the post-1.0 cycle.

## [1.0.0] - 2026-06-20

### Added

- Modular skill-pack workflow with atomic skills, combo skills, a router, references, skill
  maps, rejected candidates, and validation records.
- Standard-library helpers for source inspection, TXT/Markdown/DOCX extraction, pack
  scaffolding, and structural validation.
- Automated tests with synthetic fixtures.
- Public setup, architecture, source-processing, contribution, security, roadmap, and sample
  pack documentation.

### Changed

- Prepared the repository for its first stable public release.
- Clarified installation, supported formats, limitations, and helper behavior.
- Expanded the root skill instructions and public documentation.
- Verified user-level and repository-local installations with the documented helper commands.

### Security

- Kept extraction local and network-free.
- Restricted processing to explicitly selected sources.
- Ignored extracted workspaces and excluded private or copyrighted source material from tests
  and examples.

## Pre-1.0 milestones

The following development milestones preceded the first stable public release.

### 0.7 - 2026-06-20

Added:

- Lightweight DOCX extraction using Python's standard library.
- Synthetic DOCX tests for valid and malformed documents.

### 0.6 - 2026-06-20

Added:

- Standard-library automated tests for source inspection, extraction, and pack validation.

### 0.5 - 2026-06-20

Added:

- TXT and Markdown extraction with local workspace metadata.

### 0.1 - 2026-06-20

Added:

- Initial Agent Skill workflow, templates, sample pack, helper scripts, and documentation.
