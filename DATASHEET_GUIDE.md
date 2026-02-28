# 📄 Component Datasheet Guide

This guide explains how to use component datasheets with the Verilog Component Verification Agent.

## Overview

The agent analyzes component datasheets (PDF or text) to verify that your Verilog implementation matches the component specifications. This helps ensure your code correctly implements the component's functionality, timing, and interface requirements.

## Supported Formats

### PDF Datasheets
- **Format**: `.pdf`
- **Source**: Manufacturer datasheets (e.g., from IC vendors)
- **Best for**: Official component specifications
- **Example**: 74HC00 datasheet from Texas Instruments

### Text Datasheets
- **Formats**: `.txt`, `.md`
- **Source**: Extracted or manually created specifications
- **Best for**: Quick testing or custom components
- **Example**: Markdown file with pin descriptions and truth tables

## What to Include in Datasheets

For best verification results, ensure your datasheet includes:

### 1. Component Information
- Component name and part number
- Component type (logic gate, flip-flop, counter, etc.)
- Brief functional description

### 2. Pin Configuration
- Pin names and numbers
- Pin types (input, output, bidirectional)
- Power and ground pins

### 3. Electrical Specifications
- Voltage levels (VCC, VIH, VIL, VOH, VOL)
- Current specifications
- Timing parameters (setup, hold, propagation delay)

### 4. Functional Description
- Truth tables
- State diagrams
- Operation modes
- Control signals

### 5. Timing Diagrams
- Clock timing
- Input/output relationships
- Setup and hold times

## Example: Using a PDF Datasheet

### Step 1: Obtain Datasheet
Download the official datasheet from the manufacturer:
```
74HC00.pdf - Quad 2-Input NAND Gate
Downloaded from: https://www.ti.com/
```

### Step 2: Upload to Agent
1. Click "Upload component datasheet"
2. Select your PDF file
3. Review the preview to ensure it loaded correctly

### Step 3: Provide Verilog Code
Paste or upload your Verilog implementation:

```verilog
module nand_gate(
    input wire a,
    input wire b,
    output wire y
);
    assign y = ~(a & b);
endmodule
```

### Step 4: Run Verification
The agent will:
1. Extract specifications from the datasheet
2. Analyze your Verilog code
3. Identify any mismatches
4. Suggest fixes
5. Generate a comprehensive report

## Example: Using a Text Datasheet

For quick testing or custom components, create a text file:

**74HC00_spec.txt**
```
Component: 74HC00 Quad 2-Input NAND Gate

PIN CONFIGURATION:
- A (input): First input
- B (input): Second input
- Y (output): NAND output

TRUTH TABLE:
A | B | Y
0 | 0 | 1
0 | 1 | 1
1 | 0 | 1
1 | 1 | 0

FUNCTION:
Y = NOT(A AND B)

TIMING (typical @ 25°C, VCC=5V):
- Propagation delay: 8ns
- Setup time: 3ns
- Hold time: 2ns

ELECTRICAL:
- VCC: 2.0V to 6.0V
- VIH: 0.7*VCC
- VIL: 0.3*VCC
```

## Tips for Best Results

### 1. Complete Datasheets
Include all relevant sections - incomplete datasheets may miss issues

### 2. Clear Formatting
- Use tables for truth tables
- Clear section headers
- Readable diagrams

### 3. Focus on Relevant Pages
If using a large PDF, ensure key pages are included:
- Pin diagram/description
- Truth tables
- Timing diagrams
- Electrical specifications

### 4. Accurate Specifications
Ensure specifications match your target design:
- Correct voltage levels
- Appropriate timing constraints
- Relevant operation modes

## Common Components

### Digital Logic
- Gates (AND, OR, NAND, NOR, XOR)
- Multiplexers/Demultiplexers
- Encoders/Decoders
- Comparators

### Sequential Logic
- Flip-flops (D, JK, T)
- Registers
- Counters
- Shift registers

### Memory
- RAM (SRAM, DRAM)
- ROM
- Flash
- FIFO

### Interface
- UART
- SPI
- I2C
- GPIO expanders

## Datasheet Sources

