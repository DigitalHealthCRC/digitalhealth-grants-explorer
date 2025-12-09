#!/usr/bin/env python3
"""
Unified Data Preprocessing Script
==================================
Combines funding amount parsing, deadline parsing, and data merging into one script.

Usage:
    python preprocess_data.py

Input:
    data.csv - Original grants data

Output:
    data_parsed_complete.csv - Fully processed data ready for web app

This script replaces running three separate scripts:
    - parse_funding_amounts.py
    - parse_deadlines.py
    - merge_parsed_data.py
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            env=env
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ Error: {script_name} not found!")
        return False

def main():
    print("\n" + "="*60)
    print("UNIFIED DATA PREPROCESSING")
    print("="*60)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Input file: data.csv")
    
    # Check if input file exists
    if not os.path.exists('data.csv'):
        print("\n❌ Error: data.csv not found!")
        print("Please make sure data.csv is in the current directory.")
        sys.exit(1)
    
    # Step 1: Parse funding amounts
    if not run_script('parse_funding_amounts.py', '[1/3] Parsing Funding Amounts'):
        sys.exit(1)
    
    # Step 2: Parse deadlines
    if not run_script('parse_deadlines.py', '[2/3] Parsing Deadlines'):
        sys.exit(1)
    
    # Step 3: Merge data
    if not run_script('merge_parsed_data.py', '[3/3] Merging Parsed Data'):
        sys.exit(1)
    
    # Cleanup intermediate files
    print(f"\n{'='*60}")
    print("Cleaning up intermediate files...")
    print(f"{'='*60}\n")
    
    intermediate_files = [
        'data_with_parsed_funding.csv',
        'data_with_parsed_deadlines.csv'
    ]
    
    for file in intermediate_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Deleted {file}")
    
    # Final summary
    print(f"\n{'='*60}")
    print("✅ PREPROCESSING COMPLETE!")
    print(f"{'='*60}\n")
    print(f"Output file: data_parsed_complete.csv")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nYour web app will now use the parsed data automatically.")
    print(f"Just refresh your browser (Ctrl+F5) to see the changes.\n")

if __name__ == '__main__':
    main()
