<p align="center">
  <h1 align="center">Book Skills Creator</h1>
</p>

<p align="center">
  <strong>Convert selected books into structured Agent Skill packs: atomic skills, combo skills, router skills, references, and validation workflows.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Agent%20Skills-Open%20Standard-blueviolet" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Skill%20Pack-Generator-green" alt="Skill Pack Generator">
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT License">
</p>

---

## What is Book Skills Creator?

**Book Skills Creator** is an Agent Skill that turns a selected book or document into a complete, reusable **skill pack**.

Instead of producing one giant summary or one overloaded skill, it analyzes the source, plans the architecture, and generates only the useful operational skills the book can actually support.

A single book can become:

- **atomic skills** — focused skills that do one practical job well;
- **combo skills** — orchestrated workflows that combine multiple atomic skills;
- **a router skill** — the entry point that chooses the right skill for the user's task;
- **references** — chapter notes, concepts, examples, anti-patterns, and source indexes;
- **validation files** — quality checks to keep the generated pack usable and grounded.

---

## Why?

Books are dense. Agents can read them, but raw reading is slow, repetitive, and easy to misuse.

Book Skills Creator converts a book into a practical operating system for that book:

```text
book -> analysis -> plan -> skill map -> atomic skills -> combo skills -> router -> validation
```

The result is not a book report. It is a set of tools the agent can reuse while solving real problems.

---

## How it differs from simple book-to-skill conversion

Many book-to-skill workflows convert a document into one unified skill.

Book Skills Creator goes further:

| Standard conversion | Book Skills Creator |
|---|---|
| One book becomes one skill | One book becomes a skill pack |
| Summarizes or indexes the book | Extracts operational capabilities |
| Loads one master skill | Uses router + atomic + combo skills |
| Good for study/reference | Good for applying the book in workflows |
| Usually linear | Planned, modular, and validated |

This project is inspired by the wider book-to-skill idea, including [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill), but it implements a different architecture: **multi-skill extraction, routing, combination, and validation**.

---

## Install

Clone or copy this repository into a skill directory supported by your agent environment.

Common locations:

```bash
~/.agents/skills/book-skills-creator
~/.claude/skills/book-skills-creator
~/.copilot/skills/book-skills-creator
.github/skills/book-skills-creator
.agents/skills/book-skills-creator
```

Then reload or restart your agent session so the skill can be discovered.

---

## Usage

Ask your agent something like:

```text
Use Book Skills Creator on ./books/my-book.pdf
```

or:

```text
Use Book Skills Creator on ./sources/my-book/ and create a skill pack called strategic-thinking-pack
```

The skill will:

1. validate the selected source;
2. estimate extraction complexity;
3. analyze the structure and usable knowledge;
4. enter planning mode;
5. propose the skill-pack architecture;
6. generate the router, atomic skills, combo skills, references, and validation files;
7. run a final quality check.

Book Skills Creator processes **only the source explicitly selected by the user**. It does not automatically convert every book in a folder unless the user explicitly requests that folder or glob.

---

## Generated output

A typical generated pack looks like this:

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
    communication-method/
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

---

## Design principles

- **Selected source only** — never process a library by accident.
- **Plan before writing** — every pack starts with an explicit architecture plan.
- **Operational over encyclopedic** — create skills for usable capabilities, not for every chapter.
- **Atomic first** — each atomic skill has one mission.
- **Combine only when useful** — combo skills exist only when multiple skills form a real workflow.
- **Router as entry point** — the router decides which skill to use.
- **Source grounded** — every skill points back to the source and reference files.
- **No long copying** — synthesize methods; do not reproduce copyrighted text.
- **Validation required** — every pack includes checks for overlap, hallucination risk, and usability.

---

## Helper scripts

This repository includes small helper scripts:

```bash
python scripts/preflight.py
python scripts/inspect_source.py ./books/my-book.pdf
python scripts/create_pack_scaffold.py my-book-skill-pack
python scripts/check_pack.py my-book-skill-pack
```

The scripts are optional. The main product is the Agent Skill in `SKILL.md`.

---

## Legal and ethical note

Use books and documents you have the right to process. Book Skills Creator is designed to extract operational structure and references, not to reproduce copyrighted works.

---

## License

MIT License.