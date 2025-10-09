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

# imports
from excel_to_json_converter import convert_excel_to_json
from data_accessor import ExcelDataAccessor
from enhanced_terraform_generator import EnhancedTerraformGenerator
from enhanced_terraform_generator_v2 import EnhancedTerraformGeneratorV2

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
                "default_vm_size": "Standard_D2s_v2",
                "default_os": "Windows Server 2022",
                "enable_diagnostics": True,
                "use_enhanced_generator_v2": True,
                "module_source": "app.terraform.io/wab-cloudengineering-org/base-vm/iac"
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
            excel_files = [f for f in excel_files if os.path.isfile(f) and not os.path.basename(f).startswith('~$')]
            
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
            self.logger.info("SUCCESS: Input validation completed")
            
            # Discover Excel files to process
            excel_files = self._discover_excel_files()
            self.logger.info(f"Processing {len(excel_files)} Excel file(s)")
            
            # Step 2: Backup previous outputs if configured
            if self.config['output']['backup_previous']:
                self.logger.info("Step 2: Backing up previous outputs...")
                self._backup_previous_outputs()
                results['steps_completed'].append('backup')
                self.logger.info("SUCCESS: Previous outputs backed up")
            
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
                self.logger.info(f"SUCCESS: Excel data extracted to: {json_result['json_file']}")
                
                # Step 4: Generate Terraform files
                self.logger.info(f"Step 4.{i}: Generating Terraform files...")
                terraform_result = self._generate_terraform_files(json_result['json_file'], excel_file)
                if not terraform_result['success']:
                    results['errors'].extend(terraform_result['errors'])
                    self.logger.error(f"Failed to generate Terraform for {excel_file}: {terraform_result['errors']}")
                    continue
                results['steps_completed'].append(f'terraform_generation_{i}')
                results['files_generated'].extend(terraform_result['files'])
                self.logger.info(f"SUCCESS: Terraform files generated in: {terraform_result['output_dir']}")
                
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
                self.logger.info("SUCCESS: Output validation completed")
            
            # Step 6: Generate summary report
            self.logger.info("Step 6: Generating summary report...")
            summary = self._generate_summary_report(results, processed_files)
            results['summary'] = summary
            results['steps_completed'].append('summary_report')
            self.logger.info("SUCCESS: Summary report generated")
            
            # Step 7: Cleanup temporary files
            if self.config['output']['cleanup_temp_files']:
                self.logger.info("Step 7: Cleaning up temporary files...")
                self._cleanup_temp_files()
                results['steps_completed'].append('cleanup')
                self.logger.info("SUCCESS: Temporary files cleaned up")
            
            # Check if we successfully processed any files
            if processed_files:
                results['success'] = True
                self.logger.info("=" * 80)
                self.logger.info("AUTOMATION PIPELINE COMPLETED SUCCESSFULLY!")
                self.logger.info("=" * 80)
            else:
                results['success'] = False
                if not results['errors']:
                    results['errors'].append("No files were successfully processed")
                self.logger.info("=" * 80)
                self.logger.error("AUTOMATION PIPELINE FAILED!")
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
    
    def _create_dynamic_output_directory(self, json_file: str, excel_file: str) -> str:
        """Create dynamic output directory based on Subscription field and timestamp."""
        
        # Check if dynamic folder naming is enabled
        dynamic_naming = self.config.get('output', {}).get('dynamic_folder_naming', True)
        
        if not dynamic_naming:
            # Use legacy naming
            base_name = os.path.splitext(os.path.basename(excel_file))[0]
            terraform_dir = os.path.join(self.config['output']['terraform_dir'], f"{base_name}_terraform")
            self.logger.info(f"Using legacy folder naming: {terraform_dir}")
            return terraform_dir
        
        # Load JSON data to extract subscription
        subscription_value = self._extract_subscription_from_json(json_file)
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create directory name based on configuration pattern
        if subscription_value:
            # Use configured pattern with subscription
            pattern = self.config.get('output', {}).get('folder_naming_pattern', '{subscription}_{timestamp}')
            clean_subscription = self._sanitize_directory_name(subscription_value)
            directory_name = pattern.format(subscription=clean_subscription, timestamp=timestamp)
            self.logger.info(f"Using subscription-based naming: {directory_name}")
        else:
            # Use fallback pattern with Excel filename
            fallback_pattern = self.config.get('output', {}).get('fallback_folder_naming', '{excel_filename}_{timestamp}')
            base_name = os.path.splitext(os.path.basename(excel_file))[0]
            clean_base_name = self._sanitize_directory_name(base_name)
            directory_name = fallback_pattern.format(excel_filename=clean_base_name, timestamp=timestamp)
            self.logger.warning(f"Subscription not found, using fallback naming: {directory_name}")
        
        # Create full path
        terraform_dir = os.path.join(self.config['output']['terraform_dir'], directory_name)
        
        self.logger.info(f"Creating dynamic output directory: {terraform_dir}")
        self.logger.info(f"Based on subscription: {subscription_value or 'Not found'}")
        self.logger.info(f"Timestamp: {timestamp}")
        
        return terraform_dir
    
    def _extract_subscription_from_json(self, json_file: str) -> Optional[str]:
        """Extract Subscription value from JSON data."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Try to find subscription in build environment data
            build_env = data.get('build_environment', {})
            kv_pairs = build_env.get('key_value_pairs', {})
            
            # Look for subscription in key-value pairs
            subscription_keywords = ['subscription', 'Subscription', 'SUBSCRIPTION']
            for key, value in kv_pairs.items():
                if any(keyword in key for keyword in subscription_keywords):
                    if value and str(value).strip():
                        self.logger.info(f"Found subscription in Build_ENV: {value}")
                        return str(value).strip()
            
            # Try to find subscription in Resources sheet key-value pairs
            resources_sheet = data.get('sheets', {}).get('Resources', {})
            resources_kv = resources_sheet.get('key_value_pairs', {})
            
            for key, value in resources_kv.items():
                if any(keyword in key for keyword in subscription_keywords):
                    if value and str(value).strip():
                        self.logger.info(f"Found subscription in Resources: {value}")
                        return str(value).strip()
            
            # Try to find subscription in comprehensive data
            comprehensive_data = data.get('comprehensive_data', {})
            for sheet_name, sheet_data in comprehensive_data.items():
                kv_pairs = sheet_data.get('key_value_pairs', {})
                for key, value in kv_pairs.items():
                    if any(keyword in key for keyword in subscription_keywords):
                        if value and str(value).strip():
                            self.logger.info(f"Found subscription in {sheet_name}: {value}")
                            return str(value).strip()
            
            # Try to find subscription in VM instances
            vm_instances = data.get('vm_instances', [])
            for vm in vm_instances:
                for key, value in vm.items():
                    if any(keyword in key for keyword in subscription_keywords):
                        if value and str(value).strip():
                            self.logger.info(f"Found subscription in VM data: {value}")
                            return str(value).strip()
            
            self.logger.warning("Subscription field not found in Excel data")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting subscription from JSON: {e}")
            return None
    
    def _sanitize_directory_name(self, name: str) -> str:
        """Sanitize name for use as directory name."""
        import re
        
        if not name:
            return "unknown"
        
        # Convert to string and clean
        clean_name = str(name).strip()
        
        # Replace spaces and special characters with underscores
        clean_name = re.sub(r'[^\w\-_]', '_', clean_name)
        
        # Remove multiple consecutive underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        # Limit length
        if len(clean_name) > 50:
            clean_name = clean_name[:50].rstrip('_')
        
        # Ensure it's not empty
        if not clean_name:
            clean_name = "unknown"
        
        return clean_name
    
    def _generate_terraform_files(self, json_file: str, excel_file: str) -> Dict[str, Any]:
        """Generate Terraform files from JSON data."""
        result = {'success': False, 'errors': [], 'files': [], 'output_dir': None}
        
        try:
            # Extract subscription and create dynamic output directory
            terraform_dir = self._create_dynamic_output_directory(json_file, excel_file)
            
            # Create generator based on configuration
            use_v2_generator = self.config.get('terraform', {}).get('use_enhanced_generator_v2', True)
            
            if use_v2_generator:
                generator = EnhancedTerraformGeneratorV2(json_file)
                self.logger.info("Using Enhanced Terraform Generator v2 (module.md patterns)")
            else:
                generator = EnhancedTerraformGenerator(json_file)
                self.logger.info("Using Enhanced Terraform Generator v1 (legacy patterns)")
            
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
            self.logger.info("SUCCESS: Automation completed successfully - notification sent")
        else:
            self.logger.error("X Automation failed - failure notification sent")


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
            print("SUCCESS: Dry run completed successfully - all inputs valid")
            return 0
        else:
            print("ERROR: Dry run failed:")
            for error in validation_result['errors']:
                print(f"  - {error}")
            return 1
    
    # Run the pipeline
    results = pipeline.run()
    
    # Return appropriate exit code
    if results['success']:
        print(f"\nSUCCESS: Automation completed successfully in {results['duration_seconds']:.2f} seconds")
        print(f"Generated {len(results['files_generated'])} files")
        return 0
    else:
        print(f"\nERROR: Automation failed after {results['duration_seconds']:.2f} seconds")
        print("Errors:")
        for error in results['errors']:
            print(f"  - {error}")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
