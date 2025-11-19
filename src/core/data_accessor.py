#!/usr/bin/env python3
"""
Module 2: Data Accessor
========================
Provides easy access to extracted Excel data with keyword search capabilities.
Consolidates: data_accessor.py, excel_data_mapper.py
"""

import json
from typing import Dict, Any, List, Optional, Union
import pandas as pd


class DataAccessor:
    """Access and query extracted Excel data."""

    def __init__(self, json_file_path: str):
        """
        Initialize the data accessor.

        Args:
            json_file_path: Path to the extracted JSON data
        """
        self.json_file_path = json_file_path
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Load the JSON data."""
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_sheet_data(self, sheet_name: str) -> Optional[Dict]:
        """Get data from a specific sheet."""
        sheets = self.data.get('sheets', {})
        return sheets.get(sheet_name)

    def get_value_by_keywords(
        self,
        sheet_name: str,
        keywords: List[str]
    ) -> Optional[Any]:
        """
        Find a value using keywords.

        Args:
            sheet_name: Name of the sheet to search
            keywords: List of keywords to match

        Returns:
            The found value or None
        """
        sheet_data = self.get_sheet_data(sheet_name)
        if not sheet_data:
            return None

        raw_data = sheet_data.get('raw_data', [])

        # Search through rows for matching keywords
        for row in raw_data:
            for col_key, col_value in row.items():
                if col_value and isinstance(col_value, str):
                    if any(keyword.lower() in col_value.lower() for keyword in keywords):
                        # Get the next column value (typical key-value pattern)
                        next_col = str(int(col_key) + 1)
                        if next_col in row:
                            return row[next_col]

        return None

    def get_column_data(
        self,
        sheet_name: str,
        column_header: str,
        table_index: int = 0
    ) -> List[Any]:
        """
        Get all values from a column by header name.

        Args:
            sheet_name: Name of the sheet
            column_header: Header text to search for
            table_index: Which table to use if multiple exist

        Returns:
            List of column values
        """
        sheet_data = self.get_sheet_data(sheet_name)
        if not sheet_data:
            return []

        raw_data = sheet_data.get('raw_data', [])

        # Find the header row
        header_row = None
        header_col = None

        for idx, row in enumerate(raw_data):
            for col_key, col_value in row.items():
                if col_value and isinstance(col_value, str):
                    if column_header.lower() in col_value.lower():
                        header_row = idx
                        header_col = col_key
                        break
            if header_row is not None:
                break

        if header_row is None or header_col is None:
            return []

        # Extract column data
        column_data = []
        for row in raw_data[header_row + 1:]:
            if header_col in row:
                value = row[header_col]
                if value is not None and value != '':
                    column_data.append(value)
                else:
                    break  # Stop at first empty cell

        return column_data

    def search_across_sheets(self, search_term: str) -> Dict[str, List]:
        """
        Search for a term across all sheets.

        Args:
            search_term: Term to search for

        Returns:
            Dictionary of sheet names and matching locations
        """
        results = {}

        sheets = self.data.get('sheets', {})
        for sheet_name, sheet_data in sheets.items():
            matches = []
            raw_data = sheet_data.get('raw_data', [])

            for row_idx, row in enumerate(raw_data):
                for col_key, col_value in row.items():
                    if col_value and isinstance(col_value, str):
                        if search_term.lower() in col_value.lower():
                            matches.append({
                                'row': row_idx,
                                'column': col_key,
                                'value': col_value
                            })

            if matches:
                results[sheet_name] = matches

        return results

    def get_terraform_ready_data(self) -> Dict[str, Any]:
        """
        Get data formatted for Terraform generation.

        Returns:
            Dictionary ready for Terraform generation
        """
        return {
            'comprehensive_data': self.data.get('sheets', {}),
            'metadata': self.data.get('metadata', {})
        }
