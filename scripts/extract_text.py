#!/usr/bin/env python3
"""Compatibility entry point for `book-skills extract`."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from book_skills.cli import main
if __name__ == "__main__":
    raise SystemExit(main(["extract", *sys.argv[1:]]))
