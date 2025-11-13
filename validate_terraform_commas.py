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
    
    # Track brace depth to know when we're inside a map
    brace_depth = 0
    # Track the last closing brace line at the current depth
    last_closing_brace = {}  # depth -> line number
    # Track the current map entry key at each depth
    current_map_keys = {}  # depth -> key name
    
    # Top-level variables that don't need commas before them
    top_level_vars = {
        'spn', 'location', 'resource_group_name', 'disk_encryption_set_name',
        'user_assigned_identity_name', 'key_vault', 'subnets', 'private_endpoints',
        'application_security_groups', 'network_security_rules', 'vm_list', 'common_tags'
    }
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        original_line = line.rstrip()
        
        # Count opening and closing braces to track depth
        open_braces = stripped.count('{')
        close_braces = stripped.count('}')
        
        # Detect map entry: key = {
        if '=' in stripped and stripped.endswith('{'):
            key = stripped.split('=')[0].strip()
            
            # Check if this is a map entry (not a top-level variable)
            # We're in a map if brace_depth > 0 (inside at least one map)
            if brace_depth > 0:
                # This is a map entry inside a parent map
                # Check if previous entry at this depth had a comma
                # The depth where we check is the current depth (where siblings exist)
                if brace_depth in last_closing_brace:
                    prev_brace_line_num = last_closing_brace[brace_depth]
                    prev_brace_line = lines[prev_brace_line_num - 1]
                    
                    # Check if the previous closing brace line ends with a comma
                    if prev_brace_line.strip() == '}' and not prev_brace_line.rstrip().endswith(','):
                        # Check if there's only whitespace/comments between the brace and this key
                        has_content_between = False
                        for j in range(prev_brace_line_num, i - 1):
                            between_line = lines[j].strip()
                            if between_line and not between_line.startswith('#'):
                                has_content_between = True
                                break
                        
                        if not has_content_between:
                            prev_key = current_map_keys.get(brace_depth, 'previous entry')
                            issues.append({
                                'line': i,
                                'key': key,
                                'issue': f'Missing comma after closing brace before "{key}"',
                                'context': f'Line {prev_brace_line_num}: {prev_brace_line.strip()}\nLine {i}: {line.strip()}',
                                'prev_key': prev_key
                            })
                
                # Track this as the current map key at this depth
                current_map_keys[brace_depth] = key
        
        # Update brace depth
        if open_braces > 0:
            # Opening braces increase depth
            for _ in range(open_braces):
                brace_depth += 1
        
        if close_braces > 0:
            # Closing braces decrease depth
            for _ in range(close_braces):
                # Calculate parent depth (where we'll be after closing)
                parent_depth = max(0, brace_depth - 1)
                
                # Check if we're closing a map entry
                # The map entry is recorded at the depth where it started (parent_depth),
                # not at the current depth (which is one level deeper due to the opening brace)
                if parent_depth > 0 and parent_depth in current_map_keys:
                    # We're closing a map entry, record the closing brace at parent depth for sibling checking
                    last_closing_brace[parent_depth] = i
                    # Remove the map key entry since we've closed it
                    del current_map_keys[parent_depth]
                
                brace_depth = max(0, brace_depth - 1)
                # Keep tracking at current depth for sibling checking
    
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

