#!/usr/bin/env python3
"""
Quick momentum swing trade check
Run this every 5 minutes to catch swing opportunities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from swing_trader import main

if __name__ == "__main__":
    main()
