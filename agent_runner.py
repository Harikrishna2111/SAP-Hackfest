"""
agent_runner.py
VIGIL-AI — CI Agent Runner
Runs in GitHub Actions. Reads inputs from the repo, calls verilog_agent.py,
writes structured outputs, then commits them back via the GitHub API.

Usage (in GitHub Actions or locally):
    python agent_runner.py
"""

import os
import json
import sys
import tempfile
import textwrap
import traceback
from datetime import datetime
from pathlib import Path

# ── Ensure project root on path ───────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from config import Config
from verilog_agent import VerilogVerificationAgent
from github_client import GitHubClient


def run_agent(datasheet_path: str, verilog_code: str) -> dict:
    """
    Run the verification agent and return a structured result dict.
    """
    agent = VerilogVerificationAgent(
        api_key=Config.GOOGLE_API_KEY,
        max_iterations=Config.MAX_ITERATIONS,
    )
    state = agent.run(
        datasheet_path=datasheet_path,
        verilog_code=verilog_code,
    )
    return state


def build_suggested_changes(original: str, fixed: str) -> str:
    """
    Produce a unified diff of original vs fixed code.
    If the agent returned the same code, show a placeholder.
    """
    if original.strip() == fixed.strip():
        return "// No changes suggested by the agent.\n"

    import difflib
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        fixed.splitlines(keepends=True),
        fromfile="original_rtl.v",
        tofile="suggested_changes.v",
        lineterm="",
    )
    return "\n".join(diff)


def build_report(run_id: str, state: dict, spec_filename: str, rtl_filename: str) -> dict:
    """
    Convert agent state into a structured JSON report.
    """
    issues = state.get("issues_found", [])
    fixes  = state.get("fixes_applied", [])

    high   = sum(1 for i in issues if i.get("severity") in ("critical", "high"))
    medium = sum(1 for i in issues if i.get("severity") == "medium")
    low    = sum(1 for i in issues if i.get("severity") == "low")

    if high > 0:
        risk = "HIGH"
    elif medium > 0:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "run_id":        run_id,
        "timestamp":     datetime.utcnow().isoformat(),
        "spec_file":     spec_filename,
        "rtl_file":      rtl_filename,
        "status":        state.get("status", "unknown"),
        "iterations":    state.get("iteration", 0),
        "issues_found":  len(issues),
        "fixes_applied": len(fixes),
        "risk_level":    risk,
        "risk_counts":   {"high": high, "medium": medium, "low": low},
        "issues":        issues,
    }


def build_risk_summary(report: dict) -> str:
    """Human-readable risk summary text."""
    lines = [
        f"VIGIL-AI Verification Risk Summary",
        f"Run: {report['run_id']}",
        f"Date: {report['timestamp']}",
        f"Spec: {report['spec_file']}",
        f"RTL:  {report['rtl_file']}",
        f"",
        f"Overall Risk Level : {report['risk_level']}",
        f"Status             : {report['status']}",
        f"Iterations         : {report['iterations']}",
        f"Issues Found       : {report['issues_found']}",
        f"  HIGH   : {report['risk_counts']['high']}",
        f"  MEDIUM : {report['risk_counts']['medium']}",
        f"  LOW    : {report['risk_counts']['low']}",
        f"",
        f"--- Issues ---",
    ]
    for i, issue in enumerate(report.get("issues", []), 1):
        lines.append(
            f"{i}. [{issue.get('severity','?').upper()}] {issue.get('type','?')}: "
            f"{issue.get('description','')}"
        )
        if issue.get("suggested_fix"):
            lines.append(f"   Fix: {issue['suggested_fix']}")
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("VIGIL-AI Agent Runner")
    print("=" * 60)

    gh_token = os.getenv("GITHUB_TOKEN", "")
    if not gh_token:
        print("❌ GITHUB_TOKEN not set. Exiting.")
        sys.exit(1)

    # ── Read current_run.json from repo ────────────────────────────────────────
    gh = GitHubClient(token=gh_token)

    try:
        meta_file = gh._repo.get_contents("inputs/current_run.json")
        meta      = json.loads(meta_file.decoded_content.decode())
    except Exception as e:
        print(f"❌ Could not read inputs/current_run.json: {e}")
        sys.exit(1)

    run_id        = meta["run_id"]
    spec_filename = meta["spec_filename"]
    rtl_filename  = meta["rtl_filename"]

    print(f"Run ID      : {run_id}")
    print(f"Spec file   : {spec_filename}")
    print(f"RTL file    : {rtl_filename}")

    # ── Download input files ───────────────────────────────────────────────────
    try:
        spec_bytes = gh._repo.get_contents(
            f"inputs/spec/{spec_filename}"
        ).decoded_content
        rtl_text = gh._repo.get_contents(
            f"inputs/rtl/{rtl_filename}"
        ).decoded_content.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"❌ Could not download input files: {e}")
        sys.exit(1)

    # ── Write spec to a temp file (agent expects a file path) ─────────────────
    suffix = Path(spec_filename).suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tf:
        tf.write(spec_bytes)
        spec_tmp = tf.name

    # ── Run agent ──────────────────────────────────────────────────────────────
    logs = []

    def log(msg: str):
        print(msg)
        logs.append(msg)

    try:
        log(f"\n[{datetime.utcnow().isoformat()}] Starting verification agent...")
        state = run_agent(spec_tmp, rtl_text)
        log(f"[{datetime.utcnow().isoformat()}] Agent finished. Status: {state.get('status')}")
    except Exception as e:
        error_msg = traceback.format_exc()
        log(f"❌ Agent error: {e}\n{error_msg}")
        state = {
            "status": "error",
            "iteration": 0,
            "issues_found": [],
            "fixes_applied": [],
            "current_code": rtl_text,
            "verilog_code": rtl_text,
            "final_report": f"Agent failed: {e}",
        }
    finally:
        os.unlink(spec_tmp)

    # ── Build outputs ──────────────────────────────────────────────────────────
    report          = build_report(run_id, state, spec_filename, rtl_filename)
    risk_summary    = build_risk_summary(report)
    fixed_rtl       = state.get("current_code", rtl_text)   # Full corrected code
    suggested_diff  = build_suggested_changes(
        state.get("verilog_code", rtl_text),
        fixed_rtl,
    )
    final_report_md = state.get("final_report", "No report generated.")
    log_text        = "\n".join(logs)


    # ── Commit results ─────────────────────────────────────────────────────────
    log(f"\nCommitting results to verification_runs/{run_id}/...")

    files_to_commit = {
        "input_spec" + Path(spec_filename).suffix: spec_bytes,
        "input_rtl.v":            rtl_text,
        "fixed_rtl.v":            fixed_rtl,       # ← Full corrected Verilog code
        "report.json":            json.dumps(report, indent=2),
        "risk_summary.txt":       risk_summary,
        "suggested_changes.v":    suggested_diff,  # ← Diff view of what changed
        "verification_report.md": final_report_md,
        "logs.txt":               log_text,
    }

    try:
        gh.commit_results(run_id, files_to_commit)
        log(f"✅ Results committed to verification_runs/{run_id}/")
    except Exception as e:
        log(f"❌ Commit failed: {e}\n{traceback.format_exc()}")
        sys.exit(1)

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"RUN COMPLETE: {run_id}")
    print(f"Risk Level  : {report['risk_level']}")
    print(f"Issues Found: {report['issues_found']}")
    print(f"Status      : {report['status']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
