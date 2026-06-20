# Book skill creator specification

This document defines the public behavior of the project.

## Purpose

Convert a selected book or document into a modular agent skill pack.

The output is not a summary. The output is a practical pack with focused skills, combined workflows, routing rules, references, and validation notes.

## Core idea

One book can contain many reusable capabilities.

The correct transformation is:

```text
source -> extraction -> analysis -> plan -> map -> atomic skills -> combo skills -> router -> validation
```

## Source selection

The system processes only the source explicitly selected by the user.

A folder or glob can be processed only when the user explicitly gives that folder or glob as input.

## Skill types

### Atomic skill

A focused skill with one mission, one procedure, clear inputs, and a practical output.

### Combo skill

A workflow skill that orchestrates two or more atomic skills in a useful sequence.

### Router skill

The entry point of the generated pack. It decides whether the request should use an atomic skill, a combo skill, references, or a clarification step.

## Planning requirement

Before writing generated files, the agent must create a plan containing:

- pack name;
- source list;
- extraction quality;
- candidate atomic skills;
- candidate combo skills;
- router behavior;
- rejected candidates;
- risks and uncertainties.

## Candidate filter

A candidate becomes a skill only when it has:

- a clear mission;
- a repeatable procedure;
- concrete user inputs;
- a useful output;
- enough source support;
- low overlap with other skills.

## Recommended output tree

```text
pack-name/
  README.md
  source_index.md
  skill_map.md
  validation.md
  router/SKILL.md
  atomic/name/SKILL.md
  combo/name/SKILL.md
  references/concepts.md
  references/glossary.md
  references/examples.md
  references/anti_patterns.md
  references/chapters/
```

## Validation checklist

- Every skill has a valid SKILL.md.
- Every atomic skill has one mission.
- Combo skills orchestrate instead of duplicating.
- Router can reach every generated skill.
- References point back to the selected source.
- Claims unsupported by the source are removed or marked uncertain.
- Names are lowercase and hyphenated.
- The final pack is useful in real tasks.