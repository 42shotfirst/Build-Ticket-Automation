#!/usr/bin/env python3
"""
Excel Data Mapper
=================
Correctly maps Excel data based on the actual structure:
- Column 0: Labels/Descriptions
- Column 1: Terraform variable names
- Column 2: Actual values
"""

import json
import os
from typing import Dict, Any, List, Optional


class ExcelDataMapper:
    """Maps Excel data correctly based on actual column structure."""

    def __init__(self, json_file_path: str):
        """Initialize with JSON file from comprehensive extraction."""
        self.json_file_path = json_file_path
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.sheets = self.data.get('sheets', {})

    def extract_terraform_data(self) -> Dict[str, Any]:
        """Extract Terraform data with correct column mapping."""

        terraform_data = {
            'build_environment': {},
            'project_info': {},
            'vm_configuration': {},
            'network_security_rules': [],
            'storage_accounts': {},
            'key_vault': {},
            'subnets': {}
        }

        # Extract Build_ENV data
        self._extract_build_env(terraform_data)

        # Extract Resources data
        self._extract_resources(terraform_data)

        # Extract NSG rules
        self._extract_nsg_rules(terraform_data)

        return terraform_data

    def _extract_build_env(self, terraform_data: Dict):
        """Extract Build_ENV sheet data with correct column mapping."""

        build_sheet = self.sheets.get('Build_ENV', {})
        raw_data = build_sheet.get('raw_data', [])

        print("Extracting Build_ENV data...")

        # Process each row looking for terraform variable and value
        for row in raw_data:
            # Column 1 = Terraform variable name
            # Column 2 = Value
            terraform_var = str(row.get('1', '')).strip() if row.get('1') else ''
            value = str(row.get('2', '')).strip() if row.get('2') else ''

            # Skip header rows and empty values
            if terraform_var and value and terraform_var != 'Terraform Variable':
                terraform_data['build_environment'][terraform_var] = value
                print(f"  {terraform_var}: {value}")

    def _extract_resources(self, terraform_data: Dict):
        """Extract Resources sheet data with correct structure."""

        resources_sheet = self.sheets.get('Resources', {})
        raw_data = resources_sheet.get('raw_data', [])

        print("\nExtracting Resources data...")

        # Track current section
        current_section = None

        for i, row in enumerate(raw_data):
            label = str(row.get('0', '')).strip() if row.get('0') else ''
            terraform_var = str(row.get('1', '')).strip() if row.get('1') else ''
            value = str(row.get('2', '')).strip() if row.get('2') else ''

            # Detect section headers
            if label and terraform_var == 'Terraform Variable' and value == 'Value':
                current_section = label
                print(f"\n  Found section: {current_section}")
                continue

            # Skip empty rows or header duplicates
            if not terraform_var or terraform_var == 'Terraform Variable':
                continue

            # Process based on current section
            if current_section == 'Overview':
                # Project information
                if terraform_var and value:
                    # Map overview fields to project_info
                    if 'project' in label.lower():
                        terraform_data['project_info']['project_name'] = value
                    elif 'app' in label.lower() and 'name' in label.lower():
                        terraform_data['project_info']['application_name'] = value
                    elif 'service now' in label.lower():
                        terraform_data['project_info']['service_now_ticket'] = value
                    elif 'environment' in label.lower():
                        terraform_data['project_info']['environment'] = value
                    print(f"    {label}: {value}")

            elif current_section == 'Virtual Machine':
                # VM configuration
                if terraform_var and value:
                    # Clean up the terraform variable name for nested access
                    terraform_data['vm_configuration'][terraform_var] = value
                    print(f"    {terraform_var}: {value}")

            elif current_section == 'Storage Account':
                # Storage account configuration
                if terraform_var and value:
                    terraform_data['storage_accounts'][terraform_var] = value
                    print(f"    {terraform_var}: {value}")

    def _extract_nsg_rules(self, terraform_data: Dict):
        """Extract NSG rules from NSG sheet."""

        nsg_sheet = self.sheets.get('NSG', {})
        raw_data = nsg_sheet.get('raw_data', [])

        print("\nExtracting NSG rules...")

        # First row contains headers
        if not raw_data:
            return

        headers = raw_data[0] if raw_data else {}

        # Map column numbers to header names
        column_map = {}
        for col, header in headers.items():
            if header and str(header).strip():
                column_map[col] = str(header).strip()

        print(f"  Column mapping: {column_map}")

        # Process data rows
        for i, row in enumerate(raw_data[1:], 1):
            rule = {}
            has_data = False

            for col, header in column_map.items():
                value = row.get(col)
                if value and str(value).strip():
                    rule[header] = value
                    has_data = True

            if has_data and 'name' in rule:
                terraform_data['network_security_rules'].append(rule)
                print(f"  Rule {i}: {rule.get('name')} - {rule.get('direction')} {rule.get('access')} {rule.get('protocol')}")

    def get_clean_terraform_values(self) -> Dict[str, Any]:
        """Get clean Terraform values with proper defaults."""

        tf_data = self.extract_terraform_data()

        # Build environment values
        build_env = tf_data.get('build_environment', {})

        # Get actual values or sensible defaults
        clean_values = {
            'location': build_env.get('location', 'WEST US 3'),
            'resource_group_name': build_env.get('resource_group_name', 'rsg1'),
            'subscription': build_env.get('subscription', 'subscription1'),
            'resource_group_key': build_env.get('key', 'rsg1'),
        }

        # VM configuration
        vm_config = tf_data.get('vm_configuration', {})

        # Parse VM values correctly
        vm_data = {
            'name': 'Default',  # Will be replaced if actual value exists
            'size': 'Standard_B2s',
            'os_type': 'windows',
            'os_disk_size': 127,
            'os_disk_type': 'StandardSSD_LRS',
            'data_disk_sizes': [50, 50],
            'data_disk_type': 'Standard_LRS',
            'ip_allocation': 'Dynamic',
            'ip_address': None,
            'subnet_key': 'snet1',
            'asg_key': 'asg_nic',
            'admin_username': 'azureadmin'
        }

        # Update with actual VM values
        for key, value in vm_config.items():
            if 'vm_list.vm1.name' in key:
                vm_data['name'] = value if value != 'Default' else f"vm-{clean_values.get('resource_group_name', 'app')}-01"
            elif 'vm_list.vm1.size' in key and value != 'vm1':
                vm_data['size'] = value
            elif 'vm_list.vm1.image_os' in key and value != 'vm1':
                vm_data['os_type'] = 'windows' if 'win' in value.lower() else 'linux'
            elif 'vm_list.vm1.os_disk_size' in key:
                try:
                    vm_data['os_disk_size'] = int(value)
                except:
                    pass
            elif 'vm_list.vm1.ip_allocation' in key:
                vm_data['ip_allocation'] = value
            elif 'vm_list.vm1.ip_address' in key and value != '4.4.4.4':
                vm_data['ip_address'] = value
            elif 'admin_username' in key:
                vm_data['admin_username'] = value

        clean_values['vm_configuration'] = vm_data

        # NSG rules
        clean_values['nsg_rules'] = tf_data.get('network_security_rules', [])

        # Project info
        clean_values['project_info'] = tf_data.get('project_info', {})

        return clean_values


