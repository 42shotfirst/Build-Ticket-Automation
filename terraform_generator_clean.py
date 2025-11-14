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

        # Use client-standard placeholder for module version
        module_version = "__DYNAMIC_MODULE_VERSION__"

        return f'''# Begin main.tf

module "base-vm" {{
  source = "app.terraform.io/wab-cloudengineering-org/base-vm/iac"

  # Using a variable for the module version isn't supported yet: https://github.com/hashicorp/terraform/issues/28912
  #version                     = var.test_module_version
  version                              = "{module_version}"
  spn                                  = var.spn
  location                             = var.location
  resource_group_name                  = var.resource_group_name
  existing_application_security_groups = var.existing_application_security_groups
  application_security_groups          = var.application_security_groups
  key_vault                            = var.key_vault
  user_assigned_identity_name          = var.user_assigned_identity_name
  disk_encryption_set_name             = var.disk_encryption_set_name
  subnets                              = var.subnets
  existing_subnets                     = var.existing_subnets
  private_endpoints                    = var.private_endpoints
  admin_username                       = var.admin_username
  admin_password                       = var.admin_password
  vm_list                              = var.vm_list
  network_security_rules               = var.network_security_rules
  common_tags                          = var.common_tags
  resource_specific_tags               = var.resource_specific_tags
}}
'''

    def _generate_variables_tf(self) -> str:
        """Generate variables.tf with client-standard validation blocks."""

        location = self._fix_location(self.clean_values.get('location', 'WEST US 3'))

        return f'''# Begin variables.tf

variable "spn" {{
  type        = string
  default     = null
  description = "Display name for Service Principal"
}}

variable "resource_group_name" {{
  type    = string
  default = null
}}

variable "location" {{
  type     = string
  default  = "{location}"
  nullable = false
  validation {{
    condition = contains(
      [
        "WEST US",
        "WEST US 2",
        "WEST US 3",
        "EAST US",
      ], var.location
    )
    error_message = format("A location value of '%s' is not allowed. Please use one of the following: \\n %s", var.location,
      join("\\n ",
        [
          "US WEST",
          "US WEST 2",
          "US WEST 3",
          "US EAST",
        ]
      )
    )
  }}
}}

variable "existing_application_security_groups" {{
  type = map(object({{
    name                = string
    resource_group_name = optional(string)
  }}))
  default     = {{}}
  description = <<-EOT
  map(object({{
    name         = Name of the application security group
  }}))
  EOT
  nullable    = false
}}

variable "application_security_groups" {{
  type = map(object({{
    name = string
  }}))
  default     = {{}}
  description = <<-EOT
  map(object({{
    name         = Name of the application security group
  }}))
  EOT
  nullable    = false
}}

variable "key_vault" {{
  type = object({{
    name                       = optional(string)
    sku_name                   = optional(string)
    soft_delete_retention_days = optional(number)
    public_network_access      = optional(string)
    snet_key                   = string
    key_name                   = optional(string)
  }})
  default = {{
    name                       = null
    sku_name                   = "standard"
    soft_delete_retention_days = 90
    public_network_access      = true
    snet_key                   = "snet1"
    key_name                   = null
  }}
  description = <<-EOT
  name                          = The name of the vault
  sku_name                      = The name of the SKU used for this Key Vault. Possible values are standard and premium
  soft_delete_retention_days    = The number of days that items should be retained for once soft-deleted. This value can be between 7 and 90
  public_network_access_enabled = Whether public network access is allowed for this Key Vault.
  snet_key                      = Subnet key that this key vault should be in
  key_name                = The name of the key vault key
  EOT
  nullable    = false
}}

variable "user_assigned_identity_name" {{
  type        = string
  default     = null
  description = "User assigned identity name"
}}

variable "disk_encryption_set_name" {{
  type        = string
  default     = null
  description = "Disk encryption set name"
}}

variable "existing_subnets" {{
  type = map(object({{
    resource_group_name  = string
    virtual_network_name = string
    name                 = string
  }}))
  default     = null
  description = <<-EOT
  map(object({{
    resource_group_name         = Name of the resource group the vnet is in
    virtual_network_name        = Name of virtual network the subnet is will be attached to
    network_security_group_name = Name of the network security group to associate with the subnet
    route_table_name            = Name of the route table to associate with the subnet
    name                        = Name of the subnet
    prefixes                    = Address prefixes to use for the subnet
    service_endpoints           = List of Service endpoints to associate with the subnet
  }}))
  EOT
}}

variable "subnets" {{
  type = map(object({{
    resource_group_name         = string
    virtual_network_name        = string
    network_security_group_name = optional(string)
    network_security_group_id   = optional(string)
    route_table_name            = optional(string)
    route_table_id              = optional(string)
    name                        = string
    prefixes                    = list(string)
    service_endpoints           = list(string)
  }}))
  default     = null
  description = <<-EOT
  map(object({{
    resource_group_name         = Name of the resource group the vnet is in
    virtual_network_name        = Name of virtual network the subnet is will be attached to
    network_security_group_name = Name of the network security group to associate with the subnet
    route_table_name            = Name of the route table to associate with the subnet
    name                        = Name of the subnet
    prefixes                    = Address prefixes to use for the subnet
    service_endpoints           = List of Service endpoints to associate with the subnet
  }}))
  EOT
}}

variable "private_endpoints" {{
  type = map(object({{
    name                           = string
    subresource_names              = list(string)
    private_connection_resource_id = optional(string)
    is_manual_connection           = optional(string)
    private_dns_zone_group_name    = optional(string)
    private_dns_zone_ids           = optional(list(string))
    snet_key                       = string
    asg_key                        = string
  }}))
  default     = {{}}
  description = <<-EOT
  map(object({{
    name                           = (Required) Specifies the Name of the Private Endpoint.
    subresource_names              = (Optional) A list of subresource names which the Private Endpoint is able to connect to. subresource_names corresponds to group_id. Possible values are detailed in the product documentation in the Subresources column.
    private_connection_resource_id = (Optional) The ID of the Private Link Enabled Remote Resource which this Private Endpoint should be connected to.
    is_manual_connection           = (Required) Does the Private Endpoint require Manual Approval from the remote resource owner?
    private_dns_zone_group_name    = (Required) Specifies the Name of the Private Service Connection
    private_dns_zone_ids           = (Required) Specifies the list of Private DNS Zones to include within the private_dns_zone_group
  }}))
  EOT
  nullable    = false
}}

variable "network_security_rules" {{
  type = object({{
    resource_group_name         = string
    network_security_group_name = string
    rules = list(object({{
      name                         = optional(string)
      priority                     = number
      direction                    = string
      access                       = string
      protocol                     = string
      description                  = optional(string)
      source_port_range            = optional(string)
      source_port_ranges           = optional(list(string))
      destination_port_range       = optional(string)
      destination_port_ranges      = optional(list(string))
      source_address_prefix        = optional(string)
      source_address_prefixes      = optional(list(string))
      destination_address_prefix   = optional(string)
      destination_address_prefixes = optional(list(string))
      source_asg_keys              = optional(list(string))
      destination_asg_keys         = optional(list(string))
      source_name                  = optional(string)
      destination_name             = optional(string)
      snow-item                    = optional(string)
    }}))
  }})
  default = null
}}

variable "admin_username" {{
  type     = string
  default  = "cisadmin"
  nullable = false
}}

variable "admin_password" {{
  sensitive = true
  type      = string
  default   = null
}}

variable "vm_list" {{
  type = map(object({{
    name              = string
    size              = string
    zone              = optional(number)
    image_os          = string
    image_urn         = optional(string)
    source_image_id   = optional(string)
    marketplace_image = optional(bool)
    ip_allocation     = string
    ip_address        = optional(string)
    identity_type     = optional(string)
    os_disk_name      = optional(string)
    os_disk_size      = number
    os_disk_type      = optional(string)
    os_disk_tier      = optional(string)
    data_disk_sizes   = optional(list(number))
    data_disk_type    = optional(string)
    data_disks = optional(map(object({{
      name = optional(string)
      size = string
      type = optional(string)
      tier = optional(string)
    }})))
    snet_key = string
    asg_key  = string
    tags = object({{
      role        = string
      patch-optin = string
      snow-item   = optional(string)
    }})
  }}))
  default     = null
  description = "Virtual machine configurations"
  nullable    = true
}}

variable "common_tags" {{
  type = object({{
    terraform           = optional(bool)
    shared-service-name = string
    app-name            = string
    environment         = string
    app-tier            = string
    snow-item           = string
    it-cost-center      = string
    it-domain           = string
    notes               = optional(string)
    segment             = optional(string)
    lineofbusiness      = optional(string)
    department          = optional(string)
    cost-center         = optional(string)
  }})

  description = "Required tags on all resources."

  validation {{
    condition = contains(
      [
        "DEV",
        "QA",
        "UAT",
        "PROD",
        "DR"
      ], var.common_tags.environment
    )
    error_message = format("An environment tag value of '%s' is not allowed. Please use one of the following: \\n %s", var.common_tags.environment,
      join("\\n ",
        [
          "DEV",
          "QA",
          "UAT",
          "PROD",
          "DR"
        ]
      )
    )
  }}

  validation {{
    condition = contains(
      [
        "Platinum",
        "Gold",
        "Iron",
        "Silver",
        "Bronze",
      ], var.common_tags.app-tier
    )
    error_message = format("A app-tier tag value of '%s' is not allowed. Please use one of the following: \\n %s", var.common_tags.app-tier,
      join("\\n ",
        [
          "Platinum",
          "Gold",
          "Iron",
          "Silver",
          "Bronze",
        ]
      )
    )
  }}

  validation {{
    condition     = var.common_tags.it-cost-center == "NA" || can(var.common_tags.it-cost-center * 1)
    error_message = format("An it-cost-center tag value of '%s' is not allowed. Please use NA or a whole number", var.common_tags.it-cost-center)
  }}
}}

variable "resource_specific_tags" {{
  type = object({{
    role        = optional(string)
    patch-optin = optional(string)
  }})
  default = {{
    role        = "NA"
    patch-optin = "NA"
  }}
  description = "These need to be on all resources. Some resources such as VMs will have values. Those tag values are controlled under that variable."

  validation {{
    condition     = contains(["YES", "NO", "NA"], var.resource_specific_tags.patch-optin)
    error_message = format("A patch-optin tag value of '%s' is not allowed. Please use one of the following: YES, NO, NA", var.resource_specific_tags.patch-optin)
  }}
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
        admin_username = vm_config.get('admin_username', 'cisadmin')

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

            # Handle ASGs - client standard uses lists
            source_asg_keys = rule.get('source_asg_keys', ['asg_nic'])
            if not isinstance(source_asg_keys, list):
                source_asg_keys = [str(source_asg_keys)]
            source_asg_formatted = ', '.join(f'"{k}"' for k in source_asg_keys)

            dest_asg_keys = rule.get('destination_asg_keys', ['asg_pe'])
            if not isinstance(dest_asg_keys, list):
                dest_asg_keys = [str(dest_asg_keys)]
            dest_asg_formatted = ', '.join(f'"{k}"' for k in dest_asg_keys)

            source_name = str(rule.get('source_name', 'Source'))
            destination_name = str(rule.get('destination_name', 'Destination'))
            description = str(rule.get('description', f'Security rule for {app_name}'))

            rule_text = f'''    {{
      name                       = "{name}"
      source_name                = "{source_name}"
      destination_name           = "{destination_name}"
      priority                   = {priority}
      direction                  = "{direction}"
      access                     = "{access}"
      protocol                   = "{protocol}"
      source_port_range          = "{source_port}"
      destination_port_ranges    = [{dest_ports_formatted}]
      source_asg_keys            = [{source_asg_formatted}]
      destination_asg_keys       = [{dest_asg_formatted}]
      description                = "{description}"
    }}'''
            formatted_rules.append(rule_text)

        # Join rules with commas
        rules_string = ',\n'.join(formatted_rules) if formatted_rules else ''

        return f'''# Begin terraform.tfvars

