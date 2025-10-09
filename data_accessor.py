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
        
        # List of values to skip (headers, placeholders, etc.)
        skip_values = {
            'Value', 'Existing', 'Validation', 'Terraform Variable', 'SNOW form', 
            'User', 'EA', 'CMDB', 'Cloud Engineering', 'Azure Client Managed', 
            'Azure CMS Managed', 'OnPrem', 'AWS Client Managed', 'YES', 'NO', 
            'ASR', 'GRS Backup/Restore', 'Warm/Standby', 'Cold Rebuild', 
            'User/CMDB', 'CMDB APP NAME', 'SNOW team after request is complete?', 
            'User/EA', 'DEV', 'UAT', 'QA', 'PROD', 'DR', 'Platinum', 'Gold', 
            'Silver', 'Bronze', 'Iron', 'CMDB?', 'MUST BE A NUMBER', 
            'Commercial', 'Consumer Related', 'Corporate', 'Corporate Support',
            'Overview'
        }
        
        for table in tables:
            data = table.get('data', [])
            for row in data:
                # Look for the pattern where the first column is a field name
                row_items = list(row.items())
                
                # Need at least value_column_index + 1 columns
                if len(row_items) >= value_column_index + 1:
                    field_name = str(row_items[0][1])  # First column is field name
                    field_value = str(row_items[value_column_index][1])  # Value at specified index (0-based)
                    
                    # Skip if it's a header row, empty, or invalid data
                    if (field_name and field_value and 
                        str(field_value).strip() and
                        field_name not in skip_values and 
                        field_value not in skip_values and
                        not field_value.startswith('wab:') and
                        not field_value.startswith('vm_list')):
                        
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
        
        # Try to find VM tables in Resources sheet
        resources_tables = terraform_data['all_tables'].get('Resources', [])
        vm_instances = []
        
        # Look for VM-related tables with improved detection
        for i, table in enumerate(resources_tables):
            headers = table.get('headers', [])
            data = table.get('data', [])
            
            # Expanded VM keywords for better detection
            vm_keywords = ['hostname', 'vm', 'server', 'machine', 'instance', 'node', 'compute', 'sku', 'recommended sku']
            
            # Check if this table contains VM data by looking at headers
            is_vm_table = any(any(keyword in str(header).lower() for keyword in vm_keywords) for header in headers)
            
            # Also check if table has sufficient columns that look like VM config
            has_vm_like_columns = len(headers) >= 5 and len(data) > 0
            
            # Check data content for VM-like patterns
            has_vm_data = False
            if data:
                first_row = data[0]
                # Look for common VM fields in the data
                for key in first_row.keys():
                    if any(kw in str(key).lower() for kw in ['owner', 'recommended', 'os', 'disk', 'image']):
                        has_vm_data = True
                        break
            
            if (is_vm_table or has_vm_data) and has_vm_like_columns:
                print(f"  Found potential VM table {i+1}: {len(data)} entries")
                print(f"    Headers ({len(headers)}): {headers[:8] if len(headers) > 8 else headers}")
                
                # Process each VM entry
                for j, row in enumerate(data):
                    vm_instance = {}
                    for key, value in row.items():
                        if value and str(value).strip():  # Only include non-empty values
                            vm_instance[key] = value
                    
                    if vm_instance and len(vm_instance) >= 3:  # Only add if we have meaningful data
                        vm_instances.append(vm_instance)
                        if j < 2:  # Show first 2 VMs
                            print(f"    VM {j+1} fields: {list(vm_instance.keys())[:6]}...")
        
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
        print("COMPREHENSIVE NSG EXTRACTION")
        print("=" * 30)
        
        nsg_tables = terraform_data['all_tables'].get('NSG', [])
        security_rules = []
        
        for i, table in enumerate(nsg_tables):
            data = table.get('data', [])
            headers = table.get('headers', [])
            
            if data:
                print(f"  Found NSG table {i+1}: {len(data)} rules")
                print(f"    Headers: {headers[:5]}...")
                
                for j, rule in enumerate(data):
                    if rule:  # Only add non-empty rules
                        security_rules.append(rule)
                        if j < 3:  # Show first 3 rules
                            print(f"    Rule {j+1}: {list(rule.keys())[:5]}...")
        
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
        
        return terraform_data
    
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
