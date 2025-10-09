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
            print(f"SUCCESS: JSON conversion completed: {json_result}")
            
            # Step 2: Create data accessor
            print("\nStep 2: Creating data accessor...")
            accessor = ExcelDataAccessor(json_result)
            summary = accessor.get_summary()
            print(f"SUCCESS: Data accessor created - {summary['total_sheets']} sheets, {summary['total_tables']} tables")
            
            # Step 3: Generate Terraform files
            print(f"\nStep 3: Generating Terraform files in '{self.terraform_output_dir}'...")
            generator = EnhancedTerraformGenerator(json_result)
            terraform_files = generator.generate_terraform_files(self.terraform_output_dir)
            
            results['terraform_files'] = terraform_files
            print(f"SUCCESS: Terraform files generated: {len(terraform_files)} files")
            
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
            print(f"\nERROR: {error_msg}")
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
        print(f"\nSUCCESS: SUCCESS! Conversion completed successfully.")
        return True
    else:
        print(f"\nERROR: FAILED! Conversion did not complete successfully.")
        if results['errors']:
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
