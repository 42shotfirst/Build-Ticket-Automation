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
        # Extract source Excel filename for auto-detection
        self.source_filename = self.data.get('metadata', {}).get('filename', '')
        
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
    
    def _extract_actual_values_from_tables(self, sheet_name: str, value_column_index: int = 1) -> Dict[str, str]:
        """Extract actual values from tables instead of variable references.

        Args:
            sheet_name: Name of the sheet to extract from
            value_column_index: Which column contains the actual value (0-indexed after field name)
                               1 = second column (default for Resources)
                               2 = third column (for Build_ENV)
        """
        actual_values = {}
        sheet_data = self.sheets.get(sheet_name, {})
        tables = sheet_data.get('tables', [])

        # List of HEADER values to skip (not data values)
        skip_headers = {
            'Terraform Variable', 'SNOW form', 'Validation', 'Column', 'Existing',
            'MUST BE A NUMBER', 'SNOW team after request is complete?', 'Field Name',
            'Variable Name', 'Parameter'
        }

        # List of VALUES to skip (placeholders)
        skip_values = {
            'User', 'EA', 'User/EA', 'User/CMDB', 'CMDB', 'CMDB?', 'CMDB APP NAME',
            'Overview', 'Value', 'TBD', 'N/A', 'NA', 'To Be Determined'
        }

        for table in tables:
            data = table.get('data', [])
            headers = table.get('headers', [])

            # Try to find the value column by looking for patterns in headers
            detected_value_column = value_column_index

            # Look for columns named 'Value', 'Actual', 'Data', etc.
            value_column_keywords = ['value', 'actual', 'data', 'current', 'setting']
            for idx, header in enumerate(headers):
                header_lower = str(header).lower()
                if any(keyword in header_lower for keyword in value_column_keywords):
                    # Don't use column 0 (usually field name)
                    if idx > 0:
                        detected_value_column = idx
                        break

            for row in data:
                # Look for the pattern where the first column is a field name
                row_items = list(row.items())

                # Need at least detected_value_column + 1 columns
                if len(row_items) >= detected_value_column + 1:
                    field_name = str(row_items[0][1])  # First column is field name
                    field_value = str(row_items[detected_value_column][1])  # Value at detected index

                    # Skip if it's a header row or empty
                    if not field_name or not field_value or not str(field_value).strip():
                        continue

                    # Skip if field name is a known header
                    if field_name in skip_headers:
                        continue

                    # Skip if value is a placeholder
                    if field_value in skip_values:
                        continue

                    # Skip if value starts with internal references
                    if field_value.startswith('wab:') or field_value.startswith('vm_list'):
                        continue

                    # Skip numeric-only placeholders
                    if field_value.strip() in ['0', '1', '2', '3', '4', '5']:
                        continue

                    # Accept the value if it has substantial content
                    if len(str(field_value).strip()) > 1:
                        actual_values[field_name] = field_value

        return actual_values
    
    def _resolve_variable_reference(self, value: str, sheet_name: str = 'Resources') -> str:
        """Resolve wab: prefixed variables to actual values."""
        if not value or not str(value).startswith('wab:'):
            return value
        
        # Get actual values from tables
        actual_values = self._extract_actual_values_from_tables(sheet_name)
        
        # Try to find a matching value
        var_name = str(value).replace('wab:', '').replace('-', ' ')
        
        # Look for exact match first
        for key, val in actual_values.items():
            if var_name.lower() in key.lower():
                return val
        
        # Look for partial matches
        for key, val in actual_values.items():
            if any(word in key.lower() for word in var_name.split()):
                return val
        
        return value  # Return original if no match found

    def _map_nsg_generic_columns(self, headers: List[str], data: List[Dict]) -> List[str]:
        """Map generic Column_N names to proper NSG field names.

        Analyzes column content and position to determine the actual field names.
        Expected NSG fields: name, priority, direction, access, protocol,
        source_port_range, destination_port_ranges, source_asg, destination_asg, description
        """
        mapped_headers = headers.copy()

        # NSG field patterns to detect by content
        field_patterns = {
            'direction': ['inbound', 'outbound', 'in', 'out'],
            'access': ['allow', 'deny'],
            'protocol': ['tcp', 'udp', 'icmp', 'any', '*'],
            'priority': ['100', '110', '120', '200', '300', '400', '500'],  # Common priority values
        }

        # Analyze first few rows to detect patterns
        sample_size = min(5, len(data))
        sample_data = data[:sample_size] if data else []

        for col_idx, header in enumerate(headers):
            if not header.startswith('Column_'):
                continue  # Already has a proper name

            # Collect values from this column
            column_values = []
            for row in sample_data:
                value = row.get(header, '')
                if value:
                    column_values.append(str(value).lower().strip())

            # Try to detect field by content
            detected_field = None

            # Check each field pattern
            for field_name, patterns in field_patterns.items():
                matches = sum(1 for val in column_values if any(p in val for p in patterns))
                if matches >= len(column_values) * 0.5:  # 50% or more match
                    detected_field = field_name
                    break

            # Positional detection (common NSG table layouts)
            if not detected_field:
                # Common positions: name(0), priority(1), direction(2), access(3), protocol(4)
                position_map = {
                    0: 'name',
                    1: 'priority',
                    2: 'direction',
                    3: 'access',
                    4: 'protocol',
                    5: 'source_port_range',
                    6: 'destination_port_ranges',
                    7: 'source_address_prefix',
                    8: 'destination_address_prefix',
                    9: 'source_asg',
                    10: 'destination_asg',
                    11: 'description'
                }

                if col_idx in position_map:
                    detected_field = position_map[col_idx]

            if detected_field:
                mapped_headers[col_idx] = detected_field
                print(f"    Mapped {header} -> {detected_field}")

        return mapped_headers

    def _remap_table_data(self, data: List[Dict], old_headers: List[str], new_headers: List[str]) -> List[Dict]:
        """Remap table data dictionaries from old headers to new headers."""
        if not data or len(old_headers) != len(new_headers):
            return data

        remapped_data = []
        for row in data:
            new_row = {}
            for old_h, new_h in zip(old_headers, new_headers):
                if old_h in row:
                    new_row[new_h] = row[old_h]
            if new_row:  # Only add if there's data
                remapped_data.append(new_row)

        return remapped_data

    def _standardize_nsg_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize NSG rule field names to common naming convention.

        Maps various Excel column names to standard Terraform NSG field names.
        """
        standardized = {}

        # Field name mapping patterns (Excel name patterns -> standard name)
        field_mappings = {
            # Rule name
            'name': ['name', 'rule name', 'rule_name', 'security rule', 'rule'],
            # Priority
            'priority': ['priority', 'pri', 'order', 'precedence'],
            # Direction
            'direction': ['direction', 'dir', 'flow direction'],
            # Access
            'access': ['access', 'action', 'allow/deny'],
            # Protocol
            'protocol': ['protocol', 'proto', 'ip protocol'],
            # Source port
            'source_port_range': ['source port', 'source_port', 'source port range', 'source_port_range', 'src port', 'src_port'],
            # Destination port
            'destination_port_ranges': ['destination port', 'dest port', 'destination_port', 'dest_port',
                                       'destination port range', 'destination_port_range', 'destination_port_ranges',
                                       'dst port', 'dst_port'],
            # Source address
            'source_address_prefix': ['source', 'source address', 'source_address', 'source_address_prefix',
                                     'src address', 'src_address', 'source ip', 'src ip'],
            # Destination address
            'destination_address_prefix': ['destination', 'dest address', 'destination_address', 'destination_address_prefix',
                                          'dst address', 'dst_address', 'destination ip', 'dest ip', 'dst ip'],
            # Source ASG
            'source_asg': ['source asg', 'source_asg', 'src asg', 'source application security group'],
            # Destination ASG
            'destination_asg': ['destination asg', 'destination_asg', 'dest asg', 'dst asg',
                               'destination application security group'],
            # Description
            'description': ['description', 'desc', 'notes', 'comment', 'purpose'],
        }

        # Map each field in the rule
        for rule_key, rule_value in rule.items():
            rule_key_lower = rule_key.lower().strip()
            mapped = False

            # Try to find a matching standard field
            for standard_field, patterns in field_mappings.items():
                for pattern in patterns:
                    if pattern in rule_key_lower or rule_key_lower == pattern:
                        # Don't overwrite if already set with a better value
                        if standard_field not in standardized or not standardized[standard_field]:
                            standardized[standard_field] = rule_value
                        mapped = True
                        break
                if mapped:
                    break

            # If no mapping found, keep original key (cleaned)
            if not mapped and rule_value:
                clean_key = rule_key.lower().replace(' ', '_').replace('-', '_')
                standardized[clean_key] = rule_value

        return standardized

    def _is_valid_nsg_rule(self, rule: Dict[str, Any]) -> bool:
        """Check if an NSG rule has minimum required fields to be valid.

        Returns:
            True if rule has at least name or priority, False otherwise
        """
        if not rule:
            return False

        # Check for instruction text in values
        instruction_phrases = [
            'to add', 'click here', 'example', 'sample', 'instructions',
            'open this', 'hit the button', 'add more'
        ]

        for value in rule.values():
            value_str = str(value).lower()
            if any(phrase in value_str for phrase in instruction_phrases):
                return False

        # Must have at least a name or priority to be considered valid
        has_name = rule.get('name') and str(rule.get('name')).strip() not in ['', 'None', 'N/A', 'TBD']
        has_priority = rule.get('priority') and str(rule.get('priority')).strip() not in ['', 'None', 'N/A', 'TBD']

        # Count how many standard fields have values
        standard_fields = ['direction', 'access', 'protocol', 'source_port_range', 'destination_port_ranges']
        filled_fields = sum(1 for field in standard_fields
                          if rule.get(field) and str(rule.get(field)).strip() not in ['', 'None', 'N/A', 'TBD'])

        # Valid if has name/priority AND at least 2 other fields
        return (has_name or has_priority) and filled_fields >= 2

    def _standardize_vm_fields(self, vm_instance: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize VM field names to common naming convention.

        Maps various Excel column names to standard Terraform field names.
        """
        standardized = {}

        # Field name mapping patterns (Excel name patterns -> standard name)
        field_mappings = {
            # Hostname/Name patterns
            'hostname': ['hostname', 'host name', 'vm name', 'server name', 'name', 'vm_name'],
            # SKU/Size patterns
            'vm_size': ['recommended sku', 'sku', 'vm size', 'size', 'vm_size', 'instance type'],
            # Owner patterns
            'owner': ['owner', 'server owner', 'vm owner', 'responsible'],
            # OS patterns
            'os_type': ['os', 'operating system', 'os type', 'platform'],
            'os_image': ['os image', 'image', 'os_image', 'template'],
            # Disk patterns
            'data_disk': ['data disk', 'data_disk', 'disk', 'additional disk', 'extra disk'],
            'disk_size': ['disk size', 'disk_size', 'storage'],
            # Network patterns
            'subnet': ['subnet', 'network', 'vnet', 'virtual network'],
            'ip_address': ['ip', 'ip address', 'ip_address', 'private ip'],
            # Zone/Location patterns
            'availability_zone': ['zone', 'availability zone', 'az', 'availability_zone'],
            # Role/Purpose patterns
            'role': ['role', 'purpose', 'function', 'tier'],
            # Patch settings
            'patch_optin': ['patch optin', 'patch', 'patching', 'patch_optin'],
        }

        # Map each field in the VM instance
        for vm_key, vm_value in vm_instance.items():
            vm_key_lower = vm_key.lower().strip()
            mapped = False

            # Try to find a matching standard field
            for standard_field, patterns in field_mappings.items():
                for pattern in patterns:
                    if pattern in vm_key_lower:
                        standardized[standard_field] = vm_value
                        mapped = True
                        break
                if mapped:
                    break

            # If no mapping found, keep original key (cleaned)
            if not mapped and vm_value:
                # Clean the key name
                clean_key = vm_key.lower().replace(' ', '_').replace('-', '_')
                standardized[clean_key] = vm_value

        return standardized

    def _auto_detect_environment(self, terraform_data: Dict[str, Any]) -> Optional[str]:
        """Auto-detect environment from filename, sheet names, or data.

        Returns detected environment or None if not found.
        """
        import re

        # Environment keywords in priority order
        env_patterns = {
            'prod': ['prod', 'production', 'prd'],
            'dr': ['dr', 'disaster', 'recovery', 'disaster recovery'],
            'uat': ['uat', 'user acceptance', 'test'],
            'dev': ['dev', 'development', 'dvlp'],
            'qa': ['qa', 'quality', 'qas'],
            'stg': ['stg', 'staging', 'stage'],
            'sbx': ['sbx', 'sandbox', 'sand'],
        }

        # 0. Check Build_ENV extracted values first (highest priority)
        build_env = terraform_data.get('build_environment', {}).get('key_value_pairs', {})
        for key, value in build_env.items():
            key_lower = key.lower()
            value_lower = str(value).lower()

            # Direct environment field
            if 'environment' in key_lower or 'env' in key_lower:
                # Check if value matches known environments
                for env, patterns in env_patterns.items():
                    for pattern in patterns:
                        if pattern in value_lower or value_lower == env:
                            print(f"  Auto-detected environment '{env}' from Build_ENV/{key}: {value}")
                            return env

        # 1. Check filename
        filename = self.source_filename.lower()
        for env, patterns in env_patterns.items():
            for pattern in patterns:
                if pattern in filename:
                    print(f"  Auto-detected environment '{env}' from filename: {self.source_filename}")
                    return env

        # 2. Check sheet names
        for sheet_name in self.get_sheet_names():
            sheet_lower = sheet_name.lower()
            for env, patterns in env_patterns.items():
                for pattern in patterns:
                    if pattern in sheet_lower:
                        print(f"  Auto-detected environment '{env}' from sheet name: {sheet_name}")
                        return env

        # 3. Check Build_ENV data
        build_env = terraform_data.get('all_key_value_pairs', {}).get('Build_ENV', {})
        for key, value in build_env.items():
            key_lower = key.lower()
            value_lower = str(value).lower()

            # Look for environment-related keys
            if any(term in key_lower for term in ['environment', 'env', 'tier']):
                for env, patterns in env_patterns.items():
                    for pattern in patterns:
                        if pattern in value_lower:
                            print(f"  Auto-detected environment '{env}' from {key}: {value}")
                            return env

        # 4. Check Resources data
        resources = terraform_data.get('all_key_value_pairs', {}).get('Resources', {})
        for key, value in resources.items():
            value_lower = str(value).lower()
            for env, patterns in env_patterns.items():
                for pattern in patterns:
                    if pattern in value_lower and any(term in key.lower() for term in ['environment', 'env']):
                        print(f"  Auto-detected environment '{env}' from Resources/{key}: {value}")
                        return env

        print("  Could not auto-detect environment")
        return None

    def _auto_detect_service_now_ticket(self, terraform_data: Dict[str, Any]) -> Optional[str]:
        """Auto-detect Service Now ticket from filename or data.

        Returns detected ticket number or None if not found.
        """
        import re

        # ServiceNow ticket patterns
        ticket_patterns = [
            r'(INC\d{7,})',      # Incident: INC0012345
            r'(RITM\d{7,})',     # Request Item: RITM0012345
            r'(REQ\d{7,})',      # Request: REQ0012345
            r'(CHG\d{7,})',      # Change: CHG0012345
            r'(TASK\d{7,})',     # Task: TASK0012345
            r'(CTASK\d{7,})',    # Change Task: CTASK0012345
            r'(PRB\d{7,})',      # Problem: PRB0012345
        ]

        # 0. Check Build_ENV extracted values first (highest priority)
        build_env = terraform_data.get('build_environment', {}).get('key_value_pairs', {})
        for key, value in build_env.items():
            key_lower = key.lower()
            value_upper = str(value).upper()

            # Direct ticket field
            if any(term in key_lower for term in ['ticket', 'snow', 'service now', 'ritm', 'inc', 'req', 'chg']):
                for pattern in ticket_patterns:
                    match = re.search(pattern, value_upper)
                    if match:
                        ticket = match.group(1)
                        print(f"  Auto-detected Service Now ticket '{ticket}' from Build_ENV/{key}: {value}")
                        return ticket

        # 1. Check filename
        filename = self.source_filename.upper()
        for pattern in ticket_patterns:
            match = re.search(pattern, filename)
            if match:
                ticket = match.group(1)
                print(f"  Auto-detected Service Now ticket '{ticket}' from filename: {self.source_filename}")
                return ticket

        # 2. Check Build_ENV data
        build_env = terraform_data.get('all_key_value_pairs', {}).get('Build_ENV', {})
        for key, value in build_env.items():
            key_lower = key.lower()
            value_upper = str(value).upper()

            # Look for ticket-related keys
            if any(term in key_lower for term in ['ticket', 'snow', 'service now', 'incident', 'request', 'change']):
                for pattern in ticket_patterns:
                    match = re.search(pattern, value_upper)
                    if match:
                        ticket = match.group(1)
                        print(f"  Auto-detected Service Now ticket '{ticket}' from {key}: {value}")
                        return ticket

        # 3. Check Resources data
        resources = terraform_data.get('all_key_value_pairs', {}).get('Resources', {})
        for key, value in resources.items():
            value_upper = str(value).upper()
            if any(term in key.lower() for term in ['ticket', 'snow', 'service now']):
                for pattern in ticket_patterns:
                    match = re.search(pattern, value_upper)
                    if match:
                        ticket = match.group(1)
                        print(f"  Auto-detected Service Now ticket '{ticket}' from Resources/{key}: {value}")
                        return ticket

        # 4. Scan all key-value pairs across all sheets
        all_kv = terraform_data.get('all_key_value_pairs', {})
        for sheet_name, kv_pairs in all_kv.items():
            for key, value in kv_pairs.items():
                value_upper = str(value).upper()
                for pattern in ticket_patterns:
                    match = re.search(pattern, value_upper)
                    if match:
                        ticket = match.group(1)
                        print(f"  Auto-detected Service Now ticket '{ticket}' from {sheet_name}/{key}: {value}")
                        return ticket

        print("  Could not auto-detect Service Now ticket")
        return None

    def _auto_detect_location(self, terraform_data: Dict[str, Any]) -> Optional[str]:
        """Auto-detect Azure location from filename or data.

        Returns detected location or None if not found.
        """
        # Common Azure locations
        location_patterns = {
            'eastus': ['east us', 'eastus', 'us east', 'useast'],
            'eastus2': ['east us 2', 'eastus2', 'us east 2'],
            'westus': ['west us', 'westus', 'us west', 'uswest'],
            'westus2': ['west us 2', 'westus2', 'us west 2'],
            'westus3': ['west us 3', 'westus3', 'us west 3'],
            'centralus': ['central us', 'centralus', 'us central'],
            'northcentralus': ['north central us', 'northcentralus'],
            'southcentralus': ['south central us', 'southcentralus'],
            'westcentralus': ['west central us', 'westcentralus'],
            'northeurope': ['north europe', 'northeurope', 'europe north'],
            'westeurope': ['west europe', 'westeurope', 'europe west'],
            'uksouth': ['uk south', 'uksouth', 'south uk'],
            'ukwest': ['uk west', 'ukwest', 'west uk'],
            'southeastasia': ['southeast asia', 'southeastasia', 'asia southeast'],
            'eastasia': ['east asia', 'eastasia', 'asia east'],
        }

        # 1. Check Build_ENV values
        build_env = terraform_data.get('build_environment', {}).get('key_value_pairs', {})
        for key, value in build_env.items():
            key_lower = key.lower()
            value_lower = str(value).lower()

            if any(term in key_lower for term in ['location', 'region', 'azure region']):
                for location, patterns in location_patterns.items():
                    for pattern in patterns:
                        if pattern in value_lower:
                            print(f"  Auto-detected location '{location}' from Build_ENV/{key}: {value}")
                            return location

        # 2. Check all key-value pairs
        all_kv = terraform_data.get('all_key_value_pairs', {})
        for sheet_name, kv_pairs in all_kv.items():
            for key, value in kv_pairs.items():
                key_lower = key.lower()
                value_lower = str(value).lower()

                if any(term in key_lower for term in ['location', 'region', 'azure location']):
                    for location, patterns in location_patterns.items():
                        for pattern in patterns:
                            if pattern in value_lower:
                                print(f"  Auto-detected location '{location}' from {sheet_name}/{key}: {value}")
                                return location

        # 3. Check filename
        filename_lower = self.source_filename.lower()
        for location, patterns in location_patterns.items():
            for pattern in patterns:
                if pattern in filename_lower:
                    print(f"  Auto-detected location '{location}' from filename: {self.source_filename}")
                    return location

        print("  Could not auto-detect location")
        return None

    def _auto_detect_subscription(self, terraform_data: Dict[str, Any]) -> Optional[str]:
        """Auto-detect Azure subscription from data.

        Returns detected subscription or None if not found.
        """
        import re

        # Subscription ID pattern (GUID format)
        subscription_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

        # 1. Check Build_ENV values
        build_env = terraform_data.get('build_environment', {}).get('key_value_pairs', {})
        for key, value in build_env.items():
            key_lower = key.lower()

            if any(term in key_lower for term in ['subscription', 'sub', 'azure subscription']):
                value_str = str(value)
                # Check if it's a GUID
                match = re.search(subscription_pattern, value_str, re.IGNORECASE)
                if match:
                    sub_id = match.group(0).lower()
                    print(f"  Auto-detected subscription ID from Build_ENV/{key}: {sub_id}")
                    return sub_id
                # Could also be subscription name
                if value_str and value_str.strip() not in ['', 'None', 'N/A', 'TBD']:
                    print(f"  Auto-detected subscription name from Build_ENV/{key}: {value_str}")
                    return value_str

        # 2. Check all key-value pairs
        all_kv = terraform_data.get('all_key_value_pairs', {})
        for sheet_name, kv_pairs in all_kv.items():
            for key, value in kv_pairs.items():
                key_lower = key.lower()

                if any(term in key_lower for term in ['subscription', 'sub id', 'subscription id']):
                    value_str = str(value)
                    # Check if it's a GUID
                    match = re.search(subscription_pattern, value_str, re.IGNORECASE)
                    if match:
                        sub_id = match.group(0).lower()
                        print(f"  Auto-detected subscription ID from {sheet_name}/{key}: {sub_id}")
                        return sub_id
                    # Could also be subscription name
                    if value_str and value_str.strip() not in ['', 'None', 'N/A', 'TBD']:
                        print(f"  Auto-detected subscription name from {sheet_name}/{key}: {value_str}")
                        return value_str

        print("  Could not auto-detect subscription")
        return None

    def _auto_detect_application_name(self, terraform_data: Dict[str, Any]) -> Optional[str]:
        """Auto-detect application name from filename or data.

        Returns detected application name or None if not found.
        """
        # 1. Check Build_ENV values
        build_env = terraform_data.get('build_environment', {}).get('key_value_pairs', {})
        for key, value in build_env.items():
            key_lower = key.lower()

            if any(term in key_lower for term in ['application', 'app name', 'application name', 'project']):
                value_str = str(value).strip()
                if value_str and value_str not in ['', 'None', 'N/A', 'TBD']:
                    print(f"  Auto-detected application name from Build_ENV/{key}: {value_str}")
                    return value_str

        # 2. Check all key-value pairs
        all_kv = terraform_data.get('all_key_value_pairs', {})
        for sheet_name, kv_pairs in all_kv.items():
            for key, value in kv_pairs.items():
                key_lower = key.lower()

                if any(term in key_lower for term in ['application name', 'app name', 'project name']):
                    value_str = str(value).strip()
                    if value_str and value_str not in ['', 'None', 'N/A', 'TBD']:
                        print(f"  Auto-detected application name from {sheet_name}/{key}: {value_str}")
                        return value_str

        # 3. Extract from filename (remove extension and clean)
        if self.source_filename:
            # Remove extension
            name_without_ext = self.source_filename.rsplit('.', 1)[0]
            # Remove common suffixes
            for suffix in [' DR', ' PROD', ' UAT', ' DEV', ' QA', ' STG', '_DR', '_PROD', '_UAT', '_DEV']:
                if name_without_ext.upper().endswith(suffix):
                    name_without_ext = name_without_ext[:-len(suffix)]

            # Clean and use as app name
            app_name = name_without_ext.strip()
            if app_name and len(app_name) > 3:  # Must be meaningful length
                print(f"  Auto-detected application name from filename: {app_name}")
                return app_name

        print("  Could not auto-detect application name")
        return None

    def _extract_vms_from_vertical_format(self, terraform_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract VMs from vertical key-value format (Resources sheet).

        This handles Excel sheets where VM data is structured as:
        Row N:   Virtual Machine | Value
        Row N+1: Key             | vm1
        Row N+2: SKU             | Standard_D2s_v3
        etc.
        """
        vm_instances = []

        # Check Resources sheet raw data
        resources_data = terraform_data.get('comprehensive_data', {}).get('Resources', {})
        raw_data = resources_data.get('raw_data', [])

        if not raw_data:
            return vm_instances

        print("  Searching for VM data in vertical key-value format...")

        # Find sections starting with "Virtual Machine"
        i = 0
        while i < len(raw_data):
            row = raw_data[i]
            if isinstance(row, dict):
                # Check if this row marks start of a VM section
                first_col = str(row.get('0', '')).strip()
                value_col = str(row.get('2', '')).strip()

                if 'virtual machine' in first_col.lower() and value_col.lower() in ['value', '']:
                    # Found VM section start, extract VM data
                    vm_data = {}
                    i += 1  # Move to next row

                    # Extract VM fields until we hit an empty row or new section
                    while i < len(raw_data):
                        data_row = raw_data[i]
                        if not isinstance(data_row, dict):
                            i += 1
                            continue

                        field_name = str(data_row.get('0', '')).strip()
                        field_value = str(data_row.get('2', '')).strip()

                        # Stop if we hit empty row or new section
                        if not field_name or any(marker in field_name.lower() for marker in
                            ['data disk', 'storage account', 'network', 'subnet', 'load balancer']):
                            break

                        # Skip header rows
                        if field_value.lower() in ['value', 'existing', 'validation']:
                            i += 1
                            continue

                        # Store the field
                        if field_name and field_value:
                            vm_data[field_name] = field_value

                        i += 1

                    # If we collected VM data, add it
                    if vm_data and len(vm_data) >= 3:  # Must have at least 3 fields
                        # Standardize the VM fields
                        standardized_vm = self._standardize_vm_fields(vm_data)
                        if standardized_vm:
                            vm_instances.append(standardized_vm)
                            print(f"    Found VM: {standardized_vm.get('hostname', standardized_vm.get('key', 'unknown'))}")
                    continue

            i += 1

        return vm_instances

    def get_terraform_ready_data(self) -> Dict[str, Any]:
        """Extract data in a format ready for Terraform generation."""
        terraform_data = {
            'project_info': {},
            'vm_instances': [],
            'networking': {},
            'security_groups': [],
            'application_gateway': {},
            'container_registry': {},
            'resource_options': {},
            'comprehensive_data': {},  # Store ALL extracted data
            'all_tables': {},  # Store all tables from all sheets
            'all_key_value_pairs': {}  # Store all key-value pairs from all sheets
        }
        
        # COMPREHENSIVE DATA EXTRACTION - Extract ALL data from ALL sheets
        print("COMPREHENSIVE DATA EXTRACTION")
        print("=" * 50)
        
        # Extract ALL data from ALL sheets
        for sheet_name, sheet_data in self.sheets.items():
            print(f"Processing sheet: {sheet_name}")
            
            # Store all tables from this sheet
            tables = sheet_data.get('tables', [])
            terraform_data['all_tables'][sheet_name] = tables
            print(f"  Found {len(tables)} tables")
            
            # Store all key-value pairs from this sheet
            kv_pairs = sheet_data.get('key_value_pairs', {})
            terraform_data['all_key_value_pairs'][sheet_name] = kv_pairs
            print(f"  Found {len(kv_pairs)} key-value pairs")
            
            # Store comprehensive data structure
            terraform_data['comprehensive_data'][sheet_name] = {
                'tables': tables,
                'key_value_pairs': kv_pairs,
                'dimensions': sheet_data.get('dimensions', {}),
                'raw_data': sheet_data.get('raw_data', [])
            }
        
        print(f"Total sheets processed: {len(self.sheets)}")
        print(f"Total tables across all sheets: {sum(len(tables) for tables in terraform_data['all_tables'].values())}")
        print(f"Total key-value pairs across all sheets: {sum(len(kv) for kv in terraform_data['all_key_value_pairs'].values())}")
        print()
        
        # Extract project information from Resources sheet
        resources_sheet = self.sheets.get('Resources', {})
        key_value_pairs = resources_sheet.get('key_value_pairs', {})
        
        # Extract actual values from tables instead of key-value pairs
        # For Resources sheet, values are in column 2 (index 1)
        actual_values = self._extract_actual_values_from_tables('Resources', value_column_index=1)
        
        print(f"  Extracted {len(actual_values)} actual values from Resources tables")
        
        # Map actual values to project info
        project_mapping = {
            'project name': 'project_name',
            'abbreviated app name': 'application_name',
            'application description': 'app_description',
            'cag architect': 'architect',
            'server owner': 'server_owner',
            'application owner': 'app_owner',
            'business owner': 'business_owner',
            'service now ticket': 'service_now_ticket',
            'application name': 'cmdb_app_name',
            'environment': 'environment',
            'choose node size': 'vm_size',
            'os image': 'os_image',
            'os': 'os_image',
            'role': 'role',
            'patch optin': 'patch_optin'
        }
        
        for key, value in actual_values.items():
            key_lower = key.lower()
            for search_key, terraform_key in project_mapping.items():
                if search_key in key_lower:
                    terraform_data['project_info'][terraform_key] = value
                    print(f"    Mapped {key} -> {terraform_key}: {value}")
                    break
        
        # COMPREHENSIVE VM EXTRACTION - Extract ALL VM data from Resources sheet
        print("COMPREHENSIVE VM EXTRACTION")
        print("=" * 30)

        # Section markers that indicate VM data
        vm_section_markers = [
            'virtual machine', 'vm configuration', 'server configuration',
            'compute resources', 'vm details', 'server details',
            'host configuration', 'instance details'
        ]

        # Try to extract VMs from vertical key-value format (Resources sheet)
        vm_instances = []
        vm_instances_from_kv = self._extract_vms_from_vertical_format(terraform_data)
        if vm_instances_from_kv:
            print(f"  Extracted {len(vm_instances_from_kv)} VMs from vertical key-value format")
            vm_instances.extend(vm_instances_from_kv)

        # Try to find VM tables in Resources sheet AND other sheets
        sheets_to_check = ['Resources', 'Build_ENV', 'VM', 'VMs', 'Servers', 'Compute']

        for sheet_name in sheets_to_check:
            if sheet_name not in terraform_data['all_tables']:
                continue

            sheet_tables = terraform_data['all_tables'].get(sheet_name, [])
            print(f"  Checking {sheet_name} sheet: {len(sheet_tables)} tables")

            # Look for VM-related tables with improved detection
            for i, table in enumerate(sheet_tables):
                headers = table.get('headers', [])
                data = table.get('data', [])

                # Expanded VM keywords for better detection
                vm_keywords = ['hostname', 'vm', 'server', 'machine', 'instance', 'node', 'compute',
                              'sku', 'recommended sku', 'virtual machine', 'host name', 'computer']

                # Check if this table contains VM data by looking at headers
                is_vm_table = any(any(keyword in str(header).lower() for keyword in vm_keywords) for header in headers)

                # Check for section markers before the table (in raw_data)
                has_section_marker = False
                sheet_data = terraform_data['comprehensive_data'].get(sheet_name, {})
                raw_data = sheet_data.get('raw_data', [])
                table_row_index = table.get('header_row_index', 0)

                # Look for section markers in rows above the table
                for row_idx in range(max(0, table_row_index - 5), table_row_index):
                    if row_idx < len(raw_data):
                        row = raw_data[row_idx]
                        if isinstance(row, dict):
                            for value in row.values():
                                value_str = str(value).lower()
                                if any(marker in value_str for marker in vm_section_markers):
                                    has_section_marker = True
                                    print(f"    Found VM section marker: '{value}'")
                                    break

                # Also check if table has sufficient columns that look like VM config (reduced threshold)
                has_vm_like_columns = len(headers) >= 3 and len(data) > 0

                # Check data content for VM-like patterns
                has_vm_data = False
                vm_field_keywords = ['owner', 'recommended', 'os', 'disk', 'image', 'size', 'sku',
                                    'ip', 'subnet', 'zone', 'region', 'availability']

                if data:
                    first_row = data[0]
                    # Look for common VM fields in the data
                    for key in first_row.keys():
                        if any(kw in str(key).lower() for kw in vm_field_keywords):
                            has_vm_data = True
                            break

                    # Also check if data values look like VM names (heuristic)
                    for value in first_row.values():
                        value_str = str(value).lower()
                        if any(pattern in value_str for pattern in ['-vm-', 'server', 'host', 'node']):
                            has_vm_data = True
                            break

                if (is_vm_table or has_vm_data or has_section_marker) and has_vm_like_columns:
                    print(f"  Found potential VM table in {sheet_name} ({i+1}): {len(data)} entries")
                    print(f"    Headers ({len(headers)}): {headers[:8] if len(headers) > 8 else headers}")

                    # Process each VM entry with better filtering
                    for j, row in enumerate(data):
                        vm_instance = {}
                        skip_row = False

                        # Check if row contains instruction text (not actual VM data)
                        for key, value in row.items():
                            value_str = str(value).lower()
                            # Skip rows with instruction text
                            if any(phrase in value_str for phrase in [
                                'to add resources', 'open this in desktop', 'hit the button',
                                'click here', 'instructions', 'example', 'sample'
                            ]):
                                skip_row = True
                                break

                        if skip_row:
                            continue

                        for key, value in row.items():
                            if value and str(value).strip():
                                # Skip obvious header rows or placeholder values
                                value_str = str(value).strip()
                                # Enhanced skip list
                                if value_str not in ['Value', 'Column', 'Header', 'N/A', 'TBD', '',
                                                     'None', 'null', 'NULL', '0', 'False', 'false']:
                                    # Skip column names that are just generic placeholders
                                    if not key.startswith('Column_') or value_str not in ['', 'None']:
                                        vm_instance[key] = value

                        if vm_instance and len(vm_instance) >= 2:  # Reduced threshold
                            # Standardize VM field names
                            standardized_vm = self._standardize_vm_fields(vm_instance)
                            vm_instances.append(standardized_vm)
                            if j < 2:  # Show first 2 VMs
                                print(f"    VM {j+1} fields: {list(standardized_vm.keys())[:6]}...")

        if vm_instances:
            terraform_data['vm_instances'] = vm_instances
            print(f"  Total VMs extracted: {len(vm_instances)}")
        else:
            # Fallback: Create VM instances from configuration
            print("  No explicit VM tables found, creating from configuration...")
            terraform_data['vm_instances'] = self._create_vm_instances_from_config(actual_values)
            print(f"  Created {len(terraform_data['vm_instances'])} VMs from configuration")
        
        print()
        
        # COMPREHENSIVE NSG EXTRACTION - Extract ALL security rules
        # Using field mapping: rules.name -> name, rules.priority -> priority, etc.
        print("COMPREHENSIVE NSG EXTRACTION")
        print("=" * 30)

        nsg_tables = terraform_data['all_tables'].get('NSG', [])
        security_rules = []

        for i, table in enumerate(nsg_tables):
            data = table.get('data', [])
            headers = table.get('headers', [])

            # Fix generic column names (Column_0, Column_1, etc.) with error recovery
            if headers and any(h.startswith('Column_') for h in headers):
                try:
                    headers = self._map_nsg_generic_columns(headers, data)
                    # Update table with mapped headers
                    table['headers'] = headers
                    # Remap data dictionaries to use new headers
                    data = self._remap_table_data(data, table.get('headers', []), headers)
                except Exception as e:
                    print(f"  [WARN] NSG column mapping failed: {e}, using original headers")
                    # Fallback: keep original headers

            if data:
                print(f"  Found NSG table {i+1}: {len(data)} rules (before filtering)")
                print(f"    Headers: {headers[:5]}...")

                valid_rules_count = 0
                for j, rule in enumerate(data):
                    if rule:  # Only add non-empty rules
                        # First, standardize field names
                        standardized_rule = self._standardize_nsg_rule(rule)

                        # Validate the rule has minimum required fields
                        if not self._is_valid_nsg_rule(standardized_rule):
                            continue  # Skip invalid/empty rules

                        # Map Excel field names to Terraform field names
                        mapped_rule = {}

                        # Direct mappings (same name in both)
                        for field in ['name', 'priority', 'direction', 'access', 'protocol',
                                     'source_port_range', 'description', 'source_address_prefix',
                                     'destination_address_prefix']:
                            if field in standardized_rule:
                                mapped_rule[field] = standardized_rule[field]

                        # Mapping: destination_port_ranges (Terraform) <- destination_port_ranges (Excel)
                        if 'destination_port_ranges' in standardized_rule:
                            mapped_rule['destination_port_ranges'] = standardized_rule['destination_port_ranges']
                        elif 'destination_port_range' in standardized_rule:  # Handle singular form
                            mapped_rule['destination_port_ranges'] = standardized_rule['destination_port_range']

                        # Mapping: source_asg_keys (Terraform) <- source_asg (Excel)
                        if 'source_asg' in standardized_rule:
                            mapped_rule['source_asg'] = standardized_rule['source_asg']
                            mapped_rule['source_asg_keys'] = standardized_rule.get('source_asg_keys', [])
                        elif 'source_asg_keys' in standardized_rule:
                            mapped_rule['source_asg_keys'] = standardized_rule['source_asg_keys']

                        # Mapping: destination_asg_keys (Terraform) <- destination_asg (Excel)
                        if 'destination_asg' in standardized_rule:
                            mapped_rule['destination_asg'] = standardized_rule['destination_asg']
                            mapped_rule['destination_asg_keys'] = standardized_rule.get('destination_asg_keys', [])
                        elif 'destination_asg_keys' in standardized_rule:
                            mapped_rule['destination_asg_keys'] = standardized_rule['destination_asg_keys']

                        # Keep all original fields for backward compatibility
                        mapped_rule.update(standardized_rule)
                        security_rules.append(mapped_rule)
                        valid_rules_count += 1

                        if valid_rules_count <= 3:  # Show first 3 valid rules
                            print(f"    Rule {valid_rules_count}: {mapped_rule.get('name', 'unnamed')} - {list(mapped_rule.keys())[:5]}...")

                print(f"  Valid rules extracted from table {i+1}: {valid_rules_count}")
        
        terraform_data['security_groups'] = security_rules
        print(f"  Total security rules extracted: {len(security_rules)}")
        print()
        
        # COMPREHENSIVE APPLICATION GATEWAY EXTRACTION
        print("COMPREHENSIVE APPLICATION GATEWAY EXTRACTION")
        print("=" * 45)
        
        apgw_tables = terraform_data['all_tables'].get('APGW', [])
        apgw_kv_pairs = terraform_data['all_key_value_pairs'].get('APGW', {})
        
        print(f"  Found {len(apgw_tables)} APGW tables")
        print(f"  Found {len(apgw_kv_pairs)} APGW key-value pairs")
        
        # Combine table data and key-value pairs
        apgw_data = {}
        if apgw_tables:
            for table in apgw_tables:
                data = table.get('data', [])
                for row in data:
                    for key, value in row.items():
                        if value and str(value).strip():
                            apgw_data[key] = value
        
        # Add key-value pairs
        apgw_data.update(apgw_kv_pairs)
        
        terraform_data['application_gateway'] = apgw_data
        print(f"  Total APGW configuration items: {len(apgw_data)}")
        print()
        
        # COMPREHENSIVE CONTAINER REGISTRY EXTRACTION
        print("COMPREHENSIVE CONTAINER REGISTRY EXTRACTION")
        print("=" * 40)
        
        acr_tables = terraform_data['all_tables'].get('ACR NRS', [])
        acr_kv_pairs = terraform_data['all_key_value_pairs'].get('ACR NRS', {})
        
        print(f"  Found {len(acr_tables)} ACR tables")
        print(f"  Found {len(acr_kv_pairs)} ACR key-value pairs")
        
        # Combine table data and key-value pairs
        acr_data = {}
        if acr_tables:
            for table in acr_tables:
                data = table.get('data', [])
                for row in data:
                    for key, value in row.items():
                        if value and str(value).strip():
                            acr_data[key] = value
        
        # Add key-value pairs
        acr_data.update(acr_kv_pairs)
        
        terraform_data['container_registry'] = acr_data
        print(f"  Total ACR configuration items: {len(acr_data)}")
        print()
        
        # COMPREHENSIVE RESOURCE OPTIONS EXTRACTION
        print("COMPREHENSIVE RESOURCE OPTIONS EXTRACTION")
        print("=" * 40)
        
        resource_options_tables = terraform_data['all_tables'].get('Resource Options', [])
        resource_options_kv_pairs = terraform_data['all_key_value_pairs'].get('Resource Options', {})
        
        print(f"  Found {len(resource_options_tables)} Resource Options tables")
        print(f"  Found {len(resource_options_kv_pairs)} Resource Options key-value pairs")
        
        # Combine all resource options data
        resource_options_data = []
        for table in resource_options_tables:
            data = table.get('data', [])
            for row in data:
                if row:  # Only add non-empty rows
                    resource_options_data.append(row)
        
        terraform_data['resource_options'] = resource_options_data
        print(f"  Total resource options items: {len(resource_options_data)}")
        print()
        
        # COMPREHENSIVE BUILD ENVIRONMENT EXTRACTION
        print("COMPREHENSIVE BUILD ENVIRONMENT EXTRACTION")
        print("=" * 40)
        
        build_env_tables = terraform_data['all_tables'].get('Build_ENV', [])
        build_env_kv_pairs = terraform_data['all_key_value_pairs'].get('Build_ENV', {})
        
        print(f"  Found {len(build_env_tables)} Build Environment tables")
        print(f"  Found {len(build_env_kv_pairs)} Build Environment key-value pairs")
        
        # Extract actual values from Build_ENV tables (values are in column 3, index 2)
        build_env_actual_values = self._extract_actual_values_from_tables('Build_ENV', value_column_index=2)
        print(f"  Extracted {len(build_env_actual_values)} actual values from Build_ENV tables")
        
        # Show extracted values
        for key, value in build_env_actual_values.items():
            print(f"    {key}: {value}")
        
        terraform_data['build_environment'] = {
            'key_value_pairs': build_env_actual_values,  # Use extracted actual values
            'raw_key_value_pairs': build_env_kv_pairs,  # Keep original for reference
            'tables': build_env_tables
        }
        print(f"  Total build environment items: {len(build_env_actual_values)}")
        print()
        
        # COMPREHENSIVE NAMING PATTERNS EXTRACTION
        print("COMPREHENSIVE NAMING PATTERNS EXTRACTION")
        print("=" * 40)
        
        naming_patterns = {}
        
        # Extract from resource options
        for item in resource_options_data:
            for key, value in item.items():
                if value and str(value).strip():
                    if 'Resource_Group' in str(key):
                        naming_patterns['Resource_Group'] = str(value)
                    elif 'Subnet' in str(key):
                        naming_patterns['Subnet'] = str(value)
                    elif 'Network_Security_Group' in str(key):
                        naming_patterns['Network_Security_Group'] = str(value)
                    elif 'Application_Gateway' in str(key):
                        naming_patterns['Application_Gateway'] = str(value)
                    elif 'Azure_Container_Registry' in str(key):
                        naming_patterns['Azure_Container_Registry'] = str(value)
                    elif 'Storage_Account' in str(key):
                        naming_patterns['Storage_Account'] = str(value)
        
        # Extract from key-value pairs
        for key, value in resource_options_kv_pairs.items():
            if value and str(value).strip():
                if 'Resource_Group' in str(key):
                    naming_patterns['Resource_Group'] = str(value)
                elif 'Subnet' in str(key):
                    naming_patterns['Subnet'] = str(value)
                elif 'Network_Security_Group' in str(key):
                    naming_patterns['Network_Security_Group'] = str(value)
                elif 'Application_Gateway' in str(key):
                    naming_patterns['Application_Gateway'] = str(value)
                elif 'Azure_Container_Registry' in str(key):
                    naming_patterns['Azure_Container_Registry'] = str(value)
                elif 'Storage_Account' in str(key):
                    naming_patterns['Storage_Account'] = str(value)
        
        terraform_data['naming_patterns'] = naming_patterns
        print(f"  Total naming patterns extracted: {len(naming_patterns)}")
        print()

        # MAP BUILD_ENV VALUES TO PROJECT_INFO
        print("MAPPING BUILD_ENV TO PROJECT_INFO")
        print("=" * 40)

        # Map Build_ENV extracted values to project_info
        build_env_values = build_env_actual_values

        # Mapping of Build_ENV keys to project_info keys
        build_env_mapping = {
            'application name': 'application_name',
            'app name': 'application_name',
            'service now ticket': 'service_now_ticket',
            'snow ticket': 'service_now_ticket',
            'ticket': 'service_now_ticket',
            'environment': 'environment',
            'env': 'environment',
            'location': 'location',
            'region': 'location',
            'subscription': 'subscription',
            'resource group': 'resource_group_name',
        }

        for build_key, build_value in build_env_values.items():
            build_key_lower = build_key.lower()
            # Check if this key maps to a project_info field
            for pattern, project_key in build_env_mapping.items():
                if pattern in build_key_lower:
                    # Only set if not already present or empty
                    current_value = terraform_data['project_info'].get(project_key)
                    if not current_value or str(current_value).strip() in ['', 'None', 'TBD', 'N/A']:
                        terraform_data['project_info'][project_key] = build_value
                        print(f"  Mapped Build_ENV[{build_key}] -> project_info[{project_key}]: {build_value}")
                    break

        print()

        # AUTO-DETECT MISSING REQUIRED FIELDS
        print("AUTO-DETECTION OF MISSING FIELDS")
        print("=" * 40)

        # Auto-detect application name if missing
        current_app_name = terraform_data['project_info'].get('application_name')
        if not current_app_name or str(current_app_name).strip() in ['', 'None', 'TBD', 'N/A']:
            detected_app = self._auto_detect_application_name(terraform_data)
            if detected_app:
                terraform_data['project_info']['application_name'] = detected_app

        # Auto-detect environment if missing
        current_env = terraform_data['project_info'].get('environment')
        if not current_env or str(current_env).strip() in ['', 'None', 'TBD', 'N/A']:
            detected_env = self._auto_detect_environment(terraform_data)
            if detected_env:
                terraform_data['project_info']['environment'] = detected_env

        # Auto-detect Service Now ticket if missing
        current_ticket = terraform_data['project_info'].get('service_now_ticket')
        if not current_ticket or str(current_ticket).strip() in ['', 'None', 'TBD', 'N/A']:
            detected_ticket = self._auto_detect_service_now_ticket(terraform_data)
            if detected_ticket:
                terraform_data['project_info']['service_now_ticket'] = detected_ticket

        # Auto-detect location if missing
        current_location = terraform_data['project_info'].get('location')
        if not current_location or str(current_location).strip() in ['', 'None', 'TBD', 'N/A']:
            detected_location = self._auto_detect_location(terraform_data)
            if detected_location:
                terraform_data['project_info']['location'] = detected_location

        # Auto-detect subscription if missing
        current_subscription = terraform_data['project_info'].get('subscription')
        if not current_subscription or str(current_subscription).strip() in ['', 'None', 'TBD', 'N/A']:
            detected_subscription = self._auto_detect_subscription(terraform_data)
            if detected_subscription:
                terraform_data['project_info']['subscription'] = detected_subscription

        # SET INTELLIGENT DEFAULTS FOR MISSING CRITICAL FIELDS
        print("APPLYING INTELLIGENT DEFAULTS")
        print("=" * 40)

        # Default environment based on context clues
        if not terraform_data['project_info'].get('environment') or \
           str(terraform_data['project_info'].get('environment')).strip() in ['', 'None', 'TBD', 'N/A']:
            # Check for DR indicators
            filename_lower = self.source_filename.lower() if self.source_filename else ''
            if 'dr' in filename_lower or 'disaster' in filename_lower:
                terraform_data['project_info']['environment'] = 'dr'
                print(f"  Set environment to 'dr' based on filename context")
            elif 'prod' in filename_lower:
                terraform_data['project_info']['environment'] = 'prod'
                print(f"  Set environment to 'prod' based on filename context")
            else:
                # Default to 'dev' for safety
                terraform_data['project_info']['environment'] = 'dev'
                print(f"  Set environment to 'dev' (safe default)")

        # Default service_now_ticket - generate placeholder
        if not terraform_data['project_info'].get('service_now_ticket') or \
           str(terraform_data['project_info'].get('service_now_ticket')).strip() in ['', 'None', 'TBD', 'N/A', '1', '0']:
            # Generate ticket placeholder from app name or filename
            app_name = terraform_data['project_info'].get('application_name', 'app')
            safe_app_name = ''.join(c for c in app_name if c.isalnum())[:10]
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d')
            placeholder_ticket = f"RITM{timestamp}{safe_app_name}"
            terraform_data['project_info']['service_now_ticket'] = placeholder_ticket
            print(f"  Generated placeholder service_now_ticket: {placeholder_ticket}")
            print(f"  WARNING: Please replace with actual ServiceNow ticket number")

        print()

        print()

        # COMPREHENSIVE DATA SUMMARY
        print("COMPREHENSIVE DATA EXTRACTION SUMMARY")
        print("=" * 50)
        print(f"Total sheets processed: {len(terraform_data['comprehensive_data'])}")
        print(f"Total tables across all sheets: {sum(len(tables) for tables in terraform_data['all_tables'].values())}")
        print(f"Total key-value pairs across all sheets: {sum(len(kv) for kv in terraform_data['all_key_value_pairs'].values())}")
        print(f"VM instances: {len(terraform_data['vm_instances'])}")
        print(f"Security groups: {len(terraform_data['security_groups'])}")
        print(f"Application Gateway config items: {len(terraform_data['application_gateway'])}")
        print(f"Container Registry config items: {len(terraform_data['container_registry'])}")
        print(f"Resource options items: {len(terraform_data['resource_options'])}")
        print(f"Naming patterns: {len(terraform_data['naming_patterns'])}")
        print("=" * 50)
        print()

        # GENERATE EXTRACTION QUALITY REPORT
        print("EXTRACTION QUALITY REPORT")
        print("=" * 50)
        extraction_report = self.generate_extraction_report(terraform_data)

        print(f"Summary: {extraction_report['summary']}")
        print()
        print(f"Quality Scores:")
        for score_name, score_value in extraction_report['quality_scores'].items():
            score_display = score_name.replace('_', ' ').title()
            print(f"  {score_display}: {score_value}%")
        print()

        if extraction_report['recommendations']:
            print(f"Recommendations ({len(extraction_report['recommendations'])}):")
            for i, rec in enumerate(extraction_report['recommendations'], 1):
                print(f"  {i}. {rec}")

        print("=" * 50)
        print()

        # Store report in terraform_data for later reference
        terraform_data['extraction_report'] = extraction_report

        return terraform_data

    def generate_extraction_report(self, terraform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive extraction quality report.

        Args:
            terraform_data: The extracted terraform data structure

        Returns:
            Dictionary containing extraction metrics, quality scores, and recommendations
        """
        from datetime import datetime

        report = {
            'timestamp': datetime.now().isoformat(),
            'source_file': self.source_filename or 'Unknown',
            'metrics': {},
            'quality_scores': {},
            'recommendations': [],
            'summary': ''
        }

        # Calculate extraction metrics
        metrics = report['metrics']
        metrics['sheets_processed'] = len(terraform_data.get('comprehensive_data', {}))
        metrics['vm_count'] = len(terraform_data.get('vm_instances', []))
        metrics['nsg_rules'] = len(terraform_data.get('security_groups', []))
        metrics['project_info_fields'] = sum(1 for v in terraform_data.get('project_info', {}).values()
                                             if v and str(v).strip() not in ['', 'None', 'TBD', 'N/A'])
        metrics['total_tables'] = sum(len(tables) for tables in terraform_data.get('all_tables', {}).values())
        metrics['total_key_value_pairs'] = sum(len(kv) for kv in terraform_data.get('all_key_value_pairs', {}).values())
        metrics['apgw_config_items'] = len(terraform_data.get('application_gateway', []))
        metrics['acr_config_items'] = len(terraform_data.get('container_registry', []))

        # Calculate quality scores (0-100)
        scores = report['quality_scores']

        # Project info completeness (required fields: application_name, environment, service_now_ticket, location, subscription)
        required_fields = ['application_name', 'environment', 'service_now_ticket', 'location', 'subscription']
        project_info = terraform_data.get('project_info', {})
        filled_required = sum(1 for field in required_fields
                             if project_info.get(field) and str(project_info[field]).strip() not in ['', 'None', 'TBD', 'N/A'])
        scores['project_info_completeness'] = int((filled_required / len(required_fields)) * 100)

        # VM extraction quality
        vm_instances = terraform_data.get('vm_instances', [])
        if vm_instances:
            # Check for critical VM fields
            critical_vm_fields = ['hostname', 'vm_size', 'os_type']
            vm_quality = 0
            for vm in vm_instances:
                filled = sum(1 for field in critical_vm_fields if vm.get(field))
                vm_quality += (filled / len(critical_vm_fields))
            scores['vm_extraction_quality'] = int((vm_quality / len(vm_instances)) * 100)
        else:
            scores['vm_extraction_quality'] = 0

        # NSG extraction quality
        nsg_rules = terraform_data.get('security_groups', [])
        if nsg_rules:
            # Check for critical NSG fields
            critical_nsg_fields = ['name', 'priority', 'direction', 'access', 'protocol']
            nsg_quality = 0
            for rule in nsg_rules:
                filled = sum(1 for field in critical_nsg_fields if rule.get(field))
                nsg_quality += (filled / len(critical_nsg_fields))
            scores['nsg_extraction_quality'] = int((nsg_quality / len(nsg_rules)) * 100)
        else:
            scores['nsg_extraction_quality'] = 0

        # Overall quality score (weighted average)
        weights = {
            'project_info_completeness': 0.4,
            'vm_extraction_quality': 0.3,
            'nsg_extraction_quality': 0.3
        }
        overall_score = sum(scores[key] * weight for key, weight in weights.items())
        scores['overall_quality'] = int(overall_score)

        # Generate recommendations
        recommendations = report['recommendations']

        # Project info recommendations
        missing_required = [field for field in required_fields
                           if not project_info.get(field) or str(project_info[field]).strip() in ['', 'None', 'TBD', 'N/A']]
        if missing_required:
            recommendations.append(f"Missing required project info fields: {', '.join(missing_required)}")

        # VM recommendations
        if metrics['vm_count'] == 0:
            recommendations.append("No VMs extracted. Verify VM sheet/table exists and contains data.")
        elif metrics['vm_count'] < 2:
            recommendations.append("Only 1 VM found. Consider if high availability requires multiple VMs.")

        if vm_instances and scores['vm_extraction_quality'] < 80:
            recommendations.append("VM data quality is below 80%. Check for missing hostname, vm_size, or os_type fields.")

        # NSG recommendations
        if metrics['nsg_rules'] == 0:
            recommendations.append("No NSG rules extracted. Verify NSG sheet exists and contains security rules.")
        elif metrics['nsg_rules'] < 5:
            recommendations.append(f"Only {metrics['nsg_rules']} NSG rules found. Verify all security rules are captured.")

        if nsg_rules and scores['nsg_extraction_quality'] < 80:
            recommendations.append("NSG rule quality is below 80%. Check for missing priority, direction, or protocol fields.")

        # Data extraction recommendations
        if metrics['sheets_processed'] < 3:
            recommendations.append(f"Only {metrics['sheets_processed']} sheets processed. Verify all required sheets are present.")

        # Generate summary
        quality_level = 'Excellent' if scores['overall_quality'] >= 90 else \
                       'Good' if scores['overall_quality'] >= 70 else \
                       'Fair' if scores['overall_quality'] >= 50 else 'Poor'

        report['summary'] = (
            f"Extraction Quality: {quality_level} ({scores['overall_quality']}%). "
            f"Processed {metrics['sheets_processed']} sheets, extracted {metrics['vm_count']} VMs and "
            f"{metrics['nsg_rules']} NSG rules. "
            f"Project info is {scores['project_info_completeness']}% complete."
        )

        if not recommendations:
            recommendations.append("All critical data extracted successfully.")

        return report

    def _create_vm_instances_from_config(self, actual_values: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create VM instances from configuration data when no VM table is found.
        
        Args:
            actual_values: Dictionary of actual values extracted from tables
        """
        vm_instances = []
        
        # Extract VM count from configuration - look for common patterns
        vm_count = 2  # Default to 2 VMs for redundancy
        for key, value in actual_values.items():
            key_lower = key.lower()
            if any(term in key_lower for term in ['vm', 'server', 'instance']) and any(term in key_lower for term in ['count', 'number', 'total']):
                try:
                    vm_count = int(value)
                    break
                except (ValueError, TypeError):
                    pass
        
        # Try to get actual values from the Excel file
        app_name = actual_values.get('Abbreviated App Name', 'myapp')
        project_name = actual_values.get('Project Name', 'project1')
        environment = actual_values.get('Environment', 'dev')
        vm_size = actual_values.get('Choose Node Size', 'Standard_D2s_v3')
        os_image = actual_values.get('OS', 'Ubuntu 22.04 LTS')
        
        # Get additional values
        server_owner = actual_values.get('Server Owner', 'TBD')
        app_owner = actual_values.get('Application Owner', 'TBD')
        business_owner = actual_values.get('Business Owner', 'TBD')
        service_now_ticket = actual_values.get('Service Now Ticket', 'TBD')
        role = actual_values.get('Role', 'web-server')
        patch_optin = actual_values.get('Patch Optin', 'yes')
        
        # Create VM instances based on configuration
        for i in range(vm_count):
            vm_instance = {
                'Hostname': f"{app_name}-{i+1:02d}",
                'Recommended SKU': vm_size,
                'OS Image*': os_image,
                'Environment': environment,
                'Server Owner': server_owner,
                'Application Owner': app_owner,
                'Business Owner': business_owner,
                'Project Name': project_name,
                'Application Name': app_name,
                'Service Now Ticket': service_now_ticket,
                'Role': role,
                'Patch Optin': patch_optin,
                'Private IP Address Allocation': actual_values.get('Private IP Address Allocation', 'Dynamic'),
                'OS disk size': actual_values.get('OS disk size', '30'),
                'OS disk type': actual_values.get('OS disk type', 'Premium_LRS'),
                'Data disk sizes': actual_values.get('Data disk sizes', ''),
                'Data disk type': actual_values.get('Data disk type', 'Premium_LRS')
            }
            vm_instances.append(vm_instance)
        
        return vm_instances
    
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

    def validate_extraction_quality(self, terraform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required data was extracted and report issues.

        Args:
            terraform_data: Output from get_terraform_ready_data()

        Returns:
            Dict with 'valid', 'errors', 'warnings', 'missing_fields'
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_fields': [],
            'extraction_quality': 'unknown'
        }

        # Check required fields
        required_fields = {
            'application_name': terraform_data['project_info'].get('application_name'),
            'environment': terraform_data['project_info'].get('environment'),
            'service_now_ticket': terraform_data['project_info'].get('service_now_ticket'),
        }

        # Track missing required fields
        for field_name, field_value in required_fields.items():
            if not field_value or str(field_value).strip() in ['', 'None', 'TBD', 'N/A']:
                validation['missing_fields'].append(field_name)
                validation['errors'].append(f"Required field '{field_name}' is missing or empty")
                validation['valid'] = False

        # Check VM extraction
        vm_count = len(terraform_data.get('vm_instances', []))
        if vm_count == 0:
            validation['errors'].append("No VM instances extracted")
            validation['valid'] = False
        elif vm_count <= 2:
            validation['warnings'].append(f"Only {vm_count} VM(s) extracted - may be using fallback defaults")

        # Check NSG rules
        nsg_count = len(terraform_data.get('security_groups', []))
        if nsg_count == 0:
            validation['warnings'].append("No NSG security rules extracted")

        # Assess extraction quality
        if len(validation['errors']) == 0 and len(validation['warnings']) == 0:
            validation['extraction_quality'] = 'excellent'
        elif len(validation['errors']) == 0:
            validation['extraction_quality'] = 'good'
        elif len(validation['errors']) <= 2:
            validation['extraction_quality'] = 'partial'
        else:
            validation['extraction_quality'] = 'poor'

        return validation


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
