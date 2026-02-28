# Streamlit UI Guide

## Overview

The **Streamlit UI** provides an n8n-like interface for the Verilog Verification Agent with:

- 🎨 **Visual Workflow**: Node-based workflow visualization
- 🎯 **Interactive Interface**: Upload files, configure settings, run verification
- 📊 **Real-time Progress**: See step-by-step execution
- 📥 **Download Results**: Export reports and fixed code
- 🎭 **Professional Design**: Modern, responsive UI

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Copy and configure your `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_API_KEY=your_actual_api_key_here
MAX_ITERATIONS=5
```

## Running the UI

### Option 1: Run Streamlit App

```bash
streamlit run streamlit_app.py
```

This will open the web interface at `http://localhost:8501`

### Option 2: Run with Different Config

```bash
streamlit run streamlit_app.py --config.toml config.toml
```

### Option 3: Run in the Cloud

Deploy to Streamlit Cloud:
```bash
streamlit deploy
```

## UI Components

### Header Section
- Application title and description
- Version and badge information
- Quick links to documentation

### Sidebar Configuration
- **Max Iterations**: Adjust maximum fix iterations (1-10)
- **Model Selection**: Choose Gemini model version
- **Temperature**: Control model creativity level
- **Quick Links**: Links to documentation and guides

### Input Section
Two-column layout:

#### Left Column: Design Image
- File uploader for design images
- Supported formats: PNG, JPG, JPEG, GIF, BMP
- Image preview
- Upload confirmation

#### Right Column: Verilog Code
Two input methods:
- **Paste Code**: Directly paste Verilog code
- **Upload File**: Upload `.v`, `.sv`, or `.verilog` files

### Workflow Visualization
n8n-style workflow showing:
1. **Analyze Design** - 🔍 Analyzing
2. **Identify Issues** - 🔎 Finding problems
3. **Fix Issues** - 🔧 Correcting code
4. **Verify Fixes** - ✅ Validating
5. **Generate Report** - 📊 Creating report

Node colors:
- **Blue**: Currently executing
- **Green**: Completed
- **Gray**: Pending

### Execution Section
- Control buttons and configuration display
- **Start Verification** button
- Current configuration metrics

### Results Section
After execution displays:

#### Summary Metrics
- **Status**: Verified or needs work
- **Iterations**: Number of fix cycles
- **Issues Found**: Total issues detected
- **Fixes Applied**: Total fixes implemented

#### Issues Identified
Expandable issue cards showing:
- Issue type and severity
- Description
- Location in code
- Suggested fix

#### Fixed Code
Side-by-side comparison:
- Original code
- Fixed code
- Download button for fixed code

#### Detailed Report
- Full expandable report section
- All analysis and findings
- Final verified code
- Download as markdown file

## Features

### 🎯 Configuration

Adjust agent behavior:
- **Max Iterations**: Higher = more thorough but slower
- **Model**: Different models for speed vs accuracy trade-off
- **Temperature**: Lower = more consistent, Higher = more creative

### 📤 File Upload

Supports:
- **Images**: PNG, JPG, JPEG, GIF, BMP (recommended: 800x600+)
- **Verilog**: `.v`, `.sv`, `.verilog` files
- **Direct Input**: Paste code directly

### 📊 Real-time Monitoring

- Live workflow visualization
- Status indicators for each step
- Progress tracking
- Execution timeline

### 💾 Export Options

Download:
- **Fixed Code**: Just the corrected Verilog
- **Full Report**: Complete analysis and findings
- **JSON**: Workflow execution data

## Usage Workflow

### 1. Start the App
```bash
streamlit run streamlit_app.py
```

### 2. Upload Design Image
- Click "Browse files" in Design Image section
- Select your design schematic or diagram
- Preview will be displayed

### 3. Provide Verilog Code
**Option A: Paste Code**
- Click the text area
- Paste your Verilog code
- Code is instantly visible

