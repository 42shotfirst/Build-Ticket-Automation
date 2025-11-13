#!/usr/bin/env python3
"""
Production Readiness Validator for Terraform Configuration
===========================================================
Validates Terraform output for production use and identifies issues.
"""

import json
import os
import re
from typing import Dict, List, Tuple
from datetime import datetime


class ProductionReadinessValidator:
    """Validate Terraform configuration for production readiness."""

    def __init__(self, tfvars_path: str):
        """Initialize validator with terraform.tfvars path."""
        self.tfvars_path = tfvars_path
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        self.recommendations = []
        self.valid_values = []

    def validate_all(self) -> Dict:
        """Run all validation checks."""

        with open(self.tfvars_path, 'r') as f:
            content = f.read()

        # Parse the content
        self._validate_subscription_id(content)
        self._validate_resource_names(content)
        self._validate_network_config(content)
        self._validate_vm_config(content)
        self._validate_nsg_rules(content)
        self._validate_tags(content)
        self._validate_security_settings(content)
        self._validate_naming_conventions(content)

        return self._generate_report()

    def _validate_subscription_id(self, content: str):
        """Check for valid subscription ID."""

        if 'YOUR-AZURE-SUBSCRIPTION-ID' in content:
            self.issues['critical'].append({
                'field': 'Subscription ID',
                'issue': 'Placeholder subscription ID found',
                'location': 'subnets.snet1.network_security_group_id, route_table_id',
                'fix': 'Replace with actual Azure subscription ID (36 character UUID)'
            })
        elif 'subscription1' in content.lower() and '/subscriptions/' in content:
            self.issues['critical'].append({
                'field': 'Subscription ID',
                'issue': 'Test subscription ID "subscription1" is not valid',
                'location': 'subnets configuration',
                'fix': 'Use actual Azure subscription ID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
            })

    def _validate_resource_names(self, content: str):
        """Validate resource naming."""

        # Check for test/placeholder names
        test_names = ['bob', 'rsg1', 'test', 'default', 'vm1']

        for name in test_names:
            pattern = rf'"{name}"'
            if re.search(pattern, content, re.IGNORECASE):
                if name == 'bob':
                    self.issues['high'].append({
                        'field': 'Application Name',
                        'issue': f'Test application name "{name}" found',
                        'location': 'Multiple resources use "bob" as app name',
                        'fix': 'Use meaningful application name (e.g., "webportal", "dataprocessor")'
                    })
                elif name == 'rsg1':
                    self.issues['high'].append({
                        'field': 'Resource Group',
                        'issue': f'Non-descriptive resource group name "{name}"',
                        'location': 'resource_group_name',
                        'fix': 'Use pattern: rg-<app>-<env>-<region> (e.g., rg-webportal-uat-westus3)'
                    })

    def _validate_network_config(self, content: str):
        """Validate network configuration."""

        # Check subnet prefix
        if '10.0.1.0/24' in content:
            self.issues['medium'].append({
                'field': 'Subnet Prefix',
                'issue': 'Using default subnet prefix 10.0.1.0/24',
                'location': 'subnets.snet1.prefixes',
                'fix': 'Verify this doesn\'t conflict with existing network ranges'
            })

        # Check for hardcoded IPs
        if '4.4.4.4' in content:
            self.issues['high'].append({
                'field': 'IP Address',
                'issue': 'Invalid test IP address "4.4.4.4" found',
                'location': 'VM configuration or DNS settings',
                'fix': 'Use valid private IP from subnet range or remove if using dynamic allocation'
            })

    def _validate_vm_config(self, content: str):
        """Validate VM configuration."""

        # Check OS disk size
        if 'os_disk_size      = 10' in content:
            self.issues['critical'].append({
                'field': 'OS Disk Size',
                'issue': 'OS disk size of 10 GB is too small for production',
                'location': 'vm_list.vm1.os_disk_size',
                'fix': 'Windows VMs need minimum 127 GB, Linux minimum 30 GB'
            })

        # Check VM size
        if 'Standard_B2s' in content:
            self.issues['info'].append({
                'field': 'VM Size',
                'issue': 'Using burstable B-series VM (Standard_B2s)',
                'location': 'vm_list.vm1.size',
                'fix': 'Consider D-series or E-series for production workloads'
            })

        # Check admin username
        if 'cisadmin' in content:
            self.valid_values.append({
                'field': 'Admin Username',
                'value': 'cisadmin',
                'status': 'Good - using enterprise standard admin name'
            })

    def _validate_nsg_rules(self, content: str):
        """Validate network security group rules."""

        # Check for numeric/test values in NSG rules
        nsg_issues = []

        # Port ranges that are just numbers
        if 'source_port_range       = "1"' in content:
            nsg_issues.append('Source port "1" is not a valid port configuration')
        if 'source_port_range       = "2"' in content:
            nsg_issues.append('Source port "2" is not a valid port configuration')

        # Destination ports
        if 'destination_port_ranges = ["5"]' in content:
            nsg_issues.append('Destination port "5" is not a standard service port')
        if 'destination_port_ranges = ["6"]' in content:
            nsg_issues.append('Destination port "6" is not a standard service port')

        # ASG references that are numbers
        if 'source_asg              = "9"' in content:
            nsg_issues.append('Source ASG "9" is not a valid ASG reference')
        if 'destination_asg         = "13"' in content:
            nsg_issues.append('Destination ASG "13" is not a valid ASG reference')

        if nsg_issues:
            self.issues['critical'].append({
                'field': 'NSG Rules',
                'issue': 'Invalid test data in network security rules',
                'location': 'network_security_rules.rules',
                'problems': nsg_issues,
                'fix': 'Use valid ports (22, 443, 3389, etc.) and actual ASG names'
            })

        # Check rule names
        if '"one"' in content or '"two"' in content:
            self.issues['medium'].append({
                'field': 'NSG Rule Names',
                'issue': 'Non-descriptive rule names (one, two, three, four)',
                'location': 'network_security_rules.rules[].name',
                'fix': 'Use descriptive names: "allow-https-inbound", "allow-rdp-from-bastion"'
            })

    def _validate_tags(self, content: str):
        """Validate tagging strategy."""

        # Check for TBD values
        if '"TBD"' in content:
            self.issues['medium'].append({
                'field': 'Tags',
                'issue': 'TBD placeholder values in tags',
                'location': 'common_tags: cost-center, department, line-of-business',
                'fix': 'Provide actual cost center and department information'
            })

        # Check SNOW ticket
        if '"snow-item"   = "1"' in content:
            self.issues['high'].append({
                'field': 'ServiceNow Ticket',
                'issue': 'Invalid ServiceNow ticket number "1"',
                'location': 'common_tags.snow-item, vm tags',
                'fix': 'Use valid format: RITM0123456 or CHG0123456'
            })

        # Validate existing tags
        if '"environment"         = "UAT"' in content:
            self.valid_values.append({
                'field': 'Environment Tag',
                'value': 'UAT',
                'status': 'Valid environment designation'
            })

    def _validate_security_settings(self, content: str):
        """Validate security configurations."""

        # Check Key Vault settings
        if 'public_network_access      = true' in content:
            self.recommendations.append({
                'field': 'Key Vault Network Access',
                'recommendation': 'Consider restricting public network access for Key Vault',
                'current': 'public_network_access = true',
                'suggested': 'Use private endpoints for production'
            })

        # Check encryption
        if 'disk_encryption_set_name' in content:
            self.valid_values.append({
                'field': 'Disk Encryption',
                'value': 'Configured',
                'status': 'Good - disk encryption set is configured'
            })

        # Check managed identity
        if 'SystemAssigned, UserAssigned' in content:
            self.valid_values.append({
                'field': 'Managed Identity',
                'value': 'Both System and User Assigned',
                'status': 'Good - using managed identities'
            })

    def _validate_naming_conventions(self, content: str):
        """Validate Azure naming conventions."""

        # Check Key Vault name length
        kv_match = re.search(r'name\s*=\s*"(kv-[^"]+)"', content)
        if kv_match:
            kv_name = kv_match.group(1)
            if len(kv_name) < 3 or len(kv_name) > 24:
                self.issues['high'].append({
                    'field': 'Key Vault Name',
                    'issue': f'Name "{kv_name}" may not meet Azure requirements (3-24 chars)',
                    'location': 'key_vault.name',
                    'fix': 'Ensure name is 3-24 characters, alphanumeric and hyphens only'
                })
            else:
                self.valid_values.append({
                    'field': 'Key Vault Name',
                    'value': kv_name,
                    'status': 'Valid naming convention'
                })

    def _generate_report(self) -> Dict:
        """Generate comprehensive validation report."""

        report = {
            'timestamp': datetime.now().isoformat(),
            'file': self.tfvars_path,
            'summary': {
                'critical_issues': len(self.issues['critical']),
                'high_issues': len(self.issues['high']),
                'medium_issues': len(self.issues['medium']),
                'low_issues': len(self.issues['low']),
                'info_items': len(self.issues['info']),
                'valid_configurations': len(self.valid_values),
                'recommendations': len(self.recommendations)
            },
            'production_ready': len(self.issues['critical']) == 0,
            'issues': self.issues,
            'valid_values': self.valid_values,
            'recommendations': self.recommendations
        }

        return report


