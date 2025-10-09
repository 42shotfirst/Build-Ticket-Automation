import pandas as pd
import os
from typing import Dict, Any, Optional, List
import json
import warnings

def read_all_sheets_comprehensive(file_path: str) -> Dict[str, Any]:
    """
    Read ALL sheets from Excel file and extract ALL data comprehensively.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary containing data from all sheets
    """
    print(f"Reading all sheets from '{file_path}'...")
    
    if not os.path.exists(file_path):
        print(f"Error: Excel file not found: {file_path}")
        return {}
    
    all_data = {}
    
    try:
        # Suppress openpyxl warnings about extension styles
        warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
        
        # Read the Excel file and get all sheet names
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        sheet_names = excel_file.sheet_names
        
        print(f"Found {len(sheet_names)} sheets: {sheet_names}")
        
        for sheet_name in sheet_names:
            print(f"\nProcessing sheet: '{sheet_name}'")
            
            try:
                # Read the sheet with different strategies
                sheet_data = read_sheet_comprehensive(excel_file, sheet_name, file_path)
                if sheet_data:
                    all_data[sheet_name] = sheet_data
                    print(f"  ✓ Successfully processed '{sheet_name}' - {len(sheet_data)} data points")
                else:
                    print(f"  ⚠ '{sheet_name}' appears to be empty or unreadable")
                    
            except Exception as e:
                print(f"  ✗ Error reading sheet '{sheet_name}': {e}")
                continue
        
        excel_file.close()
        print(f"\n✓ Completed processing all sheets")
        return all_data
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {}

def read_sheet_comprehensive(excel_file, sheet_name: str, file_path: str) -> Dict[str, Any]:
    """
    Read a single sheet comprehensively with multiple strategies.
    
    Args:
        excel_file: pandas ExcelFile object
        sheet_name: Name of the sheet to read
        file_path: Path to the Excel file (for fallback reading)
        
    Returns:
        Dictionary containing all data from the sheet
    """
    sheet_data = {
        'sheet_info': {
            'name': sheet_name,
            'raw_data': [],
            'tables': [],
            'key_value_pairs': {},
            'calculated_values': {}
        }
    }
    
    try:
        # Strategy 1: Read entire sheet without headers to capture everything
        df_raw = pd.read_excel(
            excel_file, 
            sheet_name=sheet_name, 
            header=None,
            engine='openpyxl'
        )
        
        if not df_raw.empty:
            # Convert to records for JSON serialization
            raw_records = df_raw.fillna('').to_dict('records')
            sheet_data['sheet_info']['raw_data'] = raw_records
            sheet_data['sheet_info']['dimensions'] = {
                'rows': len(df_raw),
                'columns': len(df_raw.columns)
            }
            
            # Extract key-value pairs (look for patterns like "Label: Value")
            key_value_pairs = extract_key_value_pairs(df_raw)
            if key_value_pairs:
                sheet_data['sheet_info']['key_value_pairs'] = key_value_pairs
            
            # Try to detect and extract tables
            tables = detect_and_extract_tables(df_raw)
            if tables:
                sheet_data['sheet_info']['tables'] = tables
        
        # Strategy 2: Try reading with different header assumptions
        for header_row in [0, 1, 2, 5, 10, 15, 20]:
            try:
                df_with_header = pd.read_excel(
                    excel_file,
                    sheet_name=sheet_name,
                    header=header_row,
                    engine='openpyxl'
                )
                
                if not df_with_header.empty and len(df_with_header.columns) > 1:
                    table_data = {
                        'header_row': header_row,
                        'columns': list(df_with_header.columns),
                        'data': df_with_header.fillna('').to_dict('records')
                    }
                    
                    # Only add if it looks like a proper table (has meaningful column names)
                    if any(str(col).strip() and str(col) != 'Unnamed' in str(col) for col in df_with_header.columns):
                        sheet_data['sheet_info']['tables'].append(table_data)
                        
            except Exception:
                continue
        
        # Strategy 3: Extract calculated values (cells that might contain formulas)
        # Note: We can only get the calculated values, not the formulas themselves
        calculated_values = extract_calculated_values(df_raw)
        if calculated_values:
            sheet_data['sheet_info']['calculated_values'] = calculated_values
            
    except Exception as e:
        print(f"    Error in comprehensive reading: {e}")
    
    return sheet_data