**Option B: Upload File**
- Choose "Upload file"
- Select a `.v` or `.sv` file
- Code preview shown

### 4. Configure Settings (Optional)
- Adjust "Max Iterations" in sidebar
- Select preferred model
- Set temperature level

### 5. Start Verification
- Click "🚀 Start Verification" button
- Workflow nodes update in real-time
- Progress shown in each section

### 6. Review Results
- Check summary metrics
- Browse identified issues
- Compare original vs fixed code
- Read detailed report

### 7. Export Results
- Download fixed code
- Download full report
- Share results with team

## Workflow Details

### Analyze Design (Step 1)
- Uses Gemini Vision to understand design image
- Analyzes Verilog code structure
- Extracts architecture and functionality

### Identify Issues (Step 2)
- Compares design with implementation
- Detects syntax errors
- Finds logic issues and best practice violations

### Fix Issues (Step 3)
- Generates corrected code
- Applies Gemini suggestions
- Maintains code quality

### Verify Fixes (Step 4)
- Validates corrected code
- Ensures syntax correctness
- Checks for new issues

### Generate Report (Step 5)
- Creates comprehensive documentation
- Includes all findings and fixes
- Provides recommendations

## Tips for Best Results

### Design Images
- 📸 Use clear, high-resolution images (800x600+)
- 🎨 Ensure all labels are readable
- 📋 Include a legend if using custom symbols
- 🔲 Avoid blurry or noisy images

### Verilog Code
- 💬 Add helpful comments
- 🔤 Use consistent formatting
- 📝 Include module descriptions
- ⚙️ Specify parameter ranges

### Configuration
- Start with default settings
- Increase iterations for complex designs
- Use lower temperature for consistency
- Try different models for comparison

## Troubleshooting

### "Google API Key not found"
**Solution**: Ensure `.env` file has `GOOGLE_API_KEY` set

### App runs slow
**Solution**: Reduce `Max Iterations` or use faster model version

### Large file handling
**Solution**: Keep images under 20MB, code files under 1MB

### API rate limits
**Solution**: Wait before running new verification, upgrade API quota

## Advanced Usage

### Batch Processing
Run multiple verifications:
1. Upload first file
2. Run verification
3. Download results
4. Repeat with next file

### Integration
The Streamlit app can be integrated with:
- CI/CD pipelines
- Design review workflows
- Automated testing suites
- Version control systems

## Customization

### Change Styling
Edit the CSS in `streamlit_app.py`:
```python
st.markdown("""
<style>
    .workflow-node { ... }
</style>
""", unsafe_allow_html=True)
```

### Add Custom Nodes
Modify `WORKFLOW_NODES` in `workflow_visualizer.py`

### Extend Functionality
Add new features to `streamlit_app.py`:
- Additional analysis panels
- Custom visualizations
- Integration plugins

## Performance Tips

### Optimization
- Cache API results
- Reduce iteration count for testing
- Use faster model (gemini-2.5-flash)
- Disable image analysis for code-only mode

### Scaling
- Run on cloud infrastructure
- Use Streamlit Cloud deployment
- Implement job queuing

## Keyboard Shortcuts

- `C`: Clear cache
- `R`: Rerun script
- `S`: Save settings
- `D`: Download results

## Support & Resources

- 📖 Full documentation: [README.md](README.md)
- 🚀 Quick start: [QUICK_START.md](QUICK_START.md)
- 🖼️ Design guide: [DESIGN_IMAGE_GUIDE.md](DESIGN_IMAGE_GUIDE.md)
- 💡 Example code: [example_usage.py](example_usage.py)

## Browser Compatibility

- Chrome/Chromium: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Edge: ✅ Full support
- Mobile browsers: ⚠️ Limited support (optimized for desktop)

## System Requirements

- Python 3.8+
- 2GB+ RAM
- Modern web browser
- Internet connection (for API calls)

---

**Happy verifying! 🚀**
