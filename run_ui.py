#!/usr/bin/env python3
"""
Quick launcher for the Streamlit UI
Run this script to start the Verilog Verification Agent UI
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path


def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'streamlit',
        'langgraph',
        'langchain',
        'google',
        'pillow'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\nInstalling missing packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("✅ All dependencies installed")


def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\n⚠️  .env file not found!")
        print("\nCreating .env from template...")
        
        template = Path(".env.example")
        if template.exists():
            with open(".env.example", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            print("✅ .env file created. Please edit it with your API key.")
        else:
            print("❌ .env.example not found")
            return False
    else:
        # Check if API key is set
        with open(".env", "r") as f:
            content = f.read()
            if "your_google_api_key_here" in content or "GOOGLE_API_KEY=" not in content:
                print("\n⚠️  GOOGLE_API_KEY not set in .env file!")
                print("Please edit .env and set your API key")
                return False
            else:
                print("✅ .env file configured")
    
    return True


def main():
    """Main launcher function"""
    print("\n" + "="*60)
    print("🚀 VERILOG VERIFICATION AGENT - STREAMLIT UI")
    print("="*60)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    check_dependencies()
    
    # Check environment
    print("\n🔑 Checking configuration...")
    if not check_env_file():
        print("\n❌ Configuration incomplete. Please set your API key and try again.")
        sys.exit(1)
    
    # Start Streamlit
    print("\n" + "="*60)
    print("🌐 Starting Streamlit UI...")
    print("="*60)
    print("\nThe app will open in your browser at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the server")
    print("\n" + "="*60 + "\n")
    
    # Open browser after a delay
    def open_browser():
        time.sleep(3)  # Wait for Streamlit to start
        try:
            webbrowser.open("http://localhost:8501")
        except:
            print("Could not open browser automatically")
    
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "streamlit_app.py",
            "--logger.level=info"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting Streamlit: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
