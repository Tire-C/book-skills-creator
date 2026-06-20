# Contributing

Contributions should preserve the project's agent-neutral, source-grounded design.

## Before opening a pull request

1. Keep changes focused on one documented capability or correction.
2. Process only synthetic fixtures or documents you have the right to use.
3. Do not commit extracted books, private documents, credentials, or `.book_skills_work/`.
4. Keep helper scripts compatible with the Python standard library unless a dependency is
   explicitly justified.
5. Run the relevant helper and validation commands from the repository root.

For changes that affect generated packs, verify the sample pack:

```bash
python -m unittest discover -s tests
python -m compileall -q scripts tests
python scripts/check_pack.py examples/sample-pack
```

For Python changes, test both successful input and expected failure behavior. Update the
public documentation when commands, outputs, supported formats, or limitations change.

## Pull request scope

- Keep public documentation user-facing; do not commit internal review logs or working notes.
- Add third-party dependencies only when the standard library is insufficient and the tradeoff
  is documented.
- Preserve agent-neutral terminology and the open `SKILL.md` structure.
- Keep examples synthetic and free of copyrighted or private source content.
