# Setup

Use Python 3.10 or newer. The core has no mandatory third-party dependencies. Clone this repository into a skills directory recognized by your agent environment, or invoke `scripts/book_skills.py` from the repository checkout. `SKILL.md` is the agent-facing workflow; the Python CLI is local and provider-neutral.

```bash
python scripts/book_skills.py preflight --json
python -m unittest discover -s tests
python scripts/book_skills.py validate examples/sample-pack --json
```

The first command reports optional local `pdftotext` and OCR availability; OCR remains an external workflow. The last command succeeds with an intentional unresolved-conflict warning in the synthetic fixture.

The old helper paths remain callable. New work should use `scripts/book_skills.py`. Use `validate --legacy` only for a v1 Markdown-only pack. See [migration](MIGRATION.md) for pack changes.
