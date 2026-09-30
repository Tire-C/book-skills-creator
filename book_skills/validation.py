"""Deterministic validation. Semantic judgments remain review obligations."""

from __future__ import annotations

import hashlib
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from .discovery import is_link
from .pack import check_slug, linked_within, render_files


HEX = re.compile(r"^[0-9a-f]{64}$")
FRONTMATTER = re.compile(r'^---\nname: ([a-z0-9-]+)\ndescription: ("(?:[^"\\]|\\.)*")\n---\n\n', re.S)
CASES = {"positive", "negative", "combo", "reference", "ambiguous", "unsupported"}


def issue(items: list[dict], severity: str, code: str, location: str, detail: str = "") -> None:
    items.append({"severity": severity, "code": code, "location": location, "detail": detail})


def is_strings(value: object, nonempty: bool = False) -> bool:
    return isinstance(value, list) and (not nonempty or bool(value)) and all(isinstance(v, str) and bool(v.strip()) for v in value)


def required_text(item: dict, fields: tuple[str, ...], items: list[dict], location: str) -> None:
    for field in fields:
        if not isinstance(item.get(field), str) or not item[field].strip():
            issue(items, "ERROR", "missing-field", location, field)


def required_list(item: dict, fields: tuple[str, ...], items: list[dict], location: str, nonempty: bool = True) -> None:
    for field in fields:
        if not is_strings(item.get(field), nonempty):
            issue(items, "ERROR", "invalid-list", location, field)


def validate_extraction(extraction: object) -> list[dict]:
    """Reject damaged extraction snapshots before comparing or reading source text."""
    issues: list[dict] = []
    if not isinstance(extraction, dict) or extraction.get("schema_version") != "2.0" or not isinstance(extraction.get("sources"), list):
        issue(issues, "ERROR", "invalid-extraction", "sources.json")
        return issues
    source_ids: set[str] = set()
    evidence_ids: set[str] = set()
    for source in extraction["sources"]:
        if (not isinstance(source, dict) or not isinstance(source.get("id"), str)
                or not source["id"] or not isinstance(source.get("units"), list)
                or any(not isinstance(source.get(key), str) or not source[key] for key in ("method", "extractor_version"))
                or any(not isinstance(source.get(key), str) or not HEX.fullmatch(source[key]) for key in ("sha256", "extracted_sha256"))):
            issue(issues, "ERROR", "invalid-extraction", "sources.json")
            return issues
        if source["id"] in source_ids:
            issue(issues, "ERROR", "invalid-extraction", "sources.json", "duplicate source ID")
            return issues
        source_ids.add(source["id"])
        for unit in source["units"]:
            if (not isinstance(unit, dict) or not isinstance(unit.get("id"), str) or not unit["id"]
                    or not isinstance(unit.get("sha256"), str) or not HEX.fullmatch(unit["sha256"])
                    or not isinstance(unit.get("text"), str)):
                issue(issues, "ERROR", "invalid-extraction", "sources.json")
                return issues
            if unit["id"] in evidence_ids:
                issue(issues, "ERROR", "invalid-extraction", "sources.json", "duplicate evidence ID")
                return issues
            if hashlib.sha256(unit["text"].encode()).hexdigest() != unit["sha256"]:
                issue(issues, "ERROR", "invalid-extraction", "sources.json", "evidence hash mismatch")
                return issues
            evidence_ids.add(unit["id"])
        if hashlib.sha256("\n".join(unit["text"] for unit in source["units"]).encode()).hexdigest() != source["extracted_sha256"]:
            issue(issues, "ERROR", "invalid-extraction", "sources.json", "extracted hash mismatch")
            return issues
    return issues


