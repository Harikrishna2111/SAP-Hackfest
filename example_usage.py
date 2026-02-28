"""
Example usage of the Verilog Verification Agent
"""

from verilog_agent import VerilogVerificationAgent
from config import Config


# Example Verilog code (4-bit counter)
EXAMPLE_VERILOG_CODE = """
module counter_4bit (
    input wire clk,
    input wire reset,
    output reg [3:0] count
);

always @(posedge clk or posedge reset) begin
    if (reset)
        count <= 4'b0000;
    else
        count <= count + 1;
end

endmodule
"""


def main():
    """Run the Verilog verification agent example"""
    
    # Initialize the agent
    print("Initializing Verilog Verification Agent...")
    agent = VerilogVerificationAgent(
        api_key=Config.GOOGLE_API_KEY,
        max_iterations=Config.MAX_ITERATIONS
    )
    
    # Example 1: Using a design image and Verilog code
    # Replace with your actual design image path
    design_image_path = "design_schematic.png"  # Change this to your image path
    
    # Check if image exists
    import os
    if not os.path.exists(design_image_path):
        print(f"\n⚠ Warning: Design image '{design_image_path}' not found.")
        print("Please provide a valid design image path.")
        print("\nFor demonstration, we'll proceed with code-only analysis.")
        print("To use image analysis, update 'design_image_path' with a valid image.")
        
        # Create a dummy image path (agent will handle gracefully)
        # In production, you should always provide a valid image
    
    # Run the agent
    print(f"\nStarting verification process...")
    print(f"Design Image: {design_image_path}")
    print(f"Max Iterations: {Config.MAX_ITERATIONS}\n")
    
    try:
        final_state = agent.run(
            design_image_path=design_image_path,
            verilog_code=EXAMPLE_VERILOG_CODE
        )
        
        # Save the report
        output_report_path = "verification_report.md"
        agent.save_report(final_state, output_report_path)
        
        # Print summary
        print("\n" + "="*60)
        print("VERIFICATION COMPLETE")
        print("="*60)
        print(f"Status: {final_state['status']}")
        print(f"Iterations: {final_state['iteration']}")
        print(f"Issues Found: {len(final_state['issues_found'])}")
        print(f"Fixes Applied: {len(final_state['fixes_applied'])}")
        print(f"\nFull report saved to: {output_report_path}")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()


def example_with_custom_code():
    """Example showing how to use with your own code"""
    
    # Your custom Verilog code
    my_verilog_code = """
    // Put your Verilog code here
    module my_design (
        // Your ports here
    );
    // Your implementation here
    endmodule
    """
    
    # Your design image
    my_design_image = "path/to/your/design.png"
    
    # Initialize and run
    agent = VerilogVerificationAgent(
        api_key=Config.GOOGLE_API_KEY,
        max_iterations=5
    )
    
    final_state = agent.run(
        design_image_path=my_design_image,
        verilog_code=my_verilog_code
    )
    
    # Save report
    agent.save_report(final_state, "my_verification_report.md")
    
    return final_state


def example_reading_from_files():
    """Example showing how to read Verilog code from a file"""
    
    # Read Verilog code from file
    verilog_file_path = "my_design.v"
    
    try:
        with open(verilog_file_path, 'r') as f:
            verilog_code = f.read()
    except FileNotFoundError:
        print(f"File {verilog_file_path} not found!")
        return
    
    # Image path
    design_image_path = "my_design_schematic.png"
    
    # Initialize and run
    agent = VerilogVerificationAgent(
        api_key=Config.GOOGLE_API_KEY,
        max_iterations=5
    )
    
    final_state = agent.run(
        design_image_path=design_image_path,
        verilog_code=verilog_code
    )
    
    # Save report
    agent.save_report(final_state, "verification_report.md")
    
    return final_state


if __name__ == "__main__":
    # Run the main example
    main()
    
    # Uncomment to run other examples:
    # example_with_custom_code()
    # example_reading_from_files()
