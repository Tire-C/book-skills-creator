# Changelog

All notable changes to Book Skills Creator are documented here.

Public releases follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