def validate_plan(plan: dict, extraction: dict | None = None) -> list[dict]:
    issues: list[dict] = []
    required = {"schema_version", "status", "pack", "sources", "evidence", "extraction_gaps", "candidates", "atomic", "combo", "routes", "references", "overlaps", "conflicts", "uncertainties", "validation_risks", "behavior_tests"}
    for key in sorted(required - plan.keys()):
        issue(issues, "ERROR", "missing-key", "pack.json", key)
    if plan.get("schema_version") != "2.0":
        issue(issues, "ERROR", "schema-version", "pack.json")
    if plan.get("status") != "ready":
        issue(issues, "ERROR", "plan-not-ready", "pack.json")
    for key in required - {"schema_version", "status", "pack"}:
        if key in plan and not isinstance(plan[key], list):
            issue(issues, "ERROR", "invalid-type", "pack.json", key)
    if any(i["severity"] == "ERROR" for i in issues):
        return issues
    pack = plan.get("pack")
    if not isinstance(pack, dict):
        return issues + [{"severity": "ERROR", "code": "invalid-pack", "location": "pack.json", "detail": "pack"}]
    required_text(pack, ("name", "title", "description"), issues, "pack")
    name = pack.get("name", "")
    if not check_slug(name) or len(str(name) + "-router") > 64:
        issue(issues, "ERROR", "invalid-name", "pack", str(name))
    source_ids: set[str] = set()
    source_paths: set[str] = set()
    evidence_ids: set[str] = set()
    if not plan["sources"]:
        issue(issues, "ERROR", "no-sources", "pack.json")
    if not plan["atomic"]:
        issue(issues, "ERROR", "no-atomic-capabilities", "pack.json")
    for source in plan["sources"]:
        if not isinstance(source, dict):
            issue(issues, "ERROR", "invalid-source", "sources")
            continue
        sid = source.get("id")
        required_text(source, ("id", "path", "format", "sha256", "method", "extractor_version", "extracted_sha256", "quality"), issues, str(sid))
        if not isinstance(sid, str):
            issue(issues, "ERROR", "invalid-source-id", str(sid))
            continue
        if sid in source_ids:
            issue(issues, "ERROR", "duplicate-source-id", str(sid))
        source_ids.add(sid)
        path_value = source.get("path")
        if isinstance(path_value, str) and path_value in source_paths:
            issue(issues, "ERROR", "duplicate-source-path", path_value)
        if isinstance(path_value, str):
            source_paths.add(path_value)
        if not HEX.fullmatch(str(source.get("sha256", ""))) or not HEX.fullmatch(str(source.get("extracted_sha256", ""))):
            issue(issues, "ERROR", "invalid-hash", str(sid))
        if not isinstance(source.get("bytes"), int) or source["bytes"] < 0 or not is_strings(source.get("warnings")):
            issue(issues, "ERROR", "invalid-source-metadata", str(sid))
        if not isinstance(source.get("quality"), str) or source["quality"] not in {"complete", "partial", "unreadable"}:
            issue(issues, "ERROR", "invalid-extraction-quality", str(sid))
    for evidence in plan["evidence"]:
        if not isinstance(evidence, dict):
            issue(issues, "ERROR", "invalid-evidence", "evidence")
            continue
        eid = evidence.get("id")
        if not isinstance(eid, str):
            issue(issues, "ERROR", "invalid-evidence-id", str(eid))
            continue
        if eid in evidence_ids:
            issue(issues, "ERROR", "duplicate-evidence-id", str(eid))
        evidence_ids.add(eid)
        if (not isinstance(evidence.get("source_id"), str) or evidence["source_id"] not in source_ids
                or not eid.startswith(evidence["source_id"] + "-")):
            issue(issues, "ERROR", "bad-source-id", str(eid))
        if not HEX.fullmatch(str(evidence.get("sha256", ""))):
            issue(issues, "ERROR", "invalid-hash", str(eid))
        if not isinstance(evidence.get("heading_path"), list) or not isinstance(evidence.get("order"), int):
            issue(issues, "ERROR", "invalid-evidence-metadata", str(eid))
    ids: set[str] = set()
    nodes: set[str] = set()
    for kind in ("atomic", "combo", "references"):
        for unit in plan[kind]:
            if not isinstance(unit, dict):
                issue(issues, "ERROR", "invalid-unit", kind)
                continue
            uid = unit.get("id")
            location = f"{kind}:{uid}"
            if not check_slug(uid) or len(str(name) + "-" + str(uid)) > 64 or uid == "router":
                issue(issues, "ERROR", "invalid-name", location)
            if not isinstance(uid, str):
                continue
            if uid in ids:
                issue(issues, "ERROR", "duplicate-id", location)
            ids.add(uid)
            nodes.add(("reference" if kind == "references" else kind) + ":" + str(uid))
            if kind == "atomic":
                required_text(unit, ("title", "description", "mission", "use_when", "output"), issues, location)
                required_list(unit, ("inputs", "steps", "evidence"), issues, location)
                required_list(unit, ("constraints",), issues, location, False)
            elif kind == "combo":
                required_text(unit, ("title", "description", "mission", "use_when", "output"), issues, location)
                required_list(unit, ("dependencies", "flow", "evidence"), issues, location)
                if is_strings(unit.get("dependencies")) and len(unit["dependencies"]) < 2:
                    issue(issues, "ERROR", "combo-too-small", location)
            else:
                required_text(unit, ("title", "content"), issues, location)
                required_list(unit, ("evidence",), issues, location)
            for eid in unit.get("evidence", []) if isinstance(unit.get("evidence"), list) else []:
                if not isinstance(eid, str) or eid not in evidence_ids:
                    issue(issues, "ERROR", "bad-evidence-id", location, str(eid))
            if unit.get("grounding") == "review":
                issue(issues, "WARNING", "grounding-review", location)
            elif kind != "references" and unit.get("grounding") != "grounded":
                issue(issues, "ERROR", "missing-grounding-status", location)
    covered: set[str] = set()
    candidate_ids: set[str] = set()
    for candidate in plan["candidates"]:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("decision"), str) or candidate["decision"] not in {"accepted", "rejected", "reference"}:
            issue(issues, "ERROR", "invalid-candidate", "candidates")
            continue
        cid = candidate.get("id")
        if not check_slug(cid) or not isinstance(candidate.get("name"), str) or not candidate["name"].strip():
            issue(issues, "ERROR", "invalid-candidate", str(cid))
        if isinstance(cid, str) and cid in candidate_ids:
            issue(issues, "ERROR", "duplicate-candidate-id", cid)
        if isinstance(cid, str):
            candidate_ids.add(cid)
        if not is_strings(candidate.get("evidence"), True):
            issue(issues, "ERROR", "candidate-missing-evidence", str(cid))
        else:
            for eid in candidate["evidence"]:
                if eid not in evidence_ids:
                    issue(issues, "ERROR", "bad-evidence-id", str(cid), eid)
        if candidate["decision"] == "rejected":
            if not isinstance(candidate.get("reason"), str) or not candidate["reason"].strip():
                issue(issues, "ERROR", "missing-rejection-reason", str(cid))
        else:
            target = candidate.get("unit")
            if not isinstance(target, str) or target not in nodes or (candidate["decision"] == "reference") != target.startswith("reference:"):
                issue(issues, "ERROR", "invalid-candidate-unit", str(cid), str(target))
            else:
                covered.add(target)
    for node in sorted(nodes - covered):
        issue(issues, "ERROR", "unit-without-candidate", node)
    graph: dict[str, list[str]] = {}
    for unit in plan["combo"]:
        if not isinstance(unit, dict):
            continue
        node = "combo:" + str(unit.get("id"))
        dependencies = unit.get("dependencies", [])
        graph[node] = [dependency for dependency in dependencies if isinstance(dependency, str)] if isinstance(dependencies, list) else []
        for dependency in graph[node]:
            if dependency not in nodes or dependency.startswith("reference:"):
                issue(issues, "ERROR", "broken-dependency", node, str(dependency))
            if dependency == node:
                issue(issues, "ERROR", "self-dependency", node)
    seen: set[str] = set()
    active: set[str] = set()
    def visit(node: str) -> None:
        if node in active:
            issue(issues, "ERROR", "dependency-cycle", node)
            return
        if node in seen:
            return
        active.add(node)
        for child in graph.get(node, []):
            if child.startswith("combo:"):
                visit(child)
        active.remove(node)
        seen.add(node)
    for node in graph:
        visit(node)
    reachable: set[str] = set()
    for route in plan["routes"]:
        if not isinstance(route, dict) or not isinstance(route.get("when"), str) or not route["when"].strip():
            issue(issues, "ERROR", "invalid-route", "routes")
            continue
        target = route.get("target")
        if not isinstance(target, str) or target not in nodes:
            issue(issues, "ERROR", "broken-route", "routes", str(target))
        else:
            reachable.add(target)
    queue = list(reachable)
    while queue:
        node = queue.pop()
        for dependency in graph.get(node, []):
            if dependency not in reachable:
                reachable.add(dependency); queue.append(dependency)
    for node in sorted(nodes - reachable):
        issue(issues, "ERROR", "orphan-unit", node)
    for conflict in plan["conflicts"]:
        if not isinstance(conflict, dict) or not isinstance(conflict.get("description"), str) or not conflict["description"].strip() or not is_strings(conflict.get("evidence"), True):
            issue(issues, "ERROR", "invalid-conflict", "conflicts")
        else:
            for eid in conflict["evidence"]:
                if eid not in evidence_ids:
                    issue(issues, "ERROR", "bad-evidence-id", "conflicts", eid)
            if conflict.get("resolution") is None or conflict.get("resolution") == "unresolved":
                issue(issues, "WARNING", "unresolved-conflict", "conflicts", "Review source evidence")
    if not is_strings(plan["uncertainties"]):
        issue(issues, "ERROR", "invalid-uncertainties", "pack.json")
    for field in ("extraction_gaps", "validation_risks"):
        if not is_strings(plan[field]):
            issue(issues, "ERROR", "invalid-list", "pack.json", field)
    for overlap in plan["overlaps"]:
        if not isinstance(overlap, dict) or not isinstance(overlap.get("description"), str) or not overlap["description"].strip() or not isinstance(overlap.get("resolution"), str) or not overlap["resolution"].strip():
            issue(issues, "ERROR", "invalid-overlap", "overlaps")
    for case in plan["behavior_tests"]:
        if not isinstance(case, dict) or not isinstance(case.get("type"), str) or case["type"] not in CASES or not isinstance(case.get("request"), str) or not case["request"].strip():
            issue(issues, "ERROR", "invalid-behavior-case", "behavior_tests")
        elif case["type"] in {"positive", "combo", "reference", "negative"}:
            expected_kind = "reference" if case["type"] == "reference" else "combo" if case["type"] == "combo" else "atomic"
            target = case.get("target")
            if not isinstance(target, str) or target not in nodes or not target.startswith(expected_kind + ":"):
                issue(issues, "ERROR", "bad-behavior-target", "behavior_tests")
    for i, left in enumerate(plan["atomic"]):
        for right in plan["atomic"][i + 1:]:
            if not isinstance(left, dict) or not isinstance(right, dict):
                continue
            a = (str(left.get("mission", "")) + " " + str(left.get("use_when", ""))).lower()
            b = (str(right.get("mission", "")) + " " + str(right.get("use_when", ""))).lower()
            if len(a) > 30 and len(b) > 30 and SequenceMatcher(None, a, b).ratio() > .82:
                issue(issues, "WARNING", "possible-overlap", str(left.get("id")), str(right.get("id")))
    for combo in plan["combo"]:
        if not isinstance(combo, dict) or not is_strings(combo.get("flow")):
            continue
        for flow_step in combo["flow"]:
            for atomic in plan["atomic"]:
                if not isinstance(atomic, dict) or not is_strings(atomic.get("steps")):
                    continue
                for atomic_step in atomic["steps"]:
                    a, b = flow_step.casefold().strip(), atomic_step.casefold().strip()
                    if len(a) > 60 and len(b) > 60 and SequenceMatcher(None, a, b).ratio() > .85:
                        issue(issues, "WARNING", "combo-duplicates-atomic", str(combo.get("id")), str(atomic.get("id")))
    if extraction is not None:
        if any(item["severity"] == "ERROR" for item in issues):
            return issues
        issues.extend(validate_extraction(extraction))
        if any(item["code"] == "invalid-extraction" for item in issues):
            return issues
        fresh_sources = extraction["sources"]
        old_sources = {s["id"]: s for s in fresh_sources}
        evidence_sources = {u["id"]: s["id"] for s in fresh_sources for u in s["units"]}
        old_evidence = {u["id"]: u for s in fresh_sources for u in s["units"]}
        planned_sources = {s["id"] for s in plan["sources"] if isinstance(s, dict) and isinstance(s.get("id"), str)}
        planned_evidence = {u["id"] for u in plan["evidence"] if isinstance(u, dict) and isinstance(u.get("id"), str)}
        for sid in sorted(old_sources.keys() - planned_sources):
            issue(issues, "ERROR", "new-source-unreviewed", sid)
        for eid in sorted(old_evidence.keys() - planned_evidence):
            if evidence_sources[eid] in planned_sources:
                issue(issues, "ERROR", "new-evidence-unreviewed", eid)
        for source in plan["sources"]:
            current = old_sources.get(source.get("id"))
            if current is None or current.get("sha256") != source.get("sha256"):
                issue(issues, "ERROR", "stale-source", str(source.get("id")))
            elif any(current.get(field) != source.get(field) for field in ("extracted_sha256", "method", "extractor_version")):
                issue(issues, "ERROR", "stale-extraction", str(source.get("id")))
        for evidence in plan["evidence"]:
            current = old_evidence.get(evidence.get("id"))
            if current is None or current.get("sha256") != evidence.get("sha256"):
                issue(issues, "ERROR", "stale-evidence", str(evidence.get("id")))
    return issues


