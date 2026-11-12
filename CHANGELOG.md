# Changelog

All notable changes to Book Skills Creator are documented here.

Public releases follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.1.0] - 2026-11-13

### Added

- Installable Python package configuration (`pyproject.toml`) providing the `book-skills`
  console entry point and `python -m book_skills` module execution from any working directory.
- New `book-skills install` subcommand and `scripts/install_pack.py` compatibility wrapper to
  install validated packs into standard Agent Skills directories (`<pack>-router`,
  `<pack>-<unit-id>`, and bundle `<pack>`) with matching YAML frontmatter `name:` metadata and
  resolved `references/` directories, supporting `--mode copy|symlink` and `--force`.
- Cross-platform GitHub Actions CI matrix running across `ubuntu-latest`, `windows-latest`, and
  `macos-latest` on Python 3.10, 3.11, 3.12, and 3.13, plus Python 3.13 package classifier.
- Regression test suite expanded to 58 tests covering Agent Skills loader contracts, bundle
  frontmatter consistency, `--force` unmanaged-file protection, partial-install rollback,
  relative symlink preservation, secret detection, path sanitization, and extractor edge cases.

### Changed

- Updated `SKILL.md`, `README.md`, `docs/SETUP.md`, and `examples/sample-pack/validation.md` to
  document editable installation (`pip install -e .`), the `book-skills` CLI, and `install`.
- Improved source extraction fidelity for Markdown list/table paragraph breaks, HTML `noscript`
  and `iframe` filtering, `<pre>` whitespace/newline preservation, DOCX spaced `Heading <N>`
  styles, and explicit `pdftotext-timeout` reporting.
- Preserved v1 legacy pack compatibility (`validate --legacy` and `scripts/check_pack.py`) and
  v2.0 `pack.json` schema (`SCHEMA_VERSION = "2.0"`).

### Fixed

- Enforced Agent Skills specification compliance for `description` length (max 1024 characters),
  non-empty Markdown link destinations, and alignment between installed directory names and
  `SKILL.md` frontmatter `name:` values.
- Implemented preflight validation and transactional backup/rollback in `install_pack` so failed
  or partially copied installations restore previous destinations and preserve unrestored backups
  if a restore step fails.
- Wired relative symlinks directly in destination directories with cross-platform privilege
  probing and clean fallback messaging when OS symlink creation is unavailable (such as
  unprivileged Windows environments).
- Exempted macOS system root symlinks (`/var`, `/tmp`, `/etc`) during ancestor symlink checks.

### Security

- Added secret/credential pattern detection (`credential-detected`) across plans, manifests, and
  generated/installed files.
- Added privacy-preserving path redaction (`label()`) across POSIX and Windows user directories
  and `local-user-path` validation warnings for unredacted source paths.
- Prevented `install --force` from deleting unmanaged foreign files or directories, including
  inside `references/`.

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
