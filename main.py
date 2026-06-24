#!/usr/bin/env python3
"""
EspressoLab — Professional Coffee Tracking Desktop Application
Entry point. Run with: python main.py
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    from logic.api_client import api
    
    if not api.is_authenticated():
        from ui.auth_screen import AuthScreen
        auth = AuthScreen()
        auth.mainloop()
        
        # If still not authenticated after window closes, exit
        if not api.is_authenticated():
            return

    # Launch GUI
    from ui.app import EspressoLabApp
    app = EspressoLabApp()
    app.mainloop()


if __name__ == "__main__":
    main()
