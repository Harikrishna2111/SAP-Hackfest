# Quick Start Guide

Get started with the Verilog Component Verification Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Key

1. Get your Google Gemini API key from: https://makersuite.google.com/app/apikey

2. Create a `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your key:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

## Step 3: Prepare Your Files

You need two things:

### A. Verilog Code
Either:
- Use the provided `sample_design.v`, OR
- Create your own `.v` file, OR  
- Pass code as a string

### B. Component Datasheet
- PDF datasheet from manufacturer (e.g., 74HC00.pdf from TI)
- Text file with component specifications
- Markdown file with pin/functional descriptions
- See [DATASHEET_GUIDE.md](DATASHEET_GUIDE.md) for details

## Step 4: Run the Agent

### Option A: Use the Example Script

```bash
python example_usage.py
```

### Option B: Create Your Own Script

```python
from verilog_agent import VerilogVerificationAgent
from config import Config

# Initialize agent
agent = VerilogVerificationAgent(
    api_key=Config.GOOGLE_API_KEY,
    max_iterations=5
)

# Your Verilog code
code = """
module my_design (
    input clk,
    output reg out
);
// your code here
endmodule
"""

# Run verification
result = agent.run(
    datasheet_path="component_datasheet.pdf",
    verilog_code=code
)

# Save report
agent.save_report(result, "report.md")
```

## Step 5: Review the Report

The agent will:
1. ✅ Analyze your design
2. ✅ Find issues
3. ✅ Suggest and apply fixes
4. ✅ Generate a detailed report

Check `verification_report.md` for results!

## Example Output

```
============================================================
VERILOG DESIGN VERIFICATION AGENT
Powered by LangGraph + Gemini
============================================================

============================================================
STEP 1: Analyzing Design
============================================================
Design analysis completed.

============================================================
STEP 2: Identifying Issues (Iteration 0)
============================================================
Found 2 issue(s)
  1. [high] syntax: Missing else clause in always block...
  2. [medium] logic: Potential latch inference...

============================================================
STEP 3: Fixing Issues
============================================================
Applied 2 fix(es)

============================================================
STEP 4: Verifying Fixes
============================================================
✓ Code verified successfully

============================================================
STEP 5: Generating Final Report
============================================================
✓ Report generated successfully

✓ Report saved to: verification_report.md

============================================================
VERIFICATION COMPLETE
============================================================
Status: verified
Iterations: 1
Issues Found: 2
Fixes Applied: 2

Full report saved to: verification_report.md
```

## Tips for Best Results

1. **Use Clear Images**: Higher quality = better analysis
2. **Comment Your Code**: Helps the AI understand intent
3. **Start Simple**: Test with small modules first
4. **Read the Report**: Contains valuable insights
5. **Iterate**: Run multiple times for complex designs

## Common Issues

### "GOOGLE_API_KEY not found"
→ Check your `.env` file

### "Image not found"
→ Verify the image path is correct

### "No issues found" but code has problems
→ Try increasing `max_iterations` or provide more context in comments

## Next Steps

- Read the full [README.md](README.md)
- Check [DESIGN_IMAGE_GUIDE.md](DESIGN_IMAGE_GUIDE.md)
- Modify `example_usage.py` for your needs
- Integrate into your workflow!

## Getting Help

- Check the documentation
- Review example files
- Open an issue on GitHub

Happy verifying! 🚀
