#!/usr/bin/env python3
"""
Main CLI Entry Point
====================
Single command-line interface for the Build Ticket Automation system.

Usage:
    python -m src.cli --input <excel_file>
    python -m src.cli --validate <terraform_dir>
    python -m src.cli --cleanup-backups
"""

import argparse
import sys
import os
from typing import Optional

from .core.pipeline import AutomationPipeline
from .core.validator import TerraformValidator
from .utils.file_handler import FileHandler
from .utils.logger import setup_logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Build Ticket Automation - Excel to Terraform Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python -m src.cli --input sourcefiles/build_ticket.xlsx

  # Validate existing Terraform
  python -m src.cli --validate terraform_output/20251118_112147

  # Cleanup old backups
  python -m src.cli --cleanup-backups

  # Run with custom config
  python -m src.cli --input file.xlsx --config custom_config.json
        """
    )

    # Main operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--input', '-i',
        metavar='FILE',
        help='Excel file to process'
    )
    group.add_argument(
        '--validate', '-v',
        metavar='DIR',
        help='Terraform directory to validate'
    )
    group.add_argument(
        '--cleanup-backups',
        action='store_true',
        help='Clean up old backup files'
    )

    # Options
    parser.add_argument(
        '--config', '-c',
        metavar='FILE',
        help='Configuration file (JSON)'
    )
    parser.add_argument(
        '--output', '-o',
        metavar='DIR',
        help='Output directory for Terraform files'
    )
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Skip validation step'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation mode'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    args = parser.parse_args()

    # Setup logger
    logger = setup_logger(
        name='cli',
        log_file='automation.log',
        level=args.log_level
    )

    try:
        if args.input:
            # Run full pipeline
            run_pipeline(args, logger)

        elif args.validate:
            # Validation only
            run_validation(args, logger)

        elif args.cleanup_backups:
            # Cleanup backups
            run_cleanup(args, logger)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def run_pipeline(args, logger):
    """Run the full automation pipeline."""
    logger.info("Starting Build Ticket Automation Pipeline")

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found: {args.input}")

    # Load config if provided
    config = None
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {}

    # Override config with CLI args
    if args.output:
        config.setdefault('output', {})['terraform_dir'] = args.output

    if args.no_validation:
        config.setdefault('validation', {})['enabled'] = False

    if args.strict:
        config.setdefault('validation', {})['strict_mode'] = True

    config.setdefault('logging', {})['level'] = args.log_level

    # Run pipeline
    pipeline = AutomationPipeline(config)
    results = pipeline.run(args.input)

    # Print summary
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Overall Status: {results['overall_status'].upper()}")

    if results['overall_status'] == 'success':
        print(f"\n+ Extraction: {results['extraction']['output']}")
        print(f"+ Generation: {results['generation']['output']}")

        if 'validation' in results:
            val_summary = results['validation']['summary']
            print(f"+ Validation: {val_summary['passed']}/{val_summary['total_checks']} checks passed")

        print("\nTerraform files are ready for deployment!")
    else:
        print(f"\n- Error: {results.get('error', 'Unknown error')}")

    print("=" * 80)


def run_validation(args, logger):
    """Run validation only."""
    logger.info(f"Validating Terraform directory: {args.validate}")

    if not os.path.exists(args.validate):
        raise FileNotFoundError(f"Directory not found: {args.validate}")

    validator = TerraformValidator(args.validate)
    report = validator.validate_all()
    validator.print_report(report)

    # Exit with appropriate code
    if report['summary']['overall_status'] == 'FAILED':
        sys.exit(1)


def run_cleanup(args, logger):
    """Clean up old backups."""
    logger.info("Cleaning up old backups")

    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print(f"Backup directory not found: {backup_dir}")
        return

    # Clean up old backups (30 days, max 5)
    deleted = FileHandler.cleanup_old_backups(
        backup_dir=backup_dir,
        max_age_days=30,
        max_count=5
    )

    if deleted:
        print(f"\nCleaned up {len(deleted)} old backups:")
        for path in deleted:
            print(f"  - {path}")
    else:
        print("\nNo backups to clean up")

    logger.info(f"Cleanup complete: {len(deleted)} items removed")


if __name__ == '__main__':
    main()
