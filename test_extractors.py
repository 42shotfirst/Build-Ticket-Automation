"""
Test script for the new modular extractors.

Tests each extractor to verify it correctly reads data from the Excel sheets.
"""

import json
from src.extractors import (
    BuildEnvExtractor,
    ResourcesExtractor,
    NSGExtractor,
    APGWExtractor,
    ACRExtractor,
)


def test_build_env_extractor():
    """Test Build_ENV sheet extractor."""
    print("="*80)
    print("TESTING BUILD_ENV EXTRACTOR")
    print("="*80)

    extractor = BuildEnvExtractor('sourcefiles/test_data.xlsm')
    data = extractor.extract()

    print("\n1. Metadata:")
    for key, value in list(data['metadata'].items())[:5]:
        print(f"  {key}: {value}")

    print(f"\n2. Tags ({len(data['tags'])} found):")
    for key, value in list(data['tags'].items())[:5]:
        print(f"  {key}: {value}")

    print(f"\n3. Subscription: {data['subscription']}")

    print(f"\n4. Resource Group:")
    for key, value in data['resource_group'].items():
        print(f"  {key}: {value}")

    print(f"\n5. Location: {data['location']}")

    print(f"\n6. Application Security Groups ({len(data['application_security_groups'])} found):")
    for idx, asg in enumerate(data['application_security_groups'], 1):
        print(f"  ASG {idx}:")
        for key, value in asg.items():
            print(f"    {key}: {value}")

    print(f"\n7. Subnets ({len(data['subnets'])} found):")
    for idx, subnet in enumerate(data['subnets'], 1):
        print(f"  Subnet {idx}:")
        for key, value in list(subnet.items())[:5]:
            print(f"    {key}: {value}")

    print(f"\n8. Private Endpoints ({len(data['private_endpoints'])} found):")
    for idx, pe in enumerate(data['private_endpoints'], 1):
        print(f"  PE {idx}:")
        for key, value in pe.items():
            print(f"    {key}: {value}")

    print(f"\n9. User Assigned Identity:")
    for key, value in data['user_assigned_identity'].items():
        print(f"  {key}: {value}")

    print(f"\n10. Key Vault:")
    for key, value in list(data['key_vault'].items())[:5]:
        print(f"  {key}: {value}")

    print(f"\n11. Disk Encryption Set:")
    for key, value in data['disk_encryption_set'].items():
        print(f"  {key}: {value}")

    print(f"\n12. Virtual Machines ({len(data['virtual_machines'])} found):")
    for idx, vm in enumerate(data['virtual_machines'], 1):
        print(f"  VM {idx}:")
        for key, value in list(vm.items())[:8]:
            print(f"    {key}: {value}")

    return data


def test_resources_extractor():
    """Test Resources sheet extractor."""
    print("\n" + "="*80)
    print("TESTING RESOURCES EXTRACTOR")
    print("="*80)

    extractor = ResourcesExtractor('sourcefiles/test_data.xlsm')
    data = extractor.extract()

    print(f"\n1. Total Terraform Variables: {len(data['terraform_variables'])}")
    print("   Sample variables:")
    for key, value in list(data['terraform_variables'].items())[:10]:
        print(f"  {key}: {value}")

    print(f"\n2. VM Configurations ({len(data['vm_configurations'])} found):")
    for idx, vm in enumerate(data['vm_configurations'], 1):
        print(f"  {vm.get('key', f'vm{idx}')}:")
        for key, value in list(vm.items())[:5]:
            print(f"    {key}: {value}")

    print(f"\n3. Tags from Resources: {len(data['tags'])} found")

    return data


def test_nsg_extractor():
    """Test NSG sheet extractor."""
    print("\n" + "="*80)
    print("TESTING NSG EXTRACTOR")
    print("="*80)

    extractor = NSGExtractor('sourcefiles/test_data.xlsm')
    data = extractor.extract()

    print(f"\n1. Headers: {data['headers']}")

    print(f"\n2. NSG Rules ({len(data['rules'])} found):")
    for idx, rule in enumerate(data['rules'], 1):
        print(f"  Rule {idx}: {rule}")

    print(f"\n3. Terraform-formatted Rules:")
    tf_rules = extractor.get_rules_for_terraform()
    for idx, rule in enumerate(tf_rules[:3], 1):
        print(f"  Rule {idx}:")
        for key, value in rule.items():
            print(f"    {key}: {value}")

    return data


