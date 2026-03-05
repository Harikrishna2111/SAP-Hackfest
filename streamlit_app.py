"""
Streamlit UI for Verilog Design Verification Agent
Provides an n8n-like workflow visualization and interactive interface
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import tempfile
import json
from typing import Optional

from verilog_agent import VerilogVerificationAgent
from config import Config
from waveform_generator import WaveformGenerator
import subprocess
try:
    from workflow_visualizer import WorkflowVisualizer
except ImportError:
    WorkflowVisualizer = None
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# Configure Streamlit page
st.set_page_config(
    page_title="Verilog Component Verification Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .workflow-node {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        text-align: center;
    }
    
    .workflow-node.active {
        background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
        box-shadow: 0 0 20px rgba(0, 153, 255, 0.6);
    }
    
    .workflow-node.completed {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .workflow-node.error {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    .issue-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #ff6b6b;
    }
    
    .issue-card.fixed {
        border-left-color: #51cf66;
        background: #f1fdf4;
    }
    
    .code-section {
        background: #282c34;
        color: #abb2bf;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
    }
    
    .info-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        margin: 2px 4px 2px 0;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitAgent:
    """Streamlit wrapper for the Verilog Verification Agent"""
    
    def __init__(self):
        """Initialize the Streamlit agent"""
        self.agent = None
        self.execution_log = []
        
    def initialize_agent(self):
        """Initialize the verification agent"""
        if not Config.GOOGLE_API_KEY:
            st.error("❌ Google API Key not found. Please set GOOGLE_API_KEY in your .env file")
            st.info("💡 Get your API key from: https://makersuite.google.com/app/apikey")
            return False
        
        try:
            self.agent = VerilogVerificationAgent(
                api_key=Config.GOOGLE_API_KEY,
                max_iterations=Config.MAX_ITERATIONS
            )
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {str(e)}")
            return False
    
    def log_step(self, step_name: str, status: str, details: str = ""):
        """Log execution steps"""
        self.execution_log.append({
            "timestamp": datetime.now(),
            "step": step_name,
            "status": status,
            "details": details
        })


def header_section():
    """Render the header section"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📄 Verilog Component Verification Agent")
        st.markdown("""
        Automated verification of Verilog designs using **LangGraph** + **Google Gemini**
        - 📄 Analyzes component datasheets (PDF or text)
        - 🔄 Iteratively identifies and fixes issues
        - 📊 Generates comprehensive reports
        """)
    
    with col2:
        st.markdown(f"""
        <div style='text-align: right; padding-top: 20px;'>
            <div class='info-badge'>v1.0.0</div><br>
            <div class='info-badge'>LangGraph</div><br>
            <div class='info-badge'>Gemini API</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()


def sidebar_configuration():
    """Render the sidebar configuration"""
    st.sidebar.title("⚙️ Configuration")
    
    max_iterations = st.sidebar.slider(
        "Max Iterations",
        min_value=1,
        max_value=10,
        value=Config.MAX_ITERATIONS,
        help="Maximum number of fix iterations"
    )
    
    model_name = st.sidebar.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        help="Gemini model version to use"
    )
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Model creativity level (lower = more consistent)"
    )
    
    st.sidebar.divider()
    st.sidebar.title("📚 Resources")
    st.sidebar.markdown("""
    - [📖 Documentation](README.md)
    - [🚀 Quick Start](QUICK_START.md)
    - [📄 Datasheet Guide](DATASHEET_GUIDE.md)
    """)
    
    return {
        "max_iterations": max_iterations,
        "model_name": model_name,
        "temperature": temperature
    }


def input_section():
    """Render the input section for datasheet and code"""
    st.header("📥 Input")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    # Datasheet Input
    with col1:
        st.subheader("📄 Component Datasheet")
        uploaded_datasheet = st.file_uploader(
            "Upload component datasheet",
            type=["pdf", "txt", "md"],
            help="Component datasheet in PDF or text format"
        )
        
        datasheet_path = None
        datasheet_content = ""
        
        if uploaded_datasheet:
            # Save uploaded datasheet temporarily
            file_ext = Path(uploaded_datasheet.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                tmp.write(uploaded_datasheet.getbuffer())
                datasheet_path = tmp.name
            
            # Display datasheet info
            if file_ext == ".pdf":
                if PdfReader:
                    try:
                        reader = PdfReader(datasheet_path)
                        num_pages = len(reader.pages)
                        st.info(f"📄 PDF uploaded: {num_pages} pages")
                        # Extract preview
                        preview_text = reader.pages[0].extract_text()[:500]
                        with st.expander("Preview first page"):
                            st.text(preview_text + "...")
                    except Exception as e:
                        st.warning(f"Could not preview PDF: {str(e)}")
                else:
                    st.warning("PDF preview not available. Install pypdf: pip install pypdf")
            else:
                # Text file - show preview
                with open(datasheet_path, 'r', encoding='utf-8') as f:
                    datasheet_content = f.read()
                    preview = datasheet_content[:500]
                    with st.expander("Preview datasheet"):
                        st.text(preview + "...")
            
            st.success("✅ Datasheet uploaded successfully")
    
    # Verilog Code Input
    with col2:
        st.subheader("💻 Verilog Code")
        
        code_input_method = st.radio(
            "Input method",
            ["Paste code", "Upload file"],
            horizontal=True
        )
        
        verilog_code = None
        
        if code_input_method == "Paste code":
            verilog_code = st.text_area(
                "Paste your Verilog code",
                height=300,
                placeholder="module my_design (...)\n  // Your code here\nendmodule",
                help="Enter your Verilog HDL code"
            )
        else:
            uploaded_code = st.file_uploader(
                "Upload Verilog file",
                type=["v", "sv", "verilog"],
                help="Verilog source file"
            )
            if uploaded_code:
                verilog_code = uploaded_code.read().decode("utf-8")
                st.code(verilog_code, language="verilog")
    
    # Waveform Generation
    with col3:
        st.subheader("📊 Waveform")
        
        # Check installed simulators
        def check_simulator(cmd):
            try:
                subprocess.run([cmd, "--version"], capture_output=True, shell=True, timeout=2)
                return True
            except:
                try:
                    subprocess.run([cmd, "-v"], capture_output=True, shell=True, timeout=2)
                    return True
                except:
                    return False
        
        xyce_installed = check_simulator("Xyce")
        iverilog_installed = check_simulator("iverilog")
        ngspice_installed = check_simulator("ngspice")
        
        # Show installation status
        with st.expander("🔧 Simulator Status"):
            st.write(f"{'✅' if xyce_installed else '❌'} Xyce")
            st.write(f"{'✅' if iverilog_installed else '❌'} Icarus Verilog")
            st.write(f"{'✅' if ngspice_installed else '❌'} Ngspice")
            if not any([xyce_installed, iverilog_installed, ngspice_installed]):
                st.warning("No simulators installed. Install at least one to generate waveforms.")
        
        # Simulator selection
        available_sims = []
        if xyce_installed:
            available_sims.append("Xyce")
        if iverilog_installed:
            available_sims.append("Icarus Verilog")
        if ngspice_installed:
            available_sims.append("Ngspice")
        
        if not available_sims:
            available_sims = ["Xyce", "Icarus Verilog", "Ngspice"]  # Show all even if not installed
        
        # Custom Xyce path if not in PATH
        xyce_custom_path = None
        if "Xyce" in available_sims or not xyce_installed:
            with st.expander("⚙️ Custom Xyce Path (if not in PATH)"):
                xyce_custom_path = st.text_input(
                    "Xyce executable path",
                    placeholder="C:\\Program Files\\Xyce\\bin\\Xyce.exe",
                    help="Full path to Xyce.exe if not in system PATH"
                )
        
        simulator = st.radio(
            "Simulator",
            available_sims,
            horizontal=True
        )
        sim_type = "xyce" if simulator == "Xyce" else ("iverilog" if simulator == "Icarus Verilog" else "ngspice")
        
        waveform_image = None
        
        if verilog_code:
            # Step 1: Compile button
            if sim_type == "iverilog":
                compile_label = "🔨 Compile Verilog"
            elif sim_type == "xyce":
                compile_label = "🔨 Prepare Xyce Netlist"
            else:
                compile_label = "🔨 Prepare SPICE"
            
            if st.button(compile_label, use_container_width=True):
                with st.spinner("Compiling..."):
                    waveform_gen = WaveformGenerator(simulator=sim_type, xyce_path=xyce_custom_path if xyce_custom_path else None)
                    success, msg = waveform_gen.compile_verilog(verilog_code)
                    if success:
                        st.success(f"✅ {msg}")
                        st.session_state.verilog_compiled = True
                        st.session_state.waveform_gen = waveform_gen
                    else:
                        st.error(f"❌ {msg}")
                        st.session_state.verilog_compiled = False
            
            # Step 2: Generate waveform button (only if compiled)
            if st.session_state.get('verilog_compiled', False):
                if st.button("📈 Generate Waveform", use_container_width=True):
                    with st.spinner("Generating waveform..."):
                        waveform_gen = st.session_state.waveform_gen
                        vcd_path, image_path, error_msg = waveform_gen.generate_waveform_from_sim()
                        
                        if image_path and os.path.exists(image_path):
                            st.success("✅ Waveform generated")
                            waveform_image = image_path
                            st.session_state.waveform_image = image_path
                        else:
                            st.error(f"❌ {error_msg}")
                            st.session_state.waveform_image = None
            
            # Always display waveform if available
            if st.session_state.get('waveform_image') and os.path.exists(st.session_state.waveform_image):
                st.image(st.session_state.waveform_image, caption="Generated Waveform", use_container_width=True)
                waveform_image = st.session_state.waveform_image
    
    st.divider()
    
    return datasheet_path, verilog_code, datasheet_content, waveform_image


def workflow_visualization(current_step: Optional[str] = None, completed_steps: list = None):
    """Render the n8n-style workflow visualization"""
    if completed_steps is None:
        completed_steps = []
    
    st.header("🔄 Workflow")
    
    # Define workflow nodes
    nodes = [
        {"id": "analyze", "label": "Analyze Design", "icon": "🔍"},
        {"id": "identify", "label": "Identify Issues", "icon": "🔎"},
        {"id": "fix", "label": "Fix Issues", "icon": "🔧"},
        {"id": "verify", "label": "Verify Fixes", "icon": "✅"},
        {"id": "report", "label": "Generate Report", "icon": "📊"},
    ]
    
    # Create columns for workflow
    cols = st.columns(len(nodes) * 2 - 1)  # Nodes + arrows
    
    for i, node in enumerate(nodes):
        node_id = node["id"]
        
        # Determine node status
        if node_id == current_step:
            status_class = "active"
            status_text = "▶️ Running"
        elif node_id in completed_steps:
            status_class = "completed"
            status_text = "✓ Done"
        else:
            status_class = ""
            status_text = "⏳ Pending"
        
        # Node column
        with cols[i * 2]:
            st.markdown(f"""
            <div class='workflow-node {status_class}'>
                <div style='font-size: 2em;'>{node['icon']}</div>
                <div style='margin-top: 8px;'>{node['label']}</div>
                <div style='font-size: 0.85em; margin-top: 4px;'>{status_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Arrow column (except after last node)
        if i < len(nodes) - 1:
            with cols[i * 2 + 1]:
                st.markdown("""
                <div style='text-align: center; padding-top: 40px;'>
                    <div style='font-size: 2em; color: #ccc;'>→</div>
                </div>
                """, unsafe_allow_html=True)


def execution_section():
    """Render the execution control section"""
    st.header("▶️ Execution")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Max Iterations", Config.MAX_ITERATIONS)
    
    with col2:
        st.metric("Model", Config.MODEL_NAME)
    
    with col3:
        st.metric("Temperature", Config.TEMPERATURE)
    
    st.divider()
    
    # Execute button
    if st.button("🚀 Start Verification", key="execute_btn", use_container_width=True):
        return True
    
    return False


def run_verification(agent: VerilogVerificationAgent, datasheet_path: str, verilog_code: str, datasheet_content: str = "", waveform_image: str = None):
    """Run the verification and display real-time progress"""
    
    if not verilog_code.strip():
        st.error("❌ Please provide Verilog code")
        return None
    
    if not datasheet_path:
        st.error("❌ Please upload a component datasheet")
        return None
    
    placeholder = st.empty()
    
    try:
        # Create a progress container
        progress_container = st.container()
        
        with progress_container:
            # Step 1: Analyze Datasheet & Code
            col = st.columns(1)[0]
            with col:
                with st.spinner("📊 Analyzing datasheet and code..."):
                    st.markdown("""
                    <div class='workflow-node active'>
                        🔍 Analyzing Datasheet<br>
                        <small>Processing component specifications and code structure...</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Run the agent with waveform image if available
        final_state = agent.run(
            datasheet_path=datasheet_path,
            verilog_code=verilog_code,
            datasheet_content=datasheet_content,
            design_image_path=waveform_image  # Pass waveform as design image
        )
        
        return final_state
        
    except Exception as e:
        st.error(f"❌ Error during verification: {str(e)}")
        return None


def results_section(state: dict):
    """Render the results section"""
    if not state:
        return
    
    st.header("📊 Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", state['status'].upper(), "✅" if state['status'] == 'verified' else "⚠️")
    
    with col2:
        st.metric("Iterations", state['iteration'])
    
    with col3:
        st.metric("Issues Found", len(state['issues_found']))
    
    with col4:
        st.metric("Fixes Applied", len(state['fixes_applied']))
    
    st.divider()
    
    # Issues section
    if state['issues_found']:
        st.subheader("🔍 Issues Identified")
        
        for i, issue in enumerate(state['issues_found'], 1):
            severity_color = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(issue.get('severity', 'unknown'), "⚪")
            
            with st.expander(f"{severity_color} Issue {i}: {issue.get('type', 'Unknown')}"):
                st.write(f"**Description:** {issue.get('description', 'N/A')}")
                st.write(f"**Location:** {issue.get('location', 'N/A')}")
                st.write(f"**Suggested Fix:** {issue.get('suggested_fix', 'N/A')}")
    else:
        st.success("✅ No issues found!")
    
    st.divider()
    
    # Fixed code section
    if state['current_code'] != state['verilog_code']:
        st.subheader("💻 Fixed Code")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Original Code:**")
            st.code(state['verilog_code'], language="verilog")
        
        with col2:
            st.write("**Fixed Code:**")
            st.code(state['current_code'], language="verilog")
        
        # Download button for fixed code
        st.download_button(
            label="📥 Download Fixed Code",
            data=state['current_code'],
            file_name="fixed_design.v",
            mime="text/plain"
        )
    else:
        st.info("ℹ️ No changes made to the code")
    
    st.divider()
    
    # Full report section
    st.subheader("📄 Detailed Report")
    
    with st.expander("View Full Report"):
        st.markdown(state['final_report'])
    
    # Download report button
    report_content = f"""# VERILOG DESIGN VERIFICATION REPORT

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Status: {state['status']}
- Iterations: {state['iteration']}
- Issues Found: {len(state['issues_found'])}
- Fixes Applied: {len(state['fixes_applied'])}

---

{state['final_report']}

---

## Final Verified Code

```verilog
{state['current_code']}
```
"""
    
    st.download_button(
        label="📥 Download Full Report",
        data=report_content,
        file_name=f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )


def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'verification_state' not in st.session_state:
        st.session_state.verification_state = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = None
    if 'completed_steps' not in st.session_state:
        st.session_state.completed_steps = []
    
    # Render header
    header_section()
    
    # Render sidebar
    config = sidebar_configuration()
    
    # Render input section
    datasheet_path, verilog_code, datasheet_content, waveform_image = input_section()
    
    # Store waveform in session state
    if 'waveform_image' not in st.session_state:
        st.session_state.waveform_image = None
    if waveform_image:
        st.session_state.waveform_image = waveform_image
    
    # Render workflow visualization
    workflow_visualization(st.session_state.current_step, st.session_state.completed_steps)
    
    # Render execution section
    if execution_section():
        # Initialize agent if needed
        if st.session_state.agent is None:
            st_agent = StreamlitAgent()
            if st_agent.initialize_agent():
                st.session_state.agent = st_agent.agent
            else:
                st.stop()
        
        # Update configuration
        st.session_state.agent.max_iterations = config['max_iterations']
        
        # Run verification
        st.session_state.current_step = "analyze"
        verification_result = run_verification(
            st.session_state.agent,
            datasheet_path,
            verilog_code,
            datasheet_content,
            st.session_state.get('waveform_image', None)
        )
        
        st.session_state.verification_state = verification_result
        st.session_state.completed_steps = ["analyze", "identify", "fix", "verify", "report"]
        st.session_state.current_step = None
        
        # Display results
        if verification_result:
            results_section(verification_result)
    
    # Display results if already executed
    elif st.session_state.verification_state:
        results_section(st.session_state.verification_state)


if __name__ == "__main__":
    main()
