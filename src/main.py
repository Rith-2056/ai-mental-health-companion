"""
Main entry point for the AI Mental Health Companion application.
This file runs the Streamlit chat interface.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from ui.chat_interface import main

if __name__ == "__main__":
    main()