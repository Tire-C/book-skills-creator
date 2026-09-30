"""Command interface for local source-to-pack work."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .discovery import Limits, discover, label
from .extraction import extract_selected, public_metadata, write_extraction
from .pack import build, draft_plan, dump_json, load_json
from .validation import report, validate_pack, validate_plan


def limits_from(args: argparse.Namespace) -> Limits:
    return Limits(**{key: getattr(args, key) for key in vars(Limits())})


def print_result(data: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif "issues" in data:
        print(data["status"])
        for item in data["issues"]:
            print(f"{item['severity']} {item['code']}: {item['location']} {item['detail']}")
    else:
        for key, value in data.items():
            if key not in {"sources", "skipped"}:
                print(f"{key}: {value}")
        for item in data.get("skipped", []):
            print(f"SKIPPED {item['path']}: {item['reason']}")


def inspect(args: argparse.Namespace) -> int:
    found, skipped = discover(args.paths, args.output, limits_from(args))
    data = {"recognized": [{"path": label(path), "format": path.suffix.lower().lstrip("."), "bytes": path.stat().st_size} for path in found], "skipped": skipped, "count": len(found)}
    if args.json:
        print_result(data, True)
    else:
        print("RECOGNIZED")
        for source in data["recognized"]:
            print(f"- {source['path']} | .{source['format']} | {source['bytes'] / 1024:.1f} KB")
        print("\nSKIPPED")
        for item in skipped:
            print(f"- {item['path']} | {item['reason']}")
        print("\nCOUNT")
        print(len(found))
    return 0 if found else 1


def extract(args: argparse.Namespace) -> int:
    data = extract_selected(args.paths, args.output, limits_from(args))
    metadata = public_metadata(data)
    if not data["sources"]:
        if args.json:
            print_result({"status": "FAIL", **metadata}, True)
        else:
            print("No readable selected sources were found.")
            print_result(metadata, False)
        return 1
    write_extraction(data, args.output)
    if args.json:
        print_result({"status": "PASS", "output": str(args.output), **metadata}, True)
    else:
        print("Extraction complete")
        print(f"Supported sources: {metadata['supported_sources']}")
        print(f"Skipped sources: {metadata['skipped_sources']}")
        print(f"Bytes read: {metadata['total_bytes']}")
        print(f"Characters extracted: {metadata['total_characters']}")
        print(f"Estimated words: {metadata['estimated_words']}")
        print(f"Output directory: {args.output}")
    return 0


def plan(args: argparse.Namespace) -> int:
    source_data = load_json(args.extraction)
    if not source_data.get("sources"):
        raise ValueError("extraction-has-no-sources")
    result = draft_plan(source_data, args.name, args.title)
    if args.output.exists() and not args.force:
        raise ValueError("plan-exists; use --force to replace")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(dump_json(result), encoding="utf-8")
    print_result({"status": "DRAFT", "plan": str(args.output), "sources": len(result["sources"]), "evidence_units": len(result["evidence"])}, args.json)
    return 0


def build_command(args: argparse.Namespace) -> int:
    plan_data = load_json(args.plan)
    result = report(validate_plan(plan_data))
    if result["errors"]:
        print_result(result, args.json)
        return 1
    build(plan_data, args.output, args.force)
    result = validate_pack(args.output)
    print_result({"output": str(args.output), **result}, args.json)
    return 1 if result["errors"] else 0


def validate_command(args: argparse.Namespace) -> int:
    extraction = load_json(args.extraction) if args.extraction else None
    result = validate_pack(args.pack, extraction, args.legacy)
    print_result(result, args.json)
    return 1 if result["errors"] else 0


def update_command(args: argparse.Namespace) -> int:
    plan_data = load_json(args.pack / "pack.json")
    fresh = load_json(args.extraction)
    old_sources = {source["id"]: source for source in plan_data["sources"]}
    new_sources = {source["id"]: source for source in fresh["sources"]}
    old_units = {unit["id"]: unit for unit in plan_data["evidence"]}
    new_units = {unit["id"]: unit for source in fresh["sources"] for unit in source["units"]}
    changed_sources = sorted(sid for sid in old_sources.keys() | new_sources.keys() if sid not in old_sources or sid not in new_sources or any(old_sources[sid].get(field) != new_sources[sid].get(field) for field in ("sha256", "extracted_sha256", "method", "extractor_version")))
    changed_evidence = sorted(eid for eid in old_units.keys() | new_units.keys() if eid not in old_units or eid not in new_units or old_units[eid]["sha256"] != new_units[eid]["sha256"])
    new_evidence = sorted(new_units.keys() - old_units.keys())
    removed_evidence = sorted(old_units.keys() - new_units.keys())
    changed_set = set(changed_evidence)
    affected = {kind + ":" + unit["id"] for kind in ("atomic", "combo", "references") for unit in plan_data[kind] if set(unit.get("evidence", [])) & changed_set}
    changed = True
    while changed:
        before = len(affected)
        for combo in plan_data["combo"]:
            if set(combo["dependencies"]) & affected:
                affected.add("combo:" + combo["id"])
        changed = len(affected) != before
    result = {"status": "STALE" if changed_sources or changed_evidence else "CURRENT", "changed_sources": changed_sources,
              "changed_evidence": changed_evidence, "new_evidence": new_evidence, "removed_evidence": removed_evidence,
              "affected_units": sorted(affected),
              "note": "Review changed and new evidence, revise affected units or discover new capabilities, then rebuild and validate." if changed_sources or changed_evidence else "No source or evidence changes detected."}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dump_json(result), encoding="utf-8")
    print_result(result, args.json)
    return 0


def preflight(args: argparse.Namespace) -> int:
    data = {"python": ".".join(map(str, sys.version_info[:3])), "supported": sys.version_info >= (3, 10),
            "built_in": ["TXT", "Markdown", "DOCX", "HTML", "EPUB"],
            "optional": {"pdftotext": bool(shutil.which("pdftotext")), "tesseract": bool(shutil.which("tesseract"))}}
    if args.json:
        print_result(data, True)
    else:
        print("Required runtime")
        print(f"- Python {data['python']}: {'OK' if data['supported'] else 'UNSUPPORTED'}")
        print("\nBuilt-in extraction")
        print("- TXT, Markdown, DOCX, HTML, EPUB: AVAILABLE (Python standard library)")
        print("\nOptional external tools")
        for name, available in data["optional"].items():
            print(f"- {name}: {'AVAILABLE' if available else 'NOT FOUND'}")
    return 0 if data["supported"] else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="book-skills", description="Create and validate modular source-grounded Agent Skill packs.")
    sub = root.add_subparsers(dest="command", required=True)
    def common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--json", action="store_true", help="Machine-readable stdout")
    def source(command: argparse.ArgumentParser) -> None:
        command.add_argument("paths", nargs="+", help="Explicit files, directories, or globs")
        command.add_argument("--output", type=Path, default=Path(".book_skills_work"))
        for key, value in vars(Limits()).items():
            command.add_argument("--" + key.replace("_", "-"), type=int, default=value)
        common(command)
    p = sub.add_parser("preflight"); common(p); p.set_defaults(func=preflight)
    p = sub.add_parser("inspect"); source(p); p.set_defaults(func=inspect)
    p = sub.add_parser("extract"); source(p); p.set_defaults(func=extract)
    p = sub.add_parser("plan"); p.add_argument("extraction", type=Path); p.add_argument("name"); p.add_argument("--title"); p.add_argument("--output", type=Path, required=True); p.add_argument("--force", action="store_true"); common(p); p.set_defaults(func=plan)
    p = sub.add_parser("build"); p.add_argument("plan", type=Path); p.add_argument("--output", type=Path, required=True); p.add_argument("--force", action="store_true"); common(p); p.set_defaults(func=build_command)
    p = sub.add_parser("validate"); p.add_argument("pack", type=Path); p.add_argument("--extraction", type=Path); p.add_argument("--legacy", action="store_true", help="Check a v1 Markdown-only pack with limited guarantees"); common(p); p.set_defaults(func=validate_command)
    p = sub.add_parser("update"); p.add_argument("pack", type=Path); p.add_argument("extraction", type=Path); p.add_argument("--output", type=Path); common(p); p.set_defaults(func=update_command)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {str(exc) if isinstance(exc, ValueError) else exc.__class__.__name__}", file=sys.stderr)
        return 2
