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
                print("\nERROR: Conversion failed during JSON export")
                return None
                
        except Exception as e:
            print(f"\nERROR: Conversion failed: {e}")
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
        print(f"\nSUCCESS: Conversion completed successfully!")
        print(f"Output file: {result}")
        return True
    else:
        print(f"\nERROR: Conversion failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
