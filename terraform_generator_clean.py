#!/usr/bin/env python3
"""
Terraform Generator - Clean Production Version
===============================================
Generates Terraform configuration without emojis and with proper formatting.
"""

import json
import os
from typing import Dict, Any, List, Optional
from excel_data_mapper import ExcelDataMapper


class TerraformGeneratorClean:
    """Generate clean Terraform configuration for production use."""

    def __init__(self, json_file_path: str):
        """Initialize with JSON file path."""
        self.mapper = ExcelDataMapper(json_file_path)
        self.clean_values = self.mapper.get_clean_terraform_values()

    def generate_all(self, output_dir: str = "terraform_clean") -> Dict[str, str]:
        """Generate all Terraform files."""

        os.makedirs(output_dir, exist_ok=True)
        generated_files = {}

        # Generate main.tf
        main_tf = self._generate_main_tf()
        main_tf_path = os.path.join(output_dir, "main.tf")
        with open(main_tf_path, 'w', encoding='utf-8') as f:
            f.write(main_tf)
        generated_files['main.tf'] = main_tf_path

        # Generate variables.tf
        variables_tf = self._generate_variables_tf()
        variables_path = os.path.join(output_dir, "variables.tf")
        with open(variables_path, 'w', encoding='utf-8') as f:
            f.write(variables_tf)
        generated_files['variables.tf'] = variables_path

        # Generate terraform.tfvars
        tfvars = self._generate_tfvars()
        tfvars_path = os.path.join(output_dir, "terraform.tfvars")
        with open(tfvars_path, 'w', encoding='utf-8') as f:
            f.write(tfvars)
        generated_files['terraform.tfvars'] = tfvars_path

        # Generate outputs.tf
        outputs_tf = self._generate_outputs_tf()
        outputs_path = os.path.join(output_dir, "outputs.tf")
        with open(outputs_path, 'w', encoding='utf-8') as f:
            f.write(outputs_tf)
        generated_files['outputs.tf'] = outputs_path

        return generated_files

    def _generate_main_tf(self) -> str:
        """Generate main.tf with module call."""

        # Get actual module version or use default
        module_version = self.clean_values.get('module_version', '1.0.0')

        return f'''# main.tf
# Generated from Excel data

terraform {{
  required_version = ">= 1.0"

  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{
    key_vault {{
      purge_soft_delete_on_destroy = false
    }}
  }}
}}

module "base-vm" {{
  source  = "app.terraform.io/wab-cloudengineering-org/base-vm/iac"
  version = "{module_version}"

  # Core configuration
  spn                 = var.spn
  location            = var.location
  resource_group_name = var.resource_group_name

  # Security groups
  application_security_groups = var.application_security_groups

  # Key vault and identity
  key_vault                   = var.key_vault
  user_assigned_identity_name = var.user_assigned_identity_name
  disk_encryption_set_name    = var.disk_encryption_set_name

  # Networking
  subnets           = var.subnets
  private_endpoints = var.private_endpoints

  # VM configuration
  admin_username = var.admin_username
  admin_password = var.admin_password
  vm_list        = var.vm_list

  # Security rules
  network_security_rules = var.network_security_rules

  # Tags
  common_tags            = var.common_tags
  resource_specific_tags = var.resource_specific_tags
}}
'''

    def _generate_variables_tf(self) -> str:
        """Generate variables.tf."""

        location = self._fix_location(self.clean_values.get('location', 'West US 3'))

        return f'''# variables.tf
# Generated from Excel data

variable "spn" {{
  type        = string
  description = "Service Principal Name"
}}

variable "location" {{
  type        = string
  default     = "{location}"
  description = "Azure region for resources"
}}

variable "resource_group_name" {{
  type        = string
  description = "Resource group name"
}}

variable "application_security_groups" {{
  type = map(object({{
    name = string
  }}))
  description = "Application security groups"
}}

variable "key_vault" {{
  type = object({{
    name                       = string
    sku_name                   = string
    soft_delete_retention_days = number
    public_network_access      = bool
    snet_key                   = string
    key_name                   = string
  }})
  description = "Key vault configuration"
}}

variable "user_assigned_identity_name" {{
  type        = string
  description = "User assigned identity name"
}}

variable "disk_encryption_set_name" {{
  type        = string
  description = "Disk encryption set name"
}}

variable "subnets" {{
  type = map(object({{
    resource_group_name         = string
    virtual_network_name        = string
    network_security_group_id   = string
    route_table_id              = string
    name                        = string
    prefixes                    = list(string)
    service_endpoints           = list(string)
  }}))
  description = "Subnet configurations"
}}

variable "private_endpoints" {{
  type = map(object({{
    name              = string
    subresource_names = list(string)
    snet_key          = string
    asg_key           = string
  }}))
  description = "Private endpoint configurations"
}}

variable "admin_username" {{
  type        = string
  default     = "azureadmin"
  description = "VM admin username"
}}

variable "admin_password" {{
  type        = string
  sensitive   = true
  description = "VM admin password"
}}

variable "vm_list" {{
  type = map(object({{
    name              = string
    size              = string
    zone              = optional(string)
    image_os          = string
    marketplace_image = bool
    image_urn         = string
    ip_allocation     = string
    ip_address        = optional(string)
    identity_type     = string
    os_disk_size      = number
    os_disk_type      = string
    os_disk_tier      = optional(string)
    data_disk_sizes   = list(number)
    data_disk_type    = string
    snet_key          = string
    asg_key           = string
    tags              = map(string)
  }}))
  description = "Virtual machine configurations"
}}

variable "network_security_rules" {{
  type = object({{
    resource_group_name         = string
    network_security_group_name = string
    rules = list(object({{
      name                    = string
      priority                = number
      direction               = string
      access                  = string
      protocol                = string
      source_port_range       = string
      destination_port_ranges = list(string)
      source_asg              = string
      destination_asg         = string
      description             = string
    }}))
  }})
  description = "Network security rules"
}}

variable "common_tags" {{
  type        = map(string)
  description = "Common tags for all resources"
}}

variable "resource_specific_tags" {{
  type        = map(map(string))
  default     = {{}}
  description = "Resource-specific tags"
}}
'''

    def _generate_tfvars(self) -> str:
        """Generate terraform.tfvars with actual Excel values."""

        # Extract values
        build_env = self.clean_values
        vm_config = build_env.get('vm_configuration', {})
        project_info = build_env.get('project_info', {})
        nsg_rules = build_env.get('nsg_rules', [])

        # Fix location value
        location = self._fix_location(build_env.get('location', 'West US 3'))

        # Get subscription ID
        subscription = build_env.get('subscription', 'subscription1')
        if subscription == 'subscription1':
            subscription_id = "YOUR-AZURE-SUBSCRIPTION-ID"
            subscription_comment = "  # TODO: Update with actual Azure subscription ID"
        else:
            subscription_id = subscription
            subscription_comment = ""

        # Resource names from Excel data
        resource_group = build_env.get('resource_group_name', 'rsg1')
        app_name = project_info.get('application_name', 'app')
        environment = project_info.get('environment', 'UAT')
        snow_ticket = project_info.get('service_now_ticket', 'RITM0000000')

        # Generate VM configuration
        vm_name = vm_config.get('name', f"vm-{app_name}-01")
        vm_size = vm_config.get('size', 'Standard_B2s')
        os_type = vm_config.get('os_type', 'windows')
        os_disk_size = vm_config.get('os_disk_size', 127)
        os_disk_type = vm_config.get('os_disk_type', 'StandardSSD_LRS')
        ip_allocation = vm_config.get('ip_allocation', 'Dynamic')
        ip_address = vm_config.get('ip_address')
        admin_username = vm_config.get('admin_username', 'azureadmin')

        # Get data disk configuration from Excel or use defaults
        data_disk_sizes = vm_config.get('data_disk_sizes', [50, 50])
        if not isinstance(data_disk_sizes, list):
            data_disk_sizes = [50, 50]
        data_disk_type = vm_config.get('data_disk_type', 'Standard_LRS')

        # Get network prefix from Excel or use default
        network_prefix = build_env.get('network_prefix', '10.0.1.0/24')
        if not network_prefix or network_prefix == '':
            network_prefix = '10.0.1.0/24'

        # Determine image URN
        if os_type == 'windows':
            image_urn = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
        else:
            image_urn = "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest"

        # Format IP address line
        ip_address_line = f'''
    ip_address        = "{ip_address}"''' if ip_address else ""

        # Format NSG rules with proper separators
        formatted_rules = []
        for i, rule in enumerate(nsg_rules):
            priority = 100 + (i * 10)

            # Extract values with defaults
            name = rule.get('name', f'rule_{i+1}')
            direction = rule.get('direction', 'Inbound')
            access = rule.get('access', 'Allow')
            protocol = rule.get('protocol', 'Tcp')
            source_port = str(rule.get('source_port_range', '*'))

            # Handle destination ports
            dest_ports = rule.get('destination_port_ranges', ['443'])
            if not isinstance(dest_ports, list):
                dest_ports = [str(dest_ports)]
            dest_ports_formatted = ', '.join(f'"{p}"' for p in dest_ports)

            # Handle ASGs
            source_asg = str(rule.get('source_asg', 'asg_nic'))
            dest_asg = str(rule.get('destination_asg', 'asg_nic'))
            description = str(rule.get('description', f'Security rule {i+1}'))

            rule_text = f'''    {{
      name                    = "{name}"
      priority                = {priority}
      direction               = "{direction}"
      access                  = "{access}"
      protocol                = "{protocol}"
      source_port_range       = "{source_port}"
      destination_port_ranges = [{dest_ports_formatted}]
      source_asg              = "{source_asg}"
      destination_asg         = "{dest_asg}"
      description             = "{description}"
    }}'''
            formatted_rules.append(rule_text)

        # Join rules with commas
        rules_string = ',\n'.join(formatted_rules) if formatted_rules else ''

        return f'''# terraform.tfvars
# Generated from Excel data extraction

# Service Principal
spn = "spn-{app_name}-{environment.lower()}"

# Location
location = "{location}"

# Resource Group
resource_group_name = "{resource_group}"

# Application Security Groups
application_security_groups = {{
  asg_nic = {{
    name = "asg-{app_name}-nic-{environment.lower()}"
  }},
  asg_pe = {{
    name = "asg-{app_name}-pe-{environment.lower()}"
  }}
}}

# Key Vault Configuration
key_vault = {{
  name                       = "kv-{app_name[:20]}-{environment.lower()}"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-{app_name}-{environment.lower()}"
}}

# Identity and Encryption
user_assigned_identity_name = "id-{app_name}-{environment.lower()}"
disk_encryption_set_name    = "des-{app_name}-{environment.lower()}"

# Admin credentials
admin_username = "{admin_username}"
# admin_password = "CHANGE-ME-IN-KEYVAULT"  # Store in Key Vault, not in code

# Subnet Configuration
subnets = {{
  snet1 = {{
    resource_group_name  = "{resource_group}-network"
    virtual_network_name = "vnet-{app_name}-{environment.lower()}"
    network_security_group_id = "/subscriptions/{subscription_id}/resourceGroups/{resource_group}-network/providers/Microsoft.Network/networkSecurityGroups/nsg-{app_name}-{environment.lower()}"{subscription_comment}
    route_table_id            = "/subscriptions/{subscription_id}/resourceGroups/{resource_group}-network/providers/Microsoft.Network/routeTables/rt-{app_name}-{environment.lower()}"{subscription_comment}
    name              = "snet-{app_name}-{environment.lower()}"
    prefixes          = ["{network_prefix}"]
    service_endpoints = ["Microsoft.KeyVault"]
  }}
}}

# Private Endpoints
private_endpoints = {{
  pe_kvlt = {{
    name              = "pe-kv-{app_name}-{environment.lower()}"
    subresource_names = ["vault"]
    snet_key          = "snet1"
    asg_key           = "asg_pe"
  }}
}}

# Virtual Machines
vm_list = {{
  vm1 = {{
    name              = "{vm_name}"
    size              = "{vm_size}"
    zone              = null
    image_os          = "{os_type}"
    marketplace_image = false
    image_urn         = "{image_urn}"
    ip_allocation     = "{ip_allocation}"{ip_address_line}
    identity_type     = "SystemAssigned, UserAssigned"
    os_disk_size      = {os_disk_size}
    os_disk_type      = "{os_disk_type}"
    os_disk_tier      = null
    data_disk_sizes   = {data_disk_sizes}
    data_disk_type    = "{data_disk_type}"
    snet_key          = "snet1"
    asg_key           = "asg_nic"
    tags = {{
      "role"        = "Application",
      "patch-optin" = "YES",
      "snow-item"   = "{snow_ticket}"
    }}
  }}
}}

# Network Security Rules
network_security_rules = {{
  resource_group_name         = "{resource_group}-network"
  network_security_group_name = "nsg-{app_name}-{environment.lower()}"
  rules = [
{rules_string}
  ]
}}

# Common Tags
common_tags = {{
  "app-name"            = "{app_name}",
  "environment"         = "{environment}",
  "snow-item"           = "{snow_ticket}",
  "managed-by"          = "terraform",
  "cost-center"         = "{project_info.get('cost_center_id', 'TBD')}",
  "department"          = "{project_info.get('department', 'TBD')}",
  "line-of-business"    = "{project_info.get('line_of_business', 'TBD')}"
}}

# Resource-specific tags (customize as needed)
resource_specific_tags = {{}}
'''

    def _generate_outputs_tf(self) -> str:
        """Generate outputs.tf file."""
        return '''# outputs.tf
# Generated from Excel data

output "resource_group_id" {
  description = "The ID of the resource group"
  value       = module.base-vm.resource_group_id
}

output "vm_ids" {
  description = "The IDs of the virtual machines"
  value       = module.base-vm.vm_ids
}

output "vm_private_ips" {
  description = "The private IP addresses of the virtual machines"
  value       = module.base-vm.vm_private_ips
}

output "key_vault_id" {
  description = "The ID of the Key Vault"
  value       = module.base-vm.key_vault_id
}

output "key_vault_uri" {
  description = "The URI of the Key Vault"
  value       = module.base-vm.key_vault_uri
}
'''

    def _fix_location(self, location: str) -> str:
        """Fix location value to be a valid Azure region."""

        # Map common values to valid Azure regions
        location_map = {
            'here': 'West US 3',
            'us': 'West US',
            'west': 'West US',
            'east': 'East US',
            'central': 'Central US',
        }

        location_lower = location.lower()

        # Check if it's already a valid region format
        if any(region in location_lower for region in ['west us', 'east us', 'central us', 'north', 'south']):
            # Capitalize properly
            return ' '.join(word.capitalize() for word in location.split())

        # Try to map it
        for key, value in location_map.items():
            if key in location_lower:
                return value

        # Default to West US 3 if unknown
        if location_lower in ['here', 'tbd', 'todo', '']:
            return 'West US 3'

        return location


def main():
    """Generate clean Terraform configuration from Excel data."""

    json_file = "LLDtest_comprehensive_extract.json"

    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        print("Please run: python3 comprehensive_excel_extractor.py <excel_file>")
        return False

    print("=" * 60)
    print("TERRAFORM GENERATOR - CLEAN VERSION")
    print("=" * 60)
    print(f"Input: {json_file}\n")

    generator = TerraformGeneratorClean(json_file)
    generated_files = generator.generate_all()

    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print("Generated files:")
    for file_name, file_path in generated_files.items():
        file_size = os.path.getsize(file_path)
        print(f"  - {file_name} ({file_size:,} bytes)")

    print("\n" + "=" * 60)
    print("IMPORTANT NOTES")
    print("=" * 60)
    print("1. Review the generated files in 'terraform_clean' directory")
    print("2. Update subscription ID if needed (look for YOUR-AZURE-SUBSCRIPTION-ID)")
    print("3. Store admin password in Azure Key Vault (never in code)")
    print("4. Verify the location is a valid Azure region")
    print("5. Run: terraform init && terraform validate")

    return True


if __name__ == "__main__":
    main()