def validate_pack(root: Path, extraction: dict | None = None, legacy: bool = False) -> dict:
    issues: list[dict] = []
    if is_link(root):
        issue(issues, "ERROR", "symlink-pack", ".")
        return report(issues)
    manifest = root / "pack.json"
    if is_link(manifest):
        issue(issues, "ERROR", "symlink-generated-file", "pack.json")
        return report(issues)
    if not manifest.is_file():
        if legacy:
            return validate_legacy(root)
        issue(issues, "ERROR", "missing-manifest", "pack.json")
        return report(issues)
    try:
        plan = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        issue(issues, "ERROR", "invalid-manifest", "pack.json")
        return report(issues)
    if not isinstance(plan, dict):
        issue(issues, "ERROR", "invalid-manifest", "pack.json")
        return report(issues)
    issues.extend(validate_plan(plan, extraction))
    if any(i["severity"] == "ERROR" for i in issues):
        return report(issues, plan)
    expected = render_files(plan)
    for relative, content in expected.items():
        target = root / relative
        if linked_within(root, target):
            issue(issues, "ERROR", "symlink-generated-file", relative)
            continue
        if not target.is_file():
            issue(issues, "ERROR", "missing-generated-file", relative)
            continue
        try:
            actual = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            issue(issues, "ERROR", "unreadable-generated-file", relative)
            continue
        if actual != content:
            issue(issues, "ERROR", "manifest-file-mismatch", relative)
        if relative.endswith("SKILL.md"):
            match = FRONTMATTER.match(actual)
            try:
                valid_description = bool(match and json.loads(match.group(2)).strip())
            except (ValueError, TypeError):
                valid_description = False
            if not valid_description:
                issue(issues, "ERROR", "invalid-frontmatter", relative)
    for actual in root.rglob("*"):
        relative = actual.relative_to(root).as_posix()
        if is_link(actual):
            issue(issues, "ERROR", "symlink-generated-file", relative)
        elif actual.is_file() and relative not in expected and relative != "pack.json":
            issue(issues, "ERROR", "unlisted-skill" if actual.name == "SKILL.md" else "unlisted-generated-file", relative)
    for relative, content in expected.items():
        for destination in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
            if destination.startswith(("http:", "https:", "mailto:", "#")):
                continue
            target = (root / relative).parent / destination.split("#", 1)[0]
            if not target.resolve().is_relative_to(root.resolve()) or not target.exists():
                issue(issues, "ERROR", "broken-reference-link", relative, destination)
    if extraction:
        compare_verbatim(expected, extraction, issues)
    return report(issues, plan)


