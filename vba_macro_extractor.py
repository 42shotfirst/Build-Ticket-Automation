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
