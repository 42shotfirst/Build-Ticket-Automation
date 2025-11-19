#!/usr/bin/env python3
"""
Module 1: Excel Extractor
==========================
Consolidates Excel data extraction functionality.
Combines: comprehensive_excel_extractor.py
"""

import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional


class ExcelExtractor:
    """Extract all data from Excel files including sheets, formulas, and metadata."""

    def __init__(self, excel_file_path: str):
        """
        Initialize the Excel extractor.

        Args:
            excel_file_path: Path to the Excel file to extract
        """
        self.excel_file_path = excel_file_path
        self.workbook = None
        self.extraction_data = {}

    def extract(self) -> Dict[str, Any]:
        """
        Extract all data from the Excel file.

        Returns:
            Dictionary containing all extracted data
        """
        if not os.path.exists(self.excel_file_path):
            raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")

        # Load workbook
        self.workbook = pd.ExcelFile(self.excel_file_path)

        # Extract metadata
        self.extraction_data['metadata'] = self._extract_metadata()

        # Extract sheets
        self.extraction_data['sheets'] = self._extract_all_sheets()

        # Extract formulas
        self.extraction_data['formulas'] = self._extract_formulas()

        return self.extraction_data

    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract workbook metadata."""
        return {
            'filename': os.path.basename(self.excel_file_path),
            'sheet_names': self.workbook.sheet_names,
            'sheet_count': len(self.workbook.sheet_names),
            'extraction_timestamp': datetime.now().isoformat(),
            'file_size_bytes': os.path.getsize(self.excel_file_path)
        }

    def _extract_all_sheets(self) -> Dict[str, Any]:
        """Extract data from all sheets."""
        sheets_data = {}

        for sheet_name in self.workbook.sheet_names:
            try:
                df = pd.read_excel(
                    self.excel_file_path,
                    sheet_name=sheet_name,
                    header=None
                )

                sheets_data[sheet_name] = {
                    'name': sheet_name,
                    'raw_data': df.to_dict('records'),
                    'dimensions': {
                        'rows': len(df),
                        'columns': len(df.columns)
                    }
                }
            except Exception as e:
                sheets_data[sheet_name] = {
                    'name': sheet_name,
                    'error': str(e)
                }

        return sheets_data

    def _extract_formulas(self) -> Dict[str, List]:
        """Extract formulas from the workbook."""
        # This is a placeholder for formula extraction
        # Full implementation would use openpyxl for formula access
        return {}

    def save_to_json(self, output_path: str):
        """
        Save extracted data to JSON file.

        Args:
            output_path: Path to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.extraction_data, f, indent=2, default=str)
