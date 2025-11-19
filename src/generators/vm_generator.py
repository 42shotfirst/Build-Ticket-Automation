"""
VM Generator

Generates VM-related terraform files from Build_ENV and Resources data:
- m-vm.tf (VM module configuration)
- r-umid.tf (User Assigned Identity)
- r-kvlt.tf (Key Vault)
- r-dsk.tf (Disk Encryption Set)
- Adds vm_list to terraform.tfvars
"""

from typing import Dict, Any, List, Optional
import os


class VMGenerator:
    """Generates VM and related security terraform files."""

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
        Generate all VM-related files.

        Args:
            output_dir: Directory to write files to

        Returns:
            Dictionary mapping filenames to their content
        """
        os.makedirs(output_dir, exist_ok=True)

        files = {
            'm-vm.tf': self._generate_m_vm_tf(),
            'r-umid.tf': self._generate_r_umid_tf(),
            'r-kvlt.tf': self._generate_r_kvlt_tf(),
            'r-dsk.tf': self._generate_r_dsk_tf(),
        }

        # Write files
        for filename, content in files.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)

        return files

    def _generate_m_vm_tf(self) -> str:
        """Generate m-vm.tf for VM module."""
        # Read template from terraform_files_pattern
        template_path = 'terraform_files_pattern/m-vm.tf'
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to basic template
            return self._generate_basic_m_vm_tf()

    def _generate_basic_m_vm_tf(self) -> str:
        """Generate basic m-vm.tf if template not found."""
        content = '''locals {
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
  admin_password      = coalesce(var.admin_password, random_password.password != [] ? random_password.password[0].result : null)
  zone                = each.value.zone
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
        return content

    def _generate_r_umid_tf(self) -> str:
        """Generate r-umid.tf for User Assigned Identity."""
        template_path = 'terraform_files_pattern/r-umid.tf'
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
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
}

resource "azurerm_role_assignment" "umid_role_assignement" {
  depends_on = [azurerm_key_vault.kvlt, azurerm_user_assigned_identity.umid]

  scope                = azurerm_key_vault.kvlt.id
  role_definition_name = "Key Vault Crypto Service Encryption User"
  principal_id         = azurerm_user_assigned_identity.umid.principal_id
}
'''

    def _generate_r_kvlt_tf(self) -> str:
        """Generate r-kvlt.tf for Key Vault."""
        template_path = 'terraform_files_pattern/r-kvlt.tf'
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
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

    def _generate_r_dsk_tf(self) -> str:
        """Generate r-dsk.tf for Disk Encryption Set."""
        template_path = 'terraform_files_pattern/r-dsk.tf'
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
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
}
'''

    def get_tfvars_content(self) -> Dict[str, Any]:
        """
        Get terraform.tfvars content for VMs and related resources.

        Returns:
            Dictionary of variable names to values
        """
        tfvars = {}

        # User Assigned Identity
        umid = self.build_env.get('user_assigned_identity', {})
        umid_name = umid.get('user_assigned_identity_name') or umid.get('name')
        if umid_name:
            tfvars['user_assigned_identity_name'] = umid_name

        # Disk Encryption Set
        dsk = self.build_env.get('disk_encryption_set', {})
        dsk_name = dsk.get('disk_encryption_set_name') or dsk.get('name')
        if dsk_name:
            tfvars['disk_encryption_set_name'] = dsk_name

        # Key Vault
        kv = self.build_env.get('key_vault', {})
        if kv:
            kv_config = {}

            kv_name = kv.get('key_vault_name') or kv.get('name')
            if kv_name:
                kv_config['name'] = kv_name

            sku = kv.get('sku_name')
            if sku:
                kv_config['sku_name'] = sku

            retention = kv.get('soft_delete_retention_days')
            if retention:
                kv_config['soft_delete_retention_days'] = int(retention) if isinstance(retention, (str, int)) else retention

            public_access = kv.get('public_network_access')
            if public_access is not None:
                # Convert to boolean
                if isinstance(public_access, str):
                    kv_config['public_network_access'] = public_access.lower() in ['true', 'yes', '1']
                else:
                    kv_config['public_network_access'] = bool(public_access)

            snet_key = kv.get('snet_key', 'snet1')
            kv_config['snet_key'] = snet_key

            key_name = kv.get('key_vault_key_name') or kv.get('key_name')
            if key_name:
                kv_config['key_name'] = key_name

            if kv_config:
                tfvars['key_vault'] = kv_config

        # Virtual Machines
        vms = self.build_env.get('virtual_machines', [])
        if vms:
            vm_map = {}
            for idx, vm in enumerate(vms, 1):
                key = f'vm{idx}'

                vm_config = {
                    'name': vm.get('name', 'Default'),
                    'size': vm.get('size'),
                    'image_os': vm.get('image_os'),
                    'image_urn': vm.get('image_urn'),
                    'ip_allocation': vm.get('ip_allocation'),
                    'os_disk_size': self._to_int(vm.get('os_disk_size')),
                    'snet_key': vm.get('snet_key', 'snet1'),
                    'asg_key': vm.get('asg_key', 'asg_nic'),
                    'tags': {
                        'role': vm.get('role'),
                        'patch-optin': vm.get('patch-optin'),
                    }
                }

                # Optional fields
                zone = vm.get('zone')
                if zone:
                    vm_config['zone'] = self._to_int(zone)

                source_image_id = vm.get('source_image_id')
                if source_image_id:
                    vm_config['source_image_id'] = source_image_id

                marketplace = vm.get('marketplace_image')
                if marketplace is not None:
                    vm_config['marketplace_image'] = bool(marketplace)

                ip_address = vm.get('ip_address')
                if ip_address:
                    vm_config['ip_address'] = ip_address

                identity_type = vm.get('identity_type')
                if identity_type:
                    vm_config['identity_type'] = identity_type

                os_disk_name = vm.get('os_disk_name')
                if os_disk_name:
                    vm_config['os_disk_name'] = os_disk_name

                os_disk_type = vm.get('os_disk_type')
                if os_disk_type:
                    vm_config['os_disk_type'] = os_disk_type

                os_disk_tier = vm.get('os_disk_tier')
                if os_disk_tier:
                    vm_config['os_disk_tier'] = os_disk_tier

                data_disk_sizes = vm.get('data_disk_sizes')
                if data_disk_sizes:
                    if not isinstance(data_disk_sizes, list):
                        data_disk_sizes = [data_disk_sizes]
                    vm_config['data_disk_sizes'] = [self._to_int(s) for s in data_disk_sizes]

                data_disk_type = vm.get('data_disk_type')
                if data_disk_type:
                    vm_config['data_disk_type'] = data_disk_type

                snow_item = vm.get('snow-item') or vm.get('snow_item')
                if snow_item:
                    vm_config['tags']['snow-item'] = snow_item

                vm_map[key] = vm_config

            if vm_map:
                tfvars['vm_list'] = vm_map

        return tfvars

    def _to_int(self, value: Any) -> Optional[int]:
        """Convert value to int, handling strings and None."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return None
