# Design Image Guide

## What is a Design Image?

A **design image** is a visual representation of your hardware design. This can be:

### Supported Image Types:

1. **Circuit Schematics**
   - Gate-level diagrams
   - Transistor-level schematics
   - Logic diagrams with gates (AND, OR, NOT, etc.)

2. **Block Diagrams**
   - High-level architectural diagrams
   - Module interconnections
   - Data flow diagrams

3. **Timing Diagrams**
   - Waveform diagrams
   - Clock and signal timing
   - State transition diagrams

4. **FSM Diagrams**
   - Finite State Machine diagrams
   - State transition graphs
   - Moore/Mealy machine representations

5. **RTL Diagrams**
   - Register Transfer Level diagrams
   - Datapath and control diagrams

## How to Prepare Your Design Image

### Format Requirements:
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP
- **Recommended format**: PNG (for clarity)
- **Resolution**: At least 800x600 for good analysis
- **File size**: Under 20MB

### Best Practices:

✅ **DO:**
- Use clear, high-resolution images
- Ensure all text is readable
- Label all components and signals
- Use standard schematic symbols
- Include a legend if using custom symbols

❌ **DON'T:**
- Use blurry or low-quality images
- Hand-drawn sketches (unless very clear)
- Images with excessive noise or artifacts
- Screenshots with UI elements

## Example Design Images

### Option 1: Create in Drawing Tools
- **Draw.io** (diagrams.net)
- **Lucidchart**
- **Microsoft Visio**
- **KiCad** (for circuit schematics)

### Option 2: Export from EDA Tools
- Xilinx Vivado RTL schematics
- Intel Quartus schematic views
- Cadence tool exports
- Synopsys design views

### Option 3: Screenshot from Waveform Tools
- ModelSim waveforms
- GTKWave timing diagrams
- Vivado simulation waveforms

## For Testing Without a Design Image

If you don't have a design image yet, the agent can still:
- Analyze your Verilog code for syntax errors
- Check for logic issues
- Suggest improvements
- Verify best practices

However, it won't be able to:
- Verify design-code alignment
- Check if implementation matches specification
- Identify architectural mismatches

## Placeholder Image

For testing purposes, you can use the provided placeholder or create a simple block diagram showing:
1. Module name
2. Input/Output ports
3. Basic functionality

## Example: 4-bit Counter Design Image

For the sample `counter_4bit` module, your design image should show:

```
┌─────────────────────────────────┐
│      4-bit Counter              │
├─────────────────────────────────┤
│  Inputs:                        │
│    - clk      (clock)           │
│    - reset    (async reset)     │
│    - enable   (count enable)    │
│                                 │
│  Output:                        │
│    - count[3:0] (4-bit output)  │
│                                 │
│  Logic:                         │
│    ┌──────┐                     │
│    │ D FF │──┐                  │
│    └──────┘  │                  │
│       ↑      │                  │
│      clk     │                  │
│              │  +1              │
│    ┌─────────▼────┐             │
│    │   Adder      │             │
│    └──────────────┘             │
└─────────────────────────────────┘
```

## Need Help?

If you're unsure about your design image:
1. Start with code-only analysis
2. Add the design image later
3. The agent will provide feedback on what it can see

---

**Tip**: The better your design image quality, the more accurate the verification will be!
