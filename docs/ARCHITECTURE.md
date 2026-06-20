# Architecture

Book Skills Creator combines an Agent Skill workflow with deterministic, optional helper
scripts.

## Layers

### 1. Agent skill layer

`SKILL.md` contains the operational instructions loaded by compatible agents.

### 2. Extraction layer

Local helpers inspect explicitly selected paths and extract TXT, Markdown, and lightweight DOCX
into a Git-ignored workspace. Other recognized formats require tools supplied by the host
environment.

### 3. Planning layer

The agent analyzes the source and presents the skill-pack architecture before writing generated
files. The plan includes rejected candidates, extraction gaps, and uncertainties.

### 4. Generation layer

The agent writes a pack with router, atomic skills, combo skills, references, maps, and validation notes.

### 5. Validation layer

The agent checks structure, source grounding, naming, overlap, routing coverage, and usability.
`scripts/check_pack.py` provides deterministic structural validation.

## Pack model

```text
router
  -> atomic skill
  -> combo skill
  -> references
```

The router is the public entry point. Atomic skills do one job. Combo skills chain multiple
jobs. References preserve context without overloading the active skill.

## Data boundaries

- Input scope comes only from user-selected paths.
- Temporary extraction data stays outside generated packs.
- Generated skills synthesize procedures rather than reproducing source material.
- No helper requires network access.
