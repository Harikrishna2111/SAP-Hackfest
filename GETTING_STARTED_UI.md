# Getting Started with Streamlit UI

Welcome to the Verilog Design Verification Agent! This guide will get you up and running with the beautiful n8n-style web interface in 2 minutes.

## Prerequisites

- Python 3.8 or higher
- A Google Gemini API key (free: https://makersuite.google.com/app/apikey)
- A modern web browser

## Step 1: Setup (1 minute)

### 1.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.2 Configure Your API Key

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your favorite editor
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

**In `.env`, change:**
```
GOOGLE_API_KEY=your_actual_api_key_here
```

**Save and close.**

## Step 2: Launch (30 seconds)

### Option A: Easy Launcher (Recommended)

```bash
python run_ui.py
```

This will:
- ✅ Check all dependencies
- ✅ Verify your configuration
- ✅ Open your browser automatically
- ✅ Start the Streamlit server

### Option B: Direct Streamlit

```bash
streamlit run streamlit_app.py
```

### Option C: Docker (If you have Docker installed)

```bash
docker-compose up
```

## Step 3: Using the UI (30 seconds)

### 1. **Upload Design Image** (Left side)
   - Click "Browse files"
   - Select your circuit diagram, block diagram, or schematic
   - See your image preview

### 2. **Provide Verilog Code** (Right side)
   - **Option 1**: Paste code directly
   - **Option 2**: Upload a `.v` file

### 3. **Configure Settings** (Sidebar)
   - Adjust "Max Iterations" if needed (1-10)
   - Change model if desired
   - Modify temperature for creativity level

### 4. **Click "🚀 Start Verification"**
   - Watch the workflow nodes execute in real-time
   - See each step complete: Analyze → Identify → Fix → Verify → Report

### 5. **Review Results**
   - ✅ Check summary metrics
   - 🔍 Browse identified issues  
   - 💻 Compare original vs fixed code
   - 📄 Read detailed report
   - 📥 Download results

## Example Walkthrough

### Sample Code to Test

Copy and paste this into the "Paste code" field:

```verilog
module counter_4bit (
    input wire clk,
    input wire reset,
    input wire enable,
    output reg [3:0] count
);

always @(posedge clk or posedge reset) begin
    if (reset)
        count <= 4'b0000;
    else
        count <= count + 1;
end

endmodule
```

### Without a Design Image

Don't have a design image? That's okay!
- The agent will analyze the code anyway
- It won't verify design-code alignment
- All other features work normally
- Just skip the image upload and proceed

## UI Tour

### 🎨 Header Section
- App title and description
- Version badges
- Quick navigation links

### ⚙️ Sidebar Configuration
- **Max Iterations**: 1-10 (more = thorough but slower)
- **Model Selection**: Choose Gemini version
- **Temperature**: 0.0-1.0 (lower = consistent, higher = creative)
- **Quick Links**: Documentation and guides

### 📥 Input Section (Two Columns)
- **Left**: Upload design image
- **Right**: Paste or upload Verilog code

### 🔄 Workflow Visualization
Visual representation of 5 steps:
1. 🔍 Analyze Design
2. 🔎 Identify Issues
3. 🔧 Fix Issues
4. ✅ Verify Fixes
5. 📊 Generate Report

Color meaning:
- 🔵 Blue = Currently running
- 🟢 Green = Completed
- ⚪ Gray = Not yet started

### ▶️ Execution Section
- Start button
- Configuration display
- Metrics preview

### 📊 Results Section (After Execution)
- **Summary Metrics**: Status, iterations, issues, fixes
- **Issues Found**: Expandable cards with details
- **Fixed Code**: Before/after comparison
- **Detailed Report**: Full analysis
- **Download Buttons**: Export results

## Tips & Tricks

### 📸 For Best Results

**With Design Images:**
- Use clear, high-quality images (800x600+)
- Ensure labels are readable
- Include component names and connections
- Avoid blurry or noisy images

**With Verilog Code:**
- Add comments explaining functionality
- Use consistent formatting
- Specify port widths and purposes
- Include module descriptions

### ⚙️ Configuration Tips

- **Testing**: Start with default settings
- **Complex Designs**: Increase max iterations (5-10)
- **Speed**: Use `gemini-2.5-flash` model
- **Accuracy**: Use `gemini-1.5-pro` model
- **Consistency**: Lower temperature (0.1-0.3)
- **Creativity**: Higher temperature (0.5-1.0)

### 🚀 Performance

- First run may take 10-30 seconds (API warmup)
- Subsequent runs are faster
- Complex designs may take 1-3 minutes
- Code-only analysis is faster than with images

## Keyboard Shortcuts

- `C`: Clear cache
- `R`: Rerun script
- `Ctrl+S`: Save (browser)
- `Ctrl+P`: Print

## Troubleshooting

### "API Key not found"
```
Solution: Edit .env file with your actual API key
```

### "Connection refused" / "Cannot connect"
```
Solution: The Streamlit server may be starting
Wait 5-10 seconds and refresh your browser
```

### App crashes on large files
```
Solution: Keep images < 20MB and code < 1MB
Or increase max iterations/temperature gradually
```

### Slow performance
```
Solution:
- Reduce max iterations
- Use faster model (gemini-2.5-flash)
- Check internet connection
- Close other applications
```

## Next Steps

After you finish verifying your design:

1. **Review Results** - Check all identified issues
2. **Download Code** - Get the corrected Verilog
3. **Download Report** - Save detailed analysis
4. **Test Further** - Use fixed code in simulators
5. **Iterate** - Upload updated designs and re-verify

## Support Resources

📖 **Full Documentation**: [README.md](README.md)
🎯 **Quick Start** (Python): [QUICK_START.md](QUICK_START.md)
🎨 **Design Guide**: [DESIGN_IMAGE_GUIDE.md](DESIGN_IMAGE_GUIDE.md)
📚 **UI Guide**: [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)
💻 **Python Examples**: [example_usage.py](example_usage.py)

## Frequently Asked Questions

**Q: Do I need a design image?**
A: No, but it improves verification. Code-only analysis works too.

**Q: How long does verification take?**
A: Typically 1-3 minutes depending on complexity.

**Q: Can I use it offline?**
A: No, it requires internet for the Gemini API.

**Q: Is my code private?**
A: Your code is sent to Google's API. Check their privacy policy.

**Q: Can I use without Docker?**
A: Yes, just use `python run_ui.py` or `streamlit run streamlit_app.py`

**Q: How many iterations should I use?**
A: Start with 3-5, increase for complex designs or subtle issues.

## Example Screenshots

### Before Verification
- Design image displayed
- Verilog code pasted
- Ready to analyze

### During Verification
- Workflow nodes light up as they execute
- Progress indicator for each step
- Real-time status updates

### After Verification
- Issues listed with severity
- Original vs fixed code side-by-side
- Comprehensive report
- Download options

## Next Steps

1. ✅ Follow this guide
2. 📝 Upload your first design
3. 🚀 Run verification
4. 📊 Review results
5. 💾 Download reports
6. 🔄 Iterate and improve

---

**Ready to get started?** Run this command:

```bash
python run_ui.py
```

The browser will open automatically!

**Happy verifying! 🎉**

---

For more detailed information, see [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)