def main():
    """Test the Excel data mapper."""

    json_file = "LLDtest_comprehensive_extract.json"

    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return False

    print("=" * 60)
    print("EXCEL DATA MAPPER")
    print("=" * 60)

    mapper = ExcelDataMapper(json_file)
    clean_values = mapper.get_clean_terraform_values()

    print("\n" + "=" * 60)
    print("EXTRACTED CLEAN VALUES")
    print("=" * 60)

    print("\nBuild Environment:")
    print(f"  Location: {clean_values['location']}")
    print(f"  Resource Group: {clean_values['resource_group_name']}")
    print(f"  Subscription: {clean_values['subscription']}")

    print("\nVM Configuration:")
    vm = clean_values['vm_configuration']
    for key, value in vm.items():
        print(f"  {key}: {value}")

    print("\nNSG Rules:")
    for rule in clean_values['nsg_rules'][:3]:  # Show first 3 rules
        print(f"  {rule.get('name')}: {rule.get('direction')} {rule.get('access')} {rule.get('protocol')}")

    print("\nProject Info:")
    for key, value in clean_values['project_info'].items():
        print(f"  {key}: {value}")

    # Save clean values to JSON
    output_file = "terraform_clean_values.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_values, f, indent=2)

    print(f"\nClean values saved to: {output_file}")

    return True


if __name__ == "__main__":
    main()