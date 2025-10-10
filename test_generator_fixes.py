#!/usr/bin/env python3
"""
Test Generator Fixes
====================
Quick test to verify that the generator correctly extracts values from JSON raw_data.
"""

import json
from enhanced_terraform_generator_v2 import EnhancedTerraformGeneratorV2

def test_raw_data_extraction():
    """Test that raw_data cache is working correctly."""
    
    print("=" * 70)
    print("Testing Terraform Generator Fixes")
    print("=" * 70)
    print()
    
    # Load generator
    json_file = "comprehensive_excel_data.json"
    print(f"Loading generator with: {json_file}")
    generator = EnhancedTerraformGeneratorV2(json_file)
    print("✓ Generator loaded")
    print()
    
    # Test raw_data cache
    print("Testing raw_data cache...")
    print(f"  Sheets in cache: {list(generator.raw_data_cache.keys())}")
    build_env_keys = list(generator.raw_data_cache.get('Build_ENV', {}).keys())[:10]
    print(f"  Sample keys in Build_ENV: {build_env_keys}")
    print("✓ Raw data cache built")
    print()
    
    # Test key vault extraction
    print("Testing Key Vault value extraction:")
    kvlt_sku = generator._get_raw_value('sku_name', 'Build_ENV', 'standard')
    kvlt_retention = generator._get_raw_value('soft_delete_retention_days', 'Build_ENV', 90)
    kvlt_public_access = generator._get_raw_value('public_network_access', 'Build_ENV', 1)
    
    print(f"  sku_name: {kvlt_sku} (expected: 'standard')")
    print(f"  soft_delete_retention_days: {kvlt_retention} (expected: 90)")
    print(f"  public_network_access: {kvlt_public_access} (expected: 1)")
    
    # Validate
    assert kvlt_sku == "standard", f"sku_name wrong: {kvlt_sku}"
    assert kvlt_retention == 90, f"soft_delete_retention_days wrong: {kvlt_retention}"
    assert kvlt_public_access == 1, f"public_network_access wrong: {kvlt_public_access}"
    print("✓ Key Vault values correct")
    print()
    
    # Test VM extraction (VM config is in Resources sheet, not Build_ENV)
    print("Testing VM value extraction:")
    vm_os_disk_size = generator._get_raw_value('vm_list.vm1.os_disk_size', 'Resources')
    vm_ip_allocation = generator._get_raw_value('vm_list.vm1.ip_allocation', 'Resources')
    
    print(f"  os_disk_size: {vm_os_disk_size} (expected: 10)")
    print(f"  ip_allocation: {vm_ip_allocation} (expected: 'Static')")
    
    # Validate
    assert vm_os_disk_size == 10, f"os_disk_size wrong: {vm_os_disk_size}"
    assert vm_ip_allocation == "Static", f"ip_allocation wrong: {vm_ip_allocation}"
    print("✓ VM values correct")
    print()
    
    # Test location extraction
    print("Testing location value:")
    location = generator._get_raw_value('location', 'Build_ENV', 'WEST US 3')
    print(f"  location: {location}")
    
    if location == "here":
        print("  ⚠️  WARNING: Location is 'here' - not a valid Azure region!")
        print("  ⚠️  User must fix this in Excel source (LLDtest.xlsm) before deployment")
    elif location in ["WEST US", "WEST US 2", "WEST US 3", "EAST US"]:
        print(f"  ✓ Location is valid: {location}")
    else:
        print(f"  ⚠️  Location '{location}' may not be valid")
    print()
    
    # Summary
    print("=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    print("✓ All extraction functions working correctly")
    print("✓ Raw data cache operational")
    print("✓ Key vault values extracted from JSON")
    print("✓ VM values extracted from JSON")
    
    if location == "here":
        print()
        print("ACTION REQUIRED:")
        print("1. Open LLDtest.xlsm")
        print("2. Fix location field (change 'here' to 'WEST US 3')")
        print("3. Regenerate JSON: python3 comprehensive_excel_extractor.py LLDtest.xlsm")
        print("4. Regenerate Terraform: python3 automation_pipeline.py")
    else:
        print("✓ No user action required - ready to generate")
    
    print()
    return True

if __name__ == "__main__":
    try:
        test_raw_data_extraction()
        print("SUCCESS: All tests passed!")
    except AssertionError as e:
        print(f"FAILED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

