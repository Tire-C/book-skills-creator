# Contributing

Keep changes focused on the book-to-capability transformation and its verifiable contracts. Use only original synthetic source fixtures or material you have the right to process. Never commit private documents, extracted workspace contents, credentials, or copyrighted book passages.

The Python core targets 3.10+ and uses the standard library. An added mandatory dependency needs a concrete correctness or maintenance case. Keep source extraction deterministic and semantic decisions in the agent workflow. When changing a format, schema, command, or validation rule, update the relevant docs and synthetic tests.

Before a pull request, run:

```bash
python -m unittest discover -s tests
python -m compileall -q book_skills scripts tests examples/build_sample.py
python scripts/book_skills.py validate examples/sample-pack --json
python scripts/book_skills.py validate examples/v1-sample-pack --legacy --json
```

The v2 sample has one expected unresolved-conflict warning. The v1 sample has a `legacy-pack` warning. Neither warning should be silently removed by changing validator thresholds.
