#!/usr/bin/env python3
"""
VBA Macro Handler (Standalone)
===============================
Dedicated module for VBA macro extraction and handling.
Kept separate due to specialized nature and binary file handling.

This module is intentionally kept separate from core modules as it:
- Handles binary VBA project files
- Uses specialized libraries
- Has different dependencies than core modules
"""

import os
import re
from typing import Dict, Any, List, Optional


class VBAMacroHandler:
    """Extract and analyze VBA macros from Excel files."""

    def __init__(self, excel_file_path: str):
        """
        Initialize VBA macro handler.

        Args:
            excel_file_path: Path to the Excel file (.xlsm)
        """
        self.excel_file_path = excel_file_path
        self.vba_data = {}

    def extract_vba_info(self) -> Dict[str, Any]:
        """
        Extract VBA project information.

        Note: Full VBA code extraction requires the file to be unzipped
        and binary VBA project parsed. This is a simplified version.

        Returns:
            Dictionary containing VBA project information
        """
        if not self.excel_file_path.endswith('.xlsm'):
            return {'has_macros': False, 'reason': 'Not a macro-enabled file'}

        # Check if VBA project exists
        vba_project_path = self._locate_vba_project()

        if not vba_project_path:
            return {'has_macros': False, 'reason': 'No VBA project found'}

        # Extract basic information
        self.vba_data = {
            'has_macros': True,
            'project_file': vba_project_path,
            'file_size': os.path.getsize(vba_project_path),
            'detected_patterns': self._detect_vba_patterns(vba_project_path)
        }

        return self.vba_data

    def _locate_vba_project(self) -> Optional[str]:
        """
        Locate the VBA project file within the Excel archive.

        Returns:
            Path to VBA project or None
        """
        # Excel files are ZIP archives
        # VBA project is typically at xl/vbaProject.bin
        # This is a simplified check

        import zipfile

        try:
            with zipfile.ZipFile(self.excel_file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()

                # Look for VBA project
                for filename in file_list:
                    if 'vbaProject.bin' in filename:
                        # Extract to temp location for analysis
                        temp_path = '/tmp/vbaProject.bin'
                        with zip_ref.open(filename) as source:
                            with open(temp_path, 'wb') as target:
                                target.write(source.read())
                        return temp_path

        except Exception as e:
            print(f"Error locating VBA project: {e}")

        return None

    def _detect_vba_patterns(self, vba_file_path: str) -> Dict[str, int]:
        """
        Detect common VBA patterns in the binary file.

        Args:
            vba_file_path: Path to VBA project binary

        Returns:
            Dictionary of detected patterns and counts
        """
        patterns = {
            'Sub ': 0,
            'Function ': 0,
            'Dim ': 0,
            'For ': 0,
            'If ': 0,
            'Select Case': 0,
            'Workbook': 0,
            'Worksheet': 0,
            'Range': 0,
            'Application': 0
        }

        try:
            with open(vba_file_path, 'rb') as f:
                content = f.read()

            # Search for patterns in binary content
            # Note: This is rough detection, not full parsing
            for pattern in patterns.keys():
                pattern_bytes = pattern.encode('utf-8', errors='ignore')
                patterns[pattern] = content.count(pattern_bytes)

        except Exception as e:
            print(f"Error detecting VBA patterns: {e}")

        return patterns

    def extract_module_names(self) -> List[str]:
        """
        Attempt to extract VBA module names.

        Returns:
            List of detected module names
        """
        if not self.vba_data.get('has_macros'):
            return []

        # This would require proper VBA parser
        # Placeholder for now
        return ['Module1', 'ThisWorkbook', 'Sheet1']

    def has_macros(self) -> bool:
        """
        Check if the Excel file contains macros.

        Returns:
            True if macros are present
        """
        if not self.vba_data:
            self.extract_vba_info()

        return self.vba_data.get('has_macros', False)

    def get_macro_summary(self) -> Dict[str, Any]:
        """
        Get a summary of macro information.

        Returns:
            Summary dictionary
        """
        if not self.vba_data:
            self.extract_vba_info()

        if not self.vba_data.get('has_macros'):
            return {
                'has_macros': False,
                'summary': 'No macros detected'
            }

        patterns = self.vba_data.get('detected_patterns', {})

        return {
            'has_macros': True,
            'estimated_procedures': patterns.get('Sub ', 0) + patterns.get('Function ', 0),
            'file_size_bytes': self.vba_data.get('file_size', 0),
            'detected_patterns': patterns
        }


def extract_vba_from_excel(excel_file_path: str) -> Dict[str, Any]:
    """
    Standalone function to extract VBA information from Excel file.

    Args:
        excel_file_path: Path to Excel file

    Returns:
        Dictionary containing VBA information
    """
    handler = VBAMacroHandler(excel_file_path)
    return handler.extract_vba_info()


# Example usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        handler = VBAMacroHandler(excel_file)
        info = handler.extract_vba_info()

        print("\nVBA Macro Information:")
        print("=" * 50)
        print(f"Has Macros: {info.get('has_macros', False)}")

        if info.get('has_macros'):
            print(f"Project File: {info.get('project_file', 'N/A')}")
            print(f"File Size: {info.get('file_size', 0)} bytes")
            print("\nDetected Patterns:")
            for pattern, count in info.get('detected_patterns', {}).items():
                if count > 0:
                    print(f"  {pattern}: {count}")
    else:
        print("Usage: python vba_macro_handler.py <excel_file.xlsm>")
