#!/usr/bin/env python3
"""
Enhanced Terraform Generator v2
===============================
Generates Terraform files following the patterns from module.md analysis.
Implements the comprehensive output schema with proper file organization,
complex variable structures, and advanced resource patterns.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from data_accessor import ExcelDataAccessor

class EnhancedTerraformGeneratorV2:
    """Generate Terraform files following module.md patterns and schema."""
    
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
            
            for row in raw_data:
                if isinstance(row, dict):
                    var_name = row.get('1')
                    value = row.get('2')
                    if var_name:
                        self.raw_data_cache[sheet_name][var_name] = value
    
    def _get_raw_value(self, var_name: str, sheet_name: str = 'Build_ENV', default: Any = None) -> Any:
        """Get a value from raw_data cache.
        
        Args:
            var_name: The variable name to look up (from column "1")
            sheet_name: The sheet to search in
            default: Default value if not found
            
        Returns:
            The value from column "2" or default if not found
        """
        return self.raw_data_cache.get(sheet_name, {}).get(var_name, default)
        
    def generate_terraform_files(self, output_dir: str = "output_package") -> Dict[str, str]:
        """Generate complete deployment package following module.md patterns."""
        
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
        
        # Generate resource files (following r-*.tf pattern)
        resource_files = self._generate_resource_files(output_dir)
        generated_files.update(resource_files)
        
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
        
        # Generate documentation
        docs = self._generate_documentation(output_dir)
        generated_files.update(docs)
        
        return generated_files
    
    def _generate_module_tf(self) -> str:
        """Generate main module call file (m-basevm.tf)."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        
        # Extract key information
        project_name = project_info.get('project_name', 'default-project')
        app_name = project_info.get('application_name', 'default-app')
        
        module_tf = f'''# Begin m-basevm.tf

module "base-vm" {{
  source = "app.terraform.io/wab-cloudengineering-org/base-vm/iac"

  # Using a variable for the module version isn't supported yet: https://github.com/hashicorp/terraform/issues/28912
  #version                     = var.test_module_version
  version                              = "__DYNAMIC_MODULE_VERSION__"
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
        
        return module_tf
    
    def _generate_resource_files(self, output_dir: str) -> Dict[str, str]:
        """Generate individual resource files following r-*.tf pattern."""
        
        generated_files = {}
        
        # Generate resource group file (r-rg.tf)
        rg_tf = self._generate_resource_group_tf()
        rg_path = os.path.join(output_dir, "r-rg.tf")
        with open(rg_path, 'w', encoding='utf-8') as f:
            f.write(rg_tf)
        generated_files['r-rg.tf'] = rg_path
        
        # Generate application security groups file (r-asg.tf)
        asg_tf = self._generate_application_security_groups_tf()
        asg_path = os.path.join(output_dir, "r-asg.tf")
        with open(asg_path, 'w', encoding='utf-8') as f:
            f.write(asg_tf)
        generated_files['r-asg.tf'] = asg_path
        
        # Generate subnets file (r-snet.tf)
        snet_tf = self._generate_subnets_tf()
        snet_path = os.path.join(output_dir, "r-snet.tf")
        with open(snet_path, 'w', encoding='utf-8') as f:
            f.write(snet_tf)
        generated_files['r-snet.tf'] = snet_path
        
        # Generate network security rules file (r-nsr.tf)
        nsr_tf = self._generate_network_security_rules_tf()
        nsr_path = os.path.join(output_dir, "r-nsr.tf")
        with open(nsr_path, 'w', encoding='utf-8') as f:
            f.write(nsr_tf)
        generated_files['r-nsr.tf'] = nsr_path
        
        # Generate key vault file (r-kvlt.tf)
        kvlt_tf = self._generate_key_vault_tf()
        kvlt_path = os.path.join(output_dir, "r-kvlt.tf")
        with open(kvlt_path, 'w', encoding='utf-8') as f:
            f.write(kvlt_tf)
        generated_files['r-kvlt.tf'] = kvlt_path
        
        # Generate user assigned identity file (r-umid.tf)
        umid_tf = self._generate_user_assigned_identity_tf()
        umid_path = os.path.join(output_dir, "r-umid.tf")
        with open(umid_path, 'w', encoding='utf-8') as f:
            f.write(umid_tf)
        generated_files['r-umid.tf'] = umid_path
        
        # Generate disk encryption set file (r-dsk.tf)
        dsk_tf = self._generate_disk_encryption_set_tf()
        dsk_path = os.path.join(output_dir, "r-dsk.tf")
        with open(dsk_path, 'w', encoding='utf-8') as f:
            f.write(dsk_tf)
        generated_files['r-dsk.tf'] = dsk_path
        
        # Generate private endpoints file (r-pe.tf)
        pe_tf = self._generate_private_endpoints_tf()
        pe_path = os.path.join(output_dir, "r-pe.tf")
        with open(pe_path, 'w', encoding='utf-8') as f:
            f.write(pe_tf)
        generated_files['r-pe.tf'] = pe_path
        
        return generated_files
    
    def _generate_configuration_files(self, output_dir: str) -> Dict[str, str]:
        """Generate configuration files (variables.tf, terraform.tfvars, etc.)."""
        
        generated_files = {}
        
        # variables.tf
        variables_tf = self._generate_variables_tf()
        variables_path = os.path.join(output_dir, "variables.tf")
        with open(variables_path, 'w', encoding='utf-8') as f:
            f.write(variables_tf)
        generated_files['variables.tf'] = variables_path
        
        # tfvars
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
        
        # Generate versions.tf
        versions_tf = self._generate_versions_tf()
        versions_path = os.path.join(output_dir, "versions.tf")
        with open(versions_path, 'w', encoding='utf-8') as f:
            f.write(versions_tf)
        generated_files['versions.tf'] = versions_path
        
        # Generate data.tf
        data_tf = self._generate_data_tf()
        data_path = os.path.join(output_dir, "data.tf")
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(data_tf)
        generated_files['data.tf'] = data_path
        
        # Generate locals.tf
        locals_tf = self._generate_locals_tf()
        locals_path = os.path.join(output_dir, "locals.tf")
        with open(locals_path, 'w', encoding='utf-8') as f:
            f.write(locals_tf)
        generated_files['locals.tf'] = locals_path
        
        return generated_files
    
    def _generate_variables_tf(self) -> str:
        """Generate variables.tf with complex object structures following module.md patterns."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        
        variables_tf = f'''# Begin variables.tf

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
  default  = "WEST US 3"
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
  description = <<-EOT
  map(object({{
    name              =  
    size              = The SKU which should be used for this Virtual Machine. Nonprod options: Standard_B2s_v2,Standard_B4as_v2,Standard_B4ls_v2,Standard_B16als_v2,Standard_B16as_v2,Standard_B8als_v2,Standard_B4als_v2,Standard_B8s_v2
    zone              = (optional) The Availability Zone which the Virtual Machine should be allocated in, only one zone would be accepted. If set then this module won't create `azurerm_availability_set` resource. Changing this forces a new resource to be created.
    image_os          = Enum flag of virtual machine's os system. windows or linux
    image_urn         = Azure urn Publisher:Offer:SKU:Version
    ip_allocation     = The allocation method used for the Private IP Address. Possible values are Dynamic and Static
    os_disk_name      = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
    os_disk_size      = The Size of the Internal OS Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you'll need to repartition the disk to use the remaining space.
    os_disk_type      = (optional) Storage type of the OS disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
    os_disk_tier      = (optional) The disk performance tier to use. Possible values are documented here https://learn.microsoft.com/en-us/azure/virtual-machines/disks-change-performance. This feature is currently supported only for premium SSDs.
    data_disk_sizes   = (optional) Specifies the size of the managed disk to create in gigabytes. If `create_option` is `Copy` or `FromImage`, then the value must be equal to or greater than the source's size. The size can only be increased. In certain conditions the Data Disk size can be updated without shutting down the Virtual Machine, however only a subset of Virtual Machine SKUs/Disk combinations support this. More information can be found [for Linux Virtual Machines](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/expand-disks?tabs=azure-cli%2Cubuntu#expand-without-downtime) and [Windows Virtual Machines](https://learn.microsoft.com/azure/virtual-machines/windows/expand-os-disk#expand-without-downtime) respectively. If No Downtime Resizing is not available, be aware that changing this value is disruptive if the disk is attached to a Virtual Machine. The VM will be shut down and de-allocated as required by Azure to action the change. Terraform will attempt to start the machine again after the update if it was in a `running` state when the apply was started."
    data_disk_type    = (optional) Storage type of the data disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
    data_disks = map(object({{
      name = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
      size = The Size of the data Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you'll need to repartition the disk to use the remaining space.
      type = (optional) Storage type of the data disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
      tier = (optional) The disk performance tier to use. Possible values are documented here https://learn.microsoft.com/en-us/azure/virtual-machines/disks-change-performance. This feature is currently supported only for premium SSDs.
    }}))
    tags = list(object({{
      "role"             = 
      "patch-optin"      = (YES,NO)
      "snow-item"        = If the vm is part of a different ticket provide it
    }}))
  }}))
  EOT
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
        
        return variables_tf
    
    def _generate_tfvars(self) -> str:
        """Generate terraform.tfvars with actual values from Excel data."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        build_env = self.terraform_data.get('build_environment', {})
        
        # Extract values from Excel data
        project_name = project_info.get('project_name', 'default-project')
        app_name = project_info.get('application_name', 'default-app')
        environment = project_info.get('environment', 'DEV')
        
        # Get location from build_environment (now properly extracted)
        location = build_env.get('key_value_pairs', {}).get('Location', 
                   build_env.get('key_value_pairs', {}).get('location', 'WEST US 3'))
        
        # Generate VM list
        vm_list = self._generate_vm_list_for_tfvars()
        
        # Generate subnets
        subnets = self._generate_subnets_for_tfvars()
        
        # Generate application security groups
        application_security_groups = self._generate_asg_for_tfvars()
        
        # Generate private endpoints
        private_endpoints = self._generate_private_endpoints_for_tfvars()
        
        # Generate network security rules
        network_security_rules = self._generate_nsg_rules_for_tfvars()
        
        # Extract or construct SPN name from project data
        spn_name = build_env.get('key_value_pairs', {}).get('SPN', 
                   build_env.get('key_value_pairs', {}).get('Service Principal', 
                   f"spn-terraform-{project_name.lower().replace(' ', '-')}"))
        
        # Extract key vault settings from raw_data (from Excel source)
        kvlt_sku = self._get_raw_value('sku_name', 'Build_ENV', 'standard')
        kvlt_retention = self._get_raw_value('soft_delete_retention_days', 'Build_ENV', 90)
        kvlt_public_access_raw = self._get_raw_value('public_network_access', 'Build_ENV', 1)
        
        # Convert public_network_access from numeric (1/0) to boolean string
        if kvlt_public_access_raw == 1:
            kvlt_public_access = 'true'
        elif kvlt_public_access_raw == 0:
            kvlt_public_access = 'false'
        else:
            kvlt_public_access = str(kvlt_public_access_raw).lower() if isinstance(kvlt_public_access_raw, bool) else 'true'
        
        tfvars = f'''# Begin terraform.tfvars

spn      = "{spn_name}"
location = "{location}"
resource_group_name = "rg-{project_name.lower().replace(' ', '-')}-{environment.lower()}"

application_security_groups = {application_security_groups}

disk_encryption_set_name    = "dsk-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
user_assigned_identity_name = "umid-{project_name.lower().replace(' ', '-')}-{environment.lower()}"

key_vault = {{
  name                       = "kvlt-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
  sku_name                   = "{kvlt_sku}"
  soft_delete_retention_days = {kvlt_retention}
  public_network_access      = {kvlt_public_access}
  snet_key                   = "snet1"
  key_name                   = "key-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
}}

subnets = {subnets}

private_endpoints = {private_endpoints}

network_security_rules = {network_security_rules}

vm_list = {vm_list}

common_tags = {{
  "shared-service-name" = "NA",
  "app-name"            = "{app_name}",
  "environment"         = "{environment}",
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "Bronze",
  "snow-item"           = "{project_info.get('service_now_ticket', 'RITM000000')}",
  "it-cost-center"      = "5541",
  "it-domain"           = "Platform Engineering",
  "lineofbusiness"      = "Amerihome Mortgage",
  "department"          = "Cloud Engineering",
  "cost-center"         = "6500"
}}
'''
        
        return tfvars
    
    def _generate_vm_list_for_tfvars(self) -> str:
        """Generate VM list for tfvars file with actual values from Excel."""
        
        vm_instances = self.terraform_data.get('vm_instances', [])
        project_info = self.terraform_data.get('project_info', {})
        
        if not vm_instances:
            return "{}"
        
        vm_entries = []
        for i, vm in enumerate(vm_instances):  # Process all VMs
            vm_name = self._extract_vm_name(vm, i)
            vm_size = self._extract_vm_size(vm)
            os_type = self._extract_os_type(vm)
            
            # Extract VM settings from raw_data first, then fall back to extraction functions
            # VM config is in Resources sheet, not Build_ENV
            # Check for vm1-specific values first, then generic values
            vm_key = f"vm{i+1}" if i < 10 else f"vm{i+1}"
            os_disk_size = (self._get_raw_value(f'vm_list.{vm_key}.os_disk_size', 'Resources') or 
                           self._get_raw_value('vm_list.vm1.os_disk_size', 'Resources') or 
                           self._extract_vm_disk_size(vm))
            os_disk_type = (self._get_raw_value(f'vm_list.{vm_key}.os_disk_type', 'Resources') or 
                           self._get_raw_value('vm_list.vm1.os_disk_type', 'Resources') or 
                           self._extract_vm_disk_type(vm))
            ip_allocation = (self._get_raw_value(f'vm_list.{vm_key}.ip_allocation', 'Resources') or 
                            self._get_raw_value('vm_list.vm1.ip_allocation', 'Resources') or 
                            'Dynamic')
            
            # Extract additional fields from VM data
            role = vm.get('Role', project_info.get('role', 'Application'))
            patch_optin = vm.get('Patch Optin', project_info.get('patch_optin', 'NO'))
            snow_item = vm.get('Service Now Ticket', project_info.get('service_now_ticket', 'RITM000000'))
            
            # Determine image URN based on OS type
            if os_type == "windows":
                image_urn = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
            else:
                image_urn = "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest"
            
            vm_entry = f'''  vm{i+1} = {{
    name              = "{vm_name}"
    size              = "{vm_size}"
    zone              = null
    image_os          = "{os_type}"
    marketplace_image = false
    image_urn         = "{image_urn}"
    ip_allocation     = "{ip_allocation}"
    identity_type     = "SystemAssigned, UserAssigned"
    os_disk_size      = {os_disk_size}
    os_disk_type      = "{os_disk_type}"
    os_disk_tier      = null
    data_disk_sizes   = [50, 50]
    data_disk_type    = "Standard_LRS"
    snet_key          = "snet1"
    asg_key           = "asg_nic"
    tags = {{
      "role"        = "{role}",
      "patch-optin" = "{patch_optin}",
      "snow-item"   = "{snow_item}"
    }}
  }}'''
            vm_entries.append(vm_entry)
        
        return f'''{{
{chr(10).join(vm_entries)}
}}'''
    
    def _generate_subnets_for_tfvars(self) -> str:
        """Generate subnets configuration for tfvars from Excel or project data."""
        
        project_info = self.terraform_data.get('project_info', {})
        build_env = self.terraform_data.get('build_environment', {})
        
        # Extract project/app name for resource naming
        app_name = project_info.get('application_name', 'app')
        project_name = project_info.get('project_name', 'project')
        environment = project_info.get('environment', 'dev')
        subscription = build_env.get('key_value_pairs', {}).get('Subscription', 'subscription')
        
        # Construct resource names from project data instead of hardcoded test values
        network_rg = f"rg-{project_name.lower()}-networking"
        vnet_name = f"vnet-{project_name.lower()}-{environment.lower()}"
        nsg_name = f"nsg-{project_name.lower()}-{environment.lower()}"
        route_table_name = f"rt-{project_name.lower()}-{environment.lower()}"
        subnet_name = f"snet-{app_name.lower()}-{environment.lower()}"
        
        # TODO: Extract actual subscription ID from Excel if available
        # For now, use placeholder that needs to be updated
        subscription_id = "SUBSCRIPTION_ID_PLACEHOLDER"
        
        return f'''{{
  snet1 = {{
    resource_group_name  = "{network_rg}"
    virtual_network_name = "{vnet_name}"
    network_security_group_id   = "/subscriptions/{subscription_id}/resourceGroups/{network_rg}/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}"
    route_table_id              = "/subscriptions/{subscription_id}/resourceGroups/{network_rg}/providers/Microsoft.Network/routeTables/{route_table_name}"
    name              = "{subnet_name}"
    prefixes          = ["10.0.1.0/24"]  # TODO: Extract from Excel if available
    service_endpoints = ["Microsoft.KeyVault"]
  }}
}}'''
    
    def _generate_asg_for_tfvars(self) -> str:
        """Generate application security groups for tfvars from project data."""
        
        project_info = self.terraform_data.get('project_info', {})
        app_name = project_info.get('application_name', 'app')
        environment = project_info.get('environment', 'dev')
        
        # Use project-specific naming instead of hardcoded test values
        return f'''{{
  asg_nic = {{
    name = "asg-{app_name.lower()}-nic-{environment.lower()}"
  }}
  asg_pe = {{
    name = "asg-{app_name.lower()}-pe-{environment.lower()}"
  }}
}}'''
    
    def _generate_private_endpoints_for_tfvars(self) -> str:
        """Generate private endpoints for tfvars from project data."""
        
        project_info = self.terraform_data.get('project_info', {})
        app_name = project_info.get('application_name', 'app')
        environment = project_info.get('environment', 'dev')
        
        # Use project-specific naming instead of hardcoded test values
        return f'''{{
  pe_kvlt = {{
    name                           = "pvep-kvlt-{app_name.lower()}-{environment.lower()}"
    subresource_names              = ["vault"]
    snet_key                       = "snet1"
    asg_key                        = "asg_pe"
  }}
}}'''
    
    def _generate_nsg_rules_for_tfvars(self) -> str:
        """Generate network security rules for tfvars from Excel NSG data."""
        
        security_groups = self.terraform_data.get('security_groups', [])
        project_info = self.terraform_data.get('project_info', {})
        
        project_name = project_info.get('project_name', 'project')
        environment = project_info.get('environment', 'dev')
        
        # Use project-specific networking resource group
        network_rg = f"rg-{project_name.lower()}-networking"
        nsg_name = f"nsg-{project_name.lower()}-{environment.lower()}"
        
        if not security_groups:
            return f'''{{
  resource_group_name         = "{network_rg}"
  network_security_group_name = "{nsg_name}"
  rules = []
}}'''
        
        rules = []
        for i, rule in enumerate(security_groups):  # Process all rules
            # Extract actual values from Excel NSG data
            rule_name = rule.get('name', f'rule_{i}')
            priority = rule.get('priority', 100 + i * 10)
            direction = rule.get('direction', 'Inbound')
            access = rule.get('access', 'Allow')
            protocol = rule.get('protocol', 'Tcp')
            source_port = rule.get('source_port_range', '*')
            dest_ports = rule.get('destination_port_ranges', ['443'])
            description = rule.get('description', f'Security rule for {project_name}')
            
            # Handle port ranges - could be string or list
            if isinstance(dest_ports, str):
                dest_ports = [dest_ports]
            
            # Convert list to Terraform format with double quotes
            dest_ports_str = '[' + ', '.join([f'"{port}"' for port in dest_ports]) + ']'
            
            rule_entry = f'''    {{
      name                       = "{rule_name}"
      source_name                = "{rule.get('source_name', 'Source')}"
      destination_name           = "{rule.get('destination_name', 'Destination')}"
      priority                   = {priority}
      direction                  = "{direction}"
      access                     = "{access}"
      protocol                   = "{protocol}"
      source_port_range          = "{source_port}"
      destination_port_ranges    = {dest_ports_str}
      source_asg_keys            = ["asg_nic"]
      destination_asg_keys       = ["asg_pe"]
      description                = "{description}"
    }}'''
            rules.append(rule_entry)
        
        rules_text = chr(10).join(rules)
        return f'''{{
  resource_group_name         = "{network_rg}"
  network_security_group_name = "{nsg_name}"
  rules = [
{rules_text}
  ]
}}'''
    
    def _generate_outputs_tf(self) -> str:
        """Generate outputs.tf following module.md pattern."""
        
        return '''# Begin outputs.tf

output "build_validation" {
  value = module.base-vm.build_validation
}'''
    
    def _generate_versions_tf(self) -> str:
        """Generate versions.tf following module.md pattern."""
        
        return '''# Begin versions.tf

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

terraform {
  required_version = ">=1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>4.14"
    }
  }
}'''
    
    def _generate_data_tf(self) -> str:
        """Generate data.tf following module.md pattern."""
        
        return '''# Begin data.tf

data "azurerm_client_config" "current" {}

data "azurerm_subscription" "subscription" {
  subscription_id = data.azurerm_client_config.current.subscription_id
}

data "azuread_service_principal" "spn" {
  display_name = var.spn
}'''
    
    def _generate_locals_tf(self) -> str:
        """Generate locals.tf following module.md pattern."""
        
        return '''# Begin locals.tf

locals {
  common_tags = {
    for tag, value in var.common_tags : "wab:${tag}" => value
  }
}

locals {
  resource_specific_tags = {
    for tag, value in var.resource_specific_tags : "wab:${tag}" => value
  }
}'''
    
    def _generate_resource_group_tf(self) -> str:
        """Generate resource group file (r-rg.tf)."""
        
        return '''# Begin r-rg.tf

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = merge(
    tomap(
      { "wab:resource-name" = var.resource_group_name }
    ),
    local.common_tags, local.resource_specific_tags
  )
}'''
    
    def _generate_application_security_groups_tf(self) -> str:
        """Generate application security groups file (r-asg.tf)."""
        
        return '''# Begin r-asg.tf

resource "azurerm_application_security_group" "asg" {
  for_each            = var.application_security_groups
  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tags = merge(
    tomap(
      { "wab:resource-name" = "${each.value.name}" }
    ),
    local.common_tags, local.resource_specific_tags
  )
}'''
    
    def _generate_subnets_tf(self) -> str:
        """Generate subnets file (r-snet.tf)."""
        
        return '''# Begin r-snet.tf

resource "azurerm_subnet" "snet" {
  for_each = coalesce(var.subnets, {})

  name                 = each.value.name
  address_prefixes     = each.value.prefixes
  resource_group_name  = each.value.resource_group_name
  service_endpoints    = each.value.service_endpoints
  virtual_network_name = each.value.virtual_network_name
}'''
    
    def _generate_network_security_rules_tf(self) -> str:
        """Generate network security rules file (r-nsr.tf)."""
        
        return '''# Begin r-nsr.tf

resource "azurerm_network_security_rule" "nsr" {
  for_each                                   = coalesce(local.rules, {})
  resource_group_name                        = each.value.resource_group_name
  network_security_group_name                = each.value.network_security_group_name
  name                                       = each.value.name
  priority                                   = each.value.priority
  direction                                  = each.value.direction
  access                                     = each.value.access
  protocol                                   = each.value.protocol
  description                                = each.value.description
  source_port_range                          = each.value.source_port_range
  source_port_ranges                         = each.value.source_port_ranges
  destination_port_range                     = each.value.destination_port_range
  destination_port_ranges                    = each.value.destination_port_ranges
  source_address_prefix                      = each.value.source_address_prefix
  source_address_prefixes                    = each.value.source_address_prefixes
  destination_address_prefix                 = each.value.destination_address_prefix
  destination_address_prefixes               = each.value.destination_address_prefixes
  source_application_security_group_ids      = each.value.source_application_security_group_ids
  destination_application_security_group_ids = each.value.destination_application_security_group_ids
}'''
    
    def _generate_key_vault_tf(self) -> str:
        """Generate key vault file (r-kvlt.tf)."""
        
        return '''# Begin r-kvlt.tf

resource "azurerm_key_vault" "kvlt" {
  name                          = coalesce(var.key_vault.name, "kvlt-${lower(trimspace(substr(local.common_tags["wab:app-name"], 0, 4)))}-${lower(local.common_tags["wab:environment"])}")
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  tenant_id                     = data.azurerm_client_config.current.tenant_id
  public_network_access_enabled = var.key_vault.public_network_access
  soft_delete_retention_days    = var.key_vault.soft_delete_retention_days
  sku_name                      = var.key_vault.sku_name

  enable_rbac_authorization       = true
  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  purge_protection_enabled        = true

  tags = merge(
    tomap(
      { "wab:resource-name" = coalesce(var.key_vault.name, "kvlt-${lower(trimspace(substr(local.common_tags["wab:app-name"], 0, 4)))}-${lower(local.common_tags["wab:environment"])}") }
    ),
    local.common_tags, local.resource_specific_tags
  )
}

resource "azurerm_key_vault_key" "kvkey" {
  name            = coalesce(var.key_vault.key_name, "key-${lower(trimspace(local.common_tags["wab:app-name"]))}-${lower(local.common_tags["wab:environment"])}")
  key_vault_id    = azurerm_key_vault.kvlt.id
  key_type        = "RSA"
  key_size        = 2048
  key_opts        = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
  curve           = null
  expiration_date = null
  not_before_date = null
  tags            = {}
}'''
    
    def _generate_user_assigned_identity_tf(self) -> str:
        """Generate user assigned identity file (r-umid.tf)."""
        
        return '''# Begin r-umid.tf

resource "azurerm_user_assigned_identity" "umid" {
  depends_on          = [azurerm_resource_group.rg]
  name                = coalesce(var.user_assigned_identity_name, "umid-${lower(trimspace(substr(local.common_tags["wab:app-name"], 0, 4)))}-${lower(local.common_tags["wab:environment"])}")
  location            = var.location
  resource_group_name = var.resource_group_name
  tags = merge(
    tomap(
      { "wab:resource-name" = coalesce(var.user_assigned_identity_name, "umid-${lower(trimspace(substr(local.common_tags["wab:app-name"], 0, 4)))}-${lower(local.common_tags["wab:environment"])}") }
    ),
    local.common_tags, local.resource_specific_tags
  )
}'''
    
    def _generate_disk_encryption_set_tf(self) -> str:
        """Generate disk encryption set file (r-dsk.tf)."""
        
        return '''# Begin r-dsk.tf

resource "azurerm_disk_encryption_set" "dsk" {
  depends_on                = [azurerm_role_assignment.umid_role_assignement]
  name                      = coalesce(var.disk_encryption_set_name, "dsk-${lower(trimspace(substr(local.common_tags["wab:app-name"], 0, 4)))}-${lower(local.common_tags["wab:environment"])}")
  location                  = var.location
  resource_group_name       = var.resource_group_name
  auto_key_rotation_enabled = true
  key_vault_key_id          = azurerm_key_vault_key.kvkey.versionless_id
  encryption_type           = "EncryptionAtRestWithCustomerKey"
  federated_client_id       = null
  tags = merge(
    tomap(
      { "wab:resource-name" = coalesce(var.disk_encryption_set_name, "dsk-${lower(trimspace(substr(local.common_tags["wab:app-name"], 0, 4)))}-${lower(local.common_tags["wab:environment"])}") }
    ),
    local.common_tags, local.resource_specific_tags
  )

  identity {
    identity_ids = [azurerm_user_assigned_identity.umid.id]
    type         = "UserAssigned"
  }
}'''
    
    def _generate_private_endpoints_tf(self) -> str:
        """Generate private endpoints file (r-pe.tf)."""
        
        return '''# Begin r-pe.tf

resource "azurerm_private_endpoint" "pe" {
  for_each            = var.private_endpoints
  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id = coalesce(
    try(azurerm_subnet.snet[each.value.snet_key].id, null),
    try(data.azurerm_subnet.snet[each.value.snet_key].id, null)
  )
  private_dns_zone_group {
    name                 = coalesce(each.value.private_dns_zone_group_name, "default")
    private_dns_zone_ids = coalesce(each.value.private_dns_zone_ids, ["/subscriptions/f3b58ef2-13a2-492a-b3b5-8688d74fd868/resourceGroups/rg-privatedns-prod-001/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net"])
  }
  private_service_connection {
    name                           = each.value.name
    is_manual_connection           = coalesce(each.value.is_manual_connection, "false")
    subresource_names              = each.value.subresource_names
    private_connection_resource_id = coalesce(each.value.private_connection_resource_id, azurerm_key_vault.kvlt.id)
  }
  custom_network_interface_name = "nic01-${each.value.name}"
  tags = merge(
    tomap(
      { "wab:resource-name" = "${each.value.name}" }
    ),
    local.common_tags, local.resource_specific_tags
  )
}'''
    
    def _generate_validate_script(self) -> str:
        """Generate validation script."""
        
        project_info = self.terraform_data.get('project_info', {})
        project_name = project_info.get('project_name', 'default-project')
        
        return f'''#!/bin/bash
# Validation Script for {project_name}
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

set -e  # Exit on any error

echo "=========================================="
echo "Validating {project_name} Infrastructure"
echo "=========================================="

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform is not installed or not in PATH"
    exit 1
fi

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init
fi

# Format check
echo "Checking Terraform formatting..."
terraform fmt -check -diff

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

# Security scan (if tfsec is available)
if command -v tfsec &> /dev/null; then
    echo "Running security scan..."
    tfsec .
else
    echo "tfsec not found - skipping security scan"
    echo "Install tfsec for security analysis: https://aquasecurity.github.io/tfsec/"
fi

echo ""
echo "=========================================="
echo "Validation completed successfully!"
echo "=========================================="
'''
    
    def _generate_documentation(self, output_dir: str) -> Dict[str, str]:
        """Generate documentation files."""
        
        generated_files = {}
        
        # readme
        readme = self._generate_readme()
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        generated_files['README.md'] = readme_path
        
        # gitignore
        gitignore = self._generate_gitignore()
        gitignore_path = os.path.join(output_dir, ".gitignore")
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore)
        generated_files['.gitignore'] = gitignore_path
        
        return generated_files
    
    def _generate_readme(self) -> str:
        """Generate README.md file."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_count = len(self.terraform_data.get('vm_instances', []))
        
        return f'''# {project_info.get('project_name', 'Default Project')} Infrastructure

This Terraform configuration follows the module.md patterns and creates Azure infrastructure using the base-vm module.

## Generated Files

This package includes the following files following the module.md organization pattern:

### Module Files
- `m-basevm.tf` - Main module call to base-vm module

### Resource Files  
- `r-rg.tf` - Resource group
- `r-asg.tf` - Application security groups
- `r-snet.tf` - Subnets
- `r-nsr.tf` - Network security rules
- `r-kvlt.tf` - Key vault
- `r-umid.tf` - User assigned identity
- `r-dsk.tf` - Disk encryption set
- `r-pe.tf` - Private endpoints

### Configuration Files
- `variables.tf` - Variable declarations with validation
- `terraform.tfvars` - Variable values
- `outputs.tf` - Output definitions
- `versions.tf` - Provider and Terraform versions
- `data.tf` - Data sources
- `locals.tf` - Local values

### Scripts
- `scripts/validate.sh` - Validation script

## Quick Start

```bash
# Initialize Terraform
terraform init

# Validate configuration
./scripts/validate.sh

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

## Infrastructure Overview

- **VMs**: {vm_count}
- **Environment**: {project_info.get('environment', 'DEV')}
- **Location**: {project_info.get('location', 'WEST US 3')}

## Configuration

Edit `terraform.tfvars` to customize:
- VM configurations
- Network settings
- Security rules
- Tags and naming

## Module Integration

This configuration uses the external base-vm module:
- **Source**: app.terraform.io/wab-cloudengineering-org/base-vm/iac
- **Version**: __DYNAMIC_MODULE_VERSION__

---

**Generated by Enhanced Terraform Generator v2**  
**Source**: Excel data from {project_info.get('project_name', 'Unknown Project')}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file for Terraform."""
        
        return '''# Terraform files
