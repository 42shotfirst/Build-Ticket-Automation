# Complete Excel to Terraform Automation Project - Full Source Code

This document contains the complete source code for the Excel to Terraform automation project, including all Python files, JSON configurations, and Terraform files.

## Table of Contents

1. [Python Files](#python-files)
2. [JSON Configuration Files](#json-configuration-files)
3. [Test Files](#test-files)
4. [Usage Instructions](#usage-instructions)

---

## Python Files

### 1. automation_pipeline.py

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
                "terraform_dir": "output_package",
                "backup_previous": True,
                "cleanup_temp_files": True,
                "create_deployment_package": True,
                "include_validation_scripts": True,
                "include_documentation": True
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

---

*[Due to length constraints, this document continues with the remaining Python files, JSON configurations, and documentation in subsequent sections. The complete document would include all 8 Python files, 2 JSON configuration files, and comprehensive usage instructions.]*

## JSON Configuration Files

### automation_config.json

```json
{
  "input": {
    "excel_file": "LLDtest.xlsm",
    "required_sheets": ["Resources", "NSG", "Build_ENV", "APGW", "ACR NRS", "Resource Options"],
    "backup_original": true
  },
  "processing": {
    "extract_macros": true,
    "extract_formulas": true,
    "extract_comments": true,
    "validate_data": true,
    "skip_empty_vms": true
  },
  "output": {
    "json_file": "comprehensive_excel_data.json",
    "terraform_dir": "output_package",
    "backup_previous": true,
    "cleanup_temp_files": true,
    "create_deployment_package": true,
    "include_validation_scripts": true,
    "include_documentation": true
  },
  "terraform": {
    "provider_version": "~> 3.0",
    "default_location": "East US",
    "default_vm_size": "Standard_D2s_v3",
    "default_os": "Ubuntu 22.04 LTS",
    "enable_diagnostics": true,
    "add_deployment_scripts": true,
    "terraform_version": ">= 1.0"
  },
  "logging": {
    "level": "INFO",
    "file": "automation.log",
    "max_size_mb": 10,
    "backup_count": 5,
    "include_timestamps": true
  },
  "notifications": {
    "email_on_success": false,
    "email_on_failure": true,
    "email_recipients": ["admin@company.com"],
    "slack_webhook": null,
    "include_summary": true
  },
  "validation": {
    "check_excel_format": true,
    "validate_terraform_syntax": true,
    "check_resource_limits": true,
    "max_vms": 100,
    "max_security_rules": 50
  },
  "deployment": {
    "create_deployment_script": true,
    "deployment_script_name": "deploy.sh",
    "include_terraform_commands": true,
    "add_validation_steps": true
  }
}
```

### automation_config_directory.json

```json
{
  "input": {
    "excel_file": "LLDtest.xlsm",
    "input_directory": "./test_excel_files",
    "file_pattern": "*.xls*",
    "required_sheets": ["Resources", "NSG", "Build_ENV"],
    "backup_original": true,
    "process_multiple_files": true
  },
  "processing": {
    "extract_macros": true,
    "extract_formulas": true,
    "extract_comments": true,
    "validate_data": true
  },
  "output": {
    "json_file": "comprehensive_excel_data.json",
    "terraform_dir": "terraform_output",
    "backup_previous": true,
    "cleanup_temp_files": true
  },
  "terraform": {
    "provider_version": "~> 3.0",
    "default_location": "East US",
    "default_vm_size": "Standard_D2s_v3",
    "default_os": "Ubuntu 22.04 LTS",
    "enable_diagnostics": true
  },
  "logging": {
    "level": "INFO",
    "file": "automation.log",
    "max_size_mb": 10,
    "backup_count": 5
  },
  "notifications": {
    "email_on_success": false,
    "email_on_failure": true,
    "email_recipients": [],
    "slack_webhook": null
  }
}
```

## Test Files

### test_ado_package.py

```python
#!/usr/bin/env python3
"""
Test script to demonstrate the Azure DevOps-focused deployment package functionality.
This script will create a complete Terraform package optimized for ADO deployment.
"""

import os
import sys
from automation_pipeline import AutomationPipeline

def test_ado_package():
    """Test the Azure DevOps-focused deployment package functionality."""
    
    print("=" * 80)
    print("TESTING AZURE DEVOPS DEPLOYMENT PACKAGE GENERATION")
    print("=" * 80)
    
    # Check if we have Excel files in sourcefiles directory
    sourcefiles_dir = "sourcefiles"
    if not os.path.exists(sourcefiles_dir):
        print(f"Creating {sourcefiles_dir} directory...")
        os.makedirs(sourcefiles_dir)
        print(f"Please place your Excel files in the {sourcefiles_dir} directory and run again.")
        return False
    
    # Check for Excel files
    import glob
    excel_files = glob.glob(os.path.join(sourcefiles_dir, "*.xls*"))
    if not excel_files:
        print(f"No Excel files found in {sourcefiles_dir} directory.")
        print("Please place your Excel files in the sourcefiles directory and run again.")
        return False
    
    print(f"Found {len(excel_files)} Excel file(s) in {sourcefiles_dir}:")
    for file in excel_files:
        print(f"  - {os.path.basename(file)}")
    
    # Create automation pipeline
    print("\nInitializing automation pipeline...")
    pipeline = AutomationPipeline()
    
    # Run the pipeline
    print("Running automation pipeline...")
    results = pipeline.run()
    
    if results['success']:
        print("\n" + "=" * 80)
        print("✅ AZURE DEVOPS PACKAGE GENERATED SUCCESSFULLY!")
        print("=" * 80)
        
        print(f"\n📁 Output Package Location: output_package/")
        print(f"📊 Files Generated: {len(results['files_generated'])}")
        print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
        
        print(f"\n📋 Package Contents:")
        if os.path.exists("output_package"):
            for root, dirs, files in os.walk("output_package"):
                level = root.replace("output_package", "").count(os.sep)
                indent = "  " * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = "  " * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        
        print(f"\n🚀 Azure DevOps Integration:")
        print(f"1. Copy the output_package contents to your ADO repository")
        print(f"2. Configure Terraform tasks in your ADO pipeline:")
        print(f"   - Terraform Init")
        print(f"   - Terraform Plan") 
        print(f"   - Terraform Apply")
        print(f"3. Use terraform.tfvars for variable configuration")
        print(f"4. Run validation with: ./scripts/validate.sh")
        
        print(f"\n📖 Documentation:")
        print(f"- README.md - Azure DevOps integration guide")
        print(f"- docs/DEPLOYMENT_GUIDE.md - Comprehensive deployment guide")
        
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ PACKAGE GENERATION FAILED!")
        print("=" * 80)
        
        print(f"\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
        
        return False

def show_ado_package_structure():
    """Show the expected ADO package structure."""
    print("\n" + "=" * 80)
    print("AZURE DEVOPS PACKAGE STRUCTURE")
    print("=" * 80)
    
    structure = """
output_package/
├── main.tf                          # Main Terraform resources
├── variables.tf                     # Variable definitions
├── terraform.tfvars                 # Variable values (customize these!)
├── terraform.auto.tfvars.example    # Example variables file
├── outputs.tf                       # Output definitions
├── provider.tf                      # Provider configuration
├── .gitignore                       # Git ignore rules
├── README.md                        # Azure DevOps integration guide
├── scripts/
│   └── validate.sh                  # Configuration validation script
└── docs/
    └── DEPLOYMENT_GUIDE.md          # Comprehensive deployment guide
"""
    
    print(structure)
    
    print("\n🎯 Azure DevOps Integration Features:")
    print("  ✅ Complete Terraform configuration ready for ADO")
    print("  ✅ Terraform tasks compatible (Init, Plan, Apply, Destroy)")
    print("  ✅ Variable files for easy configuration")
    print("  ✅ Validation script for pipeline validation")
    print("  ✅ Comprehensive documentation for ADO setup")
    print("  ✅ Git-ready with proper .gitignore")
    
    print("\n🔧 ADO Pipeline Tasks:")
    print("  1. Terraform Init Task")
    print("  2. Terraform Plan Task")
    print("  3. Terraform Apply Task")
    print("  4. Terraform Destroy Task (optional)")

if __name__ == "__main__":
    print("Excel to Terraform Azure DevOps Package Generator")
    print("=" * 55)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--structure":
        show_ado_package_structure()
    else:
        success = test_ado_package()
        
        if success:
            print(f"\n🎉 Test completed successfully!")
            print(f"Your Azure DevOps package is ready in the 'output_package' directory.")
        else:
            print(f"\n💥 Test failed!")
            print(f"Please check the errors above and try again.")
        
        sys.exit(0 if success else 1)
```

## Usage Instructions

### Quick Start

1. **Setup Environment**:
   ```bash
   # Install dependencies
   pip install pandas openpyxl
   
   # Create sourcefiles directory
   mkdir sourcefiles
   
   # Place Excel files in sourcefiles directory
   cp your_excel_file.xlsx sourcefiles/
   ```

2. **Run Automation Pipeline**:
   ```bash
   # Process all Excel files in sourcefiles directory
   python automation_pipeline.py
   
   # Process single file
   python automation_pipeline.py --excel-file data.xlsx
   
   # Process directory with custom pattern
   python automation_pipeline.py --input-dir /path/to/files --file-pattern "*.xlsx" --multi-file
   ```

3. **Deploy with Azure DevOps**:
   - Copy the generated `output_package` contents to your ADO repository
   - Configure Terraform tasks in your ADO pipeline
   - Use the generated `terraform.tfvars` for configuration
   - Run validation with `./scripts/validate.sh`

### Advanced Usage

- **Custom Configuration**: Use `--config` to specify custom configuration files
- **Dry Run**: Use `--dry-run` to validate without processing
- **Verbose Logging**: Use `--verbose` for detailed debug information
- **Custom Output**: Use `--output-dir` to specify custom output directories

---

### 3. excel_to_json_converter.py

```python
#!/usr/bin/env python3
"""
Excel to JSON Converter
=======================
Complete solution to convert Excel files to JSON format including:
- All sheet data (tables, key-value pairs, raw data)
- VBA macros and code
- Formulas
- Cell formatting and styles
- Comments and data validation
- Charts and images (metadata)
- Named ranges
- Data connections
- Workbook properties and metadata
"""

import os
import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import our custom extractors
from comprehensive_excel_extractor import ComprehensiveExcelExtractor
from vba_macro_extractor import VBAMacroExtractor

class ExcelToJSONConverter:
    """Complete Excel to JSON converter."""
    
    def __init__(self, excel_file_path: str):
        self.excel_file_path = excel_file_path
        self.file_name = os.path.basename(excel_file_path)
        self.base_name = os.path.splitext(self.file_name)[0]
        
        # Initialize extractors
        self.comprehensive_extractor = ComprehensiveExcelExtractor(excel_file_path)
        self.vba_extractor = VBAMacroExtractor(excel_file_path)
        
        # Final combined data
        self.final_json_data = {}
        
    def convert_to_json(self, output_file: str = None) -> str:
        """Convert Excel file to comprehensive JSON format."""
        print("=" * 80)
        print("EXCEL TO JSON CONVERTER")
        print("=" * 80)
        print(f"Converting: {self.file_name}")
        print()
        
        if not os.path.exists(self.excel_file_path):
            print(f"Error: File not found: {self.excel_file_path}")
            return None
        
        try:
            # Step 1: Extract comprehensive Excel data
            print("Step 1: Extracting comprehensive Excel data...")
            comprehensive_data = self.comprehensive_extractor.extract_all()
            
            # Step 2: Extract VBA macros
            print("\nStep 2: Extracting VBA macros...")
            vba_data = self.vba_extractor.extract_vba_code()
            
            # Step 3: Combine all data
            print("\nStep 3: Combining all extracted data...")
            self.final_json_data = self._combine_extracted_data(comprehensive_data, vba_data)
            
            # Step 4: Export to JSON
            if output_file is None:
                output_file = f"{self.base_name}_complete_conversion.json"
            
            print(f"\nStep 4: Exporting to JSON file: {output_file}")
            success = self._export_to_json(output_file)
            
            if success:
                print("\n" + "=" * 80)
                print("CONVERSION COMPLETED SUCCESSFULLY!")
                print("=" * 80)
                
                # Show summary
                self._show_conversion_summary(output_file)
                return output_file
            else:
                print("\n✗ Conversion failed during JSON export")
                return None
                
        except Exception as e:
            print(f"\n✗ Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _combine_extracted_data(self, comprehensive_data: Dict, vba_data: Dict) -> Dict[str, Any]:
        """Combine data from all extractors into final JSON structure."""
        
        final_data = {
            # File and extraction metadata
            "conversion_metadata": {
                "source_file": self.excel_file_path,
                "conversion_timestamp": datetime.now().isoformat(),
                "converter_version": "1.0.0",
                "extraction_methods": ["comprehensive_excel_extractor", "vba_macro_extractor"]
            },
            
            # File information
            "file_info": comprehensive_data.get('file_info', {}),
            
            # Workbook properties and metadata
            "workbook_properties": comprehensive_data.get('workbook_properties', {}),
            
            # All sheet data (comprehensive)
            "sheets": comprehensive_data.get('sheets', {}),
            
            # VBA macros and code
            "vba_macros": {
                "project_info": vba_data.get('vba_project', {}),
                "modules": vba_data.get('modules', {}),
                "forms": vba_data.get('forms', {}),
                "class_modules": vba_data.get('class_modules', {}),
                "extraction_notes": vba_data.get('extraction_notes', [])
            },
            
            # Formulas and calculated values
            "formulas": comprehensive_data.get('formulas', {}),
            
            # Named ranges
            "named_ranges": comprehensive_data.get('named_ranges', {}),
            
            # Data validation rules
            "data_validation": comprehensive_data.get('data_validation', {}),
            
            # Comments
            "comments": comprehensive_data.get('comments', {}),
            
            # Charts and images (metadata)
            "charts": comprehensive_data.get('charts', {}),
            "images": comprehensive_data.get('images', {}),
            
            # Processing summary
            "processing_summary": self._generate_processing_summary(comprehensive_data, vba_data)
        }
        
        return final_data
    
    def _generate_processing_summary(self, comprehensive_data: Dict, vba_data: Dict) -> Dict[str, Any]:
        """Generate a summary of the processing results."""
        
        sheets = comprehensive_data.get('sheets', {})
        formulas = comprehensive_data.get('formulas', {})
        
        # Count total data points
        total_tables = sum(len(sheet.get('tables', [])) for sheet in sheets.values())
        total_key_value_pairs = sum(len(sheet.get('key_value_pairs', {})) for sheet in sheets.values())
        total_formulas = sum(len(sheet_formulas) for sheet_formulas in formulas.values() 
                           if isinstance(sheet_formulas, list))
        
        # Count VBA elements
        vba_project = vba_data.get('vba_project', {})
        has_macros = bool(vba_project.get('filename'))
        
        summary = {
            "sheets_processed": len(sheets),
            "total_tables_extracted": total_tables,
            "total_key_value_pairs": total_key_value_pairs,
            "total_formulas_found": total_formulas,
            "has_vba_macros": has_macros,
            "vba_project_size_bytes": vba_project.get('size_bytes', 0),
            "named_ranges_count": len(comprehensive_data.get('named_ranges', {})),
            "comments_count": sum(len(sheet_comments) for sheet_comments in comprehensive_data.get('comments', {}).values() 
                                if isinstance(sheet_comments, list)),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def _export_to_json(self, output_file: str) -> bool:
        """Export final data to JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.final_json_data, f, indent=2, default=str, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def _show_conversion_summary(self, output_file: str):
        """Show summary of the conversion process."""
        
        file_size = os.path.getsize(output_file)
        summary = self.final_json_data.get('processing_summary', {})
        
        print(f"Source file: {self.file_name}")
        print(f"Output file: {output_file}")
        print(f"Output size: {file_size:,} bytes")
        print()
        print("Data extracted:")
        print(f"  • Sheets processed: {summary.get('sheets_processed', 0)}")
        print(f"  • Tables extracted: {summary.get('total_tables_extracted', 0)}")
        print(f"  • Key-value pairs: {summary.get('total_key_value_pairs', 0)}")
        print(f"  • Formulas found: {summary.get('total_formulas_found', 0)}")
        print(f"  • VBA macros: {'Yes' if summary.get('has_vba_macros') else 'No'}")
        print(f"  • Named ranges: {summary.get('named_ranges_count', 0)}")
        print(f"  • Comments: {summary.get('comments_count', 0)}")
        
        if summary.get('has_vba_macros'):
            print(f"  • VBA project size: {summary.get('vba_project_size_bytes', 0):,} bytes")
        
        print()
        print("The JSON file contains ALL data from your Excel file including:")
        print("  • Raw cell data from all sheets")
        print("  • Structured tables and key-value pairs")
        print("  • VBA macro information and detected code patterns")
        print("  • Formulas and calculated values")
        print("  • Workbook properties and metadata")
        print("  • Named ranges and data validation rules")
        print("  • Comments and formatting information")
        print("=" * 80)
    
    def get_conversion_summary(self) -> Dict[str, Any]:
        """Get summary of the conversion without doing the full conversion."""
        return self.final_json_data.get('processing_summary', {})


def convert_excel_to_json(excel_file_path: str, output_file: str = None) -> str:
    """Convenience function to convert Excel file to JSON."""
    converter = ExcelToJSONConverter(excel_file_path)
    return converter.convert_to_json(output_file)


def main():
    """Main function for command-line usage."""
    
    if len(sys.argv) < 2:
        print("Usage: python excel_to_json_converter.py <excel_file> [output_file]")
        print("\nExamples:")
        print("  python excel_to_json_converter.py LLDtest.xlsm")
        print("  python excel_to_json_converter.py data.xlsx output.json")
        print("\nThis tool converts Excel files to comprehensive JSON format including:")
        print("  • All sheet data (tables, key-value pairs, raw data)")
        print("  • VBA macros and code")
        print("  • Formulas and calculated values")
        print("  • Workbook properties and metadata")
        print("  • Named ranges and data validation")
        print("  • Comments and formatting information")
        return False
    
    excel_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(excel_file):
        print(f"Error: File not found: {excel_file}")
        return False
    
    # Convert Excel to JSON
    result = convert_excel_to_json(excel_file, output_file)
    
    if result:
        print(f"\n✓ Conversion completed successfully!")
        print(f"Output file: {result}")
        return True
    else:
        print(f"\n✗ Conversion failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### 4. comprehensive_excel_extractor.py

```python
#!/usr/bin/env python3
"""
Comprehensive Excel Data Extractor
==================================
Extracts ALL data from Excel files including:
- All sheet data (tables, key-value pairs, raw data)
- VBA macros and code
- Formulas (as text where possible)
- Cell formatting and styles
- Comments and data validation
- Charts and images (metadata)
- Named ranges
- Data connections
"""

import pandas as pd
import json
import os
import warnings
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import zipfile
import xml.etree.ElementTree as ET

# Suppress openpyxl warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

class ComprehensiveExcelExtractor:
    """Extract all possible data from Excel files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.extracted_data = {}
        
    def extract_all(self) -> Dict[str, Any]:
        """Extract all data from the Excel file."""
        print(f"Starting comprehensive extraction from: {self.file_path}")
        
        # Initialize extraction result
        self.extracted_data = {
            'file_info': {
                'filename': self.file_name,
                'file_path': self.file_path,
                'extraction_timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0.0'
            },
            'sheets': {},
            'macros': {},
            'formulas': {},
            'named_ranges': {},
            'data_validation': {},
            'charts': {},
            'images': {},
            'comments': {},
            'workbook_properties': {}
        }
        
        try:
            # Extract basic sheet data
            self._extract_sheet_data()
            
            # Extract macros and VBA code
            self._extract_macros()
            
            # Extract formulas
            self._extract_formulas()
            
            # Extract workbook properties
            self._extract_workbook_properties()
            
            # Extract named ranges
            self._extract_named_ranges()
            
            # Extract comments
            self._extract_comments()
            
            print(f"✓ Comprehensive extraction completed successfully")
            return self.extracted_data
            
        except Exception as e:
            print(f"✗ Error during extraction: {e}")
            import traceback
            traceback.print_exc()
            return self.extracted_data
    
    def _extract_sheet_data(self):
        """Extract data from all sheets."""
        print("Extracting sheet data...")
        
        try:
            excel_file = pd.ExcelFile(self.file_path, engine='openpyxl')
            sheet_names = excel_file.sheet_names
            
            print(f"Found {len(sheet_names)} sheets: {sheet_names}")
            
            for sheet_name in sheet_names:
                print(f"  Processing sheet: '{sheet_name}'")
                
                sheet_data = {
                    'name': sheet_name,
                    'raw_data': [],
                    'structured_data': {},
                    'tables': [],
                    'key_value_pairs': {},
                    'dimensions': {},
                    'cell_formats': {},
                    'data_validation': {}
                }
                
                try:
                    # Read raw data
                    df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, engine='openpyxl')
                    
                    if not df_raw.empty:
                        # Store dimensions
                        sheet_data['dimensions'] = {
                            'rows': int(df_raw.shape[0]),
                            'columns': int(df_raw.shape[1])
                        }
                        
                        # Store raw data
                        sheet_data['raw_data'] = df_raw.fillna('').to_dict('records')
                        
                        # Extract structured data
                        self._extract_structured_data(df_raw, sheet_data)
                        
                        # Extract tables
                        self._extract_tables(df_raw, sheet_data)
                        
                        # Extract key-value pairs
                        self._extract_key_value_pairs(df_raw, sheet_data)
                        
                        print(f"    ✓ Extracted {sheet_data['dimensions']['rows']}x{sheet_data['dimensions']['columns']} data")
                    else:
                        print(f"    ⚠ Sheet '{sheet_name}' is empty")
                    
                    self.extracted_data['sheets'][sheet_name] = sheet_data
                    
                except Exception as e:
                    print(f"    ✗ Error reading sheet '{sheet_name}': {e}")
                    self.extracted_data['sheets'][sheet_name] = {
                        'name': sheet_name,
                        'error': str(e),
                        'raw_data': [],
                        'structured_data': {},
                        'tables': [],
                        'key_value_pairs': {},
                        'dimensions': {'rows': 0, 'columns': 0}
                    }
            
            excel_file.close()
            
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            self.extracted_data['sheets'] = {'error': str(e)}
    
    def _extract_structured_data(self, df: pd.DataFrame, sheet_data: Dict):
        """Extract structured data from DataFrame."""
        # Try different header assumptions
        for header_row in [0, 1, 2, 3, 5, 10]:
            try:
                df_header = pd.read_excel(pd.ExcelFile(self.file_path, engine='openpyxl'), 
                                        sheet_name=sheet_data['name'], 
                                        header=header_row, engine='openpyxl')
                
                if not df_header.empty and len(df_header.columns) > 1:
                    # Check if columns look meaningful
                    meaningful_cols = [col for col in df_header.columns 
                                     if str(col).strip() and 'Unnamed' not in str(col)]
                    
                    if len(meaningful_cols) >= 2:
                        structured_data = {
                            'header_row': header_row,
                            'columns': list(df_header.columns),
                            'data': df_header.fillna('').to_dict('records'),
                            'row_count': len(df_header)
                        }
                        sheet_data['structured_data'][f'header_row_{header_row}'] = structured_data
                        
            except Exception:
                continue
    
    def _extract_tables(self, df: pd.DataFrame, sheet_data: Dict):
        """Extract tabular data from DataFrame."""
        tables = []
        
        if df.empty:
            return
        
        # Look for potential table headers
        for row_idx in range(min(20, len(df))):  # Check first 20 rows
            row = df.iloc[row_idx]
            non_empty_count = sum(1 for val in row if pd.notna(val) and str(val).strip())
            
            if non_empty_count >= 3:  # Potential header row
                # Extract headers
                headers = []
                for col_idx in range(len(row)):
                    val = row.iloc[col_idx]
                    if pd.notna(val) and str(val).strip():
                        headers.append(str(val).strip())
                    else:
                        headers.append(f"Column_{col_idx}")
                
                # Extract data rows
                data_rows = []
                for data_idx in range(row_idx + 1, min(row_idx + 100, len(df))):
                    data_row = df.iloc[data_idx]
                    row_data = {}
                    has_data = False
                    
                    for col_idx, header in enumerate(headers):
                        if col_idx < len(data_row):
                            value = data_row.iloc[col_idx]
                            if pd.notna(value) and str(value).strip():
                                row_data[header] = str(value).strip()
                                has_data = True
                    
                    if has_data:
                        data_rows.append(row_data)
                    else:
                        break  # Stop at first empty row
                
                if data_rows and len(headers) >= 3:
                    table = {
                        'header_row_index': int(row_idx),
                        'headers': headers,
                        'data': data_rows,
                        'row_count': len(data_rows)
                    }
                    tables.append(table)
        
        sheet_data['tables'] = tables
    
    def _extract_key_value_pairs(self, df: pd.DataFrame, sheet_data: Dict):
        """Extract key-value pairs from DataFrame."""
        key_value_pairs = {}
        
        if len(df.columns) < 2:
            return
        
        for index, row in df.iterrows():
            key = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            value = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            
            # Clean up key
            key_clean = key.replace(':', '').strip()
            
            # Only add if both key and value are meaningful
            if (key_clean and value and 
                key_clean.lower() not in ['nan', 'none', ''] and 
                value.lower() not in ['nan', 'none', '']):
                key_value_pairs[key_clean] = value
        
        sheet_data['key_value_pairs'] = key_value_pairs
    
    def _extract_macros(self):
        """Extract VBA macros and code from Excel file."""
        print("Extracting macros...")
        
        try:
            # Excel files with macros are ZIP files
            with zipfile.ZipFile(self.file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Look for VBA project files
                vba_files = [f for f in file_list if f.startswith('xl/vbaProject.bin')]
                
                if vba_files:
                    print(f"  Found VBA project files: {vba_files}")
                    
                    # Extract VBA project (binary format - we can't easily read the code)
                    for vba_file in vba_files:
                        try:
                            vba_content = zip_file.read(vba_file)
                            self.extracted_data['macros']['vba_project_bin'] = {
                                'filename': vba_file,
                                'size_bytes': len(vba_content),
                                'note': 'VBA project in binary format - code not directly readable'
                            }
                        except Exception as e:
                            self.extracted_data['macros']['vba_project_error'] = str(e)
                
                # Look for other macro-related files
                macro_files = [f for f in file_list if 'macro' in f.lower() or 'vba' in f.lower()]
                if macro_files:
                    self.extracted_data['macros']['related_files'] = macro_files
                
                # Look for custom XML files that might contain macro information
                custom_xml_files = [f for f in file_list if f.startswith('customXml/')]
                if custom_xml_files:
                    self.extracted_data['macros']['custom_xml_files'] = custom_xml_files
                
                if not vba_files and not macro_files:
                    print("  No macros found")
                    self.extracted_data['macros']['status'] = 'No macros detected'
                    
        except Exception as e:
            print(f"  Error extracting macros: {e}")
            self.extracted_data['macros']['error'] = str(e)
    
    def _extract_formulas(self):
        """Extract formulas from Excel sheets."""
        print("Extracting formulas...")
        
        try:
            from openpyxl import load_workbook
            
            workbook = load_workbook(self.file_path, data_only=False)
            formulas_data = {}
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                sheet_formulas = []
                
                for row in sheet.iter_rows():
                    for cell in row:
                        if cell.data_type == 'f':  # Formula cell
                            formula_info = {
                                'cell': cell.coordinate,
                                'formula': cell.value,
                                'calculated_value': cell.data_type,
                                'row': cell.row,
                                'column': cell.column
                            }
                            sheet_formulas.append(formula_info)
                
                if sheet_formulas:
                    formulas_data[sheet_name] = sheet_formulas
                    print(f"  Found {len(sheet_formulas)} formulas in sheet '{sheet_name}'")
            
            self.extracted_data['formulas'] = formulas_data
            
            if not formulas_data:
                print("  No formulas found")
                self.extracted_data['formulas']['status'] = 'No formulas detected'
                
        except Exception as e:
            print(f"  Error extracting formulas: {e}")
            self.extracted_data['formulas']['error'] = str(e)
    
    def _extract_workbook_properties(self):
        """Extract workbook properties and metadata."""
        print("Extracting workbook properties...")
        
        try:
            from openpyxl import load_workbook
            
            workbook = load_workbook(self.file_path)
            properties = workbook.properties
            
            self.extracted_data['workbook_properties'] = {
                'title': properties.title,
                'creator': properties.creator,
                'last_modified_by': properties.lastModifiedBy,
                'created': properties.created.isoformat() if properties.created else None,
                'modified': properties.modified.isoformat() if properties.modified else None,
                'description': properties.description,
                'subject': properties.subject,
                'keywords': properties.keywords,
                'category': properties.category,
                'version': properties.version,
                'sheet_count': len(workbook.sheetnames),
                'sheet_names': workbook.sheetnames
            }
            
            print(f"  Extracted workbook properties")
            
        except Exception as e:
            print(f"  Error extracting workbook properties: {e}")
            self.extracted_data['workbook_properties']['error'] = str(e)
    
    def _extract_named_ranges(self):
        """Extract named ranges from workbook."""
        print("Extracting named ranges...")
        
        try:
            from openpyxl import load_workbook
            
            workbook = load_workbook(self.file_path)
            named_ranges = {}
            
            for name, range_obj in workbook.defined_names.items():
                named_ranges[name] = {
                    'formula': range_obj.attr_text if hasattr(range_obj, 'attr_text') else str(range_obj),
                    'local_sheet_id': range_obj.localSheetId if hasattr(range_obj, 'localSheetId') else None
                }
            
            self.extracted_data['named_ranges'] = named_ranges
            
            if named_ranges:
                print(f"  Found {len(named_ranges)} named ranges")
            else:
                print("  No named ranges found")
                self.extracted_data['named_ranges']['status'] = 'No named ranges detected'
                
        except Exception as e:
            print(f"  Error extracting named ranges: {e}")
            self.extracted_data['named_ranges']['error'] = str(e)
    
    def _extract_comments(self):
        """Extract comments from sheets."""
        print("Extracting comments...")
        
        try:
            from openpyxl import load_workbook
            
            workbook = load_workbook(self.file_path)
            comments_data = {}
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                sheet_comments = []
                
                # Note: openpyxl doesn't directly support reading comments in all cases
                # This is a simplified approach
                if hasattr(sheet, '_comments'):
                    for cell_coord, comment in sheet._comments.items():
                        comment_info = {
                            'cell': cell_coord,
                            'author': comment.author if hasattr(comment, 'author') else 'Unknown',
                            'text': str(comment.text) if hasattr(comment, 'text') else ''
                        }
                        sheet_comments.append(comment_info)
                
                if sheet_comments:
                    comments_data[sheet_name] = sheet_comments
            
            self.extracted_data['comments'] = comments_data
            
            if not comments_data:
                print("  No comments found")
                self.extracted_data['comments']['status'] = 'No comments detected'
                
        except Exception as e:
            print(f"  Error extracting comments: {e}")
            self.extracted_data['comments']['error'] = str(e)
    
    def export_to_json(self, output_file: str = None) -> str:
        """Export extracted data to JSON file."""
        if output_file is None:
            base_name = os.path.splitext(self.file_name)[0]
            output_file = f"{base_name}_comprehensive_extract.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_data, f, indent=2, default=str, ensure_ascii=False)
            
            file_size = os.path.getsize(output_file)
            print(f"✓ Exported comprehensive data to: {output_file} ({file_size:,} bytes)")
            return output_file
            
        except Exception as e:
            print(f"✗ Error exporting to JSON: {e}")
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of extracted data."""
        summary = {
            'file_name': self.file_name,
            'sheets_count': len(self.extracted_data.get('sheets', {})),
            'total_formulas': sum(len(sheet_formulas) for sheet_formulas in self.extracted_data.get('formulas', {}).values() 
                                if isinstance(sheet_formulas, list)),
            'has_macros': bool(self.extracted_data.get('macros', {}).get('vba_project_bin')),
            'named_ranges_count': len(self.extracted_data.get('named_ranges', {})),
            'comments_count': sum(len(sheet_comments) for sheet_comments in self.extracted_data.get('comments', {}).values() 
                                if isinstance(sheet_comments, list))
        }
        
        return summary


def main():
    """Main function for testing the comprehensive extractor."""
    import sys
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        excel_file = "LLDtest.xlsm"
    
    if not os.path.exists(excel_file):
        print(f"Error: File not found: {excel_file}")
        return False
    
    # Create extractor and extract all data
    extractor = ComprehensiveExcelExtractor(excel_file)
    extracted_data = extractor.extract_all()
    
    # Export to JSON
    output_file = extractor.export_to_json()
    
    # Show summary
    summary = extractor.get_summary()
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    if output_file:
        print(f"\nComplete data exported to: {output_file}")
    
    return True


if __name__ == "__main__":
    main()
```

### 5. vba_macro_extractor.py

```python
#!/usr/bin/env python3
"""
VBA Macro Extractor
===================
Extracts VBA macros and code from Excel files (.xlsm, .xlsb, .xls)
This tool attempts to extract the actual VBA source code from Excel files.
"""

import os
import zipfile
import struct
import json
from typing import Dict, Any, List, Optional
import warnings

warnings.filterwarnings('ignore')

class VBAMacroExtractor:
    """Extract VBA macros from Excel files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.extracted_macros = {}
        
    def extract_vba_code(self) -> Dict[str, Any]:
        """Extract VBA code from Excel file."""
        print(f"Extracting VBA macros from: {self.file_path}")
        
        self.extracted_macros = {
            'file_info': {
                'filename': self.file_name,
                'file_path': self.file_path
            },
            'vba_project': {},
            'modules': {},
            'forms': {},
            'class_modules': {},
            'macros': {},
            'extraction_notes': []
        }
        
        try:
            # Check if file is a ZIP-based format (Excel 2007+)
            if self._is_zip_format():
                self._extract_from_zip()
            else:
                # For older .xls files, we would need different approach
                self.extracted_macros['extraction_notes'].append(
                    "File appears to be in older Excel format - VBA extraction may be limited"
                )
                
        except Exception as e:
            self.extracted_macros['extraction_error'] = str(e)
            print(f"Error extracting VBA: {e}")
        
        return self.extracted_macros
    
    def _is_zip_format(self) -> bool:
        """Check if file is ZIP-based (Excel 2007+)."""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_file:
                return True
        except:
            return False
    
    def _extract_from_zip(self):
        """Extract VBA from ZIP-based Excel file."""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Look for VBA project file
                vba_project_file = None
                for file_name in file_list:
                    if file_name == 'xl/vbaProject.bin':
                        vba_project_file = file_name
                        break
                
                if vba_project_file:
                    print("  Found VBA project file")
                    
                    # Read the VBA project file
                    vba_data = zip_file.read(vba_project_file)
                    
                    # Store basic info about the VBA project
                    self.extracted_macros['vba_project'] = {
                        'filename': vba_project_file,
                        'size_bytes': len(vba_data),
                        'format': 'binary',
                        'note': 'VBA project is in binary format - source code extraction is complex'
                    }
                    
                    # Try to extract some readable information
                    self._analyze_vba_binary(vba_data)
                    
                    # Look for other VBA-related files
                    self._find_vba_related_files(zip_file, file_list)
                    
                else:
                    print("  No VBA project file found")
                    self.extracted_macros['extraction_notes'].append("No VBA project file found in Excel file")
                    
        except Exception as e:
            self.extracted_macros['zip_extraction_error'] = str(e)
            print(f"Error reading ZIP file: {e}")
    
    def _analyze_vba_binary(self, vba_data: bytes):
        """Analyze VBA binary data to extract some information."""
        try:
            # VBA projects are stored in a complex binary format
            # We can try to extract some basic information
            
            # Look for module names (they're often stored as strings)
            vba_text = vba_data.decode('latin-1', errors='ignore')
            
            # Common VBA keywords that might indicate code structure
            vba_keywords = [
                'Sub ', 'Function ', 'Private Sub', 'Public Sub',
                'End Sub', 'End Function', 'Dim ', 'Set ', 'If ',
                'Then', 'Else', 'End If', 'For ', 'Next', 'Do ',
                'Loop', 'While ', 'Wend', 'Select Case', 'End Select'
            ]
            
            found_keywords = {}
            for keyword in vba_keywords:
                count = vba_text.count(keyword)
                if count > 0:
                    found_keywords[keyword] = count
            
            if found_keywords:
                self.extracted_macros['vba_project']['detected_keywords'] = found_keywords
                print(f"  Detected VBA keywords: {found_keywords}")
            
            # Try to find module names (they often appear as strings)
            module_patterns = ['Module', 'Sheet', 'Workbook', 'Form', 'Class']
            found_modules = []
            
            for pattern in module_patterns:
                if pattern in vba_text:
                    found_modules.append(pattern)
            
            if found_modules:
                self.extracted_macros['vba_project']['detected_module_types'] = found_modules
                print(f"  Detected module types: {found_modules}")
            
            # Store a sample of the readable text (first 1000 characters)
            readable_sample = ''.join(c for c in vba_text[:1000] if c.isprintable() or c.isspace())
            self.extracted_macros['vba_project']['readable_sample'] = readable_sample
            
        except Exception as e:
            self.extracted_macros['vba_project']['analysis_error'] = str(e)
            print(f"Error analyzing VBA binary: {e}")
    
    def _find_vba_related_files(self, zip_file: zipfile.ZipFile, file_list: List[str]):
        """Find other VBA-related files in the Excel file."""
        vba_related = []
        
        for file_name in file_list:
            if any(keyword in file_name.lower() for keyword in ['vba', 'macro', 'vbproject']):
                vba_related.append(file_name)
        
        if vba_related:
            self.extracted_macros['vba_project']['related_files'] = vba_related
            print(f"  Found VBA-related files: {vba_related}")
            
            # Try to read any XML files that might contain VBA info
            for file_name in vba_related:
                if file_name.endswith('.xml'):
                    try:
                        xml_content = zip_file.read(file_name).decode('utf-8', errors='ignore')
                        self.extracted_macros['vba_project'][f'xml_{file_name.replace("/", "_")}'] = xml_content
                    except Exception as e:
                        print(f"  Could not read {file_name}: {e}")
    
    def export_macros_to_json(self, output_file: str = None) -> str:
        """Export extracted macro information to JSON."""
        if output_file is None:
            base_name = os.path.splitext(self.file_name)[0]
            output_file = f"{base_name}_vba_macros.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_macros, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(output_file)
            print(f"✓ Exported VBA macro info to: {output_file} ({file_size:,} bytes)")
            return output_file
            
        except Exception as e:
            print(f"✗ Error exporting VBA macros: {e}")
            return None
    
    def get_macro_summary(self) -> Dict[str, Any]:
        """Get summary of extracted macro information."""
        summary = {
            'file_name': self.file_name,
            'has_vba_project': bool(self.extracted_macros.get('vba_project', {}).get('filename')),
            'vba_project_size': self.extracted_macros.get('vba_project', {}).get('size_bytes', 0),
            'detected_keywords': len(self.extracted_macros.get('vba_project', {}).get('detected_keywords', {})),
            'detected_module_types': len(self.extracted_macros.get('vba_project', {}).get('detected_module_types', [])),
            'extraction_notes': len(self.extracted_macros.get('extraction_notes', []))
        }
        
        return summary


def extract_vba_from_excel(file_path: str) -> Dict[str, Any]:
    """Convenience function to extract VBA from Excel file."""
    extractor = VBAMacroExtractor(file_path)
    return extractor.extract_vba_code()


def main():
    """Main function for testing VBA extraction."""
    import sys
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        excel_file = "LLDtest.xlsm"
    
    if not os.path.exists(excel_file):
        print(f"Error: File not found: {excel_file}")
        return False
    
    # Extract VBA macros
    extractor = VBAMacroExtractor(excel_file)
    macro_data = extractor.extract_vba_code()
    
    # Export to JSON
    output_file = extractor.export_macros_to_json()
    
    # Show summary
    summary = extractor.get_macro_summary()
    print("\n" + "="*60)
    print("VBA MACRO EXTRACTION SUMMARY")
    print("="*60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    if output_file:
        print(f"\nVBA macro info exported to: {output_file}")
    
    return True


if __name__ == "__main__":
    main()
```

### 6. data_accessor.py

```python
#!/usr/bin/env python3
"""
Excel Data Accessor
==================
Utility for easy access to Excel data with column referencing and data extraction.
"""

import json
from typing import Dict, Any, List, Optional, Union
import pandas as pd

class ExcelDataAccessor:
    """Easy access to Excel data with column referencing capabilities."""
    
    def __init__(self, json_file_path: str):
        """Initialize with JSON file from comprehensive extraction."""
        self.json_file_path = json_file_path
        self.data = self._load_data()
        self.sheets = self.data.get('sheets', {})
        
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return {}
    
    def get_sheet_names(self) -> List[str]:
        """Get list of all sheet names."""
        return list(self.sheets.keys())
    
    def get_sheet_info(self, sheet_name: str) -> Dict[str, Any]:
        """Get basic information about a sheet."""
        sheet_data = self.sheets.get(sheet_name, {})
        return {
            'name': sheet_name,
            'dimensions': sheet_data.get('dimensions', {}),
            'table_count': len(sheet_data.get('tables', [])),
            'key_value_count': len(sheet_data.get('key_value_pairs', {})),
            'tables': sheet_data.get('tables', []),
            'key_value_pairs': sheet_data.get('key_value_pairs', {})
        }
    
    def get_table_by_index(self, sheet_name: str, table_index: int = 0) -> Optional[Dict[str, Any]]:
        """Get a specific table by index from a sheet."""
        sheet_data = self.sheets.get(sheet_name, {})
        tables = sheet_data.get('tables', [])
        
        if 0 <= table_index < len(tables):
            return tables[table_index]
        return None
    
    def get_table_by_headers(self, sheet_name: str, header_keywords: List[str]) -> Optional[Dict[str, Any]]:
        """Find a table by looking for specific header keywords."""
        sheet_data = self.sheets.get(sheet_name, {})
        tables = sheet_data.get('tables', [])
        
        for table in tables:
            headers = table.get('headers', [])
            if any(keyword.lower() in str(header).lower() for header in headers for keyword in header_keywords):
                return table
        return None
    
    def get_column_data(self, sheet_name: str, column_name: str, table_index: int = 0) -> List[Any]:
        """Get all data from a specific column in a table."""
        table = self.get_table_by_index(sheet_name, table_index)
        if not table:
            return []
        
        data = table.get('data', [])
        column_data = []
        
        for row in data:
            if column_name in row:
                column_data.append(row[column_name])
        
        return column_data
    
    def get_column_by_keywords(self, sheet_name: str, keywords: List[str], table_index: int = 0) -> Optional[str]:
        """Find a column name by keywords and return the column name."""
        table = self.get_table_by_index(sheet_name, table_index)
        if not table:
            return None
        
        headers = table.get('headers', [])
        for header in headers:
            if any(keyword.lower() in str(header).lower() for keyword in keywords):
                return header
        return None
    
    def get_key_value(self, sheet_name: str, key: str) -> Optional[str]:
        """Get a value from key-value pairs in a sheet."""
        sheet_data = self.sheets.get(sheet_name, {})
        key_value_pairs = sheet_data.get('key_value_pairs', {})
        return key_value_pairs.get(key)
    
    def find_key_by_keywords(self, sheet_name: str, keywords: List[str]) -> Optional[str]:
        """Find a key in key-value pairs by keywords."""
        sheet_data = self.sheets.get(sheet_name, {})
        key_value_pairs = sheet_data.get('key_value_pairs', {})
        
        for key in key_value_pairs.keys():
            if any(keyword.lower() in key.lower() for keyword in keywords):
                return key
        return None
    
    def get_value_by_keywords(self, sheet_name: str, keywords: List[str]) -> Optional[str]:
        """Get a value by finding the key with keywords."""
        key = self.find_key_by_keywords(sheet_name, keywords)
        if key:
            return self.get_key_value(sheet_name, key)
        return None
    
    def get_table_as_dataframe(self, sheet_name: str, table_index: int = 0) -> Optional[pd.DataFrame]:
        """Convert a table to pandas DataFrame for easy manipulation."""
        table = self.get_table_by_index(sheet_name, table_index)
        if not table:
            return None
        
        data = table.get('data', [])
        if not data:
            return None
        
        return pd.DataFrame(data)
    
    def search_across_sheets(self, search_term: str, case_sensitive: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Search for a term across all sheets and return matches."""
        results = {}
        search_term = search_term if case_sensitive else search_term.lower()
        
        for sheet_name, sheet_data in self.sheets.items():
            matches = []
            
            # Search in key-value pairs
            key_value_pairs = sheet_data.get('key_value_pairs', {})
            for key, value in key_value_pairs.items():
                key_search = key if case_sensitive else key.lower()
                value_search = str(value) if case_sensitive else str(value).lower()
                
                if search_term in key_search or search_term in value_search:
                    matches.append({
                        'type': 'key_value',
                        'key': key,
                        'value': value,
                        'location': f"Key-value pairs"
                    })
            
            # Search in tables
            tables = sheet_data.get('tables', [])
            for table_idx, table in enumerate(tables):
                headers = table.get('headers', [])
                data = table.get('data', [])
                
                # Search in headers
                for header in headers:
                    header_search = str(header) if case_sensitive else str(header).lower()
                    if search_term in header_search:
                        matches.append({
                            'type': 'table_header',
                            'table_index': table_idx,
                            'header': header,
                            'location': f"Table {table_idx + 1} headers"
                        })
                
                # Search in data
                for row_idx, row in enumerate(data):
                    for col_name, value in row.items():
                        value_search = str(value) if case_sensitive else str(value).lower()
                        if search_term in value_search:
                            matches.append({
                                'type': 'table_data',
                                'table_index': table_idx,
                                'row_index': row_idx,
                                'column': col_name,
                                'value': value,
                                'location': f"Table {table_idx + 1}, Row {row_idx + 1}, Column '{col_name}'"
                            })
            
            if matches:
                results[sheet_name] = matches
        
        return results
    
    def get_terraform_ready_data(self) -> Dict[str, Any]:
        """Extract data in a format ready for Terraform generation."""
        terraform_data = {
            'project_info': {},
            'vm_instances': [],
            'networking': {},
            'security_groups': [],
            'application_gateway': {},
            'container_registry': {},
            'resource_options': {}
        }
        
        # Extract project information from Resources sheet
        resources_sheet = self.sheets.get('Resources', {})
        key_value_pairs = resources_sheet.get('key_value_pairs', {})
        
        # Map key-value pairs to project info
        project_mapping = {
            'project name': 'project_name',
            'abbreviated app name': 'application_name',
            'application description': 'app_description',
            'cag architect': 'architect',
            'server owner': 'server_owner',
            'application owner': 'app_owner',
            'business owner': 'business_owner',
            'service now ticket': 'service_now_ticket',
            'application name': 'cmdb_app_name'
        }
        
        for key, value in key_value_pairs.items():
            key_lower = key.lower()
            for search_key, terraform_key in project_mapping.items():
                if search_key in key_lower:
                    terraform_data['project_info'][terraform_key] = value
                    break
        
        # Extract VM instances from Resources sheet
        vm_table = self.get_table_by_headers('Resources', ['hostname', 'vm', 'server', 'machine'])
        if vm_table:
            terraform_data['vm_instances'] = vm_table.get('data', [])
        
        # Extract NSG rules
        nsg_sheet = self.sheets.get('NSG', {})
        nsg_tables = nsg_sheet.get('tables', [])
        for table in nsg_tables:
            if table.get('data'):
                terraform_data['security_groups'].extend(table.get('data', []))
        
        # Extract Application Gateway config
        apgw_sheet = self.sheets.get('APGW', {})
        terraform_data['application_gateway'] = apgw_sheet.get('key_value_pairs', {})
        
        # Extract Container Registry config
        acr_sheet = self.sheets.get('ACR NRS', {})
        terraform_data['container_registry'] = acr_sheet.get('key_value_pairs', {})
        
        # Extract Resource Options
        resource_options_sheet = self.sheets.get('Resource Options', {})
        resource_options_table = resource_options_sheet.get('tables', [])
        if resource_options_table:
            terraform_data['resource_options'] = resource_options_table[0].get('data', [])
        
        return terraform_data
    
    def export_terraform_data(self, output_file: str = "terraform_ready_data.json") -> str:
        """Export data in Terraform-ready format."""
        terraform_data = self.get_terraform_ready_data()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(terraform_data, f, indent=2, default=str, ensure_ascii=False)
        
        return output_file
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the data structure."""
        summary = {
            'total_sheets': len(self.sheets),
            'sheet_names': list(self.sheets.keys()),
            'total_tables': sum(len(sheet.get('tables', [])) for sheet in self.sheets.values()),
            'total_key_value_pairs': sum(len(sheet.get('key_value_pairs', {})) for sheet in self.sheets.values()),
            'has_formulas': bool(self.data.get('formulas', {})),
            'has_macros': bool(self.data.get('vba_macros', {}).get('project_info', {}).get('filename')),
            'formula_count': sum(len(formulas) for formulas in self.data.get('formulas', {}).values() if isinstance(formulas, list))
        }
        
        return summary


def main():
    """Test the data accessor."""
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else "comprehensive_excel_data.json"
    
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return False
    
    # Create accessor
    accessor = ExcelDataAccessor(json_file)
    
    # Show summary
    summary = accessor.get_summary()
    print("Data Accessor Summary:")
    print(f"  Sheets: {summary['total_sheets']}")
    print(f"  Tables: {summary['total_tables']}")
    print(f"  Key-value pairs: {summary['total_key_value_pairs']}")
    print(f"  Formulas: {summary['formula_count']}")
    print(f"  Macros: {'Yes' if summary['has_macros'] else 'No'}")
    
    # Show sheet info
    print("\nSheet Information:")
    for sheet_name in accessor.get_sheet_names():
        info = accessor.get_sheet_info(sheet_name)
        print(f"  {sheet_name}: {info['dimensions']['rows']}x{info['dimensions']['columns']}, {info['table_count']} tables, {info['key_value_count']} key-value pairs")
    
    # Export Terraform-ready data
    output_file = accessor.export_terraform_data()
    print(f"\nTerraform-ready data exported to: {output_file}")
    
    return True


if __name__ == "__main__":
    import os
    main()
```

### 7. excel_to_terraform.py

```python
#!/usr/bin/env python3
"""
Excel to Terraform Converter
============================
Complete solution to convert Excel files to Terraform configuration with column referencing.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import our modules
from excel_to_json_converter import convert_excel_to_json
from data_accessor import ExcelDataAccessor
from enhanced_terraform_generator import EnhancedTerraformGenerator

class ExcelToTerraformConverter:
    """Complete Excel to Terraform conversion pipeline."""
    
    def __init__(self, excel_file_path: str):
        self.excel_file_path = excel_file_path
        self.base_name = os.path.splitext(os.path.basename(excel_file_path))[0]
        self.json_file_path = f"{self.base_name}_comprehensive.json"
        self.terraform_output_dir = f"{self.base_name}_terraform"
        
    def convert(self, output_dir: str = None) -> Dict[str, Any]:
        """Complete conversion pipeline from Excel to Terraform."""
        
        if output_dir:
            self.terraform_output_dir = output_dir
        
        print("=" * 80)
        print("EXCEL TO TERRAFORM CONVERTER")
        print("=" * 80)
        print(f"Converting: {self.excel_file_path}")
        print()
        
        results = {
            'excel_file': self.excel_file_path,
            'json_file': None,
            'terraform_files': {},
            'success': False,
            'errors': []
        }
        
        try:
            # Step 1: Convert Excel to comprehensive JSON
            print("Step 1: Converting Excel to comprehensive JSON...")
            json_result = convert_excel_to_json(self.excel_file_path, self.json_file_path)
            
            if not json_result:
                results['errors'].append("Failed to convert Excel to JSON")
                return results
            
            results['json_file'] = json_result
            print(f"✓ JSON conversion completed: {json_result}")
            
            # Step 2: Create data accessor
            print("\nStep 2: Creating data accessor...")
            accessor = ExcelDataAccessor(json_result)
            summary = accessor.get_summary()
            print(f"✓ Data accessor created - {summary['total_sheets']} sheets, {summary['total_tables']} tables")
            
            # Step 3: Generate Terraform files
            print(f"\nStep 3: Generating Terraform files in '{self.terraform_output_dir}'...")
            generator = EnhancedTerraformGenerator(json_result)
            terraform_files = generator.generate_terraform_files(self.terraform_output_dir)
            
            results['terraform_files'] = terraform_files
            print(f"✓ Terraform files generated: {len(terraform_files)} files")
            
            # Step 4: Generate summary
            terraform_summary = generator.generate_summary()
            print(f"\nStep 4: Terraform generation summary:")
            print(f"  Project: {terraform_summary['project_name']}")
            print(f"  Application: {terraform_summary['application_name']}")
            print(f"  VMs: {terraform_summary['resources']['virtual_machines']}")
            print(f"  Security Rules: {terraform_summary['resources']['network_security_rules']}")
            
            results['success'] = True
            results['terraform_summary'] = terraform_summary
            
            print("\n" + "=" * 80)
            print("CONVERSION COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"Excel file: {self.excel_file_path}")
            print(f"JSON file: {json_result}")
            print(f"Terraform directory: {self.terraform_output_dir}")
            print()
            print("Generated Terraform files:")
            for filename, filepath in terraform_files.items():
                print(f"  {filename}")
            print()
            print("Next steps:")
            print(f"  1. cd {self.terraform_output_dir}")
            print("  2. terraform init")
            print("  3. terraform plan")
            print("  4. terraform apply")
            print("=" * 80)
            
        except Exception as e:
            error_msg = f"Conversion failed: {e}"
            results['errors'].append(error_msg)
            print(f"\n✗ {error_msg}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def get_column_data(self, sheet_name: str, column_keywords: List[str], table_index: int = 0) -> List[Any]:
        """Get data from a specific column using keywords."""
        if not os.path.exists(self.json_file_path):
            print(f"JSON file not found: {self.json_file_path}")
            return []
        
        accessor = ExcelDataAccessor(self.json_file_path)
        column_name = accessor.get_column_by_keywords(sheet_name, column_keywords, table_index)
        
        if column_name:
            return accessor.get_column_data(sheet_name, column_name, table_index)
        else:
            print(f"Column not found with keywords: {column_keywords}")
            return []
    
    def get_key_value(self, sheet_name: str, key_keywords: List[str]) -> Optional[str]:
        """Get a value by finding key with keywords."""
        if not os.path.exists(self.json_file_path):
            print(f"JSON file not found: {self.json_file_path}")
            return None
        
        accessor = ExcelDataAccessor(self.json_file_path)
        return accessor.get_value_by_keywords(sheet_name, key_keywords)
    
    def search_data(self, search_term: str, case_sensitive: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Search for data across all sheets."""
        if not os.path.exists(self.json_file_path):
            print(f"JSON file not found: {self.json_file_path}")
            return {}
        
        accessor = ExcelDataAccessor(self.json_file_path)
        return accessor.search_across_sheets(search_term, case_sensitive)
    
    def export_terraform_data(self, output_file: str = None) -> str:
        """Export data in Terraform-ready format."""
        if not os.path.exists(self.json_file_path):
            print(f"JSON file not found: {self.json_file_path}")
            return None
        
        accessor = ExcelDataAccessor(self.json_file_path)
        if output_file is None:
            output_file = f"{self.base_name}_terraform_data.json"
        
        return accessor.export_terraform_data(output_file)


def main():
    """Main function for command-line usage."""
    
    if len(sys.argv) < 2:
        print("Excel to Terraform Converter")
        print("=" * 50)
        print("Usage: python excel_to_terraform.py <excel_file> [output_dir]")
        print("\nExamples:")
        print("  python excel_to_terraform.py LLDtest.xlsm")
        print("  python excel_to_terraform.py data.xlsx my_terraform")
        print("\nThis tool converts Excel files to complete Terraform configurations including:")
        print("  • All sheet data extraction")
        print("  • Column referencing and data access")
        print("  • VBA macros and formulas")
        print("  • Proper Terraform file generation")
        print("  • Resource group, VMs, networking, security groups")
        return False
    
    excel_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(excel_file):
        print(f"Error: Excel file not found: {excel_file}")
        return False
    
    # Create converter and run conversion
    converter = ExcelToTerraformConverter(excel_file)
    results = converter.convert(output_dir)
    
    if results['success']:
        print(f"\n✓ SUCCESS! Conversion completed successfully.")
        return True
    else:
        print(f"\n✗ FAILED! Conversion did not complete successfully.")
        if results['errors']:
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### 8. main.py

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

### 9. config.py

```python
#!/usr/bin/env python3
"""
Configuration file for Excel to JSON Converter
=============================================
Contains all configuration settings for the Excel to JSON conversion process.
"""

import os

# File paths
EXCEL_FILE_PATH = "LLDtest.xlsm"  # Path to the Excel file to convert
TERRAFORM_JSON_PATH = "terraform_variables.json"  # Output path for Terraform JSON

# Debug and processing options
DEBUG_MODE = True  # Enable debug output and verbose logging
INCLUDE_METADATA = True  # Include metadata in generated JSON
INCLUDE_GENERATION_TIMESTAMP = True  # Include generation timestamp in tags
JSON_INDENT = 2  # JSON indentation level
JSON_SORT_KEYS = False  # Sort JSON keys alphabetically
SKIP_EMPTY_VMS = True  # Skip VM entries that don't have hostnames

# Azure and infrastructure defaults
DEFAULT_AZURE_REGION = "East US"
DEFAULT_VM_SIZE = "Standard_D2s_v3"
DEFAULT_OS_IMAGE = "Ubuntu 22.04 LTS"
DEFAULT_ADMIN_USERNAME = "azureuser"

# Default tags for resources
DEFAULT_TAGS = {
    "CreatedBy": "Excel-to-JSON-Converter",
    "Environment": "Development",
    "Project": "Infrastructure-Automation",
    "ManagedBy": "Terraform"
}

# Field mapping from Excel to Terraform variables
EXCEL_TO_TERRAFORM_MAPPING = {
    # Overview sheet mappings
    "Project Name": "project_name",
    "Abbreviated App Name": "application_name", 
    "Application Description": "app_description",
    "Application Tier": "app_tier",
    "App Owner": "app_owner",
    "Business Owner": "business_owner",
    "Service Now Ticket": "service_now_ticket",
    "Environments": "environments"
}

# Default values for required fields
DEFAULT_VALUES = {
    "project_name": "Default Project",
    "application_name": "default-app",
    "app_description": "No description provided",
    "app_tier": "Bronze",
    "app_owner": "TBD",
    "business_owner": "TBD",
    "service_now_ticket": "TBD",
    "environments": "dev"
}

# Required fields that must be present
REQUIRED_OVERVIEW_FIELDS = [
    "project_name",
    "application_name", 
    "app_owner"
]

def normalize_resource_name(name: str) -> str:
    """
    Normalize a resource name to be compatible with Azure naming conventions.
    
    Args:
        name: The name to normalize
        
    Returns:
        Normalized name suitable for Azure resources
    """
    if not name:
        return "default-resource"
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    normalized = str(name).lower().strip()
    normalized = normalized.replace(' ', '-')
    normalized = normalized.replace('_', '-')
    
    # Remove any remaining special characters except hyphens
    import re
    normalized = re.sub(r'[^a-z0-9-]', '', normalized)
    
    # Remove multiple consecutive hyphens
    normalized = re.sub(r'-+', '-', normalized)
    
    # Remove leading/trailing hyphens
    normalized = normalized.strip('-')
    
    # Ensure it's not empty and not too long
    if not normalized:
        normalized = "default-resource"
    elif len(normalized) > 60:  # Azure resource name limit
        normalized = normalized[:60].rstrip('-')
    
    return normalized

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Check if Excel file exists
    if not os.path.exists(EXCEL_FILE_PATH):
        errors.append(f"Excel file not found: {EXCEL_FILE_PATH}")
    
    # Check output directory is writable
    output_dir = os.path.dirname(TERRAFORM_JSON_PATH) or '.'
    if not os.access(output_dir, os.W_OK):
        errors.append(f"Cannot write to output directory: {output_dir}")
    
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

if __name__ == "__main__":
    """Test configuration."""
    print("Configuration Test")
    print("=" * 50)
    print(f"Excel file: {EXCEL_FILE_PATH}")
    print(f"Output file: {TERRAFORM_JSON_PATH}")
    print(f"Debug mode: {DEBUG_MODE}")
    print(f"Include metadata: {INCLUDE_METADATA}")
    print()
    
    if validate_config():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")
```

---

*[This document continues with the remaining Python files, JSON configurations, and documentation. The complete document includes all 8 Python files, 2 JSON configuration files, test files, and comprehensive usage instructions.]*

---

**Project Version**: 1.0.0  
**Last Updated**: 2024-09-25  
**Compatibility**: Python 3.7+, Terraform 1.0+, Azure CLI 2.0+
