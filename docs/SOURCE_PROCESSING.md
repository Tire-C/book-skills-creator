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

## Lightweight extraction

Use the standard-library extraction helper for explicitly selected `.txt`, `.md`, `.markdown`,
and `.docx` sources:

```bash
python scripts/extract_text.py ./books/my-book.md
python scripts/extract_text.py ./books/my-book.docx
python scripts/extract_text.py ./notes/ ./appendix.txt
```

The helper scans only the files or folders passed on the command line. Directory inputs are
processed recursively, symbolic links are skipped, unsupported files are recorded as skipped,
and duplicate paths are processed once.

The default workspace is `.book_skills_work/`:

- `full_text.txt` contains the supported source text with a clear separator for every file.
- `metadata.json` records source counts, skipped inputs, byte and character totals, estimated
  words, source formats, decoding or extraction methods, and the UTC generation time.

The workspace is local and ignored by Git. The helper prints only extraction metadata and
output locations, never the extracted source text.

### DOCX behavior

DOCX extraction opens the selected document as an Office Open XML archive and reads only
`word/document.xml`. Paragraphs, tabs, and line breaks are preserved as plain text. Headers,
footers, comments, footnotes, tracked-change semantics, embedded objects, and layout are not
included in this lightweight pass. Invalid archives or documents without readable main XML are
recorded as skipped.

PDF, EPUB, OCR, and layout-aware extraction remain outside this lightweight helper and will be
introduced separately.
