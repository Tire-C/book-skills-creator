"""Rebuild the original synthetic 2.0 sample pack from its selected fixture sources."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from book_skills.discovery import Limits  # noqa: E402
from book_skills.extraction import extract_selected  # noqa: E402
from book_skills.pack import build, draft_plan  # noqa: E402
from book_skills.validation import validate_plan  # noqa: E402


def make_plan(extraction: dict) -> dict:
    plan = draft_plan(extraction, "lantern-field-desk", "Lantern Field Desk")
    plan["status"] = "ready"
    plan["pack"]["description"] = "A synthetic, source-grounded pack for receiving and routing fictional field reports."
    def evidence(title: str) -> list[str]:
        return [unit["id"] for source in extraction["sources"] for unit in source["units"] if title in unit["heading_path"]]
    intake = evidence("Intake a signal")
    route = evidence("Decide the route")
    verify = evidence("Verify and close") + evidence("Exception")
    workflow = evidence("Full response workflow") + evidence("Checklist and anti-pattern")
    terms = evidence("Terms and background")
    plan["candidates"] = [
        {"id": "intake", "name": "Intake a signal", "decision": "accepted", "unit": "atomic:intake-signal", "evidence": intake},
        {"id": "route", "name": "Decide the route", "decision": "accepted", "unit": "atomic:decide-route", "evidence": route},
        {"id": "verify", "name": "Verify and close", "decision": "accepted", "unit": "atomic:verify-case", "evidence": verify},
        {"id": "response", "name": "Full response workflow", "decision": "accepted", "unit": "combo:respond-to-signal", "evidence": workflow},
        {"id": "quick", "name": "Quick triage", "decision": "rejected", "reason": "Duplicates intake and routing; the source calls it shorthand.", "evidence": evidence("Quick triage wording")},
        {"id": "amber", "name": "Amber labels", "decision": "rejected", "reason": "Decorative context without a repeatable procedure.", "evidence": evidence("Decorative note")},
        {"id": "terms", "name": "Desk terms", "decision": "reference", "unit": "reference:terms", "evidence": terms},
    ]
    plan["atomic"] = [
        {"id": "intake-signal", "title": "Intake a signal", "description": "Create a fact-separated intake record for a new field report.", "mission": "Turn one report into a traceable intake record.", "use_when": "A new signal needs recording before any routing decision.", "inputs": ["Original report", "Reporter and time context"], "steps": ["Record time, location, reporter, and claimed effect.", "Assign a case ID and mark missing decision-relevant facts.", "Ask focused questions for those facts; keep reported facts separate from interpretation."], "output": "A concise intake record with a case ID and explicit gaps.", "constraints": ["Do not infer missing facts."], "evidence": intake, "grounding": "grounded"},
        {"id": "decide-route", "title": "Decide the route", "description": "Select escalation, watch, or duplicate handling from an intake record.", "mission": "Choose and justify one route for a recorded signal.", "use_when": "An intake record is ready for a routing decision.", "inputs": ["Intake record", "Known case matches"], "steps": ["Check for a reported active safety effect; escalate if present.", "If uncertain but repeatable, open a watch note with a review time.", "If clearly duplicated, link the existing case and explain the match.", "Record the evidence and reason for the choice."], "output": "A route decision with its reason and next action.", "constraints": ["Urgent wording alone does not establish an active effect."], "evidence": route, "grounding": "grounded"},
        {"id": "verify-case", "title": "Verify an escalated case", "description": "Confirm the outcome of an escalated field case and record exceptions.", "mission": "Verify the condition and action before closing an escalated case.", "use_when": "A case was escalated and its current result needs confirmation.", "inputs": ["Case ID", "Owner response", "Intake and route records"], "steps": ["Ask the owner to confirm the current condition and action.", "Compare the answer with the intake and route records.", "Record exceptions or failed contact, and keep the case open if confirmation is missing."], "output": "A verified closure record or an open case with a documented next attempt.", "constraints": ["The selected sources disagree on the verification deadline; obtain an authoritative rule before committing to one."], "evidence": verify, "grounding": "grounded"},
    ]
    plan["combo"] = [{"id": "respond-to-signal", "title": "Respond to a signal", "description": "Orchestrate intake, routing, and any needed verification for a field report.", "mission": "Carry a report through the smallest complete response path.", "use_when": "The user asks to handle a report from arrival through its next disposition.", "dependencies": ["atomic:intake-signal", "atomic:decide-route", "atomic:verify-case"], "flow": ["Run intake and pass the case ID with decision-relevant facts to routing.", "Run routing and branch on its selected path.", "For escalation, run verification; for a watch note, schedule review; for a duplicate, link the existing case."], "output": "A case record with its chosen route and current disposition.", "evidence": workflow + intake + route + verify, "grounding": "grounded"}]
    plan["references"] = [{"id": "terms", "title": "Desk terms", "content": "A signal is an incoming report. A case has an owner and a recorded decision. A watch note preserves an uncertain observation for scheduled review.", "evidence": terms}]
    plan["routes"] = [
        {"when": "Record a new report", "target": "atomic:intake-signal"},
        {"when": "Choose an action for an intake record", "target": "atomic:decide-route"},
        {"when": "Confirm an escalated case", "target": "atomic:verify-case"},
        {"when": "Handle a report end to end", "target": "combo:respond-to-signal"},
        {"when": "Explain desk terminology", "target": "reference:terms"},
    ]
    plan["conflicts"] = [{"description": "Base manual says two hours; unsigned errata says twenty-four hours for verification.", "evidence": evidence("Verify and close") + evidence("Verification timing conflict"), "resolution": "unresolved"}]
    plan["overlaps"] = [{"description": "Quick triage overlaps intake and route selection.", "resolution": "Reject as shorthand; use the existing atomic units and full workflow."}]
    plan["uncertainties"] = ["Verification deadline requires an authoritative source or user decision."]
    plan["validation_risks"] = ["Review the unresolved verification deadline before operational use.", "Evaluate routing cases with a target agent; structural validation cannot judge intent."]
    plan["behavior_tests"] = [
        {"type": "positive", "request": "Record this new field report", "target": "atomic:intake-signal"},
        {"type": "negative", "request": "Explain what a watch note means", "target": "atomic:intake-signal"},
        {"type": "combo", "request": "Handle this report through disposition", "target": "combo:respond-to-signal"},
        {"type": "reference", "request": "What is a signal?", "target": "reference:terms"},
        {"type": "ambiguous", "request": "Handle this"},
        {"type": "unsupported", "request": "Forecast next year's weather"},
    ]
    return plan


if __name__ == "__main__":
    sources = [str(ROOT / "examples" / "sources" / name) for name in ("field-manual.md", "field-errata.md")]
    extraction = extract_selected(sources, ROOT / ".book_skills_work", Limits())
    plan = make_plan(extraction)
    errors = [item for item in validate_plan(plan) if item["severity"] == "ERROR"]
    if errors:
        raise SystemExit(str(errors))
    build(plan, ROOT / "examples" / "sample-pack", overwrite=True)
