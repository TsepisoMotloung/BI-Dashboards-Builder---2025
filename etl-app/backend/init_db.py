#!/usr/bin/env python3
"""
Database Initialization Script
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.init_db import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
