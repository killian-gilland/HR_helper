"""
Quick launcher for Streamlit Recruitment Analyst
Run this script to start the application
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the project root
    project_root = Path(__file__).parent
    app_file = project_root / "app_streamlit.py"
    
    if not app_file.exists():
        print("❌ app_streamlit.py not found!")
        sys.exit(1)
    
    print("=" * 60)
    print("🎯 Starting Recruitment Analyst (Streamlit)")
    print("=" * 60)
    print("\n✅ Launching application...")
    print("\n🌐 App will open at: http://localhost:8501")
    print("   (You may need to click the 'Rerun' button on first load)")
    print("\n📌 To stop the app, press CTRL+C in the terminal")
    print("\n" + "=" * 60 + "\n")
    
    # Run streamlit
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_file)],
        cwd=str(project_root)
    )

if __name__ == "__main__":
    main()
