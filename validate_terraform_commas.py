#!/usr/bin/env python3
"""
Validate Terraform tfvars file for proper comma usage in map structures.
"""

import re
import sys
import glob

def validate_terraform_commas(filepath: str) -> list:
    """Validate that all map entries have commas between them."""
    
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    issues = []
    in_map = False
    map_start_line = 0
    last_closing_brace_line = None
    
    # Top-level variables that don't need commas before them
    top_level_vars = {
        'spn', 'location', 'resource_group_name', 'disk_encryption_set_name',
        'user_assigned_identity_name', 'key_vault', 'subnets', 'private_endpoints',
        'network_security_rules', 'vm_list', 'common_tags'
    }
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Detect map start: variable_name = {
        if '=' in stripped and stripped.endswith('{'):
            var_name = stripped.split('=')[0].strip()
            if var_name not in top_level_vars:
                in_map = True
                map_start_line = i
                last_closing_brace_line = None
        
        # Detect map end: }
        if stripped == '}' and in_map:
            last_closing_brace_line = i
            in_map = False
        
        # Detect new map entry: key = {
        if in_map and '=' in stripped and stripped.endswith('{'):
            key = stripped.split('=')[0].strip()
            
            # Check if previous entry had a comma
            if last_closing_brace_line and last_closing_brace_line < i:
                # Check the line with the closing brace
                brace_line = lines[last_closing_brace_line - 1]
                if brace_line.strip() == '}' and not brace_line.rstrip().endswith(','):
                    # Check if next non-empty line is this key
                    for j in range(last_closing_brace_line, i - 1):
                        if lines[j].strip() and not lines[j].strip().startswith('#'):
                            # There's content between, might be okay
                            break
                    else:
                        issues.append({
                            'line': i,
                            'key': key,
                            'issue': f'Missing comma after closing brace before "{key}"',
                            'context': f'Line {last_closing_brace_line}: {lines[last_closing_brace_line - 1].strip()}\nLine {i}: {line.strip()}'
                        })
        
        # Reset last_closing_brace when we see a new entry
        if in_map and '=' in stripped and stripped.endswith('{'):
            last_closing_brace_line = None
    
    return issues

def main():
    """Main validation function."""
    # Find latest tfvars
    tfvars_files = sorted(glob.glob('output_package/**/terraform.tfvars', recursive=True), reverse=True)
    
    if not tfvars_files:
        print("No terraform.tfvars files found")
        return 1
    
    tfvars = tfvars_files[0]
    print(f"Validating: {tfvars}\n")
    
    issues = validate_terraform_commas(tfvars)
    
    if issues:
        print(f"Found {len(issues)} comma issues:\n")
        for issue in issues[:10]:
            print(f"Line {issue['line']}: {issue['issue']}")
            print(f"  {issue['context']}\n")
        return 1
    else:
        print("✓ All map structures have proper commas!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

