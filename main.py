#!/usr/bin/env python3
"""
Excel to Terraform Automation - Main Entry Point
================================================
Primary entry point for Excel to Terraform automation.
Kicks off the complete automation pipeline with all features.
"""

import sys
import os
import argparse
from datetime import datetime
from automation_pipeline import AutomationPipeline

def main():
    """Main entry point - kicks off automation pipeline."""
    
    parser = argparse.ArgumentParser(
        description='Excel to Terraform Automation - Complete Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all Excel files in sourcefiles directory (default)
  python main.py
  
  # Process specific Excel file
  python main.py --excel-file data.xlsx
  
  # Process files in custom directory
  python main.py --input-dir /path/to/files
  
  # Use custom configuration
  python main.py --config my_config.json
  
  # Dry run (validate without processing)
  python main.py --dry-run
  
  # Verbose output
  python main.py --verbose

Features:
  - Automatic Excel file discovery in sourcefiles directory
  - Dynamic output folders based on Subscription and timestamp
  - Enhanced Terraform generator v2 (module.md patterns)
  - Multi-file processing support
  - Comprehensive validation and logging
  - Backup of previous outputs
        """
    )
    
    parser.add_argument('--config', '-c', 
                       help='Configuration file (default: automation_config.json)')
    parser.add_argument('--excel-file', '-e',
                       help='Excel file to process (single file mode)')
    parser.add_argument('--input-dir', '-d',
                       help='Directory containing Excel files')
    parser.add_argument('--output-dir', '-o',
                       help='Terraform output directory')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate without processing')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip backup of previous outputs')
    
    args = parser.parse_args()
    
    # show header
    print("=" * 80)
    print("Excel to Terraform Automation Pipeline")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # init pipeline
    config_file = args.config or 'automation_config.json'
    pipeline = AutomationPipeline(config_file)
    
    # apply command line overrides
    if args.excel_file:
        pipeline.config['input']['process_multiple_files'] = False
        pipeline.config['input']['excel_file'] = args.excel_file
        print(f"Mode: Single file - {args.excel_file}")
    elif args.input_dir:
        pipeline.config['input']['process_multiple_files'] = True
        pipeline.config['input']['input_directory'] = args.input_dir
        print(f"Mode: Multi-file - {args.input_dir}")
    else:
        print(f"Mode: Multi-file - sourcefiles directory")
    
    if args.output_dir:
        pipeline.config['output']['terraform_dir'] = args.output_dir
    
    if args.no_backup:
        pipeline.config['output']['backup_previous'] = False
    
    if args.verbose:
        import logging
        pipeline.config['logging']['level'] = 'DEBUG'
        pipeline.logger.setLevel(logging.DEBUG)
        print("Logging: Verbose mode enabled")
    
    print("=" * 80)
    
    # dry run mode
    if args.dry_run:
        print("\nDry run mode - validating inputs...\n")
        validation_result = pipeline._validate_inputs()
        if validation_result['success']:
            print("SUCCESS: Validation passed - ready to process")
            return 0
        else:
            print("ERROR: Validation failed:")
            for error in validation_result['errors']:
                print(f"  - {error}")
            return 1
    
    # run the pipeline
    results = pipeline.run()
    
    # show results
    print("\n" + "=" * 80)
    if results['success']:
        print("SUCCESS: Automation completed")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        print(f"Files generated: {len(results['files_generated'])}")
        print("=" * 80)
        return 0
    else:
        print("ERROR: Automation failed")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        if results['errors']:
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        print("=" * 80)
        return 2


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
