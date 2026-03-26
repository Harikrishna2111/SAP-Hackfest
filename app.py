"""
app.py — VIGIL-AI Streamlit Application
Two tabs:
  1. Upload  — upload spec + RTL, push to GitHub, trigger CI
  2. Runs    — view all verification runs and their results

Run with: streamlit run app.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()   # ← loads .env so GITHUB_TOKEN and GOOGLE_API_KEY are available

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VIGIL-AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Header */
.vigil-header {
    background: linear-gradient(135deg, #0d1117, #161b22);
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 32px 36px;
    margin-bottom: 28px;
}
.vigil-header h1 { font-size: 2.4rem; font-weight: 700;
    background: linear-gradient(90deg, #58a6ff, #56d364);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.vigil-header p { color: #8b949e; margin: 0; }

/* Cards */
.run-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 18px 20px; margin: 8px 0;
}
.risk-HIGH   { color: #f85149; font-weight: 700; }
.risk-MEDIUM { color: #d29922; font-weight: 700; }
.risk-LOW    { color: #56d364; font-weight: 700; }

/* Status badges */
.badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
}
.badge-high   { background: #3d1a1a; color: #f85149; border: 1px solid #f85149; }
.badge-medium { background: #3d2e1a; color: #d29922; border: 1px solid #d29922; }
.badge-low    { background: #1a2e1a; color: #56d364; border: 1px solid #56d364; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vigil-header">
    <h1>🛡️ VIGIL-AI</h1>
    <p>Verification Intelligence & Governance using Intelligent Learning &nbsp;·&nbsp;
       AI-assisted RTL verification with full audit trail</p>
</div>
""", unsafe_allow_html=True)

# ── GitHub client check ────────────────────────────────────────────────────────
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def get_gh_client():
    from github_client import GitHubClient
    return GitHubClient(token=GITHUB_TOKEN)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_upload, tab_runs = st.tabs(["📥  Upload & Analyze", "📋  Verification Runs"])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1: UPLOAD