*.tfstate
*.tfstate.*
*.tfplan
*.tfplan.*
.terraform/
.terraform.lock.hcl

# Crash log files
crash.log
crash.*.log

# Exclude all .tfvars files, which are likely to contain sensitive data
*.tfvars
*.tfvars.json

# Ignore override files as they are usually used to override resources locally
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Include override files you do wish to add to version control using negated pattern
# !example_override.tf

# Include tfplan files to ignore the plan output of command: terraform plan -out=tfplan
# example: *tfplan*

# Ignore CLI configuration files
.terraformrc
terraform.rc

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Log files
*.log

# Temporary files
*.tmp
*.temp
'''
    
    def _extract_vm_name(self, vm: Dict[str, Any], index: int) -> str:
        """Extract VM name from various possible fields."""
        name_fields = ['Hostname', 'hostname', 'VM Name', 'vm_name', 'Server Name', 'server_name', 'Name', 'name']
        
        for field in name_fields:
            if field in vm and vm[field] and str(vm[field]).strip():
                # Clean and return the name
                name = str(vm[field]).strip()
                # Remove any non-alphanumeric characters except hyphens and underscores
                import re
                name = re.sub(r'[^\w\-]', '-', name)
                return name
        
        # If no name found, use project info to create one
        project_info = self.terraform_data.get('project_info', {})
        app_name = project_info.get('application_name', 'vm')
        return f"{app_name}-{index+1:02d}"
    
    def _extract_vm_size(self, vm: Dict[str, Any]) -> str:
        """Extract VM size from various possible fields."""
        size_fields = ['Recommended SKU', 'SKU', 'Size', 'size', 'VM Size', 'vm_size', 'Instance Type', 'instance_type', 'Choose Node Size']
        
        for field in size_fields:
            if field in vm and vm[field] and str(vm[field]).strip():
                size = str(vm[field]).strip()
                # Validate it looks like an Azure SKU
                if 'Standard_' in size or 'Basic_' in size:
                    return size
        
        # Try project_info as fallback
        project_info = self.terraform_data.get('project_info', {})
        vm_size = project_info.get('vm_size')
        if vm_size and str(vm_size).strip():
            return str(vm_size).strip()
        
        return "Standard_B2s_v2"
    
    def _extract_os_type(self, vm: Dict[str, Any]) -> str:
        """Extract OS type from various possible fields."""
        os_fields = ['OS Image*', 'OS Image', 'os_image', 'Image', 'image', 'OS', 'os', 'Operating System']
        
        for field in os_fields:
            if field in vm and vm[field] and str(vm[field]).strip():
                os_value = str(vm[field]).strip().lower()
                if 'windows' in os_value or 'win' in os_value:
                    return "windows"
                elif 'linux' in os_value or 'ubuntu' in os_value or 'rhel' in os_value or 'centos' in os_value:
                    return "linux"
        
        # Try project_info as fallback
        project_info = self.terraform_data.get('project_info', {})
        os_image = project_info.get('os_image')
        if os_image and str(os_image).strip():
            os_value = str(os_image).strip().lower()
            if 'windows' in os_value or 'win' in os_value:
                return "windows"
            elif 'linux' in os_value or 'ubuntu' in os_value:
                return "linux"
        
        return "windows"  # Default to windows
    
    def _extract_vm_disk_size(self, vm: Dict[str, Any]) -> int:
        """Extract OS disk size from VM data."""
        disk_fields = ['OS disk size', 'os_disk_size', 'Disk Size', 'disk_size']
        
        for field in disk_fields:
            if field in vm and vm[field]:
                try:
                    size = str(vm[field]).strip()
                    # Extract numeric value
                    import re
                    match = re.search(r'(\d+)', size)
                    if match:
                        return int(match.group(1))
                except (ValueError, TypeError):
                    pass
        
        return 30  # Default (more reasonable for OS disk)
    
    def _extract_vm_disk_type(self, vm: Dict[str, Any]) -> str:
        """Extract OS disk type from VM data."""
        type_fields = ['OS disk type', 'os_disk_type', 'Disk Type', 'disk_type']
        
        for field in type_fields:
            if field in vm and vm[field] and str(vm[field]).strip():
                disk_type = str(vm[field]).strip()
                if '_LRS' in disk_type or '_ZRS' in disk_type:
                    return disk_type
        
        return "Standard_LRS"  # Default
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of what will be created."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        security_groups = self.terraform_data.get('security_groups', [])
        
        summary = {
            'project_name': project_info.get('project_name', 'default-project'),
            'application_name': project_info.get('application_name', 'default-app'),
            'architecture': 'Module-based (base-vm module)',
            'resources': {
                'virtual_machines': len(vm_instances),
                'network_security_rules': len(security_groups),
                'application_security_groups': 2,
                'subnets': 1,
                'private_endpoints': 1,
                'key_vaults': 1,
                'user_assigned_identities': 1,
                'disk_encryption_sets': 1
            },
            'file_organization': {
                'module_files': 1,
                'resource_files': 8,
                'configuration_files': 6
            }
        }
        
        return summary


def main():
    """Main function for testing the enhanced Terraform generator v2."""
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else "comprehensive_excel_data.json"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "terraform_output_v2"
    
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return False
    
    # Create generator
    generator = EnhancedTerraformGeneratorV2(json_file)
    
    # Generate summary
    summary = generator.generate_summary()
    print("Enhanced Terraform Generation v2 Summary:")
    print(f"  Project: {summary['project_name']}")
    print(f"  Application: {summary['application_name']}")
    print(f"  Architecture: {summary['architecture']}")
    print(f"  VMs: {summary['resources']['virtual_machines']}")
    print(f"  Security Rules: {summary['resources']['network_security_rules']}")
    print(f"  Total Files: {sum(summary['file_organization'].values())}")
    
    # Generate Terraform files
    print(f"\nGenerating Terraform files in: {output_dir}")
    generated_files = generator.generate_terraform_files(output_dir)
    
    print("\nGenerated files:")
    for filename, filepath in generated_files.items():
        print(f"  {filename}: {filepath}")
    
    print(f"\nSUCCESS: Enhanced Terraform files generated successfully!")
    print(f"  Architecture: Module-based with base-vm module")
    print(f"  Organization: Follows module.md patterns")
    print(f"  To deploy: cd {output_dir} && terraform init && terraform plan")
    
    return True


if __name__ == "__main__":
    main()
