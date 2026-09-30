#!/usr/bin/env python3
"""Repository-local Book Skills Creator CLI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from book_skills.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