# ════════════════════════════════════════════════════════════════════════════════
with tab_upload:
    st.markdown("### 1️⃣  Upload Your Files")
    st.caption(
        "Upload your specification document and Verilog RTL code. "
        "Files are pushed to GitHub and the AI agent runs automatically."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📄 Specification Document**")
        spec_file = st.file_uploader(
            "Upload datasheet (.pdf, .txt, .md)",
            type=["pdf", "txt", "md"],
            key="spec_upload",
        )
        if spec_file:
            st.success(f"✅ {spec_file.name}  ({spec_file.size:,} bytes)")

    with col2:
        st.markdown("**💻 Verilog / SystemVerilog RTL**")
        rtl_file = st.file_uploader(
            "Upload RTL source (.v, .sv)",
            type=["v", "sv"],
            key="rtl_upload",
        )
        if rtl_file:
            rtl_preview = rtl_file.read().decode("utf-8", errors="replace")
            rtl_file.seek(0)
            st.success(f"✅ {rtl_file.name}  ({rtl_file.size:,} bytes)")
            with st.expander("Preview RTL"):
                st.code(rtl_preview[:2000], language="verilog")

    st.divider()
    st.markdown("### 2️⃣  Push to GitHub & Trigger Analysis")

    if not GITHUB_TOKEN:
        st.warning(
            "⚠️ **GITHUB_TOKEN** not found in your environment. "
            "Add it to `.env` to enable GitHub integration.\n\n"
            "Create a token: https://github.com/settings/tokens  (needs **repo** scope)"
        )

    ready = bool(spec_file and rtl_file and GITHUB_TOKEN)

    if st.button("🚀 Upload & Start Verification", type="primary",
                  disabled=not ready, use_container_width=True):
        with st.spinner("Pushing files to GitHub..."):
            try:
                gh     = get_gh_client()
                run_id = gh.push_inputs(
                    spec_bytes    = spec_file.read(),
                    spec_filename = spec_file.name,
                    rtl_bytes     = rtl_file.read(),
                    rtl_filename  = rtl_file.name,
                )
                st.success(
                    f"✅ Files uploaded! Run **{run_id}** created.\n\n"
                    f"GitHub Actions will now trigger the AI agent automatically. "
                    f"Check the **Verification Runs** tab in ~2 minutes."
                )
                st.markdown(
                    f"[🔗 View workflow run on GitHub]"
                    f"(https://github.com/RisheekeshKG/SAP-Hackfest/actions)"
                )
            except Exception as e:
                st.error(f"❌ Upload failed: {e}")

    if not ready and not (spec_file and rtl_file):
        st.info("↑ Upload both files to enable the button.")
    if not ready and GITHUB_TOKEN and (spec_file or rtl_file):
        st.info("↑ Upload both files to enable the button.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2: RUNS DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
with tab_runs:
    st.markdown("### 📋 All Verification Runs")

    col_refresh, col_spacer = st.columns([1, 5])
    with col_refresh:
        refresh = st.button("🔄 Refresh", use_container_width=True)

    if not GITHUB_TOKEN:
        st.warning("⚠️ GITHUB_TOKEN not set — cannot load runs from GitHub.")
        st.stop()

    with st.spinner("Loading runs from GitHub..."):
        try:
            gh   = get_gh_client()
            runs = gh.list_runs()
        except Exception as e:
            st.error(f"❌ Could not load runs: {e}")
            runs = []

    if not runs:
        st.info("No verification runs yet. Upload files in the **Upload** tab to start.")
        st.stop()

    # ── Summary metrics ─────────────────────────────────────────────────────────
    total  = len(runs)
    highs  = sum(1 for r in runs if r["report"].get("risk_level") == "HIGH")
    meds   = sum(1 for r in runs if r["report"].get("risk_level") == "MEDIUM")
    lows   = sum(1 for r in runs if r["report"].get("risk_level") == "LOW")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Runs",    total)
    m2.metric("🔴 HIGH Risk",  highs)
    m3.metric("🟡 MEDIUM Risk",meds)
    m4.metric("🟢 LOW Risk",   lows)

    st.divider()

    # ── Run cards ───────────────────────────────────────────────────────────────
    for run in runs:
        run_id = run["run_id"]
        report = run["report"]

        risk   = report.get("risk_level", "—")
        status = report.get("status", "—")
        ts     = report.get("timestamp", "—")[:19].replace("T", " ") if report else "—"
        issues = report.get("issues_found", "—")

        badge_cls = f"badge-{risk.lower()}" if risk in ("HIGH","MEDIUM","LOW") else ""

        with st.expander(
            f"**{run_id}** &nbsp; · &nbsp; Risk: {risk} &nbsp; · &nbsp; {ts} &nbsp; · &nbsp; {issues} issues",
            expanded=False,
        ):
            # ── Top row ─────────────────────────────────────────────────────────
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Risk Level",   risk)
            r2.metric("Status",       status)
            r3.metric("Issues Found", report.get("issues_found", "—"))
            r4.metric("Iterations",   report.get("iterations", "—"))

            st.markdown("---")

            # ── Issues list ──────────────────────────────────────────────────────
            issues_list = report.get("issues", [])
            if issues_list:
                st.markdown("**🔍 Issues Found:**")
                for i, issue in enumerate(issues_list, 1):
                    sev = issue.get("severity", "?").upper()
                    col = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}.get(sev,"⚪")
                    st.markdown(
                        f"{col} **[{sev}]** {issue.get('type','?')}: {issue.get('description','')}"
                    )
                    if issue.get("suggested_fix"):
                        st.caption(f"&nbsp;&nbsp;&nbsp;💡 {issue['suggested_fix']}")
            else:
                st.success("✅ No issues found in this run.")

            st.markdown("---")

            # ── File downloads ───────────────────────────────────────────────────
            st.markdown("**📥 Download Artifacts:**")
            dc1, dc2, dc3, dc4 = st.columns(4)

            for col, fname, label in [
                (dc1, "risk_summary.txt",     "📄 Risk Summary"),
                (dc2, "report.json",          "📊 Full Report"),
                (dc3, "suggested_changes.v",  "🔧 Suggested Changes"),
                (dc4, "verification_report.md","📝 Verification Report"),
            ]:
                with col:
                    content = gh.get_run_file(run_id, fname)
                    if content:
                        st.download_button(
                            label=label,
                            data=content,
                            file_name=fname,
                            key=f"dl_{run_id}_{fname}",
                            use_container_width=True,
                        )
                    else:
                        st.caption(f"_{fname} not ready_")

            # ── Suggested changes viewer ─────────────────────────────────────────
            suggested = gh.get_run_file(run_id, "suggested_changes.v")
            if suggested and "No changes suggested" not in suggested:
                st.markdown("**🔧 Suggested RTL Changes (diff):**")
                st.code(suggested, language="diff")
                st.warning(
                    "⚠️ **Human review required.** The agent does NOT auto-apply changes. "
                    "Review the diff above and apply manually if you approve."
                )

            # ── View logs ────────────────────────────────────────────────────────
            with st.expander("🪵 View Logs"):
                logs_txt = gh.get_run_file(run_id, "logs.txt")
                if logs_txt:
                    st.text(logs_txt)
                else:
                    st.caption("Logs not available yet.")

            # ── GitHub link ──────────────────────────────────────────────────────
            st.markdown(
                f"[🔗 View in GitHub](https://github.com/RisheekeshKG/SAP-Hackfest/tree/main/verification_runs/{run_id})"
            )
