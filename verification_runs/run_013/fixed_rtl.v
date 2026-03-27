// Sample 4-bit Synchronous Counter with Asynchronous Reset
// This is an example Verilog module for testing the verification agent

module counter_4bit (
    input wire clk,          // Clock input
    input wire reset,        // Asynchronous reset (active high)
    input wire enable,       // Enable counting
    output reg [3:0] count   // 4-bit counter output
);

// Counter logic
// The reset condition is checked first, ensuring it has the highest priority.
// If reset is active, the counter is set to 0.
// Otherwise, if enable is active, the counter increments.
// If neither reset nor enable is active, the counter holds its current value.
always @(posedge clk or posedge reset) begin
    if (reset) begin
        count <= 4'b0000;    // Reset counter to 0
    end else if (enable) begin
        count <= count + 1;  // Increment counter
    end
    // If enable is low and reset is low, counter holds its value implicitly.
end

endmodule


// Additional example: Simple D Flip-Flop
module d_flipflop (
    input wire clk,
    input wire reset,
    input wire d,
    output reg q
);

// D flip-flop logic with asynchronous reset.
// If reset is active, the output q is set to 0.
// Otherwise, on the positive edge of the clock, q takes the value of d.
always @(posedge clk or posedge reset) begin
    if (reset)
        q <= 1'b0;
    else
        q <= d;
end

endmodule


// Example 2-to-1 Multiplexer with fix for missing else case
module faulty_mux (
    input wire sel, // Select signal: 1 for 'a', 0 for 'b'
    input wire a,   // Input when sel is high
    input wire b,   // Input when sel is low
    output reg out  // Output of the multiplexer
);

// Combinational logic for the multiplexer.
// The 'always @(*)' block infers combinational logic.
// An 'else' case is added to ensure 'out' is always assigned a value,
// preventing latch inference when 'sel' is low.
always @(*) begin
    if (sel) begin
        out = a;
    end else begin // Added else case for 'sel' being low
        out = b;
    end
end

endmodule

/*
Note on Issue 3:
The provided Verilog code consists of three independent modules.
There is no explicit instantiation or connection between them.
While this might be intentional for testing individual components,
it means there's no demonstration of how these modules would interact
in a larger system. To demonstrate interaction and test connectivity,
a top-level module or a testbench instantiating these modules and
connecting their ports would be beneficial. For example, a testbench
could instantiate `counter_4bit` and `d_flipflop`, feeding the
counter's output to the flip-flop's input.
*/