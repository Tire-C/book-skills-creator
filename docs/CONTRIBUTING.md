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
python scripts/check_pack.py examples/sample-pack
```

For Python changes, test both successful input and expected failure behavior. Update the
public documentation when commands, outputs, supported formats, or limitations change.