def compare_verbatim(files: dict[str, str], extraction: dict, issues: list[dict]) -> None:
    for path, content in files.items():
        if not path.startswith(("atomic/", "combo/", "references/")):
            continue
        words = re.findall(r"\w+", content.lower())
        if len(words) < 30:
            continue
        spans = {tuple(words[i:i + 30]) for i in range(len(words) - 29)}
        copied = False
        for source in extraction.get("sources", []):
            for unit in source.get("units", []):
                source_words = re.findall(r"\w+", unit["text"].lower())
                if any(tuple(source_words[i:i + 30]) in spans for i in range(len(source_words) - 29)):
                    issue(issues, "WARNING", "long-verbatim-overlap", path, unit["id"])
                    copied = True
                    break
            if copied:
                break


def validate_legacy(root: Path) -> dict:
    issues: list[dict] = []
    for relative in ("README.md", "source_index.md", "skill_map.md", "validation.md", "router/SKILL.md"):
        target = root / relative
        if linked_within(root, target):
            issue(issues, "ERROR", "symlink-generated-file", relative)
        elif not target.is_file():
            issue(issues, "ERROR", "missing-legacy-file", relative)
    for relative in ("atomic", "combo", "references"):
        target = root / relative
        if is_link(target):
            issue(issues, "ERROR", "symlink-generated-file", relative)
        elif not target.is_dir():
            issue(issues, "ERROR", "missing-legacy-directory", relative)
    for path in root.rglob("SKILL.md") if root.exists() else []:
        if linked_within(root, path):
            issue(issues, "ERROR", "symlink-generated-file", path.relative_to(root).as_posix())
        elif not FRONTMATTER.match(path.read_text(encoding="utf-8")):
            issue(issues, "ERROR", "invalid-frontmatter", path.relative_to(root).as_posix())
    issue(issues, "WARNING", "legacy-pack", ".", "No pack.json; graph and provenance cannot be verified")
    return report(issues)