spn      = "spn-terraform-{app_name}"
location = "{location}"
resource_group_name = "{resource_group}"

application_security_groups = {{
  asg_nic = {{
    name = "asg-{app_name}-nic-{environment.lower()}"
  }}
  asg_pe = {{
    name = "asg-{app_name}-pe-{environment.lower()}"
  }}
}}

disk_encryption_set_name    = "dsk-{app_name}-{environment.lower()}"
user_assigned_identity_name = "umid-{app_name}-{environment.lower()}"

key_vault = {{
  name                       = "kvlt-{app_name}-{environment.lower()}"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-{app_name}-{environment.lower()}"
}}

subnets = {{
  snet1 = {{
    resource_group_name  = "{resource_group}-networking"
    virtual_network_name = "vnet-{app_name}-{environment.lower()}"
    network_security_group_id   = "/subscriptions/{subscription_id}/resourceGroups/{resource_group}-networking/providers/Microsoft.Network/networkSecurityGroups/nsg-{app_name}-{environment.lower()}"{subscription_comment}
    route_table_id              = "/subscriptions/{subscription_id}/resourceGroups/{resource_group}-networking/providers/Microsoft.Network/routeTables/rt-{app_name}-{environment.lower()}"{subscription_comment}
    name              = "snet-{app_name}-{environment.lower()}"
    prefixes          = ["{network_prefix}"]
    service_endpoints = ["Microsoft.KeyVault"]
  }}
}}

