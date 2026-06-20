#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def slugify(text: str) -> str:
    allowed = []
    for char in text.lower().strip().replace("_", "-").replace(" ", "-"):
        if char.isalnum() or char == "-":
            allowed.append(char)
    slug = "".join(allowed).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "book-pack"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an empty generated pack scaffold.")
    parser.add_argument("name", help="Pack name or slug")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    slug = slugify(args.name)
    root = Path(args.output) / slug

    write(root / "README.md", f"# {slug}\n\nGenerated pack scaffold.\n")
    write(root / "source_index.md", "# Source index\n\n")
    write(root / "skill_map.md", "# Skill map\n\n")
    write(root / "validation.md", "# Validation\n\n")
    write(root / "router" / "SKILL.md", f"---\nname: {slug}-router\ndescription: \"Route requests to the right generated skill in this pack.\"\n---\n\n# Router\n")
    write(root / "atomic" / ".gitkeep", "")
    write(root / "combo" / ".gitkeep", "")
    write(root / "references" / ".gitkeep", "")
    write(root / "references" / "chapters" / ".gitkeep", "")

    print(root)


if __name__ == "__main__":
    main()
