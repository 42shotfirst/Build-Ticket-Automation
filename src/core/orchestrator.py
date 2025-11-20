"""
Terraform Generation Orchestrator

Coordinates all extractors and generators to produce complete terraform configuration.
"""

from typing import Dict, Any, Optional
import os
import json

from ..extractors import (
    BuildEnvExtractor,
    ResourcesExtractor,
    NSGExtractor,
    APGWExtractor,
    ACRExtractor,
)
from ..generators import (
    CoreInfrastructureGenerator,
    NetworkingGenerator,
    NSGGenerator,
    VMGenerator,
)


class TerraformOrchestrator:
    """Orchestrates the complete terraform generation pipeline."""

    def __init__(self, excel_file_path: str):
        """
        Initialize orchestrator with Excel file.

        Args:
            excel_file_path: Path to the Excel (.xlsm) file
        """
        self.excel_file_path = excel_file_path

        # Initialize extractors
        self.build_env_extractor = BuildEnvExtractor(excel_file_path)
        self.resources_extractor = ResourcesExtractor(excel_file_path)
        self.nsg_extractor = NSGExtractor(excel_file_path)
        self.apgw_extractor = APGWExtractor(excel_file_path)
        self.acr_extractor = ACRExtractor(excel_file_path)

        # Extracted data (populated by extract_all())
        self.build_env_data = None
        self.resources_data = None
        self.nsg_data = None
        self.apgw_data = None
        self.acr_data = None

    def extract_all(self) -> Dict[str, Any]:
        """
        Extract data from all sheets.

        Returns:
            Dictionary containing all extracted data
        """
        print("Extracting data from Excel...")

        self.build_env_data = self.build_env_extractor.extract()
        print(f"  + Build_ENV: {len(self.build_env_data.get('virtual_machines', []))} VMs, "
              f"{len(self.build_env_data.get('subnets', []))} subnets, "
              f"{len(self.build_env_data.get('tags', {}))} tags")

        self.resources_data = self.resources_extractor.extract()
        print(f"  + Resources: {len(self.resources_data.get('terraform_variables', {}))} variables, "
              f"{len(self.resources_data.get('vm_configurations', []))} VM configs")

        self.nsg_data = self.nsg_extractor.extract()
        print(f"  + NSG: {len(self.nsg_data.get('rules', []))} rules")

        self.apgw_data = self.apgw_extractor.extract()
        print(f"  + APGW: {len(self.apgw_data.get('backend_address_pools', []))} pools, "
              f"{len(self.apgw_data.get('http_listeners', []))} listeners")

        self.acr_data = self.acr_extractor.extract()
        print(f"  + ACR: {len(self.acr_data.get('network_rules', []))} network rules")

        return {
            'build_env': self.build_env_data,
            'resources': self.resources_data,
            'nsg': self.nsg_data,
            'apgw': self.apgw_data,
            'acr': self.acr_data,
        }

    def generate_terraform(self, output_dir: str) -> Dict[str, str]:
        """
        Generate all terraform files.

        Args:
            output_dir: Directory to write terraform files to

        Returns:
            Dictionary mapping filenames to their content
        """
        if self.build_env_data is None:
            self.extract_all()

        print(f"\nGenerating terraform files to: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        all_files = {}

        # 1. Generate core infrastructure files
        print("\n1. Generating core infrastructure...")
        core_gen = CoreInfrastructureGenerator(self.build_env_data, self.resources_data)
        core_files = core_gen.generate(output_dir)
        all_files.update(core_files)
        print(f"   + Generated: {', '.join(core_files.keys())}")

        # 2. Generate networking files
        print("\n2. Generating networking resources...")
        net_gen = NetworkingGenerator(self.build_env_data)
        net_files = net_gen.generate(output_dir)
        all_files.update(net_files)
        print(f"   + Generated: {', '.join(net_files.keys())}")

        # 3. Generate VM and security files
        print("\n3. Generating VM and security resources...")
        vm_gen = VMGenerator(self.build_env_data, self.resources_data)
        vm_files = vm_gen.generate(output_dir)
        all_files.update(vm_files)
        print(f"   + Generated: {', '.join(vm_files.keys())}")

        # 4. Generate terraform.tfvars
        print("\n4. Generating terraform.tfvars...")
        tfvars_content = self._generate_tfvars(core_gen, net_gen, vm_gen)
        tfvars_path = os.path.join(output_dir, 'terraform.tfvars')
        with open(tfvars_path, 'w') as f:
            f.write(tfvars_content)
        all_files['terraform.tfvars'] = tfvars_content
        print(f"   + Generated: terraform.tfvars")

        # 5. Generate outputs.tf
        print("\n5. Generating outputs.tf...")
        outputs_content = self._generate_outputs_tf()
        outputs_path = os.path.join(output_dir, 'outputs.tf')
        with open(outputs_path, 'w') as f:
            f.write(outputs_content)
        all_files['outputs.tf'] = outputs_content
        print(f"   + Generated: outputs.tf")

        print(f"\nSuccessfully generated {len(all_files)} terraform files!")

        # 6. Run terraform fmt to format all files
        print("\n6. Formatting with terraform fmt...")
        self._run_terraform_fmt(output_dir)

        return all_files

    def _generate_tfvars(
        self,
        core_gen: CoreInfrastructureGenerator,
        net_gen: NetworkingGenerator,
        vm_gen: VMGenerator
    ) -> str:
        """
        Generate complete terraform.tfvars file.

        Args:
            core_gen: CoreInfrastructureGenerator instance
            net_gen: NetworkingGenerator instance
            vm_gen: VMGenerator instance

        Returns:
            terraform.tfvars content as string
        """
        # Collect all tfvars data
        tfvars_data = {}

        # Core infrastructure
        tfvars_data.update(core_gen.get_tfvars_content())

        # Networking
        tfvars_data.update(net_gen.get_tfvars_content())

        # NSG rules
        nsg_gen = NSGGenerator(self.nsg_data, self.build_env_data)
        tfvars_data.update(nsg_gen.get_tfvars_content())

        # VMs and security
        tfvars_data.update(vm_gen.get_tfvars_content())

        # Format as HCL
        return self._format_as_hcl(tfvars_data)

    def _format_as_hcl(self, data: Dict[str, Any]) -> str:
        """
        Format Python dictionary as HCL (Terraform tfvars format).

        Args:
            data: Dictionary of variable values

        Returns:
            HCL-formatted string
        """
        lines = []

        # Order of variables
        var_order = [
            'spn',
            'location',
            'resource_group_name',
            'application_security_groups',
            'disk_encryption_set_name',
            'user_assigned_identity_name',
            'key_vault',
            'existing_subnets',  # Changed from 'subnets'
            'private_endpoints',
            'network_security_rules',
            'vm_list',
            'common_tags',
            'resource_specific_tags',
        ]

        for var_name in var_order:
            if var_name in data:
                value = data[var_name]
                lines.append(self._format_variable(var_name, value))
                lines.append("")  # Blank line between sections

        # Add any remaining variables not in the order list
        for var_name, value in data.items():
            if var_name not in var_order:
                lines.append(self._format_variable(var_name, value))
                lines.append("")

        return "\n".join(lines)

    def _format_variable(self, name: str, value: Any, indent: int = 0) -> str:
        """Format a single variable in HCL."""
        indent_str = "  " * indent

        if value is None:
            return f"{indent_str}{name} = null"

        if isinstance(value, bool):
            return f"{indent_str}{name} = {str(value).lower()}"

        if isinstance(value, (int, float)):
            return f"{indent_str}{name} = {value}"

        if isinstance(value, str):
            # Escape quotes in strings
            escaped = value.replace('"', '\\"')
            return f"{indent_str}{name} = \"{escaped}\""

        if isinstance(value, list):
            if not value:
                return f"{indent_str}{name} = []"

            # Check if all items are simple values
            if all(isinstance(item, (str, int, float, bool, type(None))) for item in value):
                formatted_items = []
                for item in value:
                    if isinstance(item, str):
                        formatted_items.append(f'"{item}"')
                    elif isinstance(item, bool):
                        formatted_items.append(str(item).lower())
                    elif item is None:
                        formatted_items.append('null')
                    else:
                        formatted_items.append(str(item))
                return f"{indent_str}{name} = [{', '.join(formatted_items)}]"

            # Complex list of objects
            lines = [f"{indent_str}{name} = ["]
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{indent_str}  {{")
                    for key, val in item.items():
                        formatted = self._format_variable(key, val, indent + 2)
                        lines.append(formatted)
                    lines.append(f"{indent_str}  }},")
                else:
                    lines.append(f"{indent_str}  {self._format_value(item)},")
            lines.append(f"{indent_str}]")
            return "\n".join(lines)

        if isinstance(value, dict):
            lines = [f"{indent_str}{name} = {{"]
            # Special formatting for common_tags: quoted keys with trailing commas
            if name == 'common_tags':
                for key, val in value.items():
                    val_str = f'"{val}"' if isinstance(val, str) else str(val).lower() if isinstance(val, bool) else str(val)
                    lines.append(f'{indent_str}  "{key}" = {val_str},')
            else:
                for key, val in value.items():
                    formatted = self._format_variable(key, val, indent + 1)
                    lines.append(formatted)
            lines.append(f"{indent_str}}}")
            return "\n".join(lines)

        # Fallback
        return f"{indent_str}{name} = {str(value)}"

    def _format_value(self, value: Any) -> str:
        """Format a value without the variable name."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return f'"{value}"'
        return str(value)

    def _generate_outputs_tf(self) -> str:
        """Generate outputs.tf file."""
        # Read template if available
        template_path = 'terraform_files_pattern/outputs.tf'
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Basic outputs
            return '''# Terraform Outputs

output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "resource_group_id" {
  description = "The ID of the resource group"
  value       = azurerm_resource_group.rg.id
}

output "location" {
  description = "The Azure region location"
  value       = azurerm_resource_group.rg.location
}

output "key_vault_id" {
  description = "The ID of the Key Vault"
  value       = azurerm_key_vault.kvlt.id
}

output "key_vault_uri" {
  description = "The URI of the Key Vault"
  value       = azurerm_key_vault.kvlt.vault_uri
}

output "user_assigned_identity_id" {
  description = "The ID of the user assigned identity"
  value       = azurerm_user_assigned_identity.umid.id
}

output "disk_encryption_set_id" {
  description = "The ID of the disk encryption set"
  value       = azurerm_disk_encryption_set.dsk.id
}

output "vm_ids" {
  description = "Map of VM names to their IDs"
  value       = { for k, v in module.vm : k => v.id }
}

output "subnet_ids" {
  description = "Map of subnet keys to their IDs"
  value       = { for k, v in azurerm_subnet.snet : k => v.id }
}

output "asg_ids" {
  description = "Map of ASG keys to their IDs"
  value       = { for k, v in azurerm_application_security_group.asg : k => v.id }
}
'''

    def save_extracted_data(self, output_path: str):
        """
        Save extracted data to JSON file for debugging.

        Args:
            output_path: Path to save JSON file
        """
        if self.build_env_data is None:
            self.extract_all()

        data = {
            'build_env': self.build_env_data,
            'resources': self.resources_data,
            'nsg': self.nsg_data,
            'apgw': self.apgw_data,
            'acr': self.acr_data,
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"Saved extracted data to: {output_path}")

    def _run_terraform_fmt(self, directory: str) -> None:
        """
        Run terraform fmt on all .tf and .tfvars files in the directory.

        Args:
            directory: Path to the directory containing terraform files
        """
        import subprocess

        try:
            # Check if terraform is installed
            result = subprocess.run(
                ['terraform', 'version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print("   terraform command not found - skipping formatting")
                print("   Install terraform from: https://www.terraform.io/downloads")
                return

            # Run terraform fmt
            result = subprocess.run(
                ['terraform', 'fmt', directory],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                if result.stdout.strip():
                    formatted_files = result.stdout.strip().split('\n')
                    for file in formatted_files:
                        print(f"   + Formatted: {file}")
                else:
                    print("   + All files already properly formatted")
            else:
                print(f"   terraform fmt failed: {result.stderr}")

        except FileNotFoundError:
            print("   terraform command not found - skipping formatting")
            print("   Install terraform from: https://www.terraform.io/downloads")
        except subprocess.TimeoutExpired:
            print("   terraform fmt timed out")
        except Exception as e:
            print(f"   Error running terraform fmt: {e}")
