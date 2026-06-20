---
name: book-skills-creator
description: "Create modular, source-grounded Agent Skill packs from explicitly selected books or documents. Use when a user wants atomic skills, combo workflows, a router, references, a skill map, and validation derived from a specific source."
---

# Book Skills Creator

Convert an explicitly selected book, document, file set, directory, or glob into a modular
Agent Skill pack.

## Source scope

1. Process only paths explicitly selected by the user.
2. Treat a directory or glob as authorized only when the user provides it directly.
3. Do not expand the task to adjacent folders, libraries, or unrelated documents.
4. Do not include source text, private data, or copyrighted passages in public examples.
5. State extraction gaps and uncertainty instead of inventing missing source support.

## Workflow

### 1. Inspect

- Confirm that each selected path exists.
- Identify formats, sizes, unsupported files, and likely extraction quality.
- Use `scripts/inspect_source.py` when a deterministic inventory is useful.

### 2. Extract

- Prefer the least complex local extraction method that preserves readable structure.
- Use `scripts/extract_text.py` for TXT, Markdown, and lightweight DOCX extraction.
- Keep temporary extraction output in `.book_skills_work/` or another controlled local
  workspace outside the generated pack.
- Record skipped sources and weak extraction as limitations.

### 3. Analyze

Identify source-supported:

- concepts and vocabulary;
- repeatable procedures;
- decision rules and frameworks;
- examples and anti-patterns;
- constraints, edge cases, and uncertainties.

Do not convert every chapter into a skill. A candidate must represent a reusable capability.

### 4. Plan before writing

Create and present a pack plan containing:

- pack name and selected sources;
- extraction quality and known gaps;
- candidate atomic skills;
- candidate combo skills;
- router behavior;
- reference structure;
- rejected candidates with reasons;
- validation risks.

Resolve material ambiguity before generating the pack.

### 5. Generate

Create:

- `README.md`;
- `source_index.md`;
- `skill_map.md`;
- `validation.md`;
- `router/SKILL.md`;
- `atomic/<skill-name>/SKILL.md`;
- `combo/<workflow-name>/SKILL.md`;
- supporting files under `references/`.

Every generated skill must have valid YAML frontmatter, a lowercase hyphenated name, a specific
description, clear activation conditions, operational steps, and source references.

### 6. Validate

Check that:

- each atomic skill has one mission;
- combo skills orchestrate without duplicating atomic instructions;
- the router can reach every generated skill;
- names and paths are consistent;
- claims are grounded in the selected source;
- rejected candidates and uncertainties remain documented;
- the pack contains no unnecessary copied source text;
- `scripts/check_pack.py <pack-path>` passes.

## Failure handling

- If no selected source is readable, stop and report the skipped inputs.
- If extraction is partial, continue only with an explicit limitation and reduced confidence.
- If a candidate lacks a repeatable procedure, keep it in references or reject it.
- If two candidates substantially overlap, merge or narrow them before generation.

## References

Use the repository documentation for detailed contracts:

- `docs/SPECIFICATION.md`
- `docs/ARCHITECTURE.md`
- `docs/SOURCE_PROCESSING.md`
- `docs/FILES.md`
