#!/usr/bin/env python3
"""
Column Referencing Demo
=======================
Demonstrates how to use column referencing and data access capabilities.
"""

import os
import sys
from data_accessor import ExcelDataAccessor

def demo_column_referencing():
    """Demonstrate column referencing capabilities."""
    
    json_file = "comprehensive_excel_data.json"
    
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        print("Please run the Excel conversion first: python main.py")
        return False
    
    print("=" * 80)
    print("COLUMN REFERENCING DEMO")
    print("=" * 80)
    
    # Create data accessor
    accessor = ExcelDataAccessor(json_file)
    
    # Show available sheets
    print("\n1. Available Sheets:")
    sheet_names = accessor.get_sheet_names()
    for i, sheet_name in enumerate(sheet_names, 1):
        info = accessor.get_sheet_info(sheet_name)
        print(f"   {i}. {sheet_name} ({info['dimensions']['rows']}x{info['dimensions']['columns']}, {info['table_count']} tables)")
    
    # Demo 1: Get project information using keywords
    print("\n2. Getting Project Information:")
    project_name = accessor.get_value_by_keywords("Resources", ["project", "name"])
    app_name = accessor.get_value_by_keywords("Resources", ["app", "name"])
    app_owner = accessor.get_value_by_keywords("Resources", ["app", "owner"])
    
    print(f"   Project Name: {project_name}")
    print(f"   Application Name: {app_name}")
    print(f"   App Owner: {app_owner}")
    
    # Demo 2: Get VM data from specific columns
    print("\n3. Getting VM Data:")
    vm_table = accessor.get_table_by_headers("Resources", ["hostname", "vm", "server"])
    if vm_table:
        print(f"   Found VM table with {vm_table['row_count']} rows")
        print(f"   Headers: {vm_table['headers'][:5]}...")  # Show first 5 headers
        
        # Get hostname column data
        hostnames = accessor.get_column_data("Resources", "Hostname", 0)
        print(f"   Hostnames found: {len(hostnames)}")
        for i, hostname in enumerate(hostnames[:5]):  # Show first 5
            print(f"     {i+1}. {hostname}")
        if len(hostnames) > 5:
            print(f"     ... and {len(hostnames) - 5} more")
    
    # Demo 3: Get NSG rules
    print("\n4. Getting Network Security Group Rules:")
    nsg_table = accessor.get_table_by_headers("NSG", ["name", "direction", "access"])
    if nsg_table:
        print(f"   Found NSG table with {nsg_table['row_count']} rules")
        for i, rule in enumerate(nsg_table['data'][:3]):  # Show first 3 rules
            print(f"     Rule {i+1}: {rule.get('name', 'N/A')} - {rule.get('direction', 'N/A')} {rule.get('access', 'N/A')}")
    
    # Demo 4: Search for specific data
    print("\n5. Searching for 'Morgan' across all sheets:")
    search_results = accessor.search_across_sheets("Morgan")
    for sheet_name, matches in search_results.items():
        print(f"   {sheet_name}: {len(matches)} matches")
        for match in matches[:2]:  # Show first 2 matches per sheet
            print(f"     - {match['location']}: {match.get('value', match.get('key', 'N/A'))}")
    
    # Demo 5: Get specific column data using keywords
    print("\n6. Getting Data from Specific Columns:")
    
    # Try to find VM size column
    vm_size_column = accessor.get_column_by_keywords("Resources", ["sku", "size", "vm"], 0)
    if vm_size_column:
        vm_sizes = accessor.get_column_data("Resources", vm_size_column, 0)
        print(f"   VM Sizes found: {len(vm_sizes)}")
        unique_sizes = list(set(vm_sizes))[:5]  # Show first 5 unique sizes
        for size in unique_sizes:
            print(f"     - {size}")
    
    # Demo 6: Export Terraform-ready data
    print("\n7. Exporting Terraform-Ready Data:")
    terraform_file = accessor.export_terraform_data("demo_terraform_data.json")
    print(f"   Terraform data exported to: {terraform_file}")
    
    # Show summary
    print("\n8. Data Summary:")
    summary = accessor.get_summary()
    print(f"   Total Sheets: {summary['total_sheets']}")
    print(f"   Total Tables: {summary['total_tables']}")
    print(f"   Key-Value Pairs: {summary['total_key_value_pairs']}")
    print(f"   Formulas: {summary['formula_count']}")
    print(f"   Macros: {'Yes' if summary['has_macros'] else 'No'}")
    
    print("\n" + "=" * 80)
    print("COLUMN REFERENCING DEMO COMPLETED")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Sheet information and structure")
    print("  ✓ Keyword-based data retrieval")
    print("  ✓ Column data extraction")
    print("  ✓ Table searching and filtering")
    print("  ✓ Cross-sheet data search")
    print("  ✓ Terraform-ready data export")
    print("\nYou can now use these methods to:")
    print("  - Reference specific columns by keywords")
    print("  - Extract data for Terraform generation")
    print("  - Search and filter data across sheets")
    print("  - Build custom data processing pipelines")
    
    return True

def demo_terraform_generation():
    """Demonstrate Terraform generation with column referencing."""
    
    print("\n" + "=" * 80)
    print("TERRAFORM GENERATION DEMO")
    print("=" * 80)
    
    # Import the enhanced terraform generator
    from enhanced_terraform_generator import EnhancedTerraformGenerator
    
    json_file = "comprehensive_excel_data.json"
    
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return False
    
    # Create generator
    generator = EnhancedTerraformGenerator(json_file)
    
    # Show what will be generated
    summary = generator.generate_summary()
    print(f"\nTerraform Generation Summary:")
    print(f"  Project: {summary['project_name']}")
    print(f"  Application: {summary['application_name']}")
    print(f"  VMs: {summary['resources']['virtual_machines']}")
    print(f"  Security Rules: {summary['resources']['network_security_rules']}")
    
    # Show VM details
    if summary['vm_details']:
        print(f"\nVM Details:")
        for i, vm in enumerate(summary['vm_details'][:5]):  # Show first 5 VMs
            print(f"  {i+1}. {vm['name']} - {vm['size']} - {vm['os']}")
        if len(summary['vm_details']) > 5:
            print(f"  ... and {len(summary['vm_details']) - 5} more VMs")
    
    # Show security rules
    if summary['security_rules']:
        print(f"\nSecurity Rules:")
        for i, rule in enumerate(summary['security_rules'][:5]):  # Show first 5 rules
            print(f"  {i+1}. {rule['name']} - {rule['direction']} {rule['access']} {rule['protocol']}")
        if len(summary['security_rules']) > 5:
            print(f"  ... and {len(summary['security_rules']) - 5} more rules")
    
    print(f"\n✓ Terraform generation ready!")
    print(f"  Run: python enhanced_terraform_generator.py {json_file}")
    
    return True

def main():
    """Main demo function."""
    
    print("Excel Data Access and Terraform Generation Demo")
    print("=" * 60)
    
    # Run column referencing demo
    success1 = demo_column_referencing()
    
    # Run terraform generation demo
    success2 = demo_terraform_generation()
    
    if success1 and success2:
        print("\n✓ All demos completed successfully!")
        return True
    else:
        print("\n✗ Some demos failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
