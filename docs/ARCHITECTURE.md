# Architecture

Book skill creator is designed as an agent skill plus optional helper scripts.

## Layers

### 1. Agent skill layer

`SKILL.md` contains the operational instructions loaded by compatible agents.

### 2. Extraction layer

The agent may use local tools to convert a selected source into readable text and metadata.

### 3. Planning layer

The agent analyzes the source and proposes a skill-pack architecture before writing generated files.

### 4. Generation layer

The agent writes a pack with router, atomic skills, combo skills, references, maps, and validation notes.

### 5. Validation layer

The agent checks consistency, source grounding, naming, overlap, and usability.

## Pack model

```text
router
  -> atomic skill
  -> combo skill
  -> references
```

The router is the public entry point. Atomic skills do one job. Combo skills chain multiple jobs. References preserve context without overloading the active skill.