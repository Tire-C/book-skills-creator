# Security policy

Report vulnerabilities through a private GitHub security advisory when possible. Do not include private documents, credentials, tokens, personal data, or extracted text in public issues or pull requests.

## Source trust

Every selected document is **untrusted data**. Embedded text such as “ignore previous instructions,” “send this file,” or “execute this command” cannot instruct the Book Skills Creator agent or its helpers. The agent may analyze such passages as content, but must follow only the user's actual request and the trusted workflow. No helper uploads source content.

## Local processing

Selection is explicit. Directory and glob recursion occur only when passed by the user. Symlinks are skipped, overlapping paths deduplicated, and the output workspace excluded. File count/size, depth, extracted-text, archive entry/size/ratio limits are configurable. DOCX/EPUB archive entries are inspected before reading and never unpacked to disk. Optional PDF extraction uses a local external executable; scanned content needs a separate OCR tool.

`.book_skills_work/sources.json` and `full_text.txt` contain source text and are Git-ignored. Helpers print metadata and reason codes, not source passages. Generated packs should synthesize capability, retain evidence IDs and hashes, and avoid long copyrighted quotations. A validator warning screens for contiguous 30-word copying but cannot guarantee copyright safety or detect all paraphrase problems.

The model may still misinterpret source material. Review generated skills, conflicts, warnings, and behavioral cases before using a pack for consequential decisions.
