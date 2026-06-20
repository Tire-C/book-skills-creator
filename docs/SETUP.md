# Setup

Book Skills Creator is distributed as an Agent Skill repository with optional Python helpers.

## Requirements

- an Agent Skills-compatible environment;
- Git for clone-based installation;
- Python 3.10 or newer for helper scripts.

The included helpers use only the Python standard library.

## Clone installation

Clone the repository into a skill directory supported by your environment:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Tire-C/book-skills-creator.git \
  ~/.agents/skills/book-skills-creator
```

Repository-local installations can use:

```text
.agents/skills/book-skills-creator
.github/skills/book-skills-creator
```

Other compatible environments may use a different user-level skills directory. Keep the
repository folder intact so `SKILL.md`, scripts, templates, documentation, and examples remain
available together.

## Manual installation

Download or copy the repository into the chosen skills directory. Confirm that the final path
contains:

```text
book-skills-creator/
  SKILL.md
  scripts/
  templates/
  docs/
```

Reload or restart the agent session after installation.

## Verify the checkout

From the repository root:

```bash
python scripts/preflight.py
python -m unittest discover -s tests
python scripts/check_pack.py examples/sample-pack
```

The preflight command reports the Python runtime and optional external document tools. Missing
optional tools do not affect TXT, Markdown, or DOCX extraction.

## Updating

For a Git installation:

```bash
git pull --ff-only
```

Reload the agent session if `SKILL.md` changed.