private_endpoints = {{
  pe_kvlt = {{
    name                           = "pvep-kvlt-{app_name}-{environment.lower()}"
    subresource_names              = ["vault"]
    snet_key                       = "snet1"
    asg_key                        = "asg_pe"
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
      "patch-optin" = "NO",
      "snow-item"   = "{snow_ticket}"
    }}
  }}
}}

network_security_rules = {{
  resource_group_name         = "{resource_group}-networking"
  network_security_group_name = "nsg-{app_name}-{environment.lower()}"
  rules = [
{rules_string}
  ]
}}

common_tags = {{
  "shared-service-name" = "NA",
  "app-name"            = "{app_name}",
  "environment"         = "{environment}",
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "{project_info.get('app_tier', 'Bronze')}",
  "snow-item"           = "{snow_ticket}",
  "it-cost-center"      = "{project_info.get('it_cost_center', 'NA')}",
  "it-domain"           = "{project_info.get('it_domain', 'Platform Engineering')}",
  "lineofbusiness"      = "{project_info.get('line_of_business', 'TBD')}",
  "department"          = "{project_info.get('department', 'Cloud Engineering')}",
  "cost-center"         = "{project_info.get('cost_center', 'TBD')}"
}}
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
        """Fix location value to be a valid Azure region in uppercase format."""

        # Map common values to valid Azure regions
        location_map = {
            'here': 'WEST US 3',
            'us': 'WEST US',
            'west': 'WEST US',
            'east': 'EAST US',
            'central': 'CENTRAL US',
        }

        location_lower = location.lower()

        # Check if it's already a valid region format
        if any(region in location_lower for region in ['west us', 'east us', 'central us', 'north', 'south']):
            # Uppercase properly for client standards
            return location.upper()

        # Try to map it
        for key, value in location_map.items():
            if key in location_lower:
                return value

        # Default to WEST US 3 if unknown
        if location_lower in ['here', 'tbd', 'todo', '']:
            return 'WEST US 3'

        return location.upper()


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