def generate_production_report(tfvars_path: str):
    """Generate and display production readiness report."""

    print("=" * 80)
    print("TERRAFORM PRODUCTION READINESS REPORT")
    print("=" * 80)
    print(f"File: {tfvars_path}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    validator = ProductionReadinessValidator(tfvars_path)
    report = validator.validate_all()

    # Display critical issues
    if report['issues']['critical']:
        print("\n🔴 CRITICAL ISSUES (Must fix before production):")
        print("-" * 60)
        for issue in report['issues']['critical']:
            print(f"\n  • {issue['field']}:")
            print(f"    Issue: {issue['issue']}")
            print(f"    Location: {issue['location']}")
            print(f"    Fix: {issue['fix']}")
            if 'problems' in issue:
                print(f"    Problems found:")
                for problem in issue['problems']:
                    print(f"      - {problem}")

    # Display high priority issues
    if report['issues']['high']:
        print("\n🟠 HIGH PRIORITY ISSUES:")
        print("-" * 60)
        for issue in report['issues']['high']:
            print(f"\n  • {issue['field']}:")
            print(f"    Issue: {issue['issue']}")
            print(f"    Fix: {issue['fix']}")

    # Display medium priority issues
    if report['issues']['medium']:
        print("\n🟡 MEDIUM PRIORITY ISSUES:")
        print("-" * 60)
        for issue in report['issues']['medium']:
            print(f"\n  • {issue['field']}:")
            print(f"    Issue: {issue['issue']}")
            print(f"    Fix: {issue['fix']}")

    # Display valid configurations
    if report['valid_values']:
        print("\n✅ VALID CONFIGURATIONS:")
        print("-" * 60)
        for valid in report['valid_values']:
            print(f"  • {valid['field']}: {valid['value']}")
            print(f"    Status: {valid['status']}")

    # Display recommendations
    if report['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 60)
        for rec in report['recommendations']:
            print(f"\n  • {rec['field']}:")
            print(f"    {rec['recommendation']}")

    # Production readiness summary
    print("\n" + "=" * 80)
    print("PRODUCTION READINESS SUMMARY")
    print("=" * 80)

    if report['production_ready']:
        print("✅ Configuration is READY for production")
    else:
        print("❌ Configuration is NOT ready for production")
        print(f"\nMust fix: {report['summary']['critical_issues']} critical issues")
        print(f"Should fix: {report['summary']['high_issues']} high priority issues")

    print("\nIssue Summary:")
    print(f"  • Critical: {report['summary']['critical_issues']}")
    print(f"  • High: {report['summary']['high_issues']}")
    print(f"  • Medium: {report['summary']['medium_issues']}")
    print(f"  • Low: {report['summary']['low_issues']}")
    print(f"  • Valid Items: {report['summary']['valid_configurations']}")

    # Save report to JSON
    report_file = "production_readiness_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")

    return report


def main():
    """Run production readiness validation."""

    tfvars_path = "terraform_output/terraform.tfvars"

    if not os.path.exists(tfvars_path):
        print(f"Error: {tfvars_path} not found")
        print("Please run terraform_generator_final.py first")
        return False

    report = generate_production_report(tfvars_path)

    # Generate action items
    print("\n" + "=" * 80)
    print("ACTION ITEMS FOR PRODUCTION DEPLOYMENT")
    print("=" * 80)

    action_items = [
        "1. Replace YOUR-AZURE-SUBSCRIPTION-ID with actual subscription ID",
        "2. Update OS disk size from 10 GB to 127 GB for Windows",
        "3. Replace test application name 'bob' with actual application name",
        "4. Update NSG rules with valid ports and ASG references",
        "5. Provide valid ServiceNow ticket number (RITM/CHG format)",
        "6. Update resource group name to follow naming convention",
        "7. Verify subnet CIDR doesn't conflict with existing networks",
        "8. Update cost center and department tags with actual values",
        "9. Consider using private endpoints for Key Vault",
        "10. Review VM size for production workload requirements"
    ]

    for item in action_items:
        print(f"  {item}")

    return not report['production_ready']


if __name__ == "__main__":
    main()