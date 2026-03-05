# Waveform Generation Guide

## Overview

The Verilog Verification Agent now supports automatic waveform generation from your Verilog code. The waveform image is passed to the AI agent to provide visual context for verification.

## Prerequisites

### Install Icarus Verilog

**Windows:**
- Download from: http://bleyer.org/icarus/
- Add to system PATH

**Linux:**
```bash
sudo apt-get install iverilog
```

**macOS:**
```bash
brew install icarus-verilog
```

### Install Python Dependencies

```bash
pip install matplotlib vcdvcd
```

## Usage in Streamlit UI

1. **Upload/Paste Verilog Code** with testbench
2. **Check "Generate waveform"** checkbox
3. The waveform will be automatically generated and displayed
4. The waveform image is passed to the AI for analysis

## Verilog Code Requirements

Your Verilog code must include:

1. **A testbench module** with test cases
2. **VCD dump commands** in the testbench:

```verilog
module tb;
    // Your signals
    reg a, b;
    wire out;
    
    // Instantiate your module
    xor_gate uut(out, a, b);
    
    initial begin
        // REQUIRED: VCD file generation
        $dumpfile("waveform.vcd");
        $dumpvars(0, tb);
        
        // Your test cases
        a = 0; b = 0; #10;
        a = 0; b = 1; #10;
        a = 1; b = 0; #10;
        a = 1; b = 1; #10;
        
        $finish;
    end
endmodule
```

## Example Complete Code

```verilog
module xor_gate (out, a, b);
    input a, b;
    output out;
    assign out = a ^ b;
endmodule

module tb;
    reg a, b;
    wire out;

    xor_gate uut(out, a, b);

    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, tb);

        a = 0; b = 0; #10;
        a = 0; b = 1; #10;
        a = 1; b = 0; #10;
        a = 1; b = 1; #10;

        $finish;
    end
endmodule
```

## How It Works

1. **Compilation**: Your Verilog code is compiled using `iverilog`
2. **Simulation**: The compiled code is simulated using `vvp`
3. **VCD Generation**: Simulation produces a `.vcd` waveform file
4. **Image Generation**: VCD is converted to a PNG waveform image using matplotlib
5. **AI Analysis**: The waveform image is passed to Gemini AI along with your code and datasheet

## Benefits

- **Visual Verification**: AI can see the actual signal behavior
- **Timing Analysis**: AI can identify timing issues from waveforms
- **Better Context**: Waveforms provide additional context for verification
- **Debugging**: Visual representation helps identify logic errors

## Troubleshooting

### "Could not generate waveform"

**Causes:**
- Icarus Verilog not installed
- Missing `$dumpfile` and `$dumpvars` in testbench
- Syntax errors in Verilog code
- Testbench doesn't run to completion

**Solutions:**
1. Install Icarus Verilog
2. Add VCD dump commands to testbench
3. Fix syntax errors
4. Ensure testbench has `$finish` statement

### Waveform is too short

Increase simulation time in your testbench:

```verilog
// Add more test cases or increase delays
a = 0; b = 0; #10;
a = 0; b = 1; #10;
// ... more test cases
```

### Waveform shows no signals

Ensure `$dumpvars` includes the correct scope:

```verilog
$dumpvars(0, tb);  // Dump all signals in tb module
```

## Standalone Usage

You can also use the waveform generator independently:

```python
from waveform_generator import WaveformGenerator

# Your Verilog code with testbench
verilog_code = """
module xor_gate (out, a, b);
    input a, b;
    output out;
    assign out = a ^ b;
endmodule

module tb;
    reg a, b;
    wire out;
    xor_gate uut(out, a, b);
    
    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, tb);
        a = 0; b = 0; #10;
        a = 0; b = 1; #10;
        a = 1; b = 0; #10;
        a = 1; b = 1; #10;
        $finish;
    end
endmodule
"""

# Generate waveform
gen = WaveformGenerator()
vcd_path, image_path = gen.generate_waveform(verilog_code)

if image_path:
    print(f"Waveform saved to: {image_path}")
else:
    print("Failed to generate waveform")

# Cleanup
gen.cleanup()
```

## Advanced Configuration

### Customize Waveform Appearance

Edit `waveform_generator.py` to customize:

```python
plt.figure(figsize=(20, 6))  # Change figure size
plt.xlim(0, 100)             # Change time range
plt.grid(True, alpha=0.3)    # Customize grid
```

### Multiple Waveforms

Generate waveforms for different test scenarios and compare them.

## Integration with AI

The waveform image is passed to the AI agent as the `design_image_path` parameter:

```python
final_state = agent.run(
    datasheet_path=datasheet_path,
    verilog_code=verilog_code,
    design_image_path=waveform_image  # Waveform image
)
```

The AI can then:
- Verify signal behavior matches specifications
- Identify timing violations
- Detect logic errors
- Suggest improvements based on waveform patterns
