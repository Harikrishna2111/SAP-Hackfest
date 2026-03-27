"""
agent_runner.py
VIGIL-AI — CI Agent Runner
Runs in GitHub Actions. Reads inputs from the repo, calls Claude for
Verilog verification, writes structured outputs, then commits them back
via the GitHub API.

Usage (in GitHub Actions or locally):
    python agent_runner.py

Required environment variables:
    GITHUB_TOKEN        — GitHub PAT with repo write access
    ANTHROPIC_API_KEY   — Anthropic API key (replaces GOOGLE_API_KEY)
"""

import os
import json
import sys
import tempfile
import traceback
import difflib
from datetime import datetime
from pathlib import Path

import anthropic  # pip install anthropic

# ── Ensure project root on path ───────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from config import Config
from github_client import GitHubClient


# ─────────────────────────────────────────────────────────────────────────────
# Claude-powered Verilog Verification Agent
# ─────────────────────────────────────────────────────────────────────────────

class ClaudeVerilogAgent:
    """
    Lightweight Verilog verification agent backed by Anthropic Claude.
    Replaces the Gemini-based VerilogVerificationAgent.
    """

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4096

    SYSTEM_PROMPT = """\
You are an expert RTL (Register-Transfer Level) design verification engineer.
Your job is to:
1. Read a hardware specification (datasheet) describing the intended behaviour of a digital design.
2. Analyse the provided Verilog/SystemVerilog RTL code against that specification.
3. Identify ALL bugs, mismatches, and missing features — classify each as critical/high/medium/low severity.
4. Produce a corrected version of the RTL that fully satisfies the specification.
5. Return your answer as a single, valid JSON object — no markdown fences, no prose outside the JSON.

JSON schema (return exactly this structure):
{
  "summary": "<one-paragraph executive summary>",
  "issues": [
    {
      "type": "<e.g. logic_error | timing | reset | width_mismatch | missing_feature | ...>",
      "severity": "<critical | high | medium | low>",
      "description": "<what is wrong>",
      "suggested_fix": "<how to fix it>"
    }
  ],
  "fixed_rtl": "<complete corrected Verilog source as a single string>"
}
"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def _call(self, user_content: str) -> dict:
        """Send a single turn to Claude and parse the JSON response."""
        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = message.content[0].text.strip()

        # Strip accidental markdown fences if the model adds them
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        return json.loads(raw)

    def run(self, datasheet_text: str, verilog_code: str) -> dict:
        """
        Run verification and return a state dict compatible with the rest of
        agent_runner.py.
        """
        user_msg = (
            "=== SPECIFICATION ===\n"
            f"{datasheet_text}\n\n"
            "=== RTL CODE ===\n"
            f"{verilog_code}\n\n"
            "Analyse the RTL against the specification and return the JSON report."
        )

        try:
            result = self._call(user_msg)
        except json.JSONDecodeError as exc:
            return {
                "status": "error",
                "iteration": 1,
                "issues_found": [],
                "fixes_applied": [],
                "current_code": verilog_code,
                "verilog_code": verilog_code,
                "final_report": f"JSON parse error from Claude: {exc}",
            }

        issues = result.get("issues", [])
        fixed_rtl = result.get("fixed_rtl", verilog_code)
        summary = result.get("summary", "No summary provided.")

        # Build a markdown report
        report_lines = [
            "# VIGIL-AI Verification Report",
            "",
            "## Summary",
            summary,
            "",
            "## Issues Found",
        ]
        for idx, issue in enumerate(issues, 1):
            report_lines.append(
                f"\n### {idx}. [{issue.get('severity','?').upper()}] "
                f"{issue.get('type','unknown')}"
            )
            report_lines.append(f"**Description:** {issue.get('description','')}")
            if issue.get("suggested_fix"):
                report_lines.append(f"**Suggested fix:** {issue['suggested_fix']}")

        return {
            "status": "completed",
            "iteration": 1,
            "issues_found": issues,
            "fixes_applied": [i for i in issues if i.get("suggested_fix")],
            "current_code": fixed_rtl,
            "verilog_code": verilog_code,
            "final_report": "\n".join(report_lines),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def run_agent(datasheet_text: str, verilog_code: str) -> dict:
    """Instantiate the Claude agent and run verification."""
    api_key = os.getenv("ANTHROPIC_API_KEY") or getattr(Config, "ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. Add it as a repository secret."
        )
    agent = ClaudeVerilogAgent(api_key=api_key)
    return agent.run(datasheet_text, verilog_code)


def build_suggested_changes(original: str, fixed: str) -> str:
    """Return a unified diff of original vs fixed RTL."""
    if original.strip() == fixed.strip():
        return "// No changes suggested by the agent.\n"
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        fixed.splitlines(keepends=True),
        fromfile="original_rtl.v",
        tofile="suggested_changes.v",
        lineterm="",
    )
    return "\n".join(diff)


def build_report(
    run_id: str, state: dict, spec_filename: str, rtl_filename: str
) -> dict:
    """Convert agent state into a structured JSON report."""
    issues = state.get("issues_found", [])
    fixes  = state.get("fixes_applied", [])

    high   = sum(1 for i in issues if i.get("severity") in ("critical", "high"))
    medium = sum(1 for i in issues if i.get("severity") == "medium")
    low    = sum(1 for i in issues if i.get("severity") == "low")

    risk = "HIGH" if high > 0 else ("MEDIUM" if medium > 0 else "LOW")

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
        "VIGIL-AI Verification Risk Summary",
        f"Run: {report['run_id']}",
        f"Date: {report['timestamp']}",
        f"Spec: {report['spec_file']}",
        f"RTL:  {report['rtl_file']}",
        "",
        f"Overall Risk Level : {report['risk_level']}",
        f"Status             : {report['status']}",
        f"Iterations         : {report['iterations']}",
        f"Issues Found       : {report['issues_found']}",
        f"  HIGH   : {report['risk_counts']['high']}",
        f"  MEDIUM : {report['risk_counts']['medium']}",
        f"  LOW    : {report['risk_counts']['low']}",
        "",
        "--- Issues ---",
    ]
    for i, issue in enumerate(report.get("issues", []), 1):
        lines.append(
            f"{i}. [{issue.get('severity','?').upper()}] "
            f"{issue.get('type','?')}: {issue.get('description','')}"
        )
        if issue.get("suggested_fix"):
            lines.append(f"   Fix: {issue['suggested_fix']}")
    return "\n".join(lines)


def read_datasheet(spec_bytes: bytes, spec_filename: str) -> str:
    """
    Extract text from the spec file.
    Handles plain text and PDFs (via pypdf if available).
    """
    suffix = Path(spec_filename).suffix.lower()
    if suffix == ".pdf":
        try:
            import io
            from pypdf import PdfReader          # pip install pypdf
            reader = PdfReader(io.BytesIO(spec_bytes))
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        except ImportError:
            print("⚠  pypdf not installed — treating PDF as raw bytes (may be garbled).")
    return spec_bytes.decode("utf-8", errors="replace")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("VIGIL-AI Agent Runner")
    print("=" * 60)

    # ── Auth checks ────────────────────────────────────────────────────────────
    gh_token = os.getenv("GITHUB_TOKEN", "")
    if not gh_token:
        print("❌ GITHUB_TOKEN not set. Exiting.")
        sys.exit(1)

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not set. Add it as a repository secret.")
        sys.exit(1)

    # ── Read current_run.json from repo ────────────────────────────────────────
    gh = GitHubClient(token=gh_token)

    try:
        meta_file = gh._repo.get_contents("inputs/current_run.json")
        meta      = json.loads(meta_file.decoded_content.decode())
    except Exception as exc:
        print(f"❌ Could not read inputs/current_run.json: {exc}")
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
    except Exception as exc:
        print(f"❌ Could not download input files: {exc}")
        sys.exit(1)

    # ── Extract text from spec ─────────────────────────────────────────────────
    datasheet_text = read_datasheet(spec_bytes, spec_filename)

    # ── Run agent ──────────────────────────────────────────────────────────────
    logs = []

    def log(msg: str):
        print(msg)
        logs.append(msg)

    try:
        log(f"\n[{datetime.utcnow().isoformat()}] Starting verification agent...")
        state = run_agent(datasheet_text, rtl_text)
        log(
            f"[{datetime.utcnow().isoformat()}] Agent finished. "
            f"Status: {state.get('status')}"
        )
    except Exception as exc:
        error_msg = traceback.format_exc()
        log(f"❌ Agent error: {exc}\n{error_msg}")
        state = {
            "status": "error",
            "iteration": 0,
            "issues_found": [],
            "fixes_applied": [],
            "current_code": rtl_text,
            "verilog_code": rtl_text,
            "final_report": f"Agent failed: {exc}",
        }

    # ── Build outputs ──────────────────────────────────────────────────────────
    report         = build_report(run_id, state, spec_filename, rtl_filename)
    risk_summary   = build_risk_summary(report)
    fixed_rtl      = state.get("current_code", rtl_text)
    suggested_diff = build_suggested_changes(
        state.get("verilog_code", rtl_text), fixed_rtl
    )
    final_report_md = state.get("final_report", "No report generated.")
    log_text        = "\n".join(logs)

    # ── Commit results ─────────────────────────────────────────────────────────
    log(f"\nCommitting results to verification_runs/{run_id}/...")

    files_to_commit = {
        f"input_spec{Path(spec_filename).suffix}": spec_bytes,
        "input_rtl.v":            rtl_text,
        "fixed_rtl.v":            fixed_rtl,
        "report.json":            json.dumps(report, indent=2),
        "risk_summary.txt":       risk_summary,
        "suggested_changes.v":    suggested_diff,
        "verification_report.md": final_report_md,
        "logs.txt":               log_text,
    }

    try:
        gh.commit_results(run_id, files_to_commit)
        log(f"✅ Results committed to verification_runs/{run_id}/")
    except Exception as exc:
        log(f"❌ Commit failed: {exc}\n{traceback.format_exc()}")
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