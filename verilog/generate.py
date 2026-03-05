from itertools import cycle
import subprocess

def xor_gate_simulation():
    # Define the truth table for the XOR gate
    inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]  # All combinations of a and b
    waveform = []

    for a, b in inputs:
        # XOR logic: out = (not a and b) or (not b and a)
        abar = not a
        bbar = not b
        t1 = abar and b
        t2 = bbar and a
        out = t1 or t2

        # Append the output to the waveform
        waveform.append(int(out))  # Convert boolean to binary (0 or 1)

    return waveform

def generate_serial_outputs(count):
    # Generate 100 serial outputs based on the XOR gate waveform
    waveform = xor_gate_simulation()
    serial_outputs = []

    # Repeat the waveform in a cyclic manner to generate the required count
    for output in cycle(waveform):
        if len(serial_outputs) >= count:
            break
        serial_outputs.append(output)

    return serial_outputs

def run_verilog_simulation():
    # Run the Verilog simulation using Icarus Verilog
    subprocess.run(["iverilog", "-o", "testbench.out", "testbench.v", "test.v"], check=True)
    subprocess.run(["vvp", "testbench.out"], check=True)

def extract_output():
    # Read the output from the simulation log
    outputs = []
    with open("output.log", "r") as file:
        for line in file:
            if "Output" in line:
                # Extract the binary output
                outputs.append(int(line.strip().split(":")[1]))
    return outputs

if __name__ == "__main__":
    count = 100  # Number of serial outputs needed
    serial_outputs = generate_serial_outputs(count)
    print("Serial Outputs (100 values):", serial_outputs)

    # Uncomment below if Icarus Verilog is installed
    # run_verilog_simulation()
    # extracted_outputs = extract_output()
    # print("Extracted Outputs (100 values):", extracted_outputs)