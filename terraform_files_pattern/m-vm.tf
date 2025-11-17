locals {
  data_disks = var.vm_list != null ? merge([
    for vm_name, vm_config in var.vm_list :
    vm_config.data_disk_sizes != null && vm_config.data_disk_sizes != [] ? {
      "${vm_config.name}" = tolist([
        for i in range(length(vm_config.data_disk_sizes)) : {
          name                 = format("dataDisk%02d-%s", i + 1, vm_config.name)
          vm_name              = vm_config.name
          disk_size_gb         = vm_config.data_disk_sizes[i] #vm_config.data_disk_sizes == null ? vm_config.data_disk_size : vm_config.data_disk_sizes[i] #coalesce(vm_config.data_disk_size, vm_config.data_disk_sizes[i]) #One size for all drives, This can be used to have different sizes per drive
          storage_account_type = coalesce(vm_config.data_disk_type, "Standard_LRS")
          create_option        = "Empty"
          attach_setting = {
            lun           = i
            caching       = "None" #vm_config.data_disk_sizes == null ? vm_config.data_disk_size > 4095 ? "None" : "ReadWrite" : vm_config.data_disk_sizes[i] > 4095 ? "None" : "ReadWrite"
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
  #Both values are enumerated whether there is a value in the first slot or not. So if their is a random password check the index of the tuple
  admin_password = coalesce(var.admin_password, random_password.password != [] ? random_password.password[0].result : null)
  zone           = each.value.zone
  subnet_id = coalesce(
    try(azurerm_subnet.snet[each.value.snet_key].id, null),
    try(data.azurerm_subnet.snet[each.value.snet_key].id, null)
  )
  size     = each.value.size
  image_os = each.value.image_os
  #If the urn contains windows-server return "Windows_Server", if it contains rhel return "RHEL_BYOS"
  #license_type = strcontains(element(split(":", each.value.image_urn), 1), "windows-server") ? "Windows_Server" : null
  #If the urn contains windows-server or windowsserver (in any case) return "Windows_Server", if it contains rhel return "RHEL_BYOS"
  license_type = anytrue([for str in ["windows", "Windows"] : strcontains(lower(element(split(":", each.value.image_os), 1)), str)]) ? "Windows_Server" : null

  #If marketplace_image bool is provided use that value. If not go with true by default
  plan = coalesce(each.value.marketplace_image, true) ? {
    name      = element(split(":", each.value.image_urn), 2) #cis-windows-server2022-l1-gen2
    product   = element(split(":", each.value.image_urn), 1) #cis-windows-server
    publisher = element(split(":", each.value.image_urn), 0) #center-for-internet-security-inc
  } : null

  source_image_id = each.value.source_image_id

  #If source image id is not provided create the source_image_reference block
  source_image_reference = each.value.source_image_id == null ? {
    offer     = element(split(":", each.value.image_urn), 1) #cis-windows-server
    publisher = element(split(":", each.value.image_urn), 0) #center-for-internet-security-inc
    sku       = element(split(":", each.value.image_urn), 2) #cis-windows-server2022-l1-gen2
    version   = element(split(":", each.value.image_urn), 3) #2.0.10
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
