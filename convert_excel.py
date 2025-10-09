#!/usr/bin/env python3
"""
Excel to JSON Converter - Simple Usage Script
=============================================
This script provides a simple interface to convert Excel files to comprehensive JSON format.
"""

import os
import sys
from excel_to_json_converter import convert_excel_to_json

def main():
    """Simple command-line interface for Excel to JSON conversion."""
    
    print("Excel to JSON Converter")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python convert_excel.py <excel_file> [output_file]")
        print("\nExamples:")
        print("  python convert_excel.py LLDtest.xlsm")
        print("  python convert_excel.py data.xlsx output.json")
        print("\nThis tool extracts ALL data from Excel files including:")
        print("  • All sheet data (tables, key-value pairs, raw data)")
        print("  • VBA macros and code")
        print("  • Formulas and calculated values")
        print("  • Workbook properties and metadata")
        print("  • Named ranges and data validation")
        print("  • Comments and formatting information")
        return False
    
    excel_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if input file exists
    if not os.path.exists(excel_file):
        print(f"Error: File not found: {excel_file}")
        return False
    
    print(f"Converting: {excel_file}")
    if output_file:
        print(f"Output file: {output_file}")
    
    print("\nStarting conversion...")
    
    # Convert Excel to JSON
    result = convert_excel_to_json(excel_file, output_file)
    
    if result:
        print(f"\n✓ SUCCESS! Conversion completed.")
        print(f"Output file: {result}")
        
        # Show file size
        file_size = os.path.getsize(result)
        print(f"File size: {file_size:,} bytes")
        
        return True
    else:
        print(f"\n✗ FAILED! Conversion did not complete successfully.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
