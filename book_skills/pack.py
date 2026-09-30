"""Canonical pack representation and deterministic Markdown generation."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .discovery import is_link


SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_SLUG = 64


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug or len(slug) > MAX_SLUG or not SLUG.fullmatch(slug):
        raise ValueError("invalid-slug")
    return slug


def check_slug(value: object) -> bool:
    return isinstance(value, str) and len(value) <= MAX_SLUG and bool(SLUG.fullmatch(value))


def draft_plan(extraction: dict, name: str, title: str | None = None) -> dict:
    slug = slugify(name)
    sources = []
    evidence = []
    for source in extraction["sources"]:
        sources.append({key: source[key] for key in ("id", "path", "format", "bytes", "sha256", "method", "extractor_version", "extracted_sha256", "quality", "warnings")})
        for unit in source["units"]:
            evidence.append({key: unit[key] for key in ("id", "kind", "heading_path", "order", "line_start", "line_end", "characters", "sha256")} | {"source_id": source["id"]})
    gaps = [item["path"] + ": " + item["reason"] for item in extraction.get("skipped", [])]
    gaps += [source["path"] + ": " + warning for source in sources for warning in source["warnings"]]
    return {"schema_version": "2.0", "status": "draft", "pack": {"name": slug, "title": title or name, "description": ""},
            "sources": sources, "evidence": evidence, "extraction_gaps": gaps, "candidates": [], "atomic": [], "combo": [],
            "routes": [], "references": [], "overlaps": [], "conflicts": [], "uncertainties": [],
            "validation_risks": [], "behavior_tests": []}


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("expected-json-object")
    return data


def dump_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def linked_within(root: Path, target: Path) -> bool:
    cursor = target
    while True:
        if is_link(cursor):
            return True
        if cursor == root:
            return False
        cursor = cursor.parent


def frontmatter(name: str, description: str) -> str:
    return "---\nname: " + name + "\ndescription: " + json.dumps(description, ensure_ascii=False) + "\n---\n\n"


def bullets(items: list[str]) -> str:
    return "\n".join("- " + item for item in items) if items else "- None recorded"


def numbered(items: list[str]) -> str:
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))


def render_atomic(pack_name: str, unit: dict) -> str:
    return (frontmatter(f"{pack_name}-{unit['id']}", unit["description"]) +
            f"# {unit['title']}\n\n## Mission\n\n{unit['mission']}\n\n## Use when\n\n{unit['use_when']}\n\n"
            f"## Inputs\n\n{bullets(unit['inputs'])}\n\n## Procedure\n\n{numbered(unit['steps'])}\n\n"
            f"## Output\n\n{unit['output']}\n\n## Constraints\n\n{bullets(unit['constraints'])}\n\n"
            f"## Evidence\n\n{bullets(unit['evidence'])}\n")


def render_combo(pack_name: str, unit: dict) -> str:
    return (frontmatter(f"{pack_name}-{unit['id']}", unit["description"]) +
            f"# {unit['title']}\n\n## Mission\n\n{unit['mission']}\n\n## Use when\n\n{unit['use_when']}\n\n"
            f"## Dependencies\n\n{bullets(unit['dependencies'])}\n\n## Flow\n\n{numbered(unit['flow'])}\n\n"
            f"## Output\n\n{unit['output']}\n\n## Evidence\n\n{bullets(unit['evidence'])}\n")


def render_router(plan: dict) -> str:
    pack = plan["pack"]
    lines = [frontmatter(pack["name"] + "-router", "Route requests to the smallest supported capability in " + pack["title"] + "."),
             "# " + pack["title"] + " router\n\nChoose one atomic skill when it suffices. Use a combo for a multi-step request. Use a reference for explanation. Ask for clarification when ambiguous; state limits for unsupported requests.\n\n## Routes\n"]
    for route in plan["routes"]:
        lines.append(f"- {route['when']} → `{route['target']}`\n")
    return "".join(lines)


def render_files(plan: dict) -> dict[str, str]:
    pack = plan["pack"]
    name = pack["name"]
    files = {"router/SKILL.md": render_router(plan)}
    for unit in plan["atomic"]:
        files[f"atomic/{unit['id']}/SKILL.md"] = render_atomic(name, unit)
    for unit in plan["combo"]:
        files[f"combo/{unit['id']}/SKILL.md"] = render_combo(name, unit)
    for ref in plan["references"]:
        files[f"references/{ref['id']}.md"] = f"# {ref['title']}\n\n{ref['content']}\n\n## Evidence\n\n{bullets(ref['evidence'])}\n"
    files["README.md"] = f"# {pack['title']}\n\n{pack['description']}\n\nStart at [the router](router/SKILL.md). The selected sources and known extraction limits are in [the source index](source_index.md).\n"
    source_lines = ["# Source index\n\n"]
    for source in plan["sources"]:
        source_lines.append(f"- {json.dumps(source['path'], ensure_ascii=False)} ({source['format']}); SHA-256 `{source['sha256']}`; method `{source['method']}`; quality `{source['quality']}`; warnings: {', '.join(source['warnings']) or 'none'}\n")
    files["source_index.md"] = "".join(source_lines)
    map_lines = ["# Skill map\n\n## Atomic\n\n"]
    map_lines.extend(f"- `{unit['id']}`: {unit['mission']}\n" for unit in plan["atomic"])
    map_lines.append("\n## Combo\n\n")
    map_lines.extend(f"- `{unit['id']}` → {', '.join(unit['dependencies'])}\n" for unit in plan["combo"])
    map_lines.append("\n## Rejected candidates\n\n")
    map_lines.extend(f"- {item['name']}: {item['reason']}\n" for item in plan["candidates"] if item.get("decision") == "rejected")
    map_lines.append("\n## Extraction gaps\n\n")
    map_lines.extend(f"- {item}\n" for item in plan["extraction_gaps"])
    map_lines.append("\n## Overlaps\n\n")
    map_lines.extend(f"- {item['description']}: {item['resolution']}\n" for item in plan["overlaps"])
    map_lines.append("\n## Conflicts, uncertainties, and validation risks\n\n")
    map_lines.extend(f"- {item.get('description', '')}: {item.get('resolution', 'unresolved')}\n" for item in plan["conflicts"])
    map_lines.extend(f"- {item}\n" for item in plan["uncertainties"])
    map_lines.extend(f"- Validation risk: {item}\n" for item in plan["validation_risks"])
    files["skill_map.md"] = "".join(map_lines)
    files["validation.md"] = "# Validation\n\nRun `python scripts/check_pack.py <pack-path> --json` for the current deterministic report. Review semantic grounding, overlap, conflicts, and behavioral cases separately.\n"
    return files


def build(plan: dict, output: Path, overwrite: bool = False) -> None:
    if is_link(output):
        raise ValueError("symlink-output")
    if output.exists() and any(output.iterdir()) and not overwrite:
        raise ValueError("output-exists; use --force to replace generated files")
    files = render_files(plan)
    expected = set(files) | {"pack.json"}
    if output.exists() and overwrite:
        stale = [p for p in output.rglob("*") if p.is_file() and p.relative_to(output).as_posix() not in expected]
        if stale:
            raise ValueError("output-has-unmanaged-files")
    output.mkdir(parents=True, exist_ok=True)
    for relative in expected:
        if linked_within(output, output / relative):
            raise ValueError("symlink-generated-path")
    for relative, content in files.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    (output / "pack.json").write_text(dump_json(plan), encoding="utf-8")
