#!/usr/bin/env python3
"""
Test Dynamic Output Directory Creation
=====================================
Test script to demonstrate the dynamic output folder creation based on 
Subscription field and timestamp.
"""

import os
import json
import sys
from datetime import datetime
from automation_pipeline import AutomationPipeline

def create_test_json_data():
    """Create test JSON data with subscription information."""
    
    test_data = {
        "sheets": {
            "Resources": {
                "key_value_pairs": {
                    "Project Name": "Test Project",
                    "Application Name": "Test App"
                }
            }
        },
        "build_environment": {
            "key_value_pairs": {
                "Subscription": "subscription-dev-001",
                "Location": "WEST US 3",
                "Resource Group": "rg-test-project-dev"
            }
        },
        "vm_instances": [
            {
                "Hostname": "test-vm-01",
                "Recommended SKU": "Standard_B2s_v2",
                "OS Image*": "Windows Server 2022"
            }
        ],
        "comprehensive_data": {
            "Build_ENV": {
                "key_value_pairs": {
                    "Subscription": "subscription-dev-001",
                    "Environment": "DEV"
                }
            }
        }
    }
    
    # Write test JSON file
    test_json_file = "test_subscription_data.json"
    with open(test_json_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Created test JSON file: {test_json_file}")
    return test_json_file

def test_dynamic_output_creation():
    """Test the dynamic output directory creation."""
    
    print("Testing Dynamic Output Directory Creation")
    print("=" * 50)
    
    # Create test JSON data
    test_json_file = create_test_json_data()
    
    try:
        # Create automation pipeline instance
        pipeline = AutomationPipeline("automation_config.json")
        
        # Test the dynamic output directory creation
        test_excel_file = "test_data.xlsx"
        
        print(f"\nTesting with JSON file: {test_json_file}")
        print(f"Excel file: {test_excel_file}")
        
        # Test the dynamic directory creation method
        output_dir = pipeline._create_dynamic_output_directory(test_json_file, test_excel_file)
        
        print(f"\nGenerated output directory: {output_dir}")
        
        # Test subscription extraction
        subscription = pipeline._extract_subscription_from_json(test_json_file)
        print(f"Extracted subscription: {subscription}")
        
        # Test directory name sanitization
        test_names = [
            "subscription-dev-001",
            "My Test Subscription",
            "sub@#$%^&*()script",
            "very-long-subscription-name-that-exceeds-fifty-characters-limit",
            "",
            "   spaces   "
        ]
        
        print(f"\nTesting directory name sanitization:")
        for name in test_names:
            sanitized = pipeline._sanitize_directory_name(name)
            print(f"  '{name}' -> '{sanitized}'")
        
        # Test different configuration patterns
        print(f"\nTesting different naming patterns:")
        
        # Test with subscription
        if subscription:
            patterns = [
                "{subscription}_{timestamp}",
                "terraform_{subscription}_{timestamp}",
                "{subscription}-deployment-{timestamp}",
                "output_{subscription}_{timestamp}"
            ]
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            clean_subscription = pipeline._sanitize_directory_name(subscription)
            
            for pattern in patterns:
                directory_name = pattern.format(subscription=clean_subscription, timestamp=timestamp)
                print(f"  Pattern '{pattern}' -> '{directory_name}'")
        
        print(f"\nSUCCESS: Dynamic output directory creation test completed!")
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if os.path.exists(test_json_file):
            os.remove(test_json_file)
            print(f"\nCleaned up test file: {test_json_file}")

def test_configuration_options():
    """Test different configuration options for dynamic output."""
    
    print("\nTesting Configuration Options")
    print("=" * 40)
    
    # Test different configurations
    configs = [
        {
            "name": "Default Configuration",
            "dynamic_folder_naming": True,
            "folder_naming_pattern": "{subscription}_{timestamp}",
            "fallback_folder_naming": "{excel_filename}_{timestamp}"
        },
        {
            "name": "Custom Pattern",
            "dynamic_folder_naming": True,
            "folder_naming_pattern": "terraform_{subscription}_{timestamp}",
            "fallback_folder_naming": "terraform_{excel_filename}_{timestamp}"
        },
        {
            "name": "Legacy Mode",
            "dynamic_folder_naming": False
        }
    ]
    
    for config in configs:
        print(f"\n{config['name']}:")
        print(f"  Dynamic naming: {config.get('dynamic_folder_naming', True)}")
        if config.get('dynamic_folder_naming', True):
            print(f"  Pattern: {config.get('folder_naming_pattern', 'default')}")
            print(f"  Fallback: {config.get('fallback_folder_naming', 'default')}")
        else:
            print(f"  Mode: Legacy (filename_terraform)")

def main():
    """Main test function."""
    
    print("Dynamic Output Directory Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Dynamic output creation
    test_dynamic_output_creation()
    
    # Test 2: Configuration options
    test_configuration_options()
    
    print(f"\n{'=' * 60}")
    print("All tests completed!")
    print(f"Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
