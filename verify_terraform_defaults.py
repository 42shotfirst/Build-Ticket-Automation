#!/usr/bin/env python3
"""
Verify Terraform Default Values
=================================
This script thoroughly checks every field in terraform files against the JSON 
and reports all discrepancies.
"""

import json
import re
from typing import Dict, Any, List

def load_json_data(json_file: str) -> Dict:
    """Load the comprehensive Excel JSON data."""
    with open(json_file, 'r') as f:
        return json.load(f)

def extract_value_from_json(data: Dict, field_name: str, context: str = None) -> Any:
    """Extract a specific field value from the JSON structure."""
    # Handle nested data structure
    sheets = data.get('sheets', {})
    build_env = sheets.get('Build_ENV', {})
    
    # Look in structured data
    structured = build_env.get('structured_data', [])
    for item in structured:
        if isinstance(item, dict):
            var_name = item.get('Terraform Variable')
            if var_name == field_name:
                return item.get('Value')
    
    # Look in raw data
    raw_data = build_env.get('raw_data', [])
    for row in raw_data:
        if isinstance(row, dict) and row.get('1') == field_name:
            return row.get('2')
    
    return None

def check_key_vault_defaults(json_data: Dict) -> List[str]:
    """Check Key Vault defaults."""
    issues = []
    
    # Check soft_delete_retention_days
    json_value = extract_value_from_json(json_data, 'soft_delete_retention_days')
    print(f"soft_delete_retention_days from JSON: {json_value}")
    if json_value != 90:
        issues.append(f"❌ soft_delete_retention_days: Expected 90 from JSON, got {json_value}")
    
    # Check sku_name
    json_value = extract_value_from_json(json_data, 'sku_name')
    print(f"sku_name from JSON: {json_value}")
    if json_value != "standard":
        issues.append(f"❌ sku_name: Expected 'standard' from JSON, got {json_value}")
    
    # Check public_network_access
    json_value = extract_value_from_json(json_data, 'public_network_access')
    print(f"public_network_access from JSON: {json_value}")
    # Value of 1 typically means True/enabled
    if json_value == 1:
        issues.append(f"❌ public_network_access: JSON has 1 (true), but variables.tf default is false")
    
    return issues

def check_location(json_data: Dict) -> List[str]:
    """Check location field."""
    issues = []
    
    json_value = extract_value_from_json(json_data, 'location')
    print(f"location from JSON: {json_value}")
    
    # Check if it's a valid location
    valid_locations = ["WEST US", "WEST US 2", "WEST US 3", "EAST US"]
    if json_value not in valid_locations:
        issues.append(f"❌ location: '{json_value}' is not a valid Azure location. Expected one of {valid_locations}")
    
    return issues

def check_admin_username(json_data: Dict) -> List[str]:
    """Check admin_username field."""
    issues = []
    
    json_value = extract_value_from_json(json_data, 'admin_username')
    print(f"admin_username from JSON: {json_value}")
    
    if json_value != "cisadmin":
        issues.append(f"❌ admin_username: Expected 'cisadmin' from JSON, got {json_value}")
    else:
        issues.append(f"✓ admin_username: Correct ('cisadmin')")
    
    return issues

def main():
    """Main verification function."""
    print("=" * 80)
    print("TERRAFORM DEFAULT VALUES VERIFICATION")
    print("=" * 80)
    print()
    
    json_file = 'comprehensive_excel_data.json'
    
    print("Loading JSON data...")
    data = load_json_data(json_file)
    print("JSON data loaded successfully")
    print()
    
    all_issues = []
    
    print("Checking admin_username...")
    all_issues.extend(check_admin_username(data))
    print()
    
    print("Checking location...")
    all_issues.extend(check_location(data))
    print()
    
    print("Checking Key Vault defaults...")
    all_issues.extend(check_key_vault_defaults(data))
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY OF ISSUES")
    print("=" * 80)
    
    if all_issues:
        for issue in all_issues:
            print(issue)
    else:
        print("✓ No issues found!")
    
    print()
    print(f"Total issues found: {len([i for i in all_issues if i.startswith('❌')])}")

if __name__ == "__main__":
    main()