def report(issues: list[dict], plan: dict | None = None) -> dict:
    errors = sum(item["severity"] == "ERROR" for item in issues)
    warnings = sum(item["severity"] == "WARNING" for item in issues)
    result = {"status": "FAIL" if errors else "PASS_WITH_WARNINGS" if warnings else "PASS", "errors": errors, "warnings": warnings, "issues": issues}
    if plan is not None:
        def entries(key: str) -> list:
            value = plan.get(key)
            return value if isinstance(value, list) else []
        result["metrics"] = {
            "sources": len(plan.get("sources", [])) if isinstance(plan.get("sources"), list) else None,
            "evidence_units": len(plan.get("evidence", [])) if isinstance(plan.get("evidence"), list) else None,
            "atomic_skills": len(plan.get("atomic", [])) if isinstance(plan.get("atomic"), list) else None,
            "combo_skills": len(plan.get("combo", [])) if isinstance(plan.get("combo"), list) else None,
            "references": len(plan.get("references", [])) if isinstance(plan.get("references"), list) else None,
            "routes": len(plan.get("routes", [])) if isinstance(plan.get("routes"), list) else None,
            "behavior_cases": len(plan.get("behavior_tests", [])) if isinstance(plan.get("behavior_tests"), list) else None,
            "grounded_skills": sum(unit.get("grounding") == "grounded" for kind in ("atomic", "combo") for unit in entries(kind) if isinstance(unit, dict)),
            "unresolved_conflicts": sum(item.get("resolution") in (None, "unresolved") for item in entries("conflicts") if isinstance(item, dict)),
            "orphan_units": sum(item["code"] == "orphan-unit" for item in issues),
            "broken_dependencies": sum(item["code"] == "broken-dependency" for item in issues),
            "overlap_warnings": sum(item["code"] in {"possible-overlap", "combo-duplicates-atomic"} for item in issues),
            "verbatim_warnings": sum(item["code"] == "long-verbatim-overlap" for item in issues),
        }
    return result