def extract_key_value_pairs(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract key-value pairs from a DataFrame.
    Looks for patterns where column 0 contains keys and column 1 contains values.
    """
    key_value_pairs = {}
    
    if len(df.columns) < 2:
        return key_value_pairs
    
    for index, row in df.iterrows():
        key = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        value = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        
        # Clean up key (remove colons, extra spaces)
        key_clean = key.replace(':', '').strip()
        
        # Only add if both key and value are meaningful
        if (key_clean and value and 
            key_clean.lower() not in ['nan', 'none', ''] and 
            value.lower() not in ['nan', 'none', '']):
            key_value_pairs[key_clean] = value
    
    return key_value_pairs

def detect_and_extract_tables(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detect and extract tabular data from a DataFrame.
    """
    tables = []
    
    if df.empty:
        return tables
    
    # Look for rows that might be headers (contain multiple non-empty values)
    potential_header_rows = []
    
    for index, row in df.iterrows():
        non_empty_count = sum(1 for val in row if pd.notna(val) and str(val).strip())
        if non_empty_count >= 3:  # At least 3 columns with data
            potential_header_rows.append(index)
    
    # For each potential header, try to extract a table
    for header_idx in potential_header_rows:
        try:
            # Extract potential header
            header_row = df.iloc[header_idx]
            headers = [str(val).strip() for val in header_row if pd.notna(val) and str(val).strip()]
            
            if len(headers) >= 3:  # Valid table should have at least 3 columns
                # Extract data rows following the header
                data_rows = []
                for data_idx in range(header_idx + 1, min(header_idx + 50, len(df))):  # Look at next 50 rows max
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
                
                if data_rows:  # Only add if we found data
                    table = {
                        'header_row_index': int(header_idx),
                        'headers': headers,
                        'data': data_rows,
                        'row_count': len(data_rows)
                    }
                    tables.append(table)
                    
        except Exception:
            continue
    
    return tables

def extract_calculated_values(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract values that might be results of calculations or formulas.
    Since we can't access the formulas directly, we look for numeric patterns.
    """
    calculated_values = {}
    
    if df.empty:
        return calculated_values
    
    # Look for numeric values that might be calculated
    numeric_cells = []
    
    for row_idx in range(len(df)):
        for col_idx in range(len(df.columns)):
            cell_value = df.iloc[row_idx, col_idx]
            
            if pd.notna(cell_value):
                # Try to convert to numeric
                try:
                    numeric_value = pd.to_numeric(cell_value)
                    if not pd.isna(numeric_value):
                        # Look for context (label in adjacent cells)
                        context = find_cell_context(df, row_idx, col_idx)
                        
                        numeric_cells.append({
                            'position': f'{row_idx},{col_idx}',
                            'value': numeric_value,
                            'context': context,
                            'row': row_idx,
                            'column': col_idx
                        })
                except:
                    continue
    
    if numeric_cells:
        calculated_values['numeric_values'] = numeric_cells
    
    return calculated_values

def find_cell_context(df: pd.DataFrame, row_idx: int, col_idx: int) -> str:
    """
    Find contextual information for a cell by looking at adjacent cells.
    """
    context_parts = []
    
    # Check left cell (same row, previous column)
    if col_idx > 0:
        left_value = df.iloc[row_idx, col_idx - 1]
        if pd.notna(left_value) and str(left_value).strip():
            context_parts.append(f"Left: {str(left_value).strip()}")
    
    # Check cell above (previous row, same column)
    if row_idx > 0:
        above_value = df.iloc[row_idx - 1, col_idx]
        if pd.notna(above_value) and str(above_value).strip():
            context_parts.append(f"Above: {str(above_value).strip()}")
    
    # Check top-left cell for potential labels
    if row_idx > 0 and col_idx > 0:
        topleft_value = df.iloc[row_idx - 1, col_idx - 1]
        if pd.notna(topleft_value) and str(topleft_value).strip():
            context_parts.append(f"TopLeft: {str(topleft_value).strip()}")
    
    return " | ".join(context_parts) if context_parts else ""

def read_build_data() -> Optional[Dict[str, Any]]:
    """
    Enhanced version that reads all sheets and extracts comprehensive data.
    """
    import config
    
    print(f"Reading comprehensive data from '{config.EXCEL_FILE_PATH}'...")
    
    # Read all sheets comprehensively
    all_sheets_data = read_all_sheets_comprehensive(config.EXCEL_FILE_PATH)
    
    if not all_sheets_data:
        print("Failed to read any data from Excel file.")
        return None
    
    # Process the data to extract build information
    build_data = process_comprehensive_data(all_sheets_data)
    
    return build_data

def process_comprehensive_data(all_sheets_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process comprehensive sheet data to extract build information.
    """
    import config
    
    build_data = {
        'source_file_info': {
            'sheets_found': list(all_sheets_data.keys()),
            'total_sheets': len(all_sheets_data)
        },
        'raw_sheets_data': all_sheets_data  # Include all raw data
    }
    
    # Try to extract standard build data from known sheet patterns
    overview_data = {}
    vm_data = []
    
    # Look for Overview-like data in any sheet
    for sheet_name, sheet_data in all_sheets_data.items():
        sheet_info = sheet_data.get('sheet_info', {})
        
        # Extract key-value pairs (potential overview data)
        kv_pairs = sheet_info.get('key_value_pairs', {})
        if kv_pairs:
            overview_data.update(kv_pairs)
            print(f"Found {len(kv_pairs)} key-value pairs in sheet '{sheet_name}'")
        
        # Extract table data (potential VM data)
        tables = sheet_info.get('tables', [])
        for table in tables:
            table_data = table.get('data', [])
            if table_data:
                # Check if this looks like VM data (has hostname-like columns)
                headers = table.get('headers', [])
                if any(keyword in str(header).lower() for header in headers 
                       for keyword in ['host', 'vm', 'server', 'machine', 'instance']):
                    vm_data.extend(table_data)
                    print(f"Found {len(table_data)} VM entries in sheet '{sheet_name}'")
    
    # Map extracted data to standard fields
    field_mapping = config.EXCEL_TO_TERRAFORM_MAPPING
    
    for excel_field, terraform_field in field_mapping.items():
        if excel_field in overview_data:
            build_data[terraform_field] = overview_data[excel_field]
        elif terraform_field in config.DEFAULT_VALUES:
            build_data[terraform_field] = config.DEFAULT_VALUES[terraform_field]
    
    # Add VM instances
    build_data['vm_instances'] = vm_data
    
    # Ensure required fields
    for field in config.REQUIRED_OVERVIEW_FIELDS:
        if field not in build_data or not build_data[field]:
            if field in config.DEFAULT_VALUES:
                build_data[field] = config.DEFAULT_VALUES[field]
                print(f"Using default value for {field}: {build_data[field]}")
    
    print(f"\nProcessing Summary:")
    print(f"  Sheets processed: {len(all_sheets_data)}")
    print(f"  Key-value pairs found: {len(overview_data)}")
    print(f"  VM instances found: {len(vm_data)}")
    
    return build_data

def export_comprehensive_data(all_sheets_data: Dict[str, Any], output_file: str = "comprehensive_excel_data.json"):
    """
    Export all comprehensive data to a JSON file for review.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_sheets_data, f, indent=2, default=str)
        print(f"✓ Comprehensive data exported to: {output_file}")
        return True
    except Exception as e:
        print(f"Error exporting comprehensive data: {e}")
        return False

if __name__ == '__main__':
    """Test the comprehensive Excel reading functionality."""
    print("Testing Comprehensive Excel Data Reading...")
    print("=" * 60)
    
    import config
    
    # Read all data comprehensively
    all_data = read_all_sheets_comprehensive(config.EXCEL_FILE_PATH)
    
    if all_data:
        print(f"\n✓ Successfully read data from {len(all_data)} sheets")
        
        # Export comprehensive data for review
        export_comprehensive_data(all_data)
        
        # Process for build data
        build_data = process_comprehensive_data(all_data)
        
        print("\n" + "=" * 60)
        print("EXTRACTED BUILD DATA:")
        print("=" * 60)
        
        for key, value in build_data.items():
            if key == 'raw_sheets_data':
                print(f"{key}: [Raw data - {len(value)} sheets]")
            elif isinstance(value, list):
                print(f"{key}: [{len(value)} items]")
            elif isinstance(value, dict):
                print(f"{key}: {{{len(value)} keys}}")
            else:
                print(f"{key}: {value}")
        
        print("\n✓ Test completed successfully!")
        print("Review 'comprehensive_excel_data.json' for complete data extraction")
        
    else:
        print("\n✗ Failed to read Excel data")
        print("Check your Excel file format and configuration.")
        