def test_apgw_extractor():
    """Test APGW sheet extractor."""
    print("\n" + "="*80)
    print("TESTING APGW EXTRACTOR")
    print("="*80)

    extractor = APGWExtractor('sourcefiles/test_data.xlsm')
    data = extractor.extract()

    print(f"\n1. Backend Address Pools ({len(data['backend_address_pools'])} found):")
    for idx, pool in enumerate(data['backend_address_pools'], 1):
        print(f"  Pool {idx}: {pool}")

    print(f"\n2. Backend HTTP Settings ({len(data['backend_http_settings'])} found):")
    for idx, setting in enumerate(data['backend_http_settings'], 1):
        print(f"  Setting {idx}:")
        for key, value in list(setting.items())[:5]:
            print(f"    {key}: {value}")

    print(f"\n3. Frontend IP Configurations ({len(data['frontend_ip_configurations'])} found):")
    for idx, config in enumerate(data['frontend_ip_configurations'], 1):
        print(f"  Config {idx}:")
        for key, value in config.items():
            print(f"    {key}: {value}")

    print(f"\n4. Frontend Ports ({len(data['frontend_ports'])} found):")
    for idx, port in enumerate(data['frontend_ports'], 1):
        print(f"  Port {idx}: {port}")

    print(f"\n5. HTTP Listeners ({len(data['http_listeners'])} found):")
    for idx, listener in enumerate(data['http_listeners'], 1):
        print(f"  Listener {idx}:")
        for key, value in list(listener.items())[:5]:
            print(f"    {key}: {value}")

    print(f"\n6. Total All Variables: {len(data['all_variables'])}")

    return data


def test_acr_extractor():
    """Test ACR NRS sheet extractor."""
    print("\n" + "="*80)
    print("TESTING ACR EXTRACTOR")
    print("="*80)

    extractor = ACRExtractor('sourcefiles/test_data.xlsm')
    data = extractor.extract()

    print(f"\n1. Headers: {data['headers']}")

    print(f"\n2. Network Rules ({len(data['network_rules'])} found):")
    for idx, rule in enumerate(data['network_rules'], 1):
        print(f"  Rule {idx}: {rule}")

    print(f"\n3. Terraform-formatted Rules:")
    tf_rules = extractor.get_network_rules_for_terraform()
    for idx, rule in enumerate(tf_rules, 1):
        print(f"  Rule {idx}: {rule}")

    return data


def main():
    """Run all extractor tests."""
    print("\n" + "="*80)
    print("MODULAR EXTRACTOR TEST SUITE")
    print("="*80)
    print("\nTesting new modular extractors with proper column structure handling.")
    print("Each extractor respects its sheet's unique structure:")
    print("  - Build_ENV: Column B (TF Var) + Column C (Value)")
    print("  - Resources: Column B (TF Var) + Column C (Value)")
    print("  - NSG: Flat table with headers in Row 1")
    print("  - APGW: Column A (TF Var) + Column B (Value)")
    print("  - ACR NRS: Flat table with headers in Row 1")

    try:
        build_env_data = test_build_env_extractor()
        resources_data = test_resources_extractor()
        nsg_data = test_nsg_extractor()
        apgw_data = test_apgw_extractor()
        acr_data = test_acr_extractor()

        print("\n" + "="*80)
        print("ALL EXTRACTORS TESTED SUCCESSFULLY ✅")
        print("="*80)

        print("\nSummary:")
        print(f"  - Build_ENV: {len(build_env_data['virtual_machines'])} VMs, {len(build_env_data['subnets'])} subnets, {len(build_env_data['tags'])} tags")
        print(f"  - Resources: {len(resources_data['terraform_variables'])} variables, {len(resources_data['vm_configurations'])} VMs")
        print(f"  - NSG: {len(nsg_data['rules'])} rules")
        print(f"  - APGW: {len(apgw_data['backend_address_pools'])} pools, {len(apgw_data['http_listeners'])} listeners")
        print(f"  - ACR: {len(acr_data['network_rules'])} network rules")

        # Save sample output for review
        with open('extractor_test_output.json', 'w') as f:
            json.dump({
                'build_env': build_env_data,
                'resources': resources_data,
                'nsg': nsg_data,
                'apgw': apgw_data,
                'acr': acr_data,
            }, f, indent=2, default=str)

        print("\n✅ Sample output saved to: extractor_test_output.json")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
