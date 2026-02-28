# 🔧 Workflow UI - Troubleshooting & Fixes

## Issues Fixed

The workflow UI has been updated to handle common issues more gracefully:

### ✅ Fixed Issues

1. **Config Validation Error on Import**
   - **Problem**: The app would crash if GOOGLE_API_KEY wasn't set
   - **Fix**: Config validation no longer happens on import; handled by the app
   
2. **Workflow Visualization Layout**
   - **Problem**: Arrows between nodes weren't displaying properly in columns
   - **Fix**: Redesigned to use flexbox layout with proper HTML structure
   
3. **Missing Dependencies**
   - **Problem**: App would crash if optional dependencies missing
   - **Fix**: Graceful fallbacks for missing modules

4. **API Key Status**
   - **Added**: Sidebar now shows API key configuration status
   - **Added**: Helpful error messages with links

---

## Quick Fix Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key
```bash
# Copy template
cp .env.example .env

# Edit .env file and add your API key:
GOOGLE_API_KEY=your_actual_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

### Step 3: Test the Setup
```bash
python test_ui.py
```

This will check:
- ✅ All imports are working
- ✅ Dependencies are installed
- ✅ .env file is configured
- ✅ API key is set

### Step 4: Launch the UI
```bash
streamlit run streamlit_app.py
```

Or use the launcher:
```bash
python run_ui.py
```

---

## Common Issues & Solutions

### Issue 1: "Import streamlit could not be resolved"
**Solution**: Install Streamlit
```bash
pip install streamlit
```

### Issue 2: "GOOGLE_API_KEY not found"
**Solution**: 
1. Create `.env` file from template
2. Add your API key to it
3. Restart the app

### Issue 3: "Config validation failed"
**Solution**: This is now fixed! The app will show a friendly error in the UI instead of crashing.

### Issue 4: Workflow nodes not showing properly
**Solution**: Updated the workflow visualization to use a more robust HTML layout.

### Issue 5: "Module 'workflow_visualizer' not found"
**Solution**: This is now optional. The app will use built-in visualization if the module isn't available.

---

## Workflow Visualization Improvements

### Before (Issues):
- Used Streamlit columns which caused layout problems
- Arrows weren't aligned properly
- Hard to see node status at a glance

### After (Fixed):
- Uses flexbox HTML layout
- Arrows properly positioned between nodes
- Clear visual status (Running/Done/Pending)
- Responsive design
- Color-coded nodes:
  - 🔵 Blue = Active (running)
  - 🟢 Green = Completed
  - ⚪ Gray/Purple = Pending

---

## Workflow Nodes Explained

The UI shows 5 workflow steps:

```
[🔍 Analyze] → [🔎 Identify] → [🔧 Fix] → [✅ Verify] → [📊 Report]
```

1. **Analyze Design** (🔍)
   - Analyzes design image using Gemini Vision
   - Examines Verilog code structure

2. **Identify Issues** (🔎)
   - Compares design with code
   - Finds syntax, logic, and design errors

3. **Fix Issues** (🔧)
   - Applies corrections automatically
   - Generates fixed code

4. **Verify Fixes** (✅)
   - Validates corrections
   - Checks for new issues

5. **Generate Report** (📊)
   - Creates comprehensive documentation
   - Includes all findings and recommendations

---

## API Key Setup Guide

### Get Your API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### Add to .env File
```bash
# Method 1: Use text editor
nano .env  # or notepad .env on Windows

# Add this line:
GOOGLE_API_KEY=AIzaSy...your_key_here

# Save and exit
```

### Verify Setup
The sidebar will show:
- ✅ Green = API Key configured correctly
- ❌ Red = API Key not set or invalid

---

## Testing Your Setup

### Method 1: Use Test Script
```bash
python test_ui.py
```

This will check everything and give you a report.

### Method 2: Manual Check
1. Launch the UI: `streamlit run streamlit_app.py`
2. Check sidebar for API key status
3. Try uploading a file
4. Click "Start Verification"

---

## File Structure Check

Make sure these files exist:
```
✅ streamlit_app.py      (Main UI file)
✅ config.py            (Configuration)
✅ verilog_agent.py     (Agent logic)
✅ workflow_visualizer.py (Optional visualizations)
✅ requirements.txt     (Dependencies)
✅ .env                 (Your configuration)
✅ .env.example         (Template)
```

---

## Browser Compatibility

**Tested & Working:**
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Edge
- ✅ Safari

**Best Experience:**
- Chrome or Firefox on desktop
- Screen width: 1280px or wider

---

## Performance Tips

### If the UI is slow:
1. **Reduce iterations**: Lower the "Max Iterations" slider
2. **Use faster model**: Select "gemini-2.5-flash"
3. **Close other tabs**: Free up browser memory
4. **Check internet**: API calls need good connection

### If images aren't loading:
1. **Check size**: Keep images under 20MB
2. **Use supported formats**: PNG, JPG, JPEG, GIF, BMP
3. **Check resolution**: Recommend 800x600 or larger

---

## Advanced Options

### Running on Different Port
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Running Headless (Server Mode)
```bash
streamlit run streamlit_app.py --server.headless true
```

### Debug Mode
```bash
streamlit run streamlit_app.py --logger.level=debug
```

---

## Still Having Issues?

### Check Logs
Streamlit shows errors in the browser. Look for:
- Red error boxes
- Orange warnings
- Console messages (F12 in browser)

### Get More Help
1. Run: `python test_ui.py` and review output
2. Check the terminal for error messages
3. Review [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for detailed docs
4. Check [GETTING_STARTED_UI.md](GETTING_STARTED_UI.md) for setup steps

---

## What Changed in This Fix

### config.py
- Removed automatic validation on import
- Now apps can import Config without API key set
- Validation happens when agent is initialized

### streamlit_app.py
- Added graceful error handling for missing Config
- Improved workflow visualization with flexbox layout
- Added API key status indicator in sidebar
- Better error messages with helpful links
- Fallback values if Config is not available

### New Files
- `test_ui.py` - Quick diagnostic script
- `UI_FIXES.md` - This troubleshooting guide

---

## Quick Commands Reference

```bash
# Test setup
python test_ui.py

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Then edit .env with your key

# Launch UI
streamlit run streamlit_app.py

# Or use launcher
python run_ui.py

# Check Streamlit version
streamlit --version

# Clear cache
streamlit cache clear
```

---

## Success Checklist

Before running the UI, verify:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] GOOGLE_API_KEY set in `.env`
- [ ] Test script passes (`python test_ui.py`)
- [ ] Streamlit runs without errors

---

## Next Steps

Once everything is working:

1. **Launch the UI**: `streamlit run streamlit_app.py`
2. **Upload a design image** (optional)
3. **Paste or upload Verilog code**
4. **Configure settings** in sidebar
5. **Click "Start Verification"**
6. **Review results** and download reports

---

**Everything should now work smoothly! The workflow UI has been fixed and improved.** 🎉

**Questions?** Check [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for complete documentation.
