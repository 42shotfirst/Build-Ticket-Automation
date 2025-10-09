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

def comprehensive_conversion(excel_file_path=None, generate_terraform=True):
    """
    Convert Excel file to comprehensive JSON format (includes all data, macros, formulas, etc.)
    Optionally generate Terraform files automatically.
    
    Args:
        excel_file_path: Path to Excel file (optional, uses config default)
        generate_terraform: If True, automatically generates Terraform files after JSON conversion
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
            print(f"\nSUCCESS: Comprehensive conversion completed successfully!")
            print(f"Output file: {result}")
            
            # Automatically generate Terraform files if requested
            if generate_terraform:
                print("\n" + "=" * 60)
                print("GENERATING TERRAFORM FILES")
                print("=" * 60)
                
                try:
                    # Import automation_pipeline module
                    from automation_pipeline import AutomationPipeline
                    
                    # Run the automation pipeline
                    pipeline = AutomationPipeline()
                    pipeline_result = pipeline.run()
                    
                    # Check if pipeline was successful
                    if pipeline_result and pipeline_result.get('success', False):
                        print("\nSUCCESS: Terraform files generated successfully!")
                        print(f"Location: output_package/")
                        return True
                    else:
                        print("\nERROR: Terraform generation failed!")
                        if pipeline_result and 'errors' in pipeline_result:
                            print("Errors:")
                            for error in pipeline_result['errors']:
                                print(f"  - {error}")
                        return False
                        
                except Exception as e:
                    print(f"\nERROR: Error generating Terraform files: {e}")
                    print("JSON conversion was successful, but Terraform generation failed.")
                    return False
            
            return True
        else:
            print(f"\nERROR: Comprehensive conversion failed!")
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
                print(f"SUCCESS: Successfully processed: {os.path.basename(excel_file)}")
            else:
                print(f"ERROR: Failed to process: {os.path.basename(excel_file)}")
        except Exception as e:
            print(f"ERROR: Error processing {os.path.basename(excel_file)}: {e}")
    
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
            print(f"\nSUCCESS: Excel to Terraform conversion completed successfully!")
            return True
        else:
            print(f"\nERROR: Excel to Terraform conversion failed!")
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
Excel to Terraform Automation
==============================

This tool converts Excel files to comprehensive JSON and Terraform infrastructure:
- Extracts ALL sheet data (tables, key-value pairs, raw data)
- Captures VBA macros and code
- Preserves formulas and calculated values
- Includes workbook properties and metadata
- Automatically generates complete Terraform deployment package

USAGE:
    python main.py                         # Convert Excel to JSON + Terraform (NEW DEFAULT)
    python main.py --comprehensive         # Convert Excel to JSON + Terraform (explicit)
    python main.py --directory /path/to/files  # Process all Excel files in directory
    python main.py --terraform-complete    # Convert Excel to complete Terraform files
    python main.py --terraform             # Convert Excel to Terraform JSON (legacy)
    python main.py --demo                  # Run column referencing and Terraform demo
    python main.py --help                  # Show this help
    python main.py --config                # Show configuration status
    python main.py --test                  # Test with sample data

NEW BEHAVIOR (Default):
    Running 'python main.py' now automatically:
    1. Converts Excel file to comprehensive JSON
    2. Generates complete Terraform deployment package
    3. Creates all necessary infrastructure files
    
    Output Location: output_package/[filename]_terraform/

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