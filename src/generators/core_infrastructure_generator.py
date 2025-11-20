"""
Core Infrastructure Generator

Generates core terraform files from Build_ENV data:
- main.tf (providers, resource group)
- variables.tf (variable definitions)
- locals.tf (tag transformations)
- data.tf (data sources)
- terraform.tfvars (base values)
"""

from typing import Dict, Any, Optional
import os


class CoreInfrastructureGenerator:
    """Generates core terraform infrastructure files."""

    def __init__(self, build_env_data: Dict[str, Any], resources_data: Dict[str, Any]):
        """
        Initialize generator with extracted data.

        Args:
            build_env_data: Data from BuildEnvExtractor
            resources_data: Data from ResourcesExtractor
        """
        self.build_env = build_env_data
        self.resources = resources_data

    def generate(self, output_dir: str) -> Dict[str, str]:
        """
        Generate all core infrastructure files.

        Args:
            output_dir: Directory to write files to

        Returns:
            Dictionary mapping filenames to their content
        """
        os.makedirs(output_dir, exist_ok=True)

        files = {
            'main.tf': self._generate_main_tf(),
            'variables.tf': self._generate_variables_tf(),
            'locals.tf': self._generate_locals_tf(),
            'data.tf': self._generate_data_tf(),
        }

        # Write files
        for filename, content in files.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)

        return files

    def _generate_main_tf(self) -> str:
        """Generate main.tf with providers and resource group."""
        content = '''# Main Terraform configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Azure Provider configuration
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "azuread" {}

provider "random" {}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = merge(
    tomap(
      { "wab:resource-name" = var.resource_group_name }
    ),
    local.common_tags, local.resource_specific_tags
  )
}
'''
        return content

    def _generate_variables_tf(self) -> str:
        """Generate variables.tf with all variable definitions."""
        # Read the template from terraform_files_pattern
        template_path = 'terraform_files_pattern/variables.tf'

        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to generating basic variables
            return self._generate_basic_variables_tf()

    def _generate_basic_variables_tf(self) -> str:
        """Generate basic variables.tf if template not found."""
        content = '''variable "spn" {
  type        = string
  default     = null
  description = "Display name for Service Principal"
}

variable "resource_group_name" {
  type    = string
  default = null
}

variable "location" {
  type     = string
  default  = "WEST US 3"
  nullable = false
}

variable "application_security_groups" {
  type = map(object({
    name = string
  }))
  default     = {}
  description = "Application security groups"
  nullable    = false
}

variable "key_vault" {
  type = object({
    name                       = optional(string)
    sku_name                   = optional(string)
    soft_delete_retention_days = optional(number)
    public_network_access      = optional(string)
    snet_key                   = string
    key_name                   = optional(string)
  })
  default = {
    name                       = null
    sku_name                   = "standard"
    soft_delete_retention_days = 90
    public_network_access      = false
    snet_key                   = "snet1"
    key_name                   = null
  }
  nullable    = false
}

variable "user_assigned_identity_name" {
  type        = string
  default     = null
  description = "User assigned identity name"
}

variable "disk_encryption_set_name" {
  type        = string
  default     = null
  description = "Disk encryption set name"
}

variable "subnets" {
  type = map(object({
    resource_group_name         = string
    virtual_network_name        = string
    network_security_group_name = optional(string)
    network_security_group_id   = optional(string)
    route_table_name            = optional(string)
    route_table_id              = optional(string)
    name                        = string
    prefixes                    = list(string)
    service_endpoints           = list(string)
  }))
  default     = null
  description = "Subnets configuration"
}

variable "private_endpoints" {
  type = map(object({
    name                           = string
    subresource_names              = list(string)
    private_connection_resource_id = optional(string)
    is_manual_connection           = optional(string)
    private_dns_zone_group_name    = optional(string)
    private_dns_zone_ids           = optional(list(string))
    snet_key                       = string
    asg_key                        = string
  }))
  default     = {}
  description = "Private endpoints configuration"
  nullable    = false
}

variable "network_security_rules" {
  type = object({
    resource_group_name         = string
    network_security_group_name = string
    rules = list(object({
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
    }))
  })
  default = null
}

variable "vm_list" {
  type = map(object({
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
    data_disks = optional(map(object({
      name = optional(string)
      size = string
      type = optional(string)
      tier = optional(string)
    })))
    snet_key = string
    asg_key  = string
    tags = object({
      role        = string
      patch-optin = string
      snow-item   = optional(string)
    })
  }))
  default     = null
  description = "VM list configuration"
  nullable    = true
}

variable "admin_username" {
  type     = string
  default  = "cisadmin"
  nullable = false
}

variable "admin_password" {
  sensitive = true
  type      = string
  default   = null
}

variable "common_tags" {
  type = object({
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
  })
  description = "Required tags on all resources."
}

variable "default_common_tags" {
  description = "Map of default common tags"
  type        = map(string)
  default = {
    terraform      = true
    notes          = "NA",
    segment        = "NA",
    lineofbusiness = "NA",
    department     = "NA",
    cost-center    = "NA"
  }
}

variable "resource_specific_tags" {
  type = object({
    role        = optional(string)
    patch-optin = optional(string)
  })
  default = {
    role        = "NA"
    patch-optin = "NA"
  }
  description = "Resource-specific tags"
}
'''
        return content

    def _generate_locals_tf(self) -> str:
        """Generate locals.tf with tag transformations."""
        content = '''locals {
  merge_common_tags = merge(var.default_common_tags, { for key, value in var.common_tags : key => coalesce(value, lookup(var.default_common_tags, key, "")) })
}

locals {
  common_tags = {
    for tag, value in local.merge_common_tags : "wab:${tag}" => value
  }
}

locals {
  resource_specific_tags = {
    for tag, value in var.resource_specific_tags : "wab:${tag}" => value
  }
}
'''
        return content

    def _generate_data_tf(self) -> str:
        """Generate data.tf with data sources."""
        content = '''data "azurerm_client_config" "current" {}

data "azurerm_subscription" "subscription" {
  subscription_id = data.azurerm_client_config.current.subscription_id
}

data "azuread_service_principal" "spn" {
  display_name = var.spn
}

data "azurerm_route_table" "rt" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.route_table_name != null } : {}
  name                = each.value.route_table_name
  resource_group_name = each.value.resource_group_name
}

data "azurerm_route_table" "rt_id" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.route_table_id != null } : {}
  name                = split("/", each.value.route_table_id)[8]
  resource_group_name = split("/", each.value.route_table_id)[4]
}

data "azurerm_network_security_group" "nsg" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.network_security_group_name != null } : {}
  name                = each.value.network_security_group_name
  resource_group_name = each.value.resource_group_name
}

data "azurerm_network_security_group" "nsg_id" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.network_security_group_id != null } : {}
  name                = split("/", each.value.network_security_group_id)[8]
  resource_group_name = split("/", each.value.network_security_group_id)[4]
}

data "azurerm_virtual_network" "vnet" {
  for_each            = coalesce(var.subnets, {})
  name                = each.value.virtual_network_name
  resource_group_name = each.value.resource_group_name
}

data "azurerm_subnet" "snet" {
  for_each             = coalesce(var.existing_subnets, {})
  name                 = each.value.name
  virtual_network_name = each.value.virtual_network_name
  resource_group_name  = each.value.resource_group_name
}

data "azurerm_application_security_group" "asg" {
  for_each            = coalesce(var.existing_application_security_groups, {})
  name                = each.value.name
  resource_group_name = coalesce(each.value.resource_group_name, var.resource_group_name)
}
'''
        return content

    def get_tfvars_content(self) -> Dict[str, Any]:
        """
        Get terraform.tfvars content for core infrastructure.

        Returns:
            Dictionary of variable names to values
        """
        tfvars = {}

        # SPN - First try to get directly from Excel, then calculate from subscription
        # This matches the original enhanced_terraform_generator_v2.py pattern
        spn = None

        # Check if SPN is provided directly in Excel (highest priority)
        if 'spn' in self.build_env:
            spn = self.build_env.get('spn')

        # If not provided, calculate from subscription
        if not spn:
            subscription = self.build_env.get('subscription', '')
            if subscription:
                # Remove 'sub-' prefix if present and add 'spn-terraform-' prefix
                if subscription.lower().startswith('sub-'):
                    spn = 'spn-terraform-' + subscription[4:]
                else:
                    spn = 'spn-terraform-' + subscription

        if spn:
            tfvars['spn'] = spn

        # Location
        location = self.build_env.get('location')
        tfvars['location'] = location

        # Resource Group Name
        rg = self.build_env.get('resource_group', {})
        rg_name = rg.get('resource_group_name') or rg.get('name')
        tfvars['resource_group_name'] = rg_name

        # Common Tags
        tags = self.build_env.get('tags', {})
        common_tags = {}
        for key, value in tags.items():
            # Remove 'wab:' prefix if present
            clean_key = key.replace('wab:', '')
            common_tags[clean_key] = value

        if common_tags:
            tfvars['common_tags'] = common_tags

        return tfvars
