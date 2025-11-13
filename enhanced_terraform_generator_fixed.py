#!/usr/bin/env python3
"""
Enhanced Terraform Generator (Fixed Version)
=============================================
Generates Terraform files with:
- Actual data from Excel (no placeholders)
- Proper separators between resources
- Better error handling and data validation
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from data_accessor import ExcelDataAccessor

class EnhancedTerraformGeneratorFixed:
    """Generate Terraform files with actual Excel data and proper formatting."""

    def __init__(self, json_file_path: str):
        """Initialize with JSON file from comprehensive extraction."""
        self.accessor = ExcelDataAccessor(json_file_path)
        self.terraform_data = self.accessor.get_terraform_ready_data()
        self.schema = self._load_schema()
        # Cache raw_data for quick access
        self.raw_data_cache = {}
        self._build_raw_data_cache()

    def _load_schema(self) -> Dict[str, Any]:
        """Load the Terraform output schema."""
        schema_file = "terraform_output_schema.json"
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                return json.load(f)
        return {}

    def _build_raw_data_cache(self):
        """Build a cache of raw_data values for quick lookup."""
        comprehensive_data = self.terraform_data.get('comprehensive_data', {})

        for sheet_name, sheet_data in comprehensive_data.items():
            raw_data = sheet_data.get('raw_data', [])
            if sheet_name not in self.raw_data_cache:
                self.raw_data_cache[sheet_name] = {}

            # Process raw data - look for key-value patterns
            for row in raw_data:
                if isinstance(row, dict):
                    # Try multiple column patterns for key-value pairs
                    key_columns = ['0', '1', 'A', 'Variable', 'Key', 'Name']
                    value_columns = ['1', '2', 'B', 'Value', 'Setting', 'Data']

                    key = None
                    value = None

                    # Find the key
                    for key_col in key_columns:
                        if key_col in row and row[key_col]:
                            key = str(row[key_col]).strip()
                            break

                    # Find the value
                    for val_col in value_columns:
                        if val_col in row and row[val_col]:
                            value = row[val_col]
                            break

                    if key and value:
                        self.raw_data_cache[sheet_name][key] = value

    def _get_raw_value(self, var_name: str, sheet_name: str = 'Build_ENV', default: Any = None) -> Any:
        """Get a value from raw_data cache or key-value pairs."""
        # First check raw_data cache
        value = self.raw_data_cache.get(sheet_name, {}).get(var_name)
        if value is not None:
            return value

        # Then check key_value_pairs
        comprehensive_data = self.terraform_data.get('comprehensive_data', {})
        sheet_data = comprehensive_data.get(sheet_name, {})
        key_value_pairs = sheet_data.get('key_value_pairs', {})

        # Try exact match first
        if var_name in key_value_pairs:
            return key_value_pairs[var_name]

        # Try case-insensitive match
        for key, val in key_value_pairs.items():
            if key.lower() == var_name.lower():
                return val

        # Try partial match
        for key, val in key_value_pairs.items():
            if var_name.lower() in key.lower() or key.lower() in var_name.lower():
                return val

        return default

    def generate_terraform_files(self, output_dir: str = "output_package") -> Dict[str, str]:
        """Generate complete deployment package with proper formatting."""

        # setup output dirs
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "docs"), exist_ok=True)

        generated_files = {}

        # Generate module call file (following m-basevm.tf pattern)
        module_tf = self._generate_module_tf()
        module_tf_path = os.path.join(output_dir, "m-basevm.tf")
        with open(module_tf_path, 'w', encoding='utf-8') as f:
            f.write(module_tf)
        generated_files['m-basevm.tf'] = module_tf_path

        # Generate configuration files
        config_files = self._generate_configuration_files(output_dir)
        generated_files.update(config_files)

        # Generate validation script
        validate_script = self._generate_validate_script()
        validate_script_path = os.path.join(output_dir, "scripts", "validate.sh")
        with open(validate_script_path, 'w', encoding='utf-8') as f:
            f.write(validate_script)
        os.chmod(validate_script_path, 0o755)
        generated_files['scripts/validate.sh'] = validate_script_path

        return generated_files

    def _generate_module_tf(self) -> str:
        """Generate main module call file with actual module version."""

        project_info = self.terraform_data.get('project_info', {})

        # Try to get actual module version from Excel data
        module_version = (
            self._get_raw_value('module_version', 'Build_ENV') or
            self._get_raw_value('test_module_version', 'Build_ENV') or
            self._get_raw_value('base_vm_version', 'Build_ENV') or
            "1.0.0"  # Default version instead of placeholder
        )

        module_tf = f'''# m-basevm.tf
# Generated by Enhanced Terraform Generator

module "base-vm" {{
  source = "app.terraform.io/wab-cloudengineering-org/base-vm/iac"

  # Module version from Excel configuration
  version                              = "{module_version}"

  # Core configuration
  spn                                  = var.spn
  location                             = var.location
  resource_group_name                  = var.resource_group_name

  # Security groups
  existing_application_security_groups = var.existing_application_security_groups
  application_security_groups          = var.application_security_groups

  # Key vault and identity
  key_vault                            = var.key_vault
  user_assigned_identity_name          = var.user_assigned_identity_name
  disk_encryption_set_name             = var.disk_encryption_set_name

  # Networking
  subnets                              = var.subnets
  existing_subnets                     = var.existing_subnets
  private_endpoints                    = var.private_endpoints

  # VM configuration
  admin_username                       = var.admin_username
  admin_password                       = var.admin_password
  vm_list                              = var.vm_list

  # Security rules
  network_security_rules               = var.network_security_rules

  # Tags
  common_tags                          = var.common_tags
  resource_specific_tags               = var.resource_specific_tags
}}
'''

        return module_tf

    def _generate_configuration_files(self, output_dir: str) -> Dict[str, str]:
        """Generate configuration files (variables.tf, terraform.tfvars, etc.)."""

        generated_files = {}

        # variables.tf
        variables_tf = self._generate_variables_tf()
        variables_path = os.path.join(output_dir, "variables.tf")
        with open(variables_path, 'w', encoding='utf-8') as f:
            f.write(variables_tf)
        generated_files['variables.tf'] = variables_path

        # terraform.tfvars
        tfvars = self._generate_tfvars()
        tfvars_path = os.path.join(output_dir, "terraform.tfvars")
        with open(tfvars_path, 'w', encoding='utf-8') as f:
            f.write(tfvars)
        generated_files['terraform.tfvars'] = tfvars_path

        # outputs.tf
        outputs_tf = self._generate_outputs_tf()
        outputs_path = os.path.join(output_dir, "outputs.tf")
        with open(outputs_path, 'w', encoding='utf-8') as f:
            f.write(outputs_tf)
        generated_files['outputs.tf'] = outputs_path

        # versions.tf
        versions_tf = self._generate_versions_tf()
        versions_path = os.path.join(output_dir, "versions.tf")
        with open(versions_path, 'w', encoding='utf-8') as f:
            f.write(versions_tf)
        generated_files['versions.tf'] = versions_path

        return generated_files

    def _generate_variables_tf(self) -> str:
        """Generate variables.tf with complex object structures."""

        # Get actual location from Excel data
        build_env = self.terraform_data.get('build_environment', {})
        default_location = (
            build_env.get('key_value_pairs', {}).get('Location') or
            build_env.get('key_value_pairs', {}).get('location') or
            self._get_raw_value('location', 'Build_ENV') or
            "WEST US 3"
        )

        variables_tf = f'''# variables.tf
# Generated by Enhanced Terraform Generator

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
  default  = "{default_location}"
  nullable = false
  validation {{
    condition = contains(
      [
        "WEST US",
        "WEST US 2",
        "WEST US 3",
        "EAST US",
        "EAST US 2",
        "CENTRAL US",
        "NORTH CENTRAL US",
        "SOUTH CENTRAL US"
      ], var.location
    )
    error_message = "Invalid location. Please use a valid Azure region."
  }}
}}

variable "existing_application_security_groups" {{
  type    = map(any)
  default = {{}}
}}

variable "application_security_groups" {{
  type = map(object({{
    name = string
  }}))
  default = {{}}
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
}}

variable "user_assigned_identity_name" {{
  type = string
}}

variable "disk_encryption_set_name" {{
  type = string
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
  default = {{}}
}}

variable "existing_subnets" {{
  type    = map(any)
  default = {{}}
}}

variable "private_endpoints" {{
  type = map(object({{
    name              = string
    subresource_names = list(string)
    snet_key          = string
    asg_key           = string
  }}))
  default = {{}}
}}

variable "admin_username" {{
  type    = string
  default = "azureadmin"
}}

variable "admin_password" {{
  type      = string
  sensitive = true
  default   = null
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
  default = {{}}
}}

variable "network_security_rules" {{
  type = object({{
    resource_group_name         = string
    network_security_group_name = string
    rules = list(object({{
      name                        = string
      priority                    = number
      direction                   = string
      access                      = string
      protocol                    = string
      source_port_range           = string
      destination_port_ranges     = list(string)
      source_asg                  = string
      destination_asg             = string
      description                 = string
    }}))
  }})
}}

variable "common_tags" {{
  type    = map(string)
  default = {{}}
}}

variable "resource_specific_tags" {{
  type    = map(map(string))
  default = {{}}
}}
'''

        return variables_tf

    def _generate_tfvars(self) -> str:
        """Generate terraform.tfvars with actual values from Excel data."""

        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        build_env = self.terraform_data.get('build_environment', {})

        # Extract actual values from Excel data
        project_name = project_info.get('project_name', 'default-project')
        app_name = project_info.get('application_name', 'default-app')
        environment = project_info.get('environment', 'DEV')

        # Get actual location from Excel
        location = (
            build_env.get('key_value_pairs', {}).get('Location') or
            build_env.get('key_value_pairs', {}).get('location') or
            self._get_raw_value('location', 'Build_ENV') or
            project_info.get('location') or
            'WEST US 3'
        )

        # Get actual subscription ID from Excel
        subscription_id = (
            self._get_raw_value('subscription_id', 'Build_ENV') or
            self._get_raw_value('subscription', 'Build_ENV') or
            build_env.get('key_value_pairs', {}).get('Subscription ID') or
            build_env.get('key_value_pairs', {}).get('subscription_id') or
            project_info.get('subscription_id')
        )

        if not subscription_id or subscription_id == 'SUBSCRIPTION_ID_PLACEHOLDER':
            print("WARNING: No subscription ID found in Excel data. Please update terraform.tfvars with actual subscription ID.")
            subscription_id = "YOUR-SUBSCRIPTION-ID-HERE"

        # Get actual network configuration from Excel
        network_prefix = (
            self._get_raw_value('network_prefix', 'Build_ENV') or
            self._get_raw_value('subnet_prefix', 'Build_ENV') or
            self._get_raw_value('address_space', 'Build_ENV') or
            "10.0.1.0/24"
        )

        # Generate VM list
        vm_list = self._generate_vm_list_for_tfvars()

        # Generate subnets with actual subscription ID
        subnets = self._generate_subnets_for_tfvars(subscription_id, network_prefix)

        # Generate application security groups
        application_security_groups = self._generate_asg_for_tfvars()

        # Generate private endpoints
        private_endpoints = self._generate_private_endpoints_for_tfvars()

        # Generate network security rules
        network_security_rules = self._generate_nsg_rules_for_tfvars()

        # Get actual SPN name from Excel
        spn_name = (
            build_env.get('key_value_pairs', {}).get('SPN') or
            build_env.get('key_value_pairs', {}).get('Service Principal') or
            self._get_raw_value('spn', 'Build_ENV') or
            f"spn-terraform-{project_name.lower().replace(' ', '-')}"
        )

        # Get actual key vault settings from Excel
        kvlt_sku = self._get_raw_value('sku_name', 'Build_ENV', 'standard')
        kvlt_retention = self._get_raw_value('soft_delete_retention_days', 'Build_ENV', 90)
        kvlt_public_access = self._get_raw_value('public_network_access', 'Build_ENV', True)

        # Convert to boolean if needed
        if isinstance(kvlt_public_access, (int, str)):
            kvlt_public_access = str(kvlt_public_access).lower() in ['1', 'true', 'yes']

        # Get actual Service Now ticket from Excel
        snow_ticket = (
            project_info.get('service_now_ticket') or
            self._get_raw_value('service_now_ticket', 'Resources') or
            self._get_raw_value('snow_item', 'Resources') or
            "RITM0000000"
        )

        tfvars = f'''# terraform.tfvars
# Generated by Enhanced Terraform Generator
# Data extracted from Excel file

# Service Principal
spn = "{spn_name}"

# Location
location = "{location}"

# Resource Group
resource_group_name = "rg-{project_name.lower().replace(' ', '-')}-{environment.lower()}"

# Application Security Groups
application_security_groups = {application_security_groups}

# Encryption Settings
disk_encryption_set_name    = "dsk-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
user_assigned_identity_name = "umid-{project_name.lower().replace(' ', '-')}-{environment.lower()}"

# Key Vault Configuration
key_vault = {{
  name                       = "kvlt-{project_name.lower().replace(' ', '-')[:20]}-{environment.lower()}"
  sku_name                   = "{kvlt_sku}"
  soft_delete_retention_days = {kvlt_retention}
  public_network_access      = {str(kvlt_public_access).lower()}
  snet_key                   = "snet1"
  key_name                   = "key-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
}}

# Subnet Configuration
subnets = {subnets}

# Private Endpoints
private_endpoints = {private_endpoints}

# Network Security Rules
network_security_rules = {network_security_rules}

# Virtual Machines
vm_list = {vm_list}

# Common Tags
common_tags = {{
  "shared-service-name" = "NA"
  "app-name"            = "{app_name}"
  "environment"         = "{environment}"
  "data-classification" = "Internal"
  "criticality"         = "4-Very Minor to Operations"
  "app-tier"            = "Bronze"
  "snow-item"           = "{snow_ticket}"
  "it-cost-center"      = "5541"
  "it-domain"           = "Platform Engineering"
  "lineofbusiness"      = "Amerihome Mortgage"
  "department"          = "Cloud Engineering"
  "cost-center"         = "6500"
}}

# Resource-specific tags (can be customized per resource)
resource_specific_tags = {{}}
'''

        return tfvars

    def _generate_vm_list_for_tfvars(self) -> str:
        """Generate VM list with proper formatting and separators."""

        vm_instances = self.terraform_data.get('vm_instances', [])
        project_info = self.terraform_data.get('project_info', {})

        if not vm_instances:
            # Create at least one VM from project data
            vm_name = (
                self._get_raw_value('vm_name', 'Resources') or
                self._get_raw_value('hostname', 'Resources') or
                f"vm-{project_info.get('application_name', 'app')}-01"
            )

            vm_size = (
                self._get_raw_value('vm_size', 'Resources') or
                project_info.get('vm_size') or
                "Standard_B2s"
            )

            os_type = (
                self._get_raw_value('os_type', 'Resources') or
                project_info.get('os_image', 'windows').lower()
            )

            vm_instances = [{'Name': vm_name, 'Size': vm_size, 'OS': os_type}]

        vm_entries = []
        for i, vm in enumerate(vm_instances):
            vm_key = f"vm{i+1}"

            # Extract VM fields with actual data
            vm_name = self._extract_vm_name(vm, i)
            vm_size = self._extract_vm_size(vm)
            os_type = self._extract_os_type(vm)

            # Get actual image URN from Excel or use defaults
            image_urn = (
                self._get_raw_value(f'vm_list.{vm_key}.image_urn', 'Resources') or
                self._get_raw_value('image_urn', 'Resources')
            )
            if not image_urn:
                if os_type == "windows":
                    image_urn = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
                else:
                    image_urn = "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest"

            # Get actual disk configuration
            os_disk_size = self._extract_vm_disk_size(vm)
            os_disk_type = self._extract_vm_disk_type(vm)

            # Get actual IP configuration
            ip_allocation = (
                self._get_raw_value(f'vm_list.{vm_key}.ip_allocation', 'Resources') or
                'Dynamic'
            )

            ip_address = self._get_raw_value(f'vm_list.{vm_key}.ip_address', 'Resources')

            # Get actual tags
            role = vm.get('Role', project_info.get('role', 'Application'))
            patch_optin = vm.get('Patch Optin', project_info.get('patch_optin', 'NO'))
            snow_item = (
                vm.get('Service Now Ticket') or
                project_info.get('service_now_ticket') or
                self._get_raw_value('service_now_ticket', 'Resources') or
                'RITM0000000'
            )

            # Build VM entry with proper formatting
            ip_address_line = f'\n    ip_address        = "{ip_address}"' if ip_address else ""

            vm_entry = f'''  {vm_key} = {{
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
    data_disk_sizes   = [50, 50]
    data_disk_type    = "Standard_LRS"
    snet_key          = "snet1"
    asg_key           = "asg_nic"
    tags = {{
      "role"        = "{role}"
      "patch-optin" = "{patch_optin}"
      "snow-item"   = "{snow_item}"
    }}
  }}'''
            vm_entries.append(vm_entry)

        # Join VM entries with proper separators (commas between entries)
        return f'''{{{chr(10)}{','.join(vm_entries)}{chr(10)}}}'''

    def _generate_subnets_for_tfvars(self, subscription_id: str, network_prefix: str) -> str:
        """Generate subnets configuration with actual values."""

        project_info = self.terraform_data.get('project_info', {})
        build_env = self.terraform_data.get('build_environment', {})

        app_name = project_info.get('application_name', 'app')
        project_name = project_info.get('project_name', 'project')
        environment = project_info.get('environment', 'dev')

        # Get actual network resource group from Excel
        network_rg = (
            self._get_raw_value('network_resource_group', 'Build_ENV') or
            f"rg-{project_name.lower()}-networking"
        )

        # Get actual vnet name from Excel
        vnet_name = (
            self._get_raw_value('virtual_network_name', 'Build_ENV') or
            f"vnet-{project_name.lower()}-{environment.lower()}"
        )

        # Get actual NSG name from Excel
        nsg_name = (
            self._get_raw_value('network_security_group', 'Build_ENV') or
            f"nsg-{project_name.lower()}-{environment.lower()}"
        )

        # Get actual route table name from Excel
        route_table_name = (
            self._get_raw_value('route_table_name', 'Build_ENV') or
            f"rt-{project_name.lower()}-{environment.lower()}"
        )

        subnet_name = f"snet-{app_name.lower()}-{environment.lower()}"

        return f'''{{
  snet1 = {{
    resource_group_name  = "{network_rg}"
    virtual_network_name = "{vnet_name}"
    network_security_group_id = "/subscriptions/{subscription_id}/resourceGroups/{network_rg}/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}"
    route_table_id            = "/subscriptions/{subscription_id}/resourceGroups/{network_rg}/providers/Microsoft.Network/routeTables/{route_table_name}"
    name              = "{subnet_name}"
    prefixes          = ["{network_prefix}"]
    service_endpoints = ["Microsoft.KeyVault"]
  }}
}}'''

    def _generate_asg_for_tfvars(self) -> str:
        """Generate application security groups with proper formatting."""

        project_info = self.terraform_data.get('project_info', {})
        app_name = project_info.get('application_name', 'app')
        environment = project_info.get('environment', 'dev')

        return f'''{{
  asg_nic = {{
    name = "asg-{app_name.lower()}-nic-{environment.lower()}"
  }}
  asg_pe = {{
    name = "asg-{app_name.lower()}-pe-{environment.lower()}"
  }}
}}'''

    def _generate_private_endpoints_for_tfvars(self) -> str:
        """Generate private endpoints with proper formatting."""

        project_info = self.terraform_data.get('project_info', {})
        app_name = project_info.get('application_name', 'app')
        environment = project_info.get('environment', 'dev')

        return f'''{{
  pe_kvlt = {{
    name              = "pvep-kvlt-{app_name.lower()}-{environment.lower()}"
    subresource_names = ["vault"]
    snet_key          = "snet1"
    asg_key           = "asg_pe"
  }}
}}'''

    def _generate_nsg_rules_for_tfvars(self) -> str:
        """Generate network security rules with actual data and proper formatting."""

        security_groups = self.terraform_data.get('security_groups', [])
        project_info = self.terraform_data.get('project_info', {})

        project_name = project_info.get('project_name', 'project')
        environment = project_info.get('environment', 'dev')

        network_rg = (
            self._get_raw_value('network_resource_group', 'Build_ENV') or
            f"rg-{project_name.lower()}-networking"
        )

        nsg_name = (
            self._get_raw_value('network_security_group', 'Build_ENV') or
            f"nsg-{project_name.lower()}-{environment.lower()}"
        )

        if not security_groups:
            # Return empty rules if no NSG data
            return f'''{{
  resource_group_name         = "{network_rg}"
  network_security_group_name = "{nsg_name}"
  rules = []
}}'''

        rules = []
        for i, rule in enumerate(security_groups):
            # Extract actual values from Excel NSG data
            rule_name = rule.get('name', f'rule_{i}')
            priority = rule.get('priority', 100 + i * 10)

            # Ensure priority is an integer
            try:
                priority = int(priority)
            except (ValueError, TypeError):
                priority = 100 + i * 10

            direction = rule.get('direction', 'Inbound')
            access = rule.get('access', 'Allow')
            protocol = rule.get('protocol', 'Tcp')
            source_port_range = rule.get('source_port_range', '*')

            # Handle destination ports
            dest_ports = rule.get('destination_port_ranges', rule.get('destination_port_range', ['443']))
            if not isinstance(dest_ports, list):
                dest_ports = [str(dest_ports)]
            dest_ports_str = ', '.join(f'"{p}"' for p in dest_ports)

            source_asg = rule.get('source_asg', rule.get('source_application_security_groups', 'asg_nic'))
            dest_asg = rule.get('destination_asg', rule.get('destination_application_security_groups', 'asg_nic'))
            description = rule.get('description', f'Security rule {i+1}')

            rule_entry = f'''    {{
      name                    = "{rule_name}"
      priority                = {priority}
      direction               = "{direction}"
      access                  = "{access}"
      protocol                = "{protocol}"
      source_port_range       = "{source_port_range}"
      destination_port_ranges = [{dest_ports_str}]
      source_asg              = "{source_asg}"
      destination_asg         = "{dest_asg}"
      description             = "{description}"
    }}'''
            rules.append(rule_entry)

        # Join rules with proper separators (commas between entries)
        rules_str = ',\n'.join(rules) if rules else ''

        return f'''{{
  resource_group_name         = "{network_rg}"
  network_security_group_name = "{nsg_name}"
  rules = [
{rules_str}
  ]
}}'''

    def _extract_vm_name(self, vm: Dict, index: int) -> str:
        """Extract VM name from various possible fields."""
        name_fields = ['Name', 'Hostname', 'Server Name', 'VM Name', 'name', 'hostname']
        for field in name_fields:
            if field in vm and vm[field]:
                return str(vm[field]).strip()

        # Fallback to generated name
        project_info = self.terraform_data.get('project_info', {})
        app_name = project_info.get('application_name', 'app')
        return f"vm-{app_name.lower()}-{index+1:02d}"

    def _extract_vm_size(self, vm: Dict) -> str:
        """Extract VM size from various possible fields."""
        size_fields = ['Size', 'VM Size', 'SKU', 'Recommended SKU', 'Choose Node Size', 'size', 'sku']
        for field in size_fields:
            if field in vm and vm[field]:
                return str(vm[field]).strip()

        # Check project info
        project_info = self.terraform_data.get('project_info', {})
        if 'vm_size' in project_info:
            return project_info['vm_size']

        return "Standard_B2s"

    def _extract_os_type(self, vm: Dict) -> str:
        """Extract OS type and normalize to 'windows' or 'linux'."""
        os_fields = ['OS', 'Operating System', 'OS Image', 'OS Type', 'os', 'os_type']
        for field in os_fields:
            if field in vm and vm[field]:
                os_value = str(vm[field]).lower()
                if 'windows' in os_value:
                    return 'windows'
                elif 'linux' in os_value or 'ubuntu' in os_value or 'rhel' in os_value:
                    return 'linux'

        # Check project info
        project_info = self.terraform_data.get('project_info', {})
        os_image = project_info.get('os_image', '').lower()
        if 'windows' in os_image:
            return 'windows'
        elif 'linux' in os_image or 'ubuntu' in os_image:
            return 'linux'

        return 'windows'  # Default

    def _extract_vm_disk_size(self, vm: Dict) -> int:
        """Extract OS disk size from VM data."""
        disk_fields = ['OS Disk Size', 'Disk Size', 'OS Disk', 'os_disk_size', 'disk_size']
        for field in disk_fields:
            if field in vm and vm[field]:
                try:
                    return int(vm[field])
                except (ValueError, TypeError):
                    pass

        # Default based on OS type
        os_type = self._extract_os_type(vm)
        return 127 if os_type == 'windows' else 30

    def _extract_vm_disk_type(self, vm: Dict) -> str:
        """Extract OS disk type from VM data."""
        disk_type_fields = ['OS Disk Type', 'Disk Type', 'Storage Type', 'os_disk_type', 'disk_type']
        for field in disk_type_fields:
            if field in vm and vm[field]:
                disk_type = str(vm[field]).strip()
                # Normalize to Azure disk types
                if 'premium' in disk_type.lower():
                    return 'Premium_LRS'
                elif 'standard' in disk_type.lower() and 'ssd' in disk_type.lower():
                    return 'StandardSSD_LRS'
                elif disk_type in ['Premium_LRS', 'StandardSSD_LRS', 'Standard_LRS']:
                    return disk_type

        return 'StandardSSD_LRS'  # Default

    def _generate_outputs_tf(self) -> str:
        """Generate outputs.tf file."""
        return '''# outputs.tf
# Generated by Enhanced Terraform Generator

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

    def _generate_versions_tf(self) -> str:
        """Generate versions.tf file."""
        return '''# versions.tf
# Generated by Enhanced Terraform Generator

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
      version = "~> 3.1"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}
'''

    def _generate_validate_script(self) -> str:
        """Generate validation script."""
        return '''#!/bin/bash
# validate.sh
# Generated by Enhanced Terraform Generator

set -e

echo "========================================"
echo "Terraform Configuration Validation"
echo "========================================"

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "ERROR: Terraform is not installed"
    exit 1
fi

echo "✓ Terraform is installed: $(terraform version | head -n1)"

# Initialize Terraform
echo ""
echo "Initializing Terraform..."
terraform init -backend=false

# Validate configuration
echo ""
echo "Validating Terraform configuration..."
if terraform validate; then
    echo "✓ Configuration is valid"
else
    echo "✗ Configuration validation failed"
    exit 1
fi

# Format check
echo ""
echo "Checking Terraform formatting..."
if terraform fmt -check=true -diff; then
    echo "✓ Configuration is properly formatted"
else
    echo "✗ Configuration needs formatting"
    echo "Run 'terraform fmt' to fix formatting"
fi

echo ""
echo "========================================"
echo "Validation Complete"
echo "========================================"
'''


def main():
    """Main function for testing the fixed generator."""
    import sys

    # Check if JSON file is provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Try to find the most recent JSON extract
        import glob
        json_files = glob.glob("*_comprehensive_extract.json")
        if json_files:
            json_file = max(json_files, key=os.path.getctime)
            print(f"Using most recent extract: {json_file}")
        else:
            print("Error: No JSON extract file found.")
            print("Usage: python enhanced_terraform_generator_fixed.py <json_file>")
            print("First run: python comprehensive_excel_extractor.py <excel_file>")
            return False

    if not os.path.exists(json_file):
        print(f"Error: File not found: {json_file}")
        return False

    # Create generator and generate Terraform files
    print("="*60)
    print("ENHANCED TERRAFORM GENERATOR (FIXED)")
    print("="*60)
    print(f"Input: {json_file}")
    print()

    generator = EnhancedTerraformGeneratorFixed(json_file)
    generated_files = generator.generate_terraform_files()

    print()
    print("="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print("Generated files:")
    for file_name, file_path in generated_files.items():
        print(f"  ✓ {file_name}")

    print()
    print("Next steps:")
    print("1. Review the generated files in the 'output_package' directory")
    print("2. Update any remaining placeholders (search for 'YOUR-SUBSCRIPTION-ID-HERE')")
    print("3. Run validation: cd output_package && ./scripts/validate.sh")
    print("4. Initialize Terraform: terraform init")
    print("5. Plan deployment: terraform plan")

    return True


if __name__ == "__main__":
    main()