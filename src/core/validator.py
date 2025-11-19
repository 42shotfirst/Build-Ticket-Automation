#!/usr/bin/env python3
"""
Module 4: Terraform Validator
==============================
Unified validation framework for Terraform configurations.
Consolidates: production_readiness_validator.py, terraform_structure_validator.py,
              validate_terraform_commas.py
"""

import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class TerraformValidator:
    """Comprehensive Terraform configuration validator."""

    def __init__(self, terraform_dir: str):
        """
        Initialize the validator.

        Args:
            terraform_dir: Directory containing Terraform files
        """
        self.terraform_dir = terraform_dir
        self.results = {
            'syntax': {'passed': [], 'failed': []},
            'structure': {'passed': [], 'failed': []},
            'security': {'passed': [], 'failed': []},
            'naming': {'passed': [], 'failed': []},
            'completeness': {'passed': [], 'failed': []},
            'best_practices': {'passed': [], 'failed': []}
        }

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validations.

        Returns:
            Comprehensive validation report
        """
        self.validate_structure()
        self.validate_syntax()
        self.validate_security()
        self.validate_naming()
        self.validate_completeness()
        self.validate_best_practices()

        return self.generate_report()

    def validate_structure(self):
        """Validate file structure and organization."""
        required_files = ['main.tf', 'variables.tf', 'terraform.tfvars']
        optional_files = ['outputs.tf', 'data.tf', 'locals.tf']

        for file in required_files:
            path = os.path.join(self.terraform_dir, file)
            if os.path.exists(path):
                self.results['structure']['passed'].append(
                    f"Required file '{file}' exists"
                )
            else:
                self.results['structure']['failed'].append(
                    f"Missing required file: {file}"
                )

        for file in optional_files:
            path = os.path.join(self.terraform_dir, file)
            if os.path.exists(path):
                self.results['structure']['passed'].append(
                    f"Optional file '{file}' exists"
                )

    def validate_syntax(self):
        """Validate HCL syntax patterns."""
        tfvars_path = os.path.join(self.terraform_dir, 'terraform.tfvars')

        if not os.path.exists(tfvars_path):
            return

        with open(tfvars_path, 'r') as f:
            content = f.read()

        # Check for trailing commas
        trailing_comma_pattern = r',\s*\}'
        if re.search(trailing_comma_pattern, content):
            self.results['syntax']['failed'].append(
                "Trailing comma before closing brace found"
            )
        else:
            self.results['syntax']['passed'].append(
                "No trailing commas before closing braces"
            )

        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces == close_braces:
            self.results['syntax']['passed'].append(
                f"Balanced braces ({open_braces} pairs)"
            )
        else:
            self.results['syntax']['failed'].append(
                f"Unbalanced braces: {open_braces} open, {close_braces} close"
            )

        # Check for balanced brackets
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        if open_brackets == close_brackets:
            self.results['syntax']['passed'].append(
                f"Balanced brackets ({open_brackets} pairs)"
            )
        else:
            self.results['syntax']['failed'].append(
                f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"
            )

    def validate_security(self):
        """Validate security settings and best practices."""
        tfvars_path = os.path.join(self.terraform_dir, 'terraform.tfvars')

        if not os.path.exists(tfvars_path):
            return

        with open(tfvars_path, 'r') as f:
            content = f.read()

        # Check for placeholder subscription IDs
        if 'YOUR-AZURE-SUBSCRIPTION-ID' in content:
            self.results['security']['failed'].append(
                "Placeholder subscription ID detected"
            )
        else:
            self.results['security']['passed'].append(
                "No placeholder subscription IDs"
            )

        # Check for public network access
        if 'public_network_access' in content:
            if re.search(r'public_network_access\s*=\s*true', content):
                self.results['security']['failed'].append(
                    "Public network access enabled - review for security"
                )
            else:
                self.results['security']['passed'].append(
                    "Public network access disabled or not specified"
                )

        # Check for encryption settings
        if 'disk_encryption_set' in content:
            self.results['security']['passed'].append(
                "Disk encryption configuration present"
            )
        else:
            self.results['security']['failed'].append(
                "No disk encryption configuration found"
            )

    def validate_naming(self):
        """Validate naming conventions."""
        tfvars_path = os.path.join(self.terraform_dir, 'terraform.tfvars')

        if not os.path.exists(tfvars_path):
            return

        with open(tfvars_path, 'r') as f:
            content = f.read()

        # Check for test/placeholder names
        test_names = ['test', 'example', 'demo', 'bob', 'foo', 'bar']
        found_test_names = []

        for name in test_names:
            pattern = rf'["\']({name})["\']'
            if re.search(pattern, content, re.IGNORECASE):
                found_test_names.append(name)

        if found_test_names:
            self.results['naming']['failed'].append(
                f"Test/placeholder names found: {', '.join(found_test_names)}"
            )
        else:
            self.results['naming']['passed'].append(
                "No obvious test/placeholder names detected"
            )

        # Check naming patterns
        if re.search(r'resource_group_name\s*=\s*"rg-', content):
            self.results['naming']['passed'].append(
                "Resource group follows naming convention (rg-)"
            )

        if re.search(r'name\s*=\s*"kvlt-', content):
            self.results['naming']['passed'].append(
                "Key vault follows naming convention (kvlt-)"
            )

    def validate_completeness(self):
        """Validate configuration completeness."""
        tfvars_path = os.path.join(self.terraform_dir, 'terraform.tfvars')

        if not os.path.exists(tfvars_path):
            return

        with open(tfvars_path, 'r') as f:
            content = f.read()

        # Check for required variables
        required_vars = [
            'resource_group_name',
            'location',
            'common_tags'
        ]

        for var in required_vars:
            if var in content:
                self.results['completeness']['passed'].append(
                    f"Required variable '{var}' present"
                )
            else:
                self.results['completeness']['failed'].append(
                    f"Missing required variable: {var}"
                )

        # Check for tags
        required_tags = [
            'app-name',
            'environment',
            'it-cost-center'
        ]

        for tag in required_tags:
            if tag in content:
                self.results['completeness']['passed'].append(
                    f"Required tag '{tag}' present"
                )
            else:
                self.results['completeness']['failed'].append(
                    f"Missing required tag: {tag}"
                )

    def validate_best_practices(self):
        """Validate Terraform best practices."""

        # Check for variables.tf
        vars_path = os.path.join(self.terraform_dir, 'variables.tf')
        if os.path.exists(vars_path):
            with open(vars_path, 'r') as f:
                content = f.read()

            # Check for variable descriptions
            var_count = len(re.findall(r'variable\s+"', content))
            desc_count = len(re.findall(r'description\s*=', content))

            if var_count > 0 and desc_count >= var_count * 0.8:
                self.results['best_practices']['passed'].append(
                    f"Most variables have descriptions ({desc_count}/{var_count})"
                )
            elif var_count > 0:
                self.results['best_practices']['failed'].append(
                    f"Many variables lack descriptions ({desc_count}/{var_count})"
                )

        # Check main.tf for provider version pinning
        main_path = os.path.join(self.terraform_dir, 'main.tf')
        if os.path.exists(main_path):
            with open(main_path, 'r') as f:
                content = f.read()

            if 'required_providers' in content and 'version' in content:
                self.results['best_practices']['passed'].append(
                    "Provider versions are pinned"
                )
            else:
                self.results['best_practices']['failed'].append(
                    "Provider versions not pinned"
                )

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Returns:
            Validation report with summary and details
        """
        total_passed = sum(len(cat['passed']) for cat in self.results.values())
        total_failed = sum(len(cat['failed']) for cat in self.results.values())
        total_checks = total_passed + total_failed

        report = {
            'timestamp': datetime.now().isoformat(),
            'terraform_dir': self.terraform_dir,
            'summary': {
                'total_checks': total_checks,
                'passed': total_passed,
                'failed': total_failed,
                'pass_rate': f"{(total_passed / total_checks * 100):.1f}%" if total_checks > 0 else "0%",
                'overall_status': 'PASSED' if total_failed == 0 else 'FAILED'
            },
            'categories': {}
        }

        for category, results in self.results.items():
            cat_total = len(results['passed']) + len(results['failed'])
            report['categories'][category] = {
                'total': cat_total,
                'passed': len(results['passed']),
                'failed': len(results['failed']),
                'status': 'PASSED' if len(results['failed']) == 0 else 'FAILED',
                'details': results
            }

        return report

    def print_report(self, report: Optional[Dict] = None):
        """
        Print a formatted validation report.

        Args:
            report: Report to print (if None, generates new one)
        """
        if report is None:
            report = self.generate_report()

        print("\n" + "=" * 80)
        print("TERRAFORM VALIDATION REPORT")
        print("=" * 80)
        print(f"Directory: {report['terraform_dir']}")
        print(f"Timestamp: {report['timestamp']}")
        print()

        summary = report['summary']
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']}")
        print()

        for category, data in report['categories'].items():
            print(f"\n{category.upper()}: {data['status']}")
            print(f"  Passed: {data['passed']}/{data['total']}")

            if data['details']['failed']:
                print(f"  Failed checks:")
                for failure in data['details']['failed']:
                    print(f"    ✗ {failure}")

        print("\n" + "=" * 80)
