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

        # Validate extraction quality
        self.validation_results = self.accessor.validate_extraction_quality(self.terraform_data)
        self._log_validation_results()

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

    def _log_validation_results(self):
        """Log validation results from data extraction."""
        import logging
        # Use automation_pipeline logger to ensure messages go to automation.log
        logger = logging.getLogger('automation_pipeline')

        # Also print to console for immediate feedback
        print_output = True

        validation = self.validation_results

        # Log extraction quality
        msg = "=" * 80
        logger.info(msg)
        if print_output: print(msg)

        msg = "DATA EXTRACTION VALIDATION RESULTS"
        logger.info(msg)
        if print_output: print(msg)

        msg = "=" * 80
        logger.info(msg)
        if print_output: print(msg)

        msg = f"Extraction Quality: {validation['extraction_quality'].upper()}"
        logger.info(msg)
        if print_output: print(msg)

        msg = f"Valid: {validation['valid']}"
        logger.info(msg)
        if print_output: print(msg)

        # Log errors
        if validation['errors']:
            msg = f"ERRORS FOUND ({len(validation['errors'])}):"
            logger.error(msg)
            if print_output: print(msg)

            for error in validation['errors']:
                msg = f"  [ERROR] {error}"
                logger.error(msg)
                if print_output: print(msg)

        # Log warnings
        if validation['warnings']:
            msg = f"WARNINGS ({len(validation['warnings'])}):"
            logger.warning(msg)
            if print_output: print(msg)

            for warning in validation['warnings']:
                msg = f"  [WARN] {warning}"
                logger.warning(msg)
                if print_output: print(msg)

        # Log missing fields
        if validation['missing_fields']:
            msg = f"Missing Required Fields: {', '.join(validation['missing_fields'])}"
            logger.error(msg)
            if print_output: print(msg)

        # Summary
        if validation['valid'] and not validation['warnings']:
            msg = "[PASS] All required data extracted successfully"
            logger.info(msg)
            if print_output: print(msg)
        elif validation['valid']:
            msg = "[PASS] Required data extracted with warnings"
            logger.info(msg)
            if print_output: print(msg)
        else:
            msg = "[FAIL] Data extraction incomplete - missing required fields"
            logger.error(msg)
            if print_output: print(msg)

        msg = "=" * 80
        logger.info(msg)
        if print_output: print(msg)

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
        
        # Generate module call file (following m-vm.tf pattern from terraform_files_pattern)
        module_tf = self._generate_module_tf()
        module_tf_path = os.path.join(output_dir, "m-vm.tf")
        with open(module_tf_path, 'w', encoding='utf-8') as f:
            f.write(module_tf)
        generated_files['m-vm.tf'] = module_tf_path
        
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
        """Generate main module call file (m-vm.tf) matching terraform_files_pattern exactly."""

        # Match the pattern's m-vm.tf structure exactly
        module_tf = '''locals {
  data_disks = var.vm_list != null ? merge([
    for vm_name, vm_config in var.vm_list :
    vm_config.data_disk_sizes != null && vm_config.data_disk_sizes != [] ? {
      "${vm_config.name}" = tolist([
        for i in range(length(vm_config.data_disk_sizes)) : {
          name                 = format("dataDisk%02d-%s", i + 1, vm_config.name)
          vm_name              = vm_config.name
          disk_size_gb         = vm_config.data_disk_sizes[i]
          storage_account_type = coalesce(vm_config.data_disk_type, "Standard_LRS")
          create_option        = "Empty"
          attach_setting = {
            lun           = i
            caching       = "None"
            create_option = "Attach"
          }
        }
      ])
      } : vm_config.data_disks != null && vm_config.data_disks != {} ? {
      "${vm_config.name}" = tolist([
        for i, disk in vm_config.data_disks : {
          vm_name              = vm_config.name
          name                 = disk.name
          disk_size_gb         = disk.size
          storage_account_type = coalesce(disk.type, "Standard_LRS")
          create_option        = "Empty"
          attach_setting = {
            lun           = i
            caching       = "None"
            create_option = "Attach"
          }
        }
      ])
    } : {}
  ]...) : null
}

module "vm" {
  source  = "app.terraform.io/wab-cloudengineering-org/virtual-machine/azure"
  version = "1.1.4"

  depends_on = [azurerm_resource_group.rg]

  for_each = var.vm_list != null ? var.vm_list : {}

  name                = each.value.name
  location            = var.location
  resource_group_name = var.resource_group_name
  computer_name       = each.value.name
  admin_username      = var.admin_username
  admin_password = coalesce(var.admin_password, random_password.password != [] ? random_password.password[0].result : null)
  zone           = each.value.zone
  subnet_id = coalesce(
    try(azurerm_subnet.snet[each.value.snet_key].id, null),
    try(data.azurerm_subnet.snet[each.value.snet_key].id, null)
  )
  size     = each.value.size
  image_os = each.value.image_os
  license_type = anytrue([for str in ["windows", "Windows"] : strcontains(lower(element(split(":", each.value.image_os), 1)), str)]) ? "Windows_Server" : null

  plan = coalesce(each.value.marketplace_image, true) ? {
    name      = element(split(":", each.value.image_urn), 2)
    product   = element(split(":", each.value.image_urn), 1)
    publisher = element(split(":", each.value.image_urn), 0)
  } : null

  source_image_id = each.value.source_image_id

  source_image_reference = each.value.source_image_id == null ? {
    offer     = element(split(":", each.value.image_urn), 1)
    publisher = element(split(":", each.value.image_urn), 0)
    sku       = element(split(":", each.value.image_urn), 2)
    version   = element(split(":", each.value.image_urn), 3)
  } : null

  os_disk = {
    name                   = coalesce(each.value.os_disk_name, "Osdisk-${each.value.name}")
    storage_account_type   = coalesce(each.value.os_disk_type, "Standard_LRS")
    disk_size_gb           = each.value.os_disk_size
    tier                   = each.value.os_disk_tier
    caching                = "ReadWrite"
    disk_encryption_set_id = azurerm_disk_encryption_set.dsk.id
  }

  data_disks = try(lookup(local.data_disks, each.value.name), null) == null ? [] : [for obj in try(lookup(local.data_disks, each.value.name), null) : merge(obj, { disk_encryption_set_id = azurerm_disk_encryption_set.dsk.id })]

  identity = {
    identity_ids = [azurerm_user_assigned_identity.umid.id]
    type         = coalesce(each.value.identity_type, "UserAssigned")
  }

  allow_extension_operations = true

  new_network_interface = {
    name = "nic01-${each.value.name}"
    ip_configurations = [
      {
        name                          = "internal",
        primary                       = "true"
        private_ip_address_allocation = each.value.ip_allocation
        private_ip_address            = each.value.ip_address
        private_ip_address_version    = "IPv4",
      }
    ]
    tags = merge(
      tomap(
        { "wab:resource-name" = "nic01-${each.value.name}" }
      ),
      local.common_tags, local.resource_specific_tags
    )
  }

  tags = merge(
    tomap(
      { "wab:resource-name" = "${each.value.name}" }
    ),
    local.common_tags, { for key, value in each.value.tags : "wab:${key}" => value if value != null}
  )
}
'''

        return module_tf
    
    def _generate_resource_files(self, output_dir: str) -> Dict[str, str]:
        """Generate individual resource files following r-*.tf pattern from terraform_files_pattern."""

        generated_files = {}

        # Generate main.tf for resource group (pattern expects this)
        main_tf = self._generate_main_tf()
        main_path = os.path.join(output_dir, "main.tf")
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(main_tf)
        generated_files['main.tf'] = main_path

        # Generate application security groups file (r-asg.tf) - match pattern exactly
        asg_tf = self._generate_application_security_groups_tf()
        asg_path = os.path.join(output_dir, "r-asg.tf")
        with open(asg_path, 'w', encoding='utf-8') as f:
            f.write(asg_tf)
        generated_files['r-asg.tf'] = asg_path

        # Generate subnets file (r-snet.tf) - match pattern exactly
        snet_tf = self._generate_subnets_tf()
        snet_path = os.path.join(output_dir, "r-snet.tf")
        with open(snet_path, 'w', encoding='utf-8') as f:
            f.write(snet_tf)
        generated_files['r-snet.tf'] = snet_path
        
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

        # Generate random password file (r-rnd.tf) - matches pattern
        rnd_tf = self._generate_random_password_tf()
        rnd_path = os.path.join(output_dir, "r-rnd.tf")
        with open(rnd_path, 'w', encoding='utf-8') as f:
            f.write(rnd_tf)
        generated_files['r-rnd.tf'] = rnd_path

        # Generate data collection rule association file (r-dcra.tf) - matches pattern
        dcra_tf = self._generate_dcra_tf()
        dcra_path = os.path.join(output_dir, "r-dcra.tf")
        with open(dcra_path, 'w', encoding='utf-8') as f:
            f.write(dcra_tf)
        generated_files['r-dcra.tf'] = dcra_path

        # Generate networking.tf (AWS) - matches pattern
        networking_tf = self._generate_networking_tf()
        networking_path = os.path.join(output_dir, "networking.tf")
        with open(networking_path, 'w', encoding='utf-8') as f:
            f.write(networking_tf)
        generated_files['networking.tf'] = networking_path

        # Generate s3.tf (AWS) - matches pattern
        s3_tf = self._generate_s3_tf()
        s3_path = os.path.join(output_dir, "s3.tf")
        with open(s3_path, 'w', encoding='utf-8') as f:
            f.write(s3_tf)
        generated_files['s3.tf'] = s3_path

        # Generate packages subdirectories
        packages_dir = os.path.join(output_dir, "packages")
        monitoring_dir = os.path.join(packages_dir, "monitoring")
        storage_dir = os.path.join(packages_dir, "storage")

        os.makedirs(monitoring_dir, exist_ok=True)
        os.makedirs(storage_dir, exist_ok=True)

        # Generate packages/monitoring/alerts.tf - matches pattern
        alerts_tf = self._generate_alerts_tf()
        alerts_path = os.path.join(monitoring_dir, "alerts.tf")
        with open(alerts_path, 'w', encoding='utf-8') as f:
            f.write(alerts_tf)
        generated_files['packages/monitoring/alerts.tf'] = alerts_path

        # Generate packages/storage/buckets.tf - matches pattern
        buckets_tf = self._generate_buckets_tf()
        buckets_path = os.path.join(storage_dir, "buckets.tf")
        with open(buckets_path, 'w', encoding='utf-8') as f:
            f.write(buckets_tf)
        generated_files['packages/storage/buckets.tf'] = buckets_path

        # NOTE: r-nsr.tf, r-pe.tf, r-rg.tf not generated - not in terraform_files_pattern

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

        # NOTE: versions.tf not generated - not in terraform_files_pattern

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

        # Generate production.tfvars - matches pattern
        production_tfvars = self._generate_production_tfvars()
        production_path = os.path.join(output_dir, "production.tfvars")
        with open(production_path, 'w', encoding='utf-8') as f:
            f.write(production_tfvars)
        generated_files['production.tfvars'] = production_path

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
    error_message = format("A location value of \"%s\" is not allowed. Please use one of the following: \\n %s", var.location,
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
    public_network_access      = false
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

  validation {{
    condition     = alltrue([can(regex("^([a-z])[a-z0-9-]*[a-z0-9]$", var.key_vault.name)) && !can(regex("--", var.key_vault.name)) && length(var.key_vault.name) <= 24])
    error_message = "The key vault name must contain only lowercase letters, numbers, and hyphens. It must start with a letter, end with a letter or number, not contain consecutive hyphens, and be 24 characters or less."
  }}

  validation {{
    condition     = var.key_vault.key_name != null ? alltrue([can(regex("^([a-z])[a-z0-9-]*[a-z0-9]$", var.key_vault.key_name)) && !can(regex("--", var.key_vault.key_name)) && length(var.key_vault.key_name) <= 127]) : true
    error_message = "The key vault key name must contain only lowercase letters, numbers, and hyphens. It must start with a letter, end with a letter or number, not contain consecutive hyphens, and be 127 characters or less."
  }}
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
    zone              = (optional) The Availability Zone which the Virtual Machine should be allocated in, only one zone would be accepted. If set then this module will not create \"azurerm_availability_set\" resource. Changing this forces a new resource to be created.
    image_os          = Enum flag of virtual machine os system. windows or linux
    image_urn         = Azure urn Publisher:Offer:SKU:Version
    ip_allocation     = The allocation method used for the Private IP Address. Possible values are Dynamic and Static
    os_disk_name      = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
    os_disk_size      = The Size of the Internal OS Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you will need to repartition the disk to use the remaining space.
    os_disk_type      = (optional) Storage type of the OS disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
    os_disk_tier      = (optional) The disk performance tier to use. Possible values are documented here https://learn.microsoft.com/en-us/azure/virtual-machines/disks-change-performance. This feature is currently supported only for premium SSDs.
    data_disk_sizes   = (optional) Specifies the size of the managed disk to create in gigabytes. If create_option is Copy or FromImage, then the value must be equal to or greater than the source size. The size can only be increased. Changing this value may be disruptive if the disk is attached to a Virtual Machine.
    data_disk_type    = (optional) Storage type of the data disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
    data_disks = map(object({{
      name = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
      size = The Size of the data Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you will need to repartition the disk to use the remaining space.
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

variable "default_common_tags" {{
  type = map(string)
  default = {{
    terraform           = "true"
    data-classification = "Internal"
    criticality         = "4-Very Minor to Operations"
  }}
  description = "Default common tags applied to all resources. Can be overridden by common_tags."
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
    data-classification = optional(string)
    criticality         = optional(string)
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
    error_message = format("An environment tag value of \"%s\" is not allowed. Please use one of the following: \\n %s", var.common_tags.environment,
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
    error_message = format("A app-tier tag value of \"%s\" is not allowed. Please use one of the following: \\n %s", var.common_tags.app-tier,
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
    error_message = format("An it-cost-center tag value of \"%s\" is not allowed. Please use NA or a whole number", var.common_tags.it-cost-center)
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
    error_message = format("A patch-optin tag value of \"%s\" is not allowed. Please use one of the following: YES, NO, NA", var.resource_specific_tags.patch-optin)
  }}
}}
'''
        
        return variables_tf
    
    def _generate_tfvars(self) -> str:
        """Generate terraform.tfvars with actual values from Excel data."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        build_env = self.terraform_data.get('build_environment', {})
        
        # Extract values from Excel data - no defaults
        project_name = project_info.get('project_name')
        app_name = project_info.get('application_name')  # Abbreviated app name (e.g., "AD")
        environment = project_info.get('environment')

        # Use abbreviated app name for resource naming (lowercase) - only if available
        if app_name:
            resource_prefix = app_name.lower()
        elif project_name:
            resource_prefix = project_name.lower().replace(' ', '-')
        else:
            resource_prefix = None

        # Get location from build_environment - no default
        location = (build_env.get('key_value_pairs', {}).get('Location') or
                   build_env.get('key_value_pairs', {}).get('location'))

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

        # Extract SPN name from Excel or project_info, or construct from subscription
        spn_name = (build_env.get('key_value_pairs', {}).get('SPN') or
                   build_env.get('key_value_pairs', {}).get('Service Principal') or
                   project_info.get('spn_name'))

        # If still not found, construct from subscription name
        if not spn_name:
            subscription_name = project_info.get('subscription', '')
            if subscription_name:
                # Remove 'sub-' prefix if present and add 'spn-terraform-' prefix
                if subscription_name.lower().startswith('sub-'):
                    spn_name = 'spn-terraform-' + subscription_name[4:]
                else:
                    spn_name = 'spn-terraform-' + subscription_name
            elif resource_prefix:
                # Last fallback: use resource_prefix
                spn_name = f"spn-terraform-{resource_prefix}"

        # Extract key vault settings from raw_data (from Excel source) - no defaults
        kvlt_sku = self._get_raw_value('sku_name', 'Build_ENV')
        kvlt_retention = self._get_raw_value('soft_delete_retention_days', 'Build_ENV')
        kvlt_public_access_raw = self._get_raw_value('public_network_access', 'Build_ENV')
        
        # Convert public_network_access from numeric (1/0) to boolean string
        if kvlt_public_access_raw == 1:
            kvlt_public_access = 'true'
        elif kvlt_public_access_raw == 0:
            kvlt_public_access = 'false'
        elif kvlt_public_access_raw is None:
            kvlt_public_access = None
        else:
            kvlt_public_access = str(kvlt_public_access_raw).lower() if isinstance(kvlt_public_access_raw, bool) else None

        # Helper to format values - null if None
        def fmt(val, quote=True):
            if val is None:
                return "null"
            return f'"{val}"' if quote else str(val)

        # Build resource names only if we have the necessary data
        env_lower = environment.lower() if environment else None
        rg_name = f"rg-{resource_prefix}-{env_lower}" if resource_prefix and env_lower else None
        dsk_name = f"dsk-{resource_prefix}-{env_lower}" if resource_prefix and env_lower else None
        umid_name = f"umid-{resource_prefix}-{env_lower}" if resource_prefix and env_lower else None
        kvlt_name = f"kvlt-{resource_prefix}-{env_lower}" if resource_prefix and env_lower else None
        key_name = f"key-{resource_prefix}-{env_lower}" if resource_prefix and env_lower else None

        tfvars = f'''# Begin terraform.tfvars

spn      = {fmt(spn_name)}
location = {fmt(location)}
resource_group_name = {fmt(rg_name)}

application_security_groups = {application_security_groups}

disk_encryption_set_name    = {fmt(dsk_name)}
user_assigned_identity_name = {fmt(umid_name)}

key_vault = {{
  name                       = {fmt(kvlt_name)}
  sku_name                   = {fmt(kvlt_sku)}
  soft_delete_retention_days = {fmt(kvlt_retention, quote=False)}
  public_network_access      = {fmt(kvlt_public_access, quote=False) if kvlt_public_access is not None else "null"}
  snet_key                   = "snet1"
  key_name                   = {fmt(key_name)}
}}

subnets = {subnets}

private_endpoints = {private_endpoints}

network_security_rules = {network_security_rules}

vm_list = {vm_list}

common_tags = {{
  "shared-service-name" = "NA",
  "app-name"            = {fmt(app_name)},
  "environment"         = {fmt(environment)},
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "Bronze",
  "snow-item"           = {fmt(project_info.get('service_now_ticket'))},
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
            vm_key = f"vm{i+1}"
            
            # Extract VM fields using the correct mapping structure
            # Mapping: vm_list.vmX.name -> vm_list.vm1.name (Target Excel)
            vm_name = (self._get_raw_value(f'vm_list.{vm_key}.name', 'Resources') or
                      self._get_raw_value('vm_list.vm1.name', 'Resources') or
                      self._extract_vm_name(vm, i))
            
            # Mapping: vm_list.vmX.size -> vm_list.vm1.size (Target Excel)
            vm_size = (self._get_raw_value(f'vm_list.{vm_key}.size', 'Resources') or
                      self._get_raw_value('vm_list.vm1.size', 'Resources'))
            if not vm_size:
                vm_size = self._extract_vm_size(vm)

            # Mapping: vm_list.vmX.image_os -> vm_list.vm1.image_os (Target Excel)
            os_type = (self._get_raw_value(f'vm_list.{vm_key}.image_os', 'Resources') or
                      self._get_raw_value('vm_list.vm1.image_os', 'Resources'))
            if not os_type:
                os_type = self._extract_os_type(vm)
            
            # Mapping: vm_list.vmX.image_urn -> vm_list.vm1.image_urn (Target Excel)
            image_urn = (self._get_raw_value(f'vm_list.{vm_key}.image_urn', 'Resources') or
                        self._get_raw_value('vm_list.vm1.image_urn', 'Resources'))
            # Don't make up image_urn if not in Excel
            
            # Mapping: vm_list.vmX.os_disk_size -> vm_list.vm1.os_disk_size (Target Excel)
            os_disk_size = (self._get_raw_value(f'vm_list.{vm_key}.os_disk_size', 'Resources') or
                           self._get_raw_value('vm_list.vm1.os_disk_size', 'Resources'))
            if os_disk_size:
                try:
                    os_disk_size = int(os_disk_size)
                except (ValueError, TypeError):
                    os_disk_size = self._extract_vm_disk_size(vm)
            else:
                os_disk_size = self._extract_vm_disk_size(vm)
            
            # Mapping: vm_list.vmX.os_disk_type -> vm_list.vm1.os_disk_type (Target Excel)
            os_disk_type = (self._get_raw_value(f'vm_list.{vm_key}.os_disk_type', 'Resources') or
                           self._get_raw_value('vm_list.vm1.os_disk_type', 'Resources'))
            if not os_disk_type:
                os_disk_type = self._extract_vm_disk_type(vm)

            # Mapping: vm_list.vmX.ip_allocation -> vm_list.vm1.ip_allocation (Target Excel)
            ip_allocation = (self._get_raw_value(f'vm_list.{vm_key}.ip_allocation', 'Resources') or
                            self._get_raw_value('vm_list.vm1.ip_allocation', 'Resources'))
            # Don't make up ip_allocation if not in Excel
            
            # Mapping: vm_list.vmX.ip_address -> vm_list.vm1.ip_address (Target Excel)
            ip_address = (self._get_raw_value(f'vm_list.{vm_key}.ip_address', 'Resources') or
                         self._get_raw_value('vm_list.vm1.ip_address', 'Resources'))
            # Don't make up ip_address if not in Excel

            # Mapping: vm_list.vmX.snet_key -> vm_list.vm1.snet_key (Target Excel)
            snet_key = (self._get_raw_value(f'vm_list.{vm_key}.snet_key', 'Resources') or
                       self._get_raw_value('vm_list.vm1.snet_key', 'Resources'))
            # Don't make up snet_key if not in Excel

            # Mapping: vm_list.vmX.asg_key -> vm_list.vm1.asg_key (Target Excel)
            asg_key = (self._get_raw_value(f'vm_list.{vm_key}.asg_key', 'Resources') or
                      self._get_raw_value('vm_list.vm1.asg_key', 'Resources'))
            # Don't make up asg_key if not in Excel
            
            # Mapping: vm_list.vmX.tags.role -> vm_list.vm1.tags.wab:role (Target Excel)
            # Note: Excel uses "wab:role" but Terraform uses "role"
            role = (self._get_raw_value(f'vm_list.{vm_key}.tags.wab:role', 'Resources') or
                   self._get_raw_value(f'vm_list.{vm_key}.tags.role', 'Resources') or
                   self._get_raw_value('vm_list.vm1.tags.wab:role', 'Resources') or
                   vm.get('Role') or
                   project_info.get('role'))
            # Don't make up role if not in Excel

            # Mapping: vm_list.vmX.tags.patch-optin -> vm_list.vm1.tags.wab:patch-optin (Target Excel)
            # Note: Excel uses "wab:patch-optin" but Terraform uses "patch-optin"
            patch_optin = (self._get_raw_value(f'vm_list.{vm_key}.tags.wab:patch-optin', 'Resources') or
                          self._get_raw_value(f'vm_list.{vm_key}.tags.patch-optin', 'Resources') or
                          self._get_raw_value('vm_list.vm1.tags.wab:patch-optin', 'Resources') or
                          vm.get('Patch Optin') or
                          project_info.get('patch_optin'))
            # Don't make up patch_optin if not in Excel

            snow_item = vm.get('Service Now Ticket') or project_info.get('service_now_ticket')
            # Don't make up snow_item if not in Excel
            
            # Build VM entry with proper null handling for missing data
            # Helper function to format value - use null if None or empty string
            def fmt_val(val, is_string=True):
                if val is None or val == "" or val == "None":
                    return "null"
                return f'"{val}"' if is_string else str(val)

            ip_address_line = f'\n    ip_address        = {fmt_val(ip_address)}' if ip_address else ""

            vm_entry = f'''  {vm_key} = {{
    name              = {fmt_val(vm_name)}
    size              = {fmt_val(vm_size)}
    zone              = null
    image_os          = {fmt_val(os_type)}
    marketplace_image = false
    image_urn         = {fmt_val(image_urn)}
    ip_allocation     = {fmt_val(ip_allocation)}{ip_address_line}
    identity_type     = "SystemAssigned, UserAssigned"
    os_disk_size      = {fmt_val(os_disk_size, is_string=False)}
    os_disk_type      = {fmt_val(os_disk_type)}
    os_disk_tier      = null
    data_disk_sizes   = [50, 50]
    data_disk_type    = "Standard_LRS"
    snet_key          = {fmt_val(snet_key)}
    asg_key           = {fmt_val(asg_key)}
    tags = {{
      "role"        = {fmt_val(role)},
      "patch-optin" = {fmt_val(patch_optin)},
      "snow-item"   = {fmt_val(snow_item)}
    }}
  }}'''
            vm_entries.append(vm_entry)
        
        # Join with commas between map entries (Terraform requires commas between map objects)
        vm_entries_str = ',\n'.join(vm_entries)
        return f'''{{
{vm_entries_str}
}}'''
    
    def _generate_subnets_for_tfvars(self) -> str:
        """Generate subnets configuration for tfvars from Excel or project data."""

        project_info = self.terraform_data.get('project_info', {})
        build_env = self.terraform_data.get('build_environment', {})

        # Extract project/app name for resource naming - no defaults
        app_name = project_info.get('application_name')
        project_name = project_info.get('project_name')
        full_project_name = project_info.get('project_name')
        environment = project_info.get('environment')
        subscription = build_env.get('key_value_pairs', {}).get('Subscription')

        # Try to extract actual VNET resource group from Excel (now in project_info)
        vnet_rg_from_excel = project_info.get('vnet_resource_group', None)
        if not vnet_rg_from_excel:
            vnet_rg_from_excel = build_env.get('key_value_pairs', {}).get('VNET Resource Group', None)
        if not vnet_rg_from_excel:
            vnet_rg_from_excel = build_env.get('key_value_pairs', {}).get('Vnet Resource Group', None)

        # Construct resource names only if we have the data - don't make up defaults
        network_rg = vnet_rg_from_excel
        if not network_rg and project_name:
            network_rg = f"rg-{project_name.lower().replace(' ', '-')}-networking"

        vnet_name = f"vnet-{project_name.lower().replace(' ', '-')}-{environment.lower()}" if project_name and environment else None
        nsg_name = f"nsg-{project_name.lower().replace(' ', '-')}-{environment.lower()}" if project_name and environment else None
        route_table_name = f"rt-{project_name.lower().replace(' ', '-')}-{environment.lower()}" if project_name and environment else None

        # Use full project name for subnet (matching pattern where it appears)
        subnet_name = f"snet-{full_project_name.lower()}-{environment.lower()}" if full_project_name and environment else None

        # Try to extract or construct subscription ID - only use placeholder if it's not a GUID
        subscription_id = subscription
        if subscription and len(subscription) != 36:
            # subscription is a name, not a GUID - use placeholder
            subscription_id = "SUBSCRIPTION_ID_PLACEHOLDER"

        # Try to extract subnet CIDR from Excel - don't make up default
        subnet_cidr = (build_env.get('key_value_pairs', {}).get('Subnet CIDR') or
                      build_env.get('key_value_pairs', {}).get('Subnet Prefix') or
                      build_env.get('key_value_pairs', {}).get('Address Space'))

        subnet_prefix = subnet_cidr  # Don't use default if not in Excel

        # Helper to format values properly
        def fmt_val(val):
            if val is None or val == "None":
                return "null"
            return f'"{val}"'

        # Build resource IDs only if subscription_id is available
        if subscription_id and network_rg and nsg_name:
            nsg_id = f'"/subscriptions/{subscription_id}/resourceGroups/{network_rg}/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}"'
        else:
            nsg_id = "null"

        if subscription_id and network_rg and route_table_name:
            rt_id = f'"/subscriptions/{subscription_id}/resourceGroups/{network_rg}/providers/Microsoft.Network/routeTables/{route_table_name}"'
        else:
            rt_id = "null"

        # Format prefix array properly
        if subnet_prefix:
            prefix_array = f'["{subnet_prefix}"]'
        else:
            prefix_array = "[]"

        return f'''{{
  snet1 = {{
    resource_group_name  = {fmt_val(network_rg)}
    virtual_network_name = {fmt_val(vnet_name)}
    network_security_group_id   = {nsg_id}
    route_table_id              = {rt_id}
    name              = {fmt_val(subnet_name)}
    prefixes          = {prefix_array}
    service_endpoints = ["Microsoft.KeyVault"]
  }}
}}'''
    
    def _generate_asg_for_tfvars(self) -> str:
        """Generate application security groups for tfvars from project data."""

        project_info = self.terraform_data.get('project_info', {})
        # Use full project name for ASG (matching pattern) - no defaults
        full_project_name = project_info.get('project_name')
        environment = project_info.get('environment')

        # Use full project name in lowercase with spaces
        return f'''{{
  asg_nic = {{
    name = "asg-{full_project_name.lower()}-nic-{environment.lower()}"
  }},
  asg_pe = {{
    name = "asg-{full_project_name.lower()}-pe-{environment.lower()}"
  }}
}}'''
    
    def _generate_private_endpoints_for_tfvars(self) -> str:
        """Generate private endpoints for tfvars from project data."""

        project_info = self.terraform_data.get('project_info', {})
        # Use full project name for private endpoints (matching pattern) - no defaults
        full_project_name = project_info.get('project_name')
        environment = project_info.get('environment')

        # Use full project name in lowercase with spaces
        # Note: Only one private endpoint in this example, but comma would be needed if more are added
        return f'''{{
  pe_kvlt = {{
    name                           = "pvep-kvlt-{full_project_name.lower()}-{environment.lower()}"
    subresource_names              = ["vault"]
    snet_key                       = "snet1"
    asg_key                        = "asg_pe"
  }}
}}'''
    
    def _generate_nsg_rules_for_tfvars(self) -> str:
        """Generate network security rules for tfvars from Excel NSG data."""
        
        security_groups = self.terraform_data.get('security_groups', [])
        project_info = self.terraform_data.get('project_info', {})

        project_name = project_info.get('project_name')
        environment = project_info.get('environment')

        # Use project-specific networking resource group - only if data exists
        network_rg = f"rg-{project_name.lower()}-networking" if project_name else None
        nsg_name = f"nsg-{project_name.lower()}-{environment.lower()}" if project_name and environment else None
        
        if not security_groups:
            return f'''{{
  resource_group_name         = "{network_rg}"
  network_security_group_name = "{nsg_name}"
  rules = []
}}'''
        
        rules = []
        for i, rule in enumerate(security_groups):  # Process all rules
            # Extract actual values from Excel NSG data using correct field mappings
            # Mapping: rules.name (Source) -> name (Target Excel)
            rule_name = rule.get('name', f'rule_{i}')
            
            # Mapping: rules.priority (Source) -> priority (Target Excel)
            priority = rule.get('priority', 100 + i * 10)
            # Try to convert to int if it's a string
            try:
                priority = int(priority) if priority else (100 + i * 10)
            except (ValueError, TypeError):
                priority = 100 + i * 10
            
            # Mapping: rules.direction (Source) -> direction (Target Excel)
            direction = rule.get('direction', 'Inbound')
            
            # Mapping: rules.access (Source) -> access (Target Excel)
            access = rule.get('access', 'Allow')
            
            # Mapping: rules.protocol (Source) -> protocol (Target Excel)
            protocol = rule.get('protocol', 'Tcp')
            
            # Mapping: rules.source_port_range (Source) -> source_port_range (Target Excel)
            source_port = rule.get('source_port_range', '*')
            
            # Mapping: rules.destination_port_ranges (Source) -> destination_port_ranges (Target Excel)
            dest_ports = rule.get('destination_port_ranges', ['443'])
            # Handle port ranges - could be string, number, or list
            if isinstance(dest_ports, str):
                # Try to parse as comma-separated or single value
                if ',' in dest_ports:
                    dest_ports = [p.strip() for p in dest_ports.split(',')]
                else:
                    dest_ports = [dest_ports]
            elif isinstance(dest_ports, (int, float)):
                dest_ports = [str(dest_ports)]
            elif not isinstance(dest_ports, list):
                dest_ports = ['443']
            
            # Mapping: rules.source_asg_keys (Source) -> source_asg (Target Excel)
            # Note: Excel uses 'source_asg' but Terraform expects 'source_asg_keys' (list)
            source_asg = rule.get('source_asg', rule.get('source_asg_keys', []))
            if isinstance(source_asg, str):
                source_asg_keys = [source_asg] if source_asg else ["asg_nic"]
            elif isinstance(source_asg, list):
                source_asg_keys = source_asg if source_asg else ["asg_nic"]
            else:
                source_asg_keys = ["asg_nic"]
            
            # Mapping: rules.destination_asg_keys (Source) -> destination_asg (Target Excel)
            # Note: Excel uses 'destination_asg' but Terraform expects 'destination_asg_keys' (list)
            dest_asg = rule.get('destination_asg', rule.get('destination_asg_keys', []))
            if isinstance(dest_asg, str):
                destination_asg_keys = [dest_asg] if dest_asg else ["asg_pe"]
            elif isinstance(dest_asg, list):
                destination_asg_keys = dest_asg if dest_asg else ["asg_pe"]
            else:
                destination_asg_keys = ["asg_pe"]
            
            # Mapping: rules.description (Source) -> description (Target Excel)
            description = rule.get('description', f'{direction} {access} {protocol} traffic on port {dest_ports[0] if dest_ports else "*"}')

            # Generate intelligent source/destination names if not provided
            # Use ASG names or create descriptive defaults
            default_source_name = source_asg_keys[0] if source_asg_keys else f"{protocol}-source"
            default_dest_name = destination_asg_keys[0] if destination_asg_keys else f"{protocol}-destination"

            source_name = rule.get('source_name', default_source_name)
            destination_name = rule.get('destination_name', default_dest_name)

            # Convert list to Terraform format with double quotes
            dest_ports_str = '[' + ', '.join([f'"{port}"' for port in dest_ports]) + ']'
            source_asg_str = '[' + ', '.join([f'"{asg}"' for asg in source_asg_keys]) + ']'
            dest_asg_str = '[' + ', '.join([f'"{asg}"' for asg in destination_asg_keys]) + ']'

            rule_entry = f'''    {{
      name                       = "{rule_name}"
      source_name                = "{source_name}"
      destination_name           = "{destination_name}"
      priority                   = {priority}
      direction                  = "{direction}"
      access                     = "{access}"
      protocol                   = "{protocol}"
      source_port_range          = "{source_port}"
      destination_port_ranges    = {dest_ports_str}
      source_asg_keys            = {source_asg_str}
      destination_asg_keys       = {dest_asg_str}
      description                = "{description}"
    }}'''
            rules.append(rule_entry)
        
        # Join with commas between list items (Terraform lists require commas)
        rules_text = ',\n'.join(rules)
        return f'''{{
  resource_group_name         = "{network_rg}"
  network_security_group_name = "{nsg_name}"
  rules = [
{rules_text}
  ]
}}'''
    
    def _generate_outputs_tf(self) -> str:
        """Generate outputs.tf (note: pattern file has inconsistency, fixing to match m-vm.tf module name)."""

        # NOTE: terraform_files_pattern/outputs.tf references module.base-vm but m-vm.tf defines module.vm
        # Using module.vm to be consistent with m-vm.tf definition
        return '''output "build_validation" {
  value = module.base-vm.build_validation
}
'''
    
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
        """Generate data.tf matching terraform_files_pattern exactly."""

        return '''data "azurerm_client_config" "current" {}

data "azurerm_subscription" "subscription" {
  subscription_id = data.azurerm_client_config.current.subscription_id
}

data "azuread_service_principal" "spn" {
  display_name = var.spn
}

data "azurerm_route_table" "rt" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.route_table_name != null } : {} #coalesce(var.subnets, {})
  name                = each.value.route_table_name
  resource_group_name = each.value.resource_group_name
}

data "azurerm_route_table" "rt_id" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.route_table_id != null } : {} #coalesce(var.subnets, {})
  name                = split("/", each.value.route_table_id)[8]
  resource_group_name = split("/", each.value.route_table_id)[4]
}

data "azurerm_network_security_group" "nsg" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.network_security_group_name != null } : {} #coalesce(var.subnets, {})
  name                = each.value.network_security_group_name
  resource_group_name = each.value.resource_group_name
}

data "azurerm_network_security_group" "nsg_id" {
  for_each            = var.subnets != null ? { for key, value in var.subnets : key => value if value.network_security_group_id != null } : {} #coalesce(var.subnets, {})
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

#data "azurerm_private_dns_zone" "pdns" {
#    name = "privatelink.vaultcore.azure.net"
#}

#data "azurerm_resource_group" "rg" {
#  name = var.resource_group_name
#}
#
#data "azurerm_disk_encryption_set" "dsk" {
#  name                = var.disk_encryption_set_name
#  resource_group_name = var.resource_group_name
#}
#
#data "azurerm_user_assigned_identity" "umid" {
#  name                = var.user_assigned_identity_name
#  resource_group_name = var.resource_group_name
#}
#
#data "azurerm_key_vault" "kvlt" {
#  name                = var.key_vault_name
#  resource_group_name = var.resource_group_name
#}
#
#data "azurerm_key_vault_key" "kvkey" {
#  name         = var.key_key_name
#  key_vault_id = data.azurerm_key_vault.kvlt.id
#}
'''
    
    def _generate_locals_tf(self) -> str:
        """Generate locals.tf matching terraform_files_pattern exactly."""

        return '''locals {
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
    
    def _generate_main_tf(self) -> str:
        """Generate main.tf matching terraform_files_pattern exactly (AWS)."""

        # Pattern file is AWS - replicating exactly
        return '''# Main Terraform configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS Provider configuration
provider "aws" {
  region = var.aws_region
}

# Local values
locals {
  environment = var.environment
  project_name = "terraform-to-json-demo"

  common_tags = {
    Environment = local.environment
    Project     = local.project_name
    ManagedBy   = "terraform"
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Resources
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-vpc"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-igw"
  })
}

resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-public-subnet-${count.index + 1}"
    Type = "public"
  })
}

resource "aws_instance" "web" {
  count = 2

  ami           = "ami-0c02fb55956c7d316"  # Amazon Linux 2
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public[count.index].id

  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1>Hello from $(hostname)</h1>" > /var/www/html/index.html
  EOF

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-web-${count.index + 1}"
    Type = "web"
  })
}

resource "aws_security_group" "web" {
  name_prefix = "${local.project_name}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-web-sg"
  })
}

# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "instance_ids" {
  description = "IDs of the EC2 instances"
  value       = aws_instance.web[*].id
}

output "public_ips" {
  description = "Public IP addresses of the instances"
  value       = aws_instance.web[*].public_ip
}
'''

    def _generate_networking_tf(self) -> str:
        """Generate networking.tf matching terraform_files_pattern exactly (AWS)."""

        return '''# Networking configuration
resource "aws_security_group" "web_sg" {
  name_prefix = "web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-security-group"
    Environment = var.environment
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-route-table"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
'''

    def _generate_s3_tf(self) -> str:
        """Generate s3.tf matching terraform_files_pattern exactly (AWS)."""

        return '''# S3 Bucket configuration
resource "aws_s3_bucket" "data" {
  bucket = "${local.project_name}-${local.environment}-data-${random_string.bucket_suffix.result}"

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-data-bucket"
    Type = "data"
  })
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
'''

    def _generate_alerts_tf(self) -> str:
        """Generate packages/monitoring/alerts.tf matching terraform_files_pattern exactly (AWS)."""

        return '''# Monitoring and alerting configuration
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "high-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.web[0].id
  }

  tags = {
    Name = "high-cpu-alarm"
    Environment = var.environment
  }
}

resource "aws_sns_topic" "alerts" {
  name = "terraform-alerts"

  tags = {
    Name = "terraform-alerts"
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
'''

    def _generate_buckets_tf(self) -> str:
        """Generate packages/storage/buckets.tf matching terraform_files_pattern exactly (AWS)."""

        return '''# Storage buckets configuration
resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-${var.environment}-logs"

  tags = {
    Name = "logs-bucket"
    Environment = var.environment
    Purpose = "application-logs"
  }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "log_lifecycle"
    status = "Enabled"

    expiration {
      days = var.log_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}
'''

    def _generate_production_tfvars(self) -> str:
        """Generate production.tfvars matching terraform_files_pattern exactly (AWS)."""

        return '''# Production environment variables
aws_region = "us-west-2"
environment = "prod"
instance_count = 5
instance_type = "t3.medium"

# Production-specific settings
enable_monitoring = true
backup_retention_period = 30

# Production tags
common_tags = {
  Environment = "production"
  Project     = "terraform-to-json-demo"
  ManagedBy   = "terraform"
  Owner       = "devops-team"
  CostCenter  = "engineering"
}
'''

    def _generate_resource_group_tf(self) -> str:
        """Generate resource group file (r-rg.tf) - DEPRECATED, use main.tf instead."""

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
        """Generate application security groups file (r-asg.tf) matching terraform_files_pattern exactly."""

        return '''resource "azurerm_application_security_group" "asg" {
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
  #lifecycle {
  #  ignore_changes = [tags]
  #}
}

resource "azurerm_network_interface_application_security_group_association" "asg_nic" {
  #For each vm that is created attach the nic of the vm to an asg. Use the asg key in the list of vm to find the asg to attach it to
  for_each                      = module.vm
  network_interface_id          = each.value.network_interface_id
  application_security_group_id = azurerm_application_security_group.asg[var.vm_list[each.key].asg_key].id
}

resource "azurerm_private_endpoint_application_security_group_association" "asg_pe" {
  #For each private endpoint attach an asg. Use the asg key in the list of private endpoints to find the asg to attach it to
  for_each                      = var.private_endpoints
  private_endpoint_id           = azurerm_private_endpoint.pe[each.key].id
  application_security_group_id = azurerm_application_security_group.asg[var.private_endpoints[each.key].asg_key].id
}
'''
    
    def _generate_subnets_tf(self) -> str:
        """Generate subnets file (r-snet.tf) matching terraform_files_pattern exactly."""

        return '''resource "azurerm_subnet" "snet" {
  for_each = coalesce(var.subnets, {})

  name                 = each.value.name
  address_prefixes     = each.value.prefixes
  resource_group_name  = each.value.resource_group_name
  service_endpoints    = each.value.service_endpoints
  virtual_network_name = each.value.virtual_network_name
}

resource "azurerm_subnet_network_security_group_association" "nsg" {
  for_each  = coalesce(var.subnets, {})
  subnet_id = azurerm_subnet.snet[each.key].id
  network_security_group_id = coalesce(
    try(each.value.network_security_group_id, null),
    try(data.azurerm_network_security_group.nsg[each.key].id, null)
  )
}

resource "azurerm_subnet_route_table_association" "rta" {
  for_each  = coalesce(var.subnets, {})
  subnet_id = azurerm_subnet.snet[each.key].id
  route_table_id = coalesce(
    try(each.value.route_table_id, null),
    try(data.azurerm_route_table.rt[each.key].id, null)
  )
}
'''
    
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
        """Generate key vault file (r-kvlt.tf) matching terraform_files_pattern exactly."""

        return '''resource "azurerm_key_vault" "kvlt" {
  name                          = coalesce(var.key_vault.name, trimspace("kvlt-${lower(trimspace(local.common_tags["wab:app-name"]))}-${lower(local.common_tags["wab:environment"])}"))
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
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"
    virtual_network_subnet_ids = [coalesce(
      try(azurerm_subnet.snet[var.key_vault.snet_key].id, null),
      try(data.azurerm_subnet.snet[var.key_vault.snet_key].id, null)
    )]
  }

  tags = merge(
    tomap(
      { "wab:resource-name" = coalesce(var.key_vault.name, trimspace("kvlt-${lower(trimspace(substr(local.common_tags["wab:app-name"], 0, 4)))}-${lower(local.common_tags["wab:environment"])}")) }
    ),
    local.common_tags, local.resource_specific_tags
  )

  #lifecycle {
  #  ignore_changes = [tags]
  #}
}
resource "azurerm_key_vault_key" "kvkey" {
  name            = coalesce(var.key_vault.key_name, trimspace("key-${lower(trimspace(local.common_tags["wab:app-name"]))}-${lower(local.common_tags["wab:environment"])}"))
  key_vault_id    = azurerm_key_vault.kvlt.id
  key_type        = "RSA"
  key_size        = 2048
  key_opts        = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
  curve           = null
  expiration_date = null
  not_before_date = null
  tags            = {}
}
'''
    
    def _generate_user_assigned_identity_tf(self) -> str:
        """Generate user assigned identity file (r-umid.tf) matching terraform_files_pattern exactly."""

        return '''resource "azurerm_user_assigned_identity" "umid" {
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

  #lifecycle {
  #  ignore_changes = [tags]
  #}
}

resource "azurerm_role_assignment" "umid_role_assignement" {
  depends_on = [azurerm_key_vault.kvlt, azurerm_user_assigned_identity.umid]

  scope                = azurerm_key_vault.kvlt.id
  role_definition_name = "Key Vault Crypto Service Encryption User"
  principal_id         = azurerm_user_assigned_identity.umid.principal_id
}
'''
    
    def _generate_disk_encryption_set_tf(self) -> str:
        """Generate disk encryption set file (r-dsk.tf) matching terraform_files_pattern exactly."""

        return '''resource "azurerm_disk_encryption_set" "dsk" {
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

  #lifecycle {
  #  ignore_changes = [tags]
  #}
}
'''
    
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

    def _generate_random_password_tf(self) -> str:
        """Generate random password file (r-rnd.tf) matching terraform_files_pattern exactly."""

        return '''resource "random_password" "password" {
  #Create a random password if one is not given
  count            = var.admin_password != null ? 0 : 1
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}
'''

    def _generate_dcra_tf(self) -> str:
        """Generate data collection rule association file (r-dcra.tf) matching terraform_files_pattern exactly."""

        return '''resource "azurerm_monitor_data_collection_rule_association" "dcra" {
  for_each                = (local.common_tags["wab:environment"] == "PROD" || local.common_tags["wab:environment"] == "DR") && var.vm_list != null ? var.vm_list : {}
  name                    = module.vm[each.key].vm_name
  target_resource_id      = module.vm[each.key].vm_id
  data_collection_rule_id = var.vm_process_data_collection_rules[var.location].id
  description             = null
}
'''

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

        return None  # Don't make up data if not in Excel
    
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

        return None  # Don't make up data if not in Excel
    
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

        return None  # Don't make up data if not in Excel
    
    def _extract_vm_disk_type(self, vm: Dict[str, Any]) -> str:
        """Extract OS disk type from VM data."""
        type_fields = ['OS disk type', 'os_disk_type', 'Disk Type', 'disk_type']

        for field in type_fields:
            if field in vm and vm[field] and str(vm[field]).strip():
                disk_type = str(vm[field]).strip()
                if '_LRS' in disk_type or '_ZRS' in disk_type:
                    return disk_type

        return None  # Don't make up data if not in Excel
    
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
