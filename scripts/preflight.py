#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys


MINIMUM_PYTHON = (3, 10)
OPTIONAL_TOOLS = {
    "pdftotext": "text-based PDF extraction",
    "ebook-convert": "EPUB and ebook conversion",
}


def main() -> None:
    current = sys.version_info[:3]
    python_status = "OK" if current >= MINIMUM_PYTHON else "UNSUPPORTED"

    print("Required runtime")
    print(f"- Python {'.'.join(map(str, current))}: {python_status}")

    print("\nOptional external tools")
    for command, purpose in OPTIONAL_TOOLS.items():
        status = "AVAILABLE" if shutil.which(command) else "NOT FOUND"
        print(f"- {command}: {status} ({purpose})")

    print("\nBuilt-in extraction")
    print("- TXT, Markdown, DOCX: AVAILABLE (Python standard library)")

    if current < MINIMUM_PYTHON:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
