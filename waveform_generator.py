"""
Waveform Generator for Verilog Code
Generates VCD files and waveform images from Verilog testbenches
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
import matplotlib.pyplot as plt

try:
    from vcdvcd import VCDVCD
except ImportError:
    VCDVCD = None


class WaveformGenerator:
    """Generate waveforms from Verilog code or SPICE netlists"""
    
    def __init__(self, simulator="xyce", xyce_path=None):
        self.temp_dir = tempfile.mkdtemp()
        self.simulator = simulator  # "iverilog", "ngspice", or "xyce"
        self.xyce_path = xyce_path or "Xyce"  # Use custom path or default
        self.sim_file = os.path.join(self.temp_dir, "sim")
        self.verilog_file = os.path.join(self.temp_dir, "test.v")
        self.spice_file = os.path.join(self.temp_dir, "circuit.cir")
    
    def compile_verilog(self, verilog_code: str) -> Tuple[bool, str]:
        """
        Compile Verilog code or prepare SPICE netlist
        
        Args:
            verilog_code: Verilog code with testbench or SPICE netlist
            
        Returns:
            Tuple of (success, message)
        """
        if self.simulator in ["ngspice", "xyce"]:
            return self.prepare_spice(verilog_code)
        
        # Clean the verilog code - remove markdown if present
        if "```verilog" in verilog_code:
            verilog_code = verilog_code.split("```verilog")[1].split("```")[0].strip()
        elif "```" in verilog_code:
            verilog_code = verilog_code.split("```")[1].split("```")[0].strip()
        
        # Check if code has module
        if "module" not in verilog_code.lower():
            return False, "No Verilog module found in code"
        
        # Save Verilog code to temp file
        try:
            with open(self.verilog_file, 'w', encoding='utf-8') as f:
                f.write(verilog_code)
        except Exception as e:
            return False, f"Failed to write file: {e}"
        
        try:
            # Compile: iverilog -o sim test.v
            result = subprocess.run(
                ["iverilog", "-o", "sim", "test.v"],
                capture_output=True,
                text=True,
                cwd=self.temp_dir,
                shell=True
            )
            
            if result.returncode != 0:
                return False, f"Compilation error: {result.stderr}"
            
            return True, "Compilation successful"
            
        except FileNotFoundError:
            return False, "iverilog not found. Install from: http://bleyer.org/icarus/"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def prepare_spice(self, spice_code: str) -> Tuple[bool, str]:
        """
        Prepare SPICE netlist for Ngspice or Xyce
        
        Args:
            spice_code: SPICE netlist code or Verilog-AMS
            
        Returns:
            Tuple of (success, message)
        """
        # Check if it's Verilog-AMS and convert to SPICE
        if "module" in spice_code and "analog" in spice_code:
            spice_code = self._convert_verilog_ams_to_spice(spice_code)
            if spice_code.startswith("ERROR:"):
                return False, spice_code
        
        # Clean markdown if present
        if "```" in spice_code:
            parts = spice_code.split("```")
            for part in parts:
                if part.strip() and not part.strip().startswith(('spice', 'cir')):
                    spice_code = part.strip()
                    break
        
        # Save SPICE netlist
        try:
            with open(self.spice_file, 'w', encoding='utf-8', newline='\n') as f:
                f.write(spice_code)
                # Ensure it has .end
                if ".end" not in spice_code.lower():
                    f.write("\n.END\n")
            
            # Verify file was created
            if not os.path.exists(self.spice_file):
                return False, "Failed to create netlist file"
            
            return True, f"{self.simulator.capitalize()} netlist prepared"
        except Exception as e:
            return False, f"Failed to write file: {e}"
    
    def _convert_verilog_ams_to_spice(self, verilog_code: str) -> str:
        """
        Convert Verilog-AMS to equivalent SPICE netlist
        This is a simplified converter for the modamp module
        """
        try:
            # Extract module name and ports
            if "modamp" not in verilog_code:
                return "ERROR: Only modamp module is supported for auto-conversion"
            
            # Create equivalent SPICE netlist
            spice = "* Auto-converted from Verilog-AMS modamp module\n"
            spice += "* Simplified behavioral op-amp model\n\n"
            
            # Simple op-amp subcircuit
            spice += ".SUBCKT modamp inp inn outp\n"
            spice += "* Input resistances\n"
            spice += "RIN1 inp 0 1MEG\n"
            spice += "RIN2 inn 0 1MEG\n"
            spice += "CIN inp inn 1p\n\n"
            
            spice += "* Differential amplifier with gain\n"
            spice += "EDIFF n1 0 inp inn 1e6\n"
            spice += "RPOLE1 n1 n2 1k\n"
            spice += "CPOLE1 n2 0 0.159u\n\n"
            
            spice += "* Output stage\n"
            spice += "EOUT n3 0 n2 0 1\n"
            spice += "ROUT n3 outp 75\n"
            spice += ".ENDS modamp\n\n"
            
            # Testbench
            spice += "* Testbench\n"
            spice += "VIN1 inp 0 SIN(0 0.01 1k)\n"
            spice += "VIN2 inn 0 DC 0\n"
            spice += "X1 inp inn outp modamp\n"
            spice += "RL outp 0 10k\n\n"
            
            spice += "* Analysis\n"
            spice += ".TRAN 1u 5m\n"
            spice += ".PRINT TRAN V(inp) V(inn) V(outp)\n"
            spice += ".END\n"
            
            return spice
            
        except Exception as e:
            return f"ERROR: Conversion failed: {str(e)}"
    
    def generate_waveform_from_sim(self) -> Tuple[Optional[str], Optional[str], str]:
        """
        Generate waveform from compiled sim file
        
        Returns:
            Tuple of (vcd_path, image_path, error_message)
        """
        if self.simulator == "ngspice":
            return self.run_ngspice_simulation()
        elif self.simulator == "xyce":
            return self.run_xyce_simulation()
        
        try:
            # Simulate: vvp sim
            result = subprocess.run(
                ["vvp", "sim"],
                capture_output=True,
                text=True,
                cwd=self.temp_dir,
                shell=True
            )
            
            if result.returncode != 0:
                return None, None, f"Simulation error: {result.stderr}"
            
            # Find VCD file in temp directory
            vcd_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.vcd')]
            if not vcd_files:
                return None, None, f"No VCD file generated. Ensure code has $dumpfile() and $dumpvars()"
            
            vcd_path = os.path.join(self.temp_dir, vcd_files[0])
            
            # Generate waveform image
            if not VCDVCD:
                return vcd_path, None, "vcdvcd library not installed. Run: pip install vcdvcd"
            
            image_path = self._generate_image(vcd_path)
            if not image_path:
                return vcd_path, None, "Failed to generate waveform image"
            
            return vcd_path, image_path, "Success"
            
        except FileNotFoundError:
            return None, None, "vvp not found. Install iverilog from: http://bleyer.org/icarus/"
        except Exception as e:
            return None, None, f"Error: {str(e)}"
    
    def run_xyce_simulation(self) -> Tuple[Optional[str], Optional[str], str]:
        """
        Run Xyce simulation and generate waveform
        
        Returns:
            Tuple of (data_path, image_path, error_message)
        """
        try:
            # Run: Xyce circuit.cir
            result = subprocess.run(
                [self.xyce_path, "circuit.cir"],
                capture_output=True,
                text=True,
                cwd=self.temp_dir,
                shell=True
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                return None, None, f"Xyce error: {error_msg}\n\nNote: Xyce requires SPICE netlist format, not Verilog-AMS. Your file needs a testbench with voltage sources, .TRAN, and .PRINT statements."
            
            # Xyce generates .prn files by default
            prn_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.prn')]
            if not prn_files:
                return None, None, "No output file generated. Add .PRINT statement to netlist"
            
            # Generate waveform from .prn output
            image_path = self._generate_xyce_plot(prn_files[0])
            if not image_path:
                return None, None, "Failed to generate waveform from Xyce output"
            
            return prn_files[0], image_path, "Success"
            
        except FileNotFoundError:
            return None, None, "Xyce not installed. Download from: https://xyce.sandia.gov/downloads/ and add to PATH"
        except Exception as e:
            return None, None, f"Error: {str(e)}"
    
    def _generate_xyce_plot(self, prn_file: str) -> Optional[str]:
        """Generate waveform plot from Xyce .prn output"""
        try:
            prn_path = os.path.join(self.temp_dir, prn_file)
            
            # Parse Xyce .prn file
            data = {}
            with open(prn_path, 'r') as f:
                lines = f.readlines()
                # Skip header lines
                header_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('TIME') or line.strip().startswith('Index'):
                        header_idx = i
                        headers = line.strip().split()
                        for h in headers:
                            data[h] = []
                        break
                
                # Parse data
                for line in lines[header_idx+1:]:
                    if line.strip():
                        values = line.strip().split()
                        for i, h in enumerate(headers):
                            if i < len(values):
                                try:
                                    data[h].append(float(values[i]))
                                except:
                                    pass
            
            # Plot
            plt.figure(figsize=(20, 6))
            
            time_key = 'TIME' if 'TIME' in data else 'Index'
            for key in data:
                if key != time_key and len(data[key]) > 0:
                    plt.plot(data[time_key], data[key], label=key)
            
            plt.xlabel("Time (s)")
            plt.ylabel("Voltage/Current")
            plt.title("Xyce Waveform")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            image_path = os.path.join(self.temp_dir, "waveform.png")
            plt.savefig(image_path)
            plt.close()
            
            return image_path
            
        except Exception as e:
            print(f"Error generating Xyce plot: {e}")
            return None
    
    def run_ngspice_simulation(self) -> Tuple[Optional[str], Optional[str], str]:
        """
        Run Ngspice simulation and generate waveform
        
        Returns:
            Tuple of (data_path, image_path, error_message)
        """
        try:
            # Run: ngspice -b circuit.cir -o output.log
            result = subprocess.run(
                ["ngspice", "-b", "circuit.cir", "-o", "output.log"],
                capture_output=True,
                text=True,
                cwd=self.temp_dir,
                shell=True
            )
            
            if result.returncode != 0:
                return None, None, f"Ngspice error: {result.stderr}"
            
            # Generate waveform from output
            image_path = self._generate_ngspice_plot()
            if not image_path:
                return None, None, "Failed to generate waveform from Ngspice output"
            
            return None, image_path, "Success"
            
        except FileNotFoundError:
            return None, None, "ngspice not found. Install from: http://ngspice.sourceforge.net/"
        except Exception as e:
            return None, None, f"Error: {str(e)}"
    

    
    def _generate_image(self, vcd_path: str) -> Optional[str]:
        """Generate waveform image from VCD file"""
        if not VCDVCD:
            return None
        
        try:
            vcd = VCDVCD(vcd_path)
            signals = vcd.signals
            
            if not signals:
                return None
            
            plt.figure(figsize=(20, 6))
            offset = 0
            
            for signal in signals:
                tv = vcd[signal].tv
                times = []
                values = []
                
                for t, v in tv:
                    times.append(t)
                    values.append(int(v) + offset)
                
                plt.step(times, values, where="post", label=signal)
                offset += 2
            
            plt.xlabel("Time")
            plt.xlim(0, 60)
            plt.title("Waveform")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            image_path = os.path.join(self.temp_dir, "waveform.png")
            plt.savefig(image_path)
            plt.close()
            
            return image_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def _generate_ngspice_plot(self) -> Optional[str]:
        """Generate waveform plot from Ngspice output"""
        try:
            output_file = os.path.join(self.temp_dir, "output.log")
            if not os.path.exists(output_file):
                return None
            
            # Parse Ngspice output and create plot
            # This is a simplified version - actual parsing depends on output format
            plt.figure(figsize=(20, 6))
            
            # Read and plot data (simplified)
            with open(output_file, 'r') as f:
                content = f.read()
                # Add actual parsing logic based on your Ngspice output format
            
            plt.xlabel("Time")
            plt.ylabel("Voltage/Current")
            plt.title("Ngspice Waveform")
            plt.grid(True)
            plt.tight_layout()
            
            image_path = os.path.join(self.temp_dir, "waveform.png")
            plt.savefig(image_path)
            plt.close()
            
            return image_path
            
        except Exception as e:
            print(f"Error generating Ngspice plot: {e}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
