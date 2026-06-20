---
name: book-skills-creator
description: "Create structured agent skill packs from selected books or documents with atomic skills, combo skills, router skills, references, skill maps, and validation workflows."
---

# Book skill creator

This skill converts a selected book or document into a modular agent skill pack.

## Workflow

1. Validate the selected source.
2. Extract readable text and structure.
3. Analyze usable concepts, methods, examples, and anti-patterns.
4. Plan the skill-pack architecture before writing files.
5. Create atomic skills for single-purpose capabilities.
6. Create combo skills for useful multi-step workflows.
7. Create a router skill as the main entry point.
8. Create references and a skill map.
9. Validate the generated pack.

## Output

A generated pack should include:

- README.md
- source_index.md
- skill_map.md
- validation.md
- router/SKILL.md
- atomic/*/SKILL.md
- combo/*/SKILL.md
- references/

## Quality rules

Create only useful skills. Keep each atomic skill focused on one mission. Ground the pack in the selected source. Prefer clear procedures over long summaries.