### Manufacturer Websites
- **Texas Instruments**: https://www.ti.com/
- **NXP**: https://www.nxp.com/
- **Microchip**: https://www.microchip.com/
- **STMicroelectronics**: https://www.st.com/
- **Analog Devices**: https://www.analog.com/

### Datasheet Archives
- **Alldatasheet**: https://www.alldatasheet.com/
- **Datasheetcatalog**: https://www.datasheetcatalog.com/

## Verification Process

### 1. Datasheet Analysis
The agent extracts:
- Component specifications
- Pin configurations
- Timing requirements
- Functional behavior

### 2. Code Analysis
The agent examines:
- Module interfaces
- Logic implementation
- Timing constraints
- Design patterns

### 3. Comparison
The agent identifies:
- Pin mismatches
- Logic errors
- Timing violations
- Missing functionality

### 4. Fix Generation
The agent provides:
- Corrected code
- Explanations
- Best practices
- Timing annotations

### 5. Report Generation
Final report includes:
- All issues found
- Applied fixes
- Verification status
- Recommendations

## Troubleshooting

### PDF Not Loading
**Problem**: PDF fails to upload or preview
**Solutions**:
- Check file size (keep under 50MB)
- Ensure PDF is not password-protected
- Try extracting text to .txt file
- Install pypdf: `pip install pypdf`

### Poor Text Extraction
**Problem**: PDF text extraction is garbled
**Solutions**:
- Use text-based PDF (not scanned images)
- Convert to text manually
- Use OCR tools if needed

### Missing Specifications
**Problem**: Agent misses some specifications
**Solutions**:
- Ensure datasheet includes all relevant sections
- Add missing specs to a text file
- Combine multiple sources

### Large Datasheets
**Problem**: Datasheet is very large (100+ pages)
**Solutions**:
- Extract only relevant pages to new PDF
- Create summary text file with key specs
- Focus on functional and timing sections

## Example Workflow

### Complete Example: D Flip-Flop

**1. Datasheet (74HC74.txt)**
```
Component: 74HC74 Dual D-Type Flip-Flop

PINS:
- D: Data input
- CLK: Clock input (rising edge)
- SET: Asynchronous set (active low)
- CLR: Asynchronous clear (active low)
- Q: Output
- Q_BAR: Inverted output

FUNCTION:
- On CLK rising edge: Q <= D
- SET low: Q = 1 (async)
- CLR low: Q = 0 (async)

TIMING:
- Setup time: 4ns
- Hold time: 2ns
- Propagation delay: 15ns
- Clock frequency: max 50MHz
```

**2. Verilog Code**
```verilog
module d_flipflop(
    input wire d,
    input wire clk,
    input wire set_n,
    input wire clr_n,
    output reg q,
    output wire q_bar
);
    always @(posedge clk or negedge set_n or negedge clr_n) begin
        if (!clr_n)
            q <= 1'b0;
        else if (!set_n)
            q <= 1'b1;
        else
            q <= d;
    end
    
    assign q_bar = ~q;
endmodule
```

**3. Run Verification**
- Upload datasheet
- Upload/paste Verilog code
- Click "Start Verification"
- Review results

**4. Expected Report**
- ✅ Pin names match specifications
- ✅ Synchronous operation correct
- ✅ Asynchronous set/clear functionality correct
- ⚠️ Consider adding timing constraints
- 📝 Suggestion: Add parameter for clock frequency

## Best Practices

1. **Use Official Datasheets**: Manufacturer datasheets are most accurate
2. **Include Timing**: Timing specifications help verify performance
3. **Check Multiple Sources**: Cross-reference if specifications unclear
4. **Keep Updated**: Use latest datasheet revisions
5. **Test Incrementally**: Start simple, add complexity gradually

## Next Steps

- [Quick Start Guide](QUICK_START.md) - Get started
- [Streamlit UI Guide](STREAMLIT_GUIDE.md) - Using the web interface
- [API Documentation](README.md) - Programmatic usage

---

**Need Help?**
- Check the [README](README.md) for general information
- Review [GETTING_STARTED_UI.md](GETTING_STARTED_UI.md) for setup help
