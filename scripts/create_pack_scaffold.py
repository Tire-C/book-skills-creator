#!/usr/bin/env python3
"""Build an exact pack from a ready plan; no example units are inserted."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from book_skills.cli import main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Ready plan JSON from `book-skills plan`, completed by an agent")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(["build", str(args.plan), "--output", str(args.output), *(["--force"] if args.force else [])]))
