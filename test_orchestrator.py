"""
Test script for the Terraform Generation Orchestrator.

This script tests the complete pipeline:
1. Extract data from all Excel sheets
2. Generate all terraform files
3. Verify output
"""

import os
import sys
from src.core.orchestrator import TerraformOrchestrator


def main():
    """Run the orchestrator test."""
    print("="*80)
    print("TERRAFORM GENERATION ORCHESTRATOR TEST")
    print("="*80)
    print()

    # Input Excel file
    excel_file = 'sourcefiles/test_data.xlsm'

    if not os.path.exists(excel_file):
        print(f"❌ Error: Excel file not found: {excel_file}")
        return 1

    # Output directory
    output_dir = 'terraform_output/test_modular_pipeline'

    print(f"Input:  {excel_file}")
    print(f"Output: {output_dir}")
    print()

    try:
        # Create orchestrator
        orchestrator = TerraformOrchestrator(excel_file)

        # Extract all data
        print("PHASE 1: DATA EXTRACTION")
        print("-" * 80)
        extracted_data = orchestrator.extract_all()

        # Save extracted data for debugging
        debug_file = os.path.join(output_dir, 'extracted_data.json')
        os.makedirs(output_dir, exist_ok=True)
        orchestrator.save_extracted_data(debug_file)

        print()
        print("PHASE 2: TERRAFORM GENERATION")
        print("-" * 80)

        # Generate all terraform files
        generated_files = orchestrator.generate_terraform(output_dir)

        # Summary
        print()
        print("="*80)
        print("✅ GENERATION COMPLETE")
        print("="*80)
        print()
        print(f"Generated {len(generated_files)} terraform files:")
        for filename in sorted(generated_files.keys()):
            filepath = os.path.join(output_dir, filename)
            size = len(generated_files[filename])
            print(f"  ✓ {filename:<25} ({size:>6} bytes)")

        print()
        print(f"Output directory: {output_dir}")
        print()
        print("Next steps:")
        print("  1. Review generated files in the output directory")
        print("  2. Run 'terraform init' in the output directory")
        print("  3. Run 'terraform validate' to check syntax")
        print("  4. Run 'terraform plan' to preview changes")
        print()

        return 0

    except Exception as e:
        print()
        print("="*80)
        print("❌ ERROR")
        print("="*80)
        print()
        print(f"Error: {e}")
        print()

        import traceback
        traceback.print_exc()

        return 1


if __name__ == '__main__':
    sys.exit(main())
