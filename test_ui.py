"""
Quick test script to verify the Streamlit app can load
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Testing Streamlit App Components")
print("=" * 60)

# Test 1: Check imports
print("\n1. Testing imports...")
try:
    from config import Config
    print("   ✅ Config module imported")
    print(f"   - Config.GOOGLE_API_KEY: {'Set' if Config.GOOGLE_API_KEY else 'Not Set'}")
    print(f"   - Config.MAX_ITERATIONS: {Config.MAX_ITERATIONS}")
except Exception as e:
    print(f"   ⚠️  Config import issue: {e}")

try:
    from verilog_agent import VerilogVerificationAgent
    print("   ✅ VerilogVerificationAgent imported")
except Exception as e:
    print(f"   ❌ VerilogVerificationAgent import failed: {e}")

try:
    from workflow_visualizer import WorkflowVisualizer
    print("   ✅ WorkflowVisualizer imported")
except Exception as e:
    print(f"   ⚠️  WorkflowVisualizer import issue (optional): {e}")

# Test 2: Check if streamlit app file is valid Python
print("\n2. Testing streamlit_app.py syntax...")
try:
    import streamlit_app
    print("   ✅ streamlit_app.py is valid Python")
except Exception as e:
    print(f"   ❌ streamlit_app.py has issues: {e}")

# Test 3: Check dependencies
print("\n3. Checking dependencies...")
try:
    import streamlit
    print(f"   ✅ Streamlit installed (v{streamlit.__version__})")
except ImportError:
    print("   ❌ Streamlit not installed")
    print("      Run: pip install streamlit")

try:
    import plotly
    print(f"   ✅ Plotly installed (v{plotly.__version__})")
except ImportError:
    print("   ⚠️  Plotly not installed (optional for visualizations)")
    print("      Run: pip install plotly")

try:
    from PIL import Image
    print("   ✅ Pillow (PIL) installed")
except ImportError:
    print("   ❌ Pillow not installed")
    print("      Run: pip install Pillow")

try:
    from dotenv import load_dotenv
    print("   ✅ python-dotenv installed")
except ImportError:
    print("   ❌ python-dotenv not installed")
    print("      Run: pip install python-dotenv")

# Test 4: Check .env file
print("\n4. Checking environment configuration...")
if os.path.exists('.env'):
    print("   ✅ .env file exists")
    with open('.env', 'r') as f:
        content = f.read()
        if 'GOOGLE_API_KEY' in content:
            if 'your_google_api_key_here' in content or 'your_actual_api_key' in content:
                print("   ⚠️  .env file has placeholder API key - please update it")
            else:
                print("   ✅ GOOGLE_API_KEY appears to be set in .env")
        else:
            print("   ⚠️  GOOGLE_API_KEY not found in .env")
else:
    print("   ⚠️  .env file not found")
    print("      Run: cp .env.example .env")

print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)

# Final recommendations
print("\nNext steps:")
print("1. If Streamlit is installed and .env is configured:")
print("   Run: streamlit run streamlit_app.py")
print("\n2. If dependencies are missing:")
print("   Run: pip install -r requirements.txt")
print("\n3. If .env is not configured:")
print("   - Copy .env.example to .env")
print("   - Add your GOOGLE_API_KEY")
print("\n4. To use the launcher:")
print("   Run: python run_ui.py")

print("\n" + "=" * 60)
