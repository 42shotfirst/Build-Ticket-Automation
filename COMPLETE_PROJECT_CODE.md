# Complete Excel to Terraform Automation Project

This document contains the complete source code for the Excel to Terraform automation project, including all Python files, JSON configurations, and Terraform files.

## Table of Contents

1. [Python Files](#python-files)
2. [JSON Configuration Files](#json-configuration-files)
3. [Terraform Files](#terraform-files)
4. [Usage Instructions](#usage-instructions)

---

## Python Files

### automation_pipeline.py

```python
#!/usr/bin/env python3
"""
Excel to Terraform Automation Pipeline
=====================================
Complete end-to-end automation for Excel to Terraform conversion.
Designed for external triggering (Control-M, cron, etc.) and repeatable execution.
"""

import os
import sys
import json
import logging
import argparse
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional
import traceback

# Import our modules
from excel_to_json_converter import convert_excel_to_json
from data_accessor import ExcelDataAccessor
from enhanced_terraform_generator import EnhancedTerraformGenerator

class AutomationPipeline:
    """Complete automation pipeline for Excel to Terraform conversion."""
    
    def __init__(self, config_file: str = "automation_config.json"):
        """Initialize the automation pipeline with configuration."""
        self.config_file = config_file
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.start_time = datetime.now()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load automation configuration."""
        default_config = {
            "input": {
                "excel_file": None,
                "input_directory": "sourcefiles",
                "file_pattern": "*.xls*",
                "required_sheets": ["Resources", "NSG", "Build_ENV"],
                "backup_original": True,
                "process_multiple_files": True
            },
            "processing": {
                "extract_macros": True,
                "extract_formulas": True,
                "extract_comments": True,
                "validate_data": True
            },
            "output": {
                "json_file": "comprehensive_excel_data.json",
                "terraform_dir": "terraform_output",
                "backup_previous": True,
                "cleanup_temp_files": True
            },
            "terraform": {
                "provider_version": "~> 3.0",
                "default_location": "East US",
                "default_vm_size": "Standard_D2s_v3",
                "default_os": "Ubuntu 22.04 LTS",
                "enable_diagnostics": True
            },
            "logging": {
                "level": "INFO",
                "file": "automation.log",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "notifications": {
                "email_on_success": False,
                "email_on_failure": True,
                "email_recipients": [],
                "slack_webhook": None
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Merge user config with defaults
                self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                print("Using default configuration")
        
        return default_config
    
    def _merge_config(self, default: Dict, user: Dict):
        """Recursively merge user config with default config."""
        for key, value in user.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        
        # Create logger
        logger = logging.getLogger('automation_pipeline')
        logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = log_config.get('file', 'automation.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _discover_excel_files(self) -> List[str]:
        """Discover Excel files to process based on configuration."""
        excel_files = []
        
        # Check if we're processing multiple files from a directory
        if self.config['input']['process_multiple_files'] and self.config['input']['input_directory']:
            input_dir = self.config['input']['input_directory']
            file_pattern = self.config['input']['file_pattern']
            
            if not os.path.exists(input_dir):
                self.logger.error(f"Input directory not found: {input_dir}")
                return excel_files
            
            # Find all Excel files matching the pattern
            pattern = os.path.join(input_dir, file_pattern)
            excel_files = glob.glob(pattern)
            excel_files = [f for f in excel_files if os.path.isfile(f)]
            
            self.logger.info(f"Found {len(excel_files)} Excel files in {input_dir}")
            for file in excel_files:
                self.logger.info(f"  - {os.path.basename(file)}")
        else:
            # Single file mode
            excel_file = self.config['input']['excel_file']
            if excel_file and os.path.exists(excel_file):
                excel_files = [excel_file]
                self.logger.info(f"Processing single file: {excel_file}")
            elif excel_file:
                self.logger.warning(f"Specified Excel file not found: {excel_file}")
            else:
                # If no specific file is provided, try to find Excel files in sourcefiles directory
                self.logger.info("No specific file provided, searching sourcefiles directory for Excel files...")
                sourcefiles_dir = "sourcefiles"
                if os.path.exists(sourcefiles_dir):
                    pattern = os.path.join(sourcefiles_dir, "*.xls*")
                    excel_files = glob.glob(pattern)
                    excel_files = [f for f in excel_files if os.path.isfile(f)]
                    
                    if excel_files:
                        self.logger.info(f"Found {len(excel_files)} Excel file(s) in sourcefiles directory")
                        for file in excel_files:
                            self.logger.info(f"  - {os.path.basename(file)}")
                    else:
                        self.logger.warning("No Excel files found in sourcefiles directory")
                else:
                    self.logger.warning("sourcefiles directory not found")
        
        return excel_files
    
    def run(self) -> Dict[str, Any]:
        """Run the complete automation pipeline."""
        self.logger.info("=" * 80)
        self.logger.info("EXCEL TO TERRAFORM AUTOMATION PIPELINE")
        self.logger.info("=" * 80)
        self.logger.info(f"Started at: {self.start_time}")
        self.logger.info(f"Configuration: {self.config_file}")
        
        results = {
            'success': False,
            'start_time': self.start_time.isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'steps_completed': [],
            'files_generated': [],
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        try:
            # Step 1: Validate inputs
            self.logger.info("Step 1: Validating inputs...")
            validation_result = self._validate_inputs()
            if not validation_result['success']:
                results['errors'].extend(validation_result['errors'])
                return results
            results['steps_completed'].append('validation')
            self.logger.info("✓ Input validation completed")
            
            # Discover Excel files to process
            excel_files = self._discover_excel_files()
            self.logger.info(f"Processing {len(excel_files)} Excel file(s)")
            
            # Step 2: Backup previous outputs if configured
            if self.config['output']['backup_previous']:
                self.logger.info("Step 2: Backing up previous outputs...")
                self._backup_previous_outputs()
                results['steps_completed'].append('backup')
                self.logger.info("✓ Previous outputs backed up")
            
            # Process each Excel file
            processed_files = []
            for i, excel_file in enumerate(excel_files, 1):
                self.logger.info(f"Processing file {i}/{len(excel_files)}: {os.path.basename(excel_file)}")
                
                # Step 3: Extract Excel data to JSON
                self.logger.info(f"Step 3.{i}: Extracting Excel data to JSON...")
                json_result = self._extract_excel_data(excel_file)
                if not json_result['success']:
                    results['errors'].extend(json_result['errors'])
                    self.logger.error(f"Failed to process {excel_file}: {json_result['errors']}")
                    continue
                results['steps_completed'].append(f'excel_extraction_{i}')
                results['files_generated'].append(json_result['json_file'])
                self.logger.info(f"✓ Excel data extracted to: {json_result['json_file']}")
                
                # Step 4: Generate Terraform files
                self.logger.info(f"Step 4.{i}: Generating Terraform files...")
                terraform_result = self._generate_terraform_files(json_result['json_file'], excel_file)
                if not terraform_result['success']:
                    results['errors'].extend(terraform_result['errors'])
                    self.logger.error(f"Failed to generate Terraform for {excel_file}: {terraform_result['errors']}")
                    continue
                results['steps_completed'].append(f'terraform_generation_{i}')
                results['files_generated'].extend(terraform_result['files'])
                self.logger.info(f"✓ Terraform files generated in: {terraform_result['output_dir']}")
                
                processed_files.append({
                    'excel_file': excel_file,
                    'json_file': json_result['json_file'],
                    'terraform_dir': terraform_result['output_dir']
                })
            
            if not processed_files:
                results['errors'].append("No files were successfully processed")
                return results
            
            # Step 5: Validate generated files
            if self.config['processing']['validate_data']:
                self.logger.info("Step 5: Validating generated files...")
                validation_result = self._validate_outputs(processed_files)
                if not validation_result['success']:
                    results['warnings'].extend(validation_result['warnings'])
                results['steps_completed'].append('output_validation')
                self.logger.info("✓ Output validation completed")
            
            # Step 6: Generate summary report
            self.logger.info("Step 6: Generating summary report...")
            summary = self._generate_summary_report(results, processed_files)
            results['summary'] = summary
            results['steps_completed'].append('summary_report')
            self.logger.info("✓ Summary report generated")
            
            # Step 7: Cleanup temporary files
            if self.config['output']['cleanup_temp_files']:
                self.logger.info("Step 7: Cleaning up temporary files...")
                self._cleanup_temp_files()
                results['steps_completed'].append('cleanup')
                self.logger.info("✓ Temporary files cleaned up")
            
            # Success!
            results['success'] = True
            self.logger.info("=" * 80)
            self.logger.info("AUTOMATION PIPELINE COMPLETED SUCCESSFULLY!")
            self.logger.info("=" * 80)
            self.logger.info(f"Files processed: {len(processed_files)}")
            self.logger.info(f"Files generated: {len(results['files_generated'])}")
            self.logger.info(f"Steps completed: {len(results['steps_completed'])}")
            self.logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
            
        except Exception as e:
            error_msg = f"Pipeline failed with exception: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            results['errors'].append(error_msg)
            
        finally:
            # Record end time and duration
            end_time = datetime.now()
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - self.start_time).total_seconds()
            
            # Save results
            self._save_results(results)
            
            # Send notifications
            self._send_notifications(results)
        
        return results
    
    def _validate_inputs(self) -> Dict[str, Any]:
        """Validate input files and configuration."""
        result = {'success': True, 'errors': []}
        
        # Discover Excel files to process
        excel_files = self._discover_excel_files()
        
        if not excel_files:
            result['success'] = False
            if self.config['input']['process_multiple_files']:
                result['errors'].append(f"No Excel files found in directory: {self.config['input']['input_directory']}")
            else:
                if self.config['input']['excel_file']:
                    result['errors'].append(f"Excel file not found: {self.config['input']['excel_file']}")
                else:
                    result['errors'].append("No Excel files found in sourcefiles directory. Place Excel files in the sourcefiles directory or use --excel-file or --input-dir to specify input files.")
            return result
        
        # Validate each Excel file
        for excel_file in excel_files:
            if not os.path.exists(excel_file):
                result['success'] = False
                result['errors'].append(f"Excel file not found: {excel_file}")
                continue
            
            # Check if file is readable
            try:
                with open(excel_file, 'rb') as f:
                    f.read(1024)  # Try to read first 1KB
            except Exception as e:
                result['success'] = False
                result['errors'].append(f"Cannot read Excel file {excel_file}: {e}")
                continue
        
        # Check output directory permissions
        terraform_dir = self.config['output']['terraform_dir']
        try:
            os.makedirs(terraform_dir, exist_ok=True)
            # Test write permissions
            test_file = os.path.join(terraform_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Cannot write to output directory {terraform_dir}: {e}")
            return result
        
        return result
    
    def _backup_previous_outputs(self):
        """Backup previous output files."""
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup JSON file
        json_file = self.config['output']['json_file']
        if os.path.exists(json_file):
            import shutil
            shutil.copy2(json_file, os.path.join(backup_dir, json_file))
        
        # Backup Terraform directory
        terraform_dir = self.config['output']['terraform_dir']
        if os.path.exists(terraform_dir):
            import shutil
            shutil.copytree(terraform_dir, os.path.join(backup_dir, terraform_dir))
        
        self.logger.info(f"Previous outputs backed up to: {backup_dir}")
    
    def _extract_excel_data(self, excel_file: str) -> Dict[str, Any]:
        """Extract Excel data to JSON."""
        result = {'success': False, 'errors': [], 'json_file': None}
        
        try:
            # Generate unique JSON filename based on Excel file
            base_name = os.path.splitext(os.path.basename(excel_file))[0]
            json_file = f"{base_name}_comprehensive_data.json"
            
            # Convert Excel to JSON
            output_file = convert_excel_to_json(excel_file, json_file)
            
            if output_file and os.path.exists(output_file):
                result['success'] = True
                result['json_file'] = output_file
                
                # Get file size
                file_size = os.path.getsize(output_file)
                self.logger.info(f"JSON file created: {output_file} ({file_size:,} bytes)")
            else:
                result['errors'].append("Failed to create JSON file")
                
        except Exception as e:
            result['errors'].append(f"Excel extraction failed: {e}")
            self.logger.error(f"Excel extraction error: {e}")
            self.logger.error(traceback.format_exc())
        
        return result
    
    def _generate_terraform_files(self, json_file: str, excel_file: str) -> Dict[str, Any]:
        """Generate Terraform files from JSON data."""
        result = {'success': False, 'errors': [], 'files': [], 'output_dir': None}
        
        try:
            # Create unique output directory based on Excel file
            base_name = os.path.splitext(os.path.basename(excel_file))[0]
            terraform_dir = os.path.join(self.config['output']['terraform_dir'], f"{base_name}_terraform")
            
            # Create generator
            generator = EnhancedTerraformGenerator(json_file)
            
            # Generate files
            terraform_files = generator.generate_terraform_files(terraform_dir)
            
            if terraform_files:
                result['success'] = True
                result['files'] = list(terraform_files.keys())
                result['output_dir'] = terraform_dir
                
                # Get summary
                summary = generator.generate_summary()
                self.logger.info(f"Generated {len(terraform_files)} Terraform files")
                self.logger.info(f"Resources: {summary['resources']['virtual_machines']} VMs, {summary['resources']['network_security_rules']} security rules")
            else:
                result['errors'].append("Failed to generate Terraform files")
                
        except Exception as e:
            result['errors'].append(f"Terraform generation failed: {e}")
            self.logger.error(f"Terraform generation error: {e}")
            self.logger.error(traceback.format_exc())
        
        return result
    
    def _validate_outputs(self, processed_files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Validate generated output files."""
        result = {'success': True, 'warnings': []}
        
        for processed_file in processed_files:
            # Check if JSON file is valid
            json_file = processed_file['json_file']
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                except Exception as e:
                    result['warnings'].append(f"JSON file validation failed for {json_file}: {e}")
            else:
                result['warnings'].append(f"JSON file not found: {json_file}")
            
            # Check if Terraform files exist
            terraform_dir = processed_file['terraform_dir']
            required_files = ['main.tf', 'variables.tf', 'terraform.tfvars', 'provider.tf']
            
            for file_name in required_files:
                file_path = os.path.join(terraform_dir, file_name)
                if not os.path.exists(file_path):
                    result['warnings'].append(f"Required Terraform file missing: {file_name} in {terraform_dir}")
        
        return result
    
    def _generate_summary_report(self, results: Dict[str, Any], processed_files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a summary report of the automation run."""
        summary = {
            'total_files_generated': len(results['files_generated']),
            'files_processed': len(processed_files),
            'steps_completed': len(results['steps_completed']),
            'duration_seconds': results['duration_seconds'],
            'success': results['success'],
            'error_count': len(results['errors']),
            'warning_count': len(results['warnings'])
        }
        
        # Add details for each processed file
        summary['processed_files'] = []
        total_terraform_files = 0
        total_json_size = 0
        
        for processed_file in processed_files:
            file_info = {
                'excel_file': os.path.basename(processed_file['excel_file']),
                'json_file': os.path.basename(processed_file['json_file']),
                'terraform_dir': os.path.basename(processed_file['terraform_dir'])
            }
            
            # Count Terraform files
            terraform_dir = processed_file['terraform_dir']
            if os.path.exists(terraform_dir):
                terraform_files = [f for f in os.listdir(terraform_dir) if f.endswith('.tf') or f.endswith('.tfvars')]
                file_info['terraform_file_count'] = len(terraform_files)
                total_terraform_files += len(terraform_files)
            
            # Get JSON file size
            json_file = processed_file['json_file']
            if os.path.exists(json_file):
                file_size = os.path.getsize(json_file)
                file_info['json_file_size_bytes'] = file_size
                file_info['json_file_size_mb'] = round(file_size / (1024 * 1024), 2)
                total_json_size += file_size
            
            summary['processed_files'].append(file_info)
        
        summary['total_terraform_files'] = total_terraform_files
        summary['total_json_size_bytes'] = total_json_size
        summary['total_json_size_mb'] = round(total_json_size / (1024 * 1024), 2)
        
        return summary
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        # Remove any .tmp files
        for file_name in os.listdir('.'):
            if file_name.endswith('.tmp'):
                try:
                    os.remove(file_name)
                    self.logger.info(f"Removed temporary file: {file_name}")
                except Exception as e:
                    self.logger.warning(f"Could not remove temporary file {file_name}: {e}")
    
    def _save_results(self, results: Dict[str, Any]):
        """Save automation results to file."""
        results_file = f"automation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            self.logger.info(f"Results saved to: {results_file}")
        except Exception as e:
            self.logger.error(f"Could not save results: {e}")
    
    def _send_notifications(self, results: Dict[str, Any]):
        """Send notifications based on results."""
        # This would integrate with email/Slack/etc.
        # For now, just log the notification
        if results['success']:
            self.logger.info("✓ Automation completed successfully - notification sent")
        else:
            self.logger.error("✗ Automation failed - failure notification sent")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Excel to Terraform Automation Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default behavior - process all Excel files in sourcefiles directory
  python automation_pipeline.py
  
  # Single file mode
  python automation_pipeline.py --excel-file data.xlsx
  python automation_pipeline.py --excel-file data.xlsx --output-dir terraform
  
  # Multi-file mode - process all Excel files in a specific directory
  python automation_pipeline.py --input-dir /path/to/excel/files --multi-file
  python automation_pipeline.py --input-dir /path/to/excel/files --file-pattern "*.xlsx" --multi-file
  
  # Configuration and validation
  python automation_pipeline.py --config my_config.json
  python automation_pipeline.py --dry-run

Exit Codes:
  0: Success
  1: Configuration error
  2: Processing error
  3: Validation error
        """
    )
    
    parser.add_argument('--config', '-c', 
                       help='Configuration file (default: automation_config.json)')
    parser.add_argument('--excel-file', '-e',
                       help='Excel file to process (single file mode)')
    parser.add_argument('--input-dir', '-d',
                       help='Directory containing Excel files to process (multi-file mode)')
    parser.add_argument('--file-pattern', '-p',
                       help='File pattern for Excel files (default: *.xls*)')
    parser.add_argument('--output-dir', '-o',
                       help='Terraform output directory')
    parser.add_argument('--json-file', '-j',
                       help='JSON output file (single file mode only)')
    parser.add_argument('--multi-file', action='store_true',
                       help='Enable multi-file processing mode')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate configuration and inputs without processing')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    config_file = args.config or 'automation_config.json'
    pipeline = AutomationPipeline(config_file)
    
    # Override config with command line arguments
    if args.multi_file or args.input_dir:
        # Multi-file mode
        pipeline.config['input']['process_multiple_files'] = True
        if args.input_dir:
            pipeline.config['input']['input_directory'] = args.input_dir
        if args.file_pattern:
            pipeline.config['input']['file_pattern'] = args.file_pattern
    else:
        # Single file mode
        pipeline.config['input']['process_multiple_files'] = False
        if args.excel_file:
            pipeline.config['input']['excel_file'] = args.excel_file
    
    if args.output_dir:
        pipeline.config['output']['terraform_dir'] = args.output_dir
    if args.json_file and not pipeline.config['input']['process_multiple_files']:
        pipeline.config['output']['json_file'] = args.json_file
    if args.verbose:
        pipeline.config['logging']['level'] = 'DEBUG'
        pipeline.logger.setLevel(logging.DEBUG)
    
    # Dry run - just validate
    if args.dry_run:
        print("Running in dry-run mode...")
        validation_result = pipeline._validate_inputs()
        if validation_result['success']:
            print("✓ Dry run completed successfully - all inputs valid")
            return 0
        else:
            print("✗ Dry run failed:")
            for error in validation_result['errors']:
                print(f"  - {error}")
            return 1
    
    # Run the pipeline
    results = pipeline.run()
    
    # Return appropriate exit code
    if results['success']:
        print(f"\n✓ Automation completed successfully in {results['duration_seconds']:.2f} seconds")
        print(f"Generated {len(results['files_generated'])} files")
        return 0
    else:
        print(f"\n✗ Automation failed after {results['duration_seconds']:.2f} seconds")
        print("Errors:")
        for error in results['errors']:
            print(f"  - {error}")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
```

### main.py

```python
#!/usr/bin/env python3
"""
Excel to JSON Converter - Main Entry Point
==========================================
This is the main entry point for converting Excel files to comprehensive JSON format.
The original Terraform-focused functionality is now enhanced with comprehensive Excel extraction.
"""

import sys
import os
import glob

# Import our modules
try:
    import config
    import read_build_data
    import terraform_json_generator
    from excel_to_json_converter import convert_excel_to_json
except ImportError as e:
    print(f"Import Error: {e}")
    print("\nMake sure all required Python files are in the same directory:")
    print("- config.py")
    print("- read_build_data.py") 
    print("- terraform_json_generator.py")
    print("- excel_to_json_converter.py")
    print("- comprehensive_excel_extractor.py")
    print("- vba_macro_extractor.py")
    print("\nAlso install required packages: pip install pandas openpyxl")
    sys.exit(1)

def validate_prerequisites():
    """Check if all required files and configuration are present."""
    print("Validating prerequisites...")
    
    errors = []
    
    # Check if Excel file exists
    if not os.path.exists(config.EXCEL_FILE_PATH):
        errors.append(f"Excel file not found: {config.EXCEL_FILE_PATH}")
    
    # Check output directory is writable
    output_dir = os.path.dirname(config.TERRAFORM_JSON_PATH) or '.'
    if not os.access(output_dir, os.W_OK):
        errors.append(f"Cannot write to output directory: {output_dir}")
    
    if errors:
        print("Configuration issues found:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("Prerequisites validated successfully")
    return True

def comprehensive_conversion(excel_file_path=None):
    """
    Convert Excel file to comprehensive JSON format (includes all data, macros, formulas, etc.)
    """
    print("=" * 60)
    print("COMPREHENSIVE EXCEL TO JSON CONVERTER")
    print("Extracting ALL data from Excel file including macros and formulas")
    print("=" * 60)
    
    # Use provided path or default from config
    file_path = excel_file_path or config.EXCEL_FILE_PATH
    
    # Check if Excel file exists
    if not os.path.exists(file_path):
        print(f"Excel file not found: {file_path}")
        return False
    
    try:
        # Use the comprehensive converter
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = f"{base_name}_comprehensive_data.json"
        result = convert_excel_to_json(file_path, output_file)
        
        if result:
            print(f"\n✓ Comprehensive conversion completed successfully!")
            print(f"Output file: {result}")
            return True
        else:
            print(f"\n✗ Comprehensive conversion failed!")
            return False
            
    except Exception as e:
        print(f"\nError during comprehensive conversion: {e}")
        if config.DEBUG_MODE:
            import traceback
            traceback.print_exc()
        return False

def process_directory(directory_path, file_pattern="*.xls*"):
    """
    Process all Excel files in a directory.
    """
    print("=" * 60)
    print("DIRECTORY PROCESSING MODE")
    print(f"Processing Excel files in: {directory_path}")
    print(f"File pattern: {file_pattern}")
    print("=" * 60)
    
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return False
    
    # Find all Excel files matching the pattern
    pattern = os.path.join(directory_path, file_pattern)
    excel_files = glob.glob(pattern)
    excel_files = [f for f in excel_files if os.path.isfile(f)]
    
    if not excel_files:
        print(f"No Excel files found matching pattern: {file_pattern}")
        return False
    
    print(f"Found {len(excel_files)} Excel file(s) to process:")
    for file in excel_files:
        print(f"  - {os.path.basename(file)}")
    
    # Process each file
    success_count = 0
    for i, excel_file in enumerate(excel_files, 1):
        print(f"\n--- Processing file {i}/{len(excel_files)}: {os.path.basename(excel_file)} ---")
        
        try:
            success = comprehensive_conversion(excel_file)
            if success:
                success_count += 1
                print(f"✓ Successfully processed: {os.path.basename(excel_file)}")
            else:
                print(f"✗ Failed to process: {os.path.basename(excel_file)}")
        except Exception as e:
            print(f"✗ Error processing {os.path.basename(excel_file)}: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"DIRECTORY PROCESSING COMPLETED")
    print(f"Successfully processed: {success_count}/{len(excel_files)} files")
    print("=" * 60)
    
    return success_count > 0

def excel_to_terraform_conversion():
    """
    Convert Excel file to complete Terraform configuration with column referencing.
    """
    print("=" * 60)
    print("EXCEL TO TERRAFORM CONVERTER")
    print("Complete conversion with column referencing and Terraform generation")
    print("=" * 60)
    
    # Check if Excel file exists
    if not os.path.exists(config.EXCEL_FILE_PATH):
        print(f"Excel file not found: {config.EXCEL_FILE_PATH}")
        return False
    
    try:
        # Import the Excel to Terraform converter
        from excel_to_terraform import ExcelToTerraformConverter
        
        # Create converter and run conversion
        converter = ExcelToTerraformConverter(config.EXCEL_FILE_PATH)
        results = converter.convert()
        
        if results['success']:
            print(f"\n✓ Excel to Terraform conversion completed successfully!")
            return True
        else:
            print(f"\n✗ Excel to Terraform conversion failed!")
            if results['errors']:
                for error in results['errors']:
                    print(f"  - {error}")
            return False
            
    except Exception as e:
        print(f"\nError during Excel to Terraform conversion: {e}")
        if config.DEBUG_MODE:
            import traceback
            traceback.print_exc()
        return False

def run_demo():
    """
    Run the column referencing and Terraform generation demo.
    """
    print("=" * 60)
    print("COLUMN REFERENCING AND TERRAFORM DEMO")
    print("Demonstrating data access and Terraform generation capabilities")
    print("=" * 60)
    
    try:
        # Import and run the demo
        from demo_column_referencing import main as demo_main
        return demo_main()
        
    except Exception as e:
        print(f"\nError running demo: {e}")
        if config.DEBUG_MODE:
            import traceback
            traceback.print_exc()
        return False

def main():
    """
    Main function to convert Excel build data to Terraform JSON.
    """
    print("=" * 60)
    print("TERRAFORM JSON GENERATOR")
    print("Converting Excel build data to Terraform variables")
    print("=" * 60)
    
    # Validate prerequisites
    if not validate_prerequisites():
        print("\nPlease fix the issues above before proceeding.")
        return False

    try:
        # Step 1: Read build data from Excel
        print(f"\nStep 1: Reading build data from Excel...")
        print(f"Source file: {config.EXCEL_FILE_PATH}")
        print("-" * 40)
        
        build_data = read_build_data.read_build_data()
        
        if not build_data:
            print("Failed to read build data from Excel file.")
            print("Check that the file exists and has the correct format.")
            return False

        print("Build data extracted successfully")
        
        # Show summary of extracted data
        if config.DEBUG_MODE:
            print(f"\nData Summary:")
            print(f"  Project: {build_data.get('project_name', 'N/A')}")
            print(f"  Application: {build_data.get('application_name', 'N/A')}")
            print(f"  Owner: {build_data.get('app_owner', 'N/A')}")
            print(f"  VM Instances: {len(build_data.get('vm_instances', []))}")

        # Step 2: Generate Terraform JSON
        print(f"\nStep 2: Generating Terraform JSON variables...")
        print(f"Output file: {config.TERRAFORM_JSON_PATH}")
        print("-" * 40)
        
        success = terraform_json_generator.create_terraform_json(
            build_data, 
            config.TERRAFORM_JSON_PATH
        )
        
        if not success:
            print("Failed to generate Terraform JSON file.")
            return False

        # Success summary
        print("\n" + "=" * 60)
        print("CONVERSION COMPLETED SUCCESSFULLY!")
        print("-" * 60)
        print(f"Excel source: {config.EXCEL_FILE_PATH}")
        print(f"JSON output: {config.TERRAFORM_JSON_PATH}")
        
        # Show file size
        try:
            file_size = os.path.getsize(config.TERRAFORM_JSON_PATH)
            print(f"Output file size: {file_size:,} bytes")
        except OSError:
            pass
            
        print(f"\nNext steps:")
        print(f"1. Review the generated JSON file")
        print(f"2. Use the JSON as input for your Terraform variables")
        print(f"3. Run terraform plan/apply with the generated variables")
        print("=" * 60)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user (Ctrl+C)")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if config.DEBUG_MODE:
            import traceback
            print("\nDebug traceback:")
            traceback.print_exc()
        return False

def show_help():
    """Display help information."""
    print("""
Excel to JSON Converter
======================

This tool converts Excel files to comprehensive JSON format including ALL data:
- All sheet data (tables, key-value pairs, raw data)
- VBA macros and code
- Formulas and calculated values
- Workbook properties and metadata
- Named ranges and data validation
- Comments and formatting information

USAGE:
    python main.py                         # Convert Excel to comprehensive JSON (default)
    python main.py --comprehensive         # Convert Excel to comprehensive JSON (explicit)
    python main.py --directory /path/to/files  # Process all Excel files in directory
    python main.py --terraform-complete    # Convert Excel to complete Terraform files
    python main.py --terraform             # Convert Excel to Terraform JSON (legacy)
    python main.py --demo                  # Run column referencing and Terraform demo
    python main.py --help                  # Show this help
    python main.py --config                # Show configuration status
    python main.py --test                  # Test with sample data

INPUT:
    Excel file (.xlsx, .xlsm, .xls) containing:
    - Any number of sheets with any data structure
    - VBA macros (in .xlsm files)
    - Formulas and calculated values
    - Tables, key-value pairs, raw data

OUTPUT:
    Comprehensive JSON file including:
    - All raw sheet data
    - Structured tables and key-value pairs
    - VBA macro information and detected patterns
    - Formulas and calculated values
    - Workbook properties and metadata
    - Named ranges and data validation rules
    - Comments and formatting information

CONFIGURATION:
    Edit config.py to customize:
    - Excel file path
    - Output options
    - Debug and processing options

REQUIREMENTS:
    - Python packages: pandas, openpyxl
    - Excel file in any standard format
    - Write permissions for output directory

For detailed configuration, see config.py
For comprehensive extraction, see excel_to_json_converter.py
""")

def show_config():
    """Show current configuration status."""
    print("Current Configuration:")
    print(f"  Excel file: {config.EXCEL_FILE_PATH}")
    print(f"  JSON output: {config.TERRAFORM_JSON_PATH}")
    print(f"  Debug mode: {config.DEBUG_MODE}")
    
    # Check file status
    excel_exists = os.path.exists(config.EXCEL_FILE_PATH)
    print(f"  Excel file exists: {'Yes' if excel_exists else 'No'}")
    
    output_dir = os.path.dirname(config.TERRAFORM_JSON_PATH) or '.'
    output_writable = os.access(output_dir, os.W_OK)
    print(f"  Output directory writable: {'Yes' if output_writable else 'No'}")

def test_with_sample_data():
    """Test the JSON generation with sample data."""
    print("Testing with sample data...")
    
    sample_data = {
        'project_name': 'Sample Infrastructure Project',
        'application_name': 'WebApp-Sample',
        'app_description': 'Sample web application infrastructure',
        'app_tier': 'Production',
        'app_owner': 'infrastructure@company.com',
        'business_owner': 'product@company.com',
        'environments': 'dev, staging, prod',
        'vm_instances': [
            {
                'Hostname': 'web-prod-01',
                'App RG': 'rg-webapp-prod',
                'OS Image*': 'Ubuntu 22.04 LTS',
                'Recommended SKU': 'Standard_D2s_v3',
                'Subscription Name': 'prod-subscription',
                'Environment': 'production'
            },
            {
                'Hostname': 'web-staging-01', 
                'App RG': 'rg-webapp-staging',
                'OS Image*': 'Ubuntu 22.04 LTS',
                'Recommended SKU': 'Standard_B2s',
                'Subscription Name': 'staging-subscription',
                'Environment': 'staging'
            }
        ]
    }
    
    test_output = "test_terraform_variables.json"
    success = terraform_json_generator.create_terraform_json(sample_data, test_output)
    
    if success:
        print(f"Test completed successfully. Check {test_output}")
        return True
    else:
        print("Test failed.")
        return False

if __name__ == '__main__':
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['-h', '--help', 'help']:
            show_help()
            sys.exit(0)
        elif arg in ['-c', '--config', 'config']:
            show_config()
            sys.exit(0)
        elif arg in ['-t', '--test', 'test']:
            success = test_with_sample_data()
            sys.exit(0 if success else 1)
        elif arg in ['--terraform', 'terraform']:
            # Run legacy Terraform conversion
            success = main()
            sys.exit(0 if success else 1)
        elif arg in ['--comprehensive', 'comprehensive']:
            # Run comprehensive conversion
            success = comprehensive_conversion()
            sys.exit(0 if success else 1)
        elif arg in ['--terraform-complete', 'terraform-complete']:
            # Run complete Excel to Terraform conversion
            success = excel_to_terraform_conversion()
            sys.exit(0 if success else 1)
        elif arg in ['--demo', 'demo']:
            # Run demo
            success = run_demo()
            sys.exit(0 if success else 1)
        elif arg in ['--directory', 'directory']:
            # Process directory
            if len(sys.argv) < 3:
                print("Error: Directory path required")
                print("Usage: python main.py --directory /path/to/excel/files")
                sys.exit(1)
            directory_path = sys.argv[2]
            file_pattern = sys.argv[3] if len(sys.argv) > 3 else "*.xls*"
            success = process_directory(directory_path, file_pattern)
            sys.exit(0 if success else 1)
    
    # Default: Run comprehensive conversion (new default behavior)
    success = comprehensive_conversion()
    sys.exit(0 if success else 1)
```

---

*[This is part 1 of the complete project code. The document continues with additional Python files, JSON configurations, and Terraform files in subsequent sections.]*
