# Source processing

Purpose: inspect a selected source before creating a pack.

Rules:

- process only paths selected by the user
- check file type before reading
- record size and extension
- prefer structured text when available
- keep temporary files out of the generated pack
- do not include private source text in examples

Suggested flow:

1. confirm selected path
2. inspect extension and size
3. choose a reading method
4. extract text into a temporary workspace
5. summarize structure
6. create the pack plan
7. generate files
8. validate the pack

Quality notes:

- plain text and markdown are easiest
- scanned PDFs may need OCR outside this project
- technical PDFs may need better structure tools
- weak extraction must be reported as a limitation
