# Begin m-basevm.tf

module "base-vm" {
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
}


# Begin outputs.tf

output "build_validation" {
  value = module.base-vm.build_validation
}

# Begin terraform.tfvars

spn      = "spn-terraform-devops_dev_qa"
location = "WEST US 3"
#abbreviated_app_name                             = "terra" #15 characters or less
resource_group_name = "rg-base-vm-module-test"
application_security_groups = {
  asg_nic = {
    name = "asg-base-vm-module-nic-test"
  }
  asg_pe = {
    name = "asg-base-vm-module-pe-test"
  }
}

disk_encryption_set_name    = "dsk-base-vm-module-test"
user_assigned_identity_name = "umid-base-vm-module-test"
key_vault = {
  name                       = "kvlt-base-vm-module-test"
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-base-vm-test"
}

#existing_subnets = {
#  snet1 = {
#    resource_group_name         = "rg-devops_dev_qa-networking"
#    virtual_network_name        = "vnet-devops_dev_qa"
#    name                        = "snet-base-vm-module-test"
#  }
#}

subnets = {
  snet1 = {
    resource_group_name  = "rg-devops_dev_qa-networking"
    virtual_network_name = "vnet-devops_dev_qa"
    network_security_group_id   = "/subscriptions/6f5e4da6-a73e-4795-8e57-49bdfaed7724/resourceGroups/rg-devops_dev_qa-networking/providers/Microsoft.Network/networkSecurityGroups/nsg-devops_dev_qa"
    #network_security_group_name = "nsg-devops_dev_qa"
    route_table_id              = "/subscriptions/6f5e4da6-a73e-4795-8e57-49bdfaed7724/resourceGroups/rg-devops_dev_qa-networking/providers/Microsoft.Network/routeTables/rt-devops_dev_qa"
    #route_table_name  = "rt-devops_dev_qa"
    name              = "snet-base-vm-module-test"
    prefixes          = ["10.187.18.128/29"]
    service_endpoints = ["Microsoft.KeyVault"]
  }
}
private_endpoints = {
  pe_kvlt = {
    name                           = "pvep-kvlt-base-vm-module-test"
    subresource_names              = ["vault"]
    snet_key                       = "snet1"
    asg_key                        = "asg_pe"
  }
}

network_security_rules = {
  resource_group_name         = "rg-devops_dev_qa-networking"
  network_security_group_name = "nsg-devops_dev_qa"
  rules = [
    {
      #name                         = ""
      #or
      source_name                = "Source"
      destination_name           = "Dest"
      priority                   = 140
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_ranges    = ["443"]
      source_asg_keys            = ["asg_nic"]
      destination_asg_keys       = ["asg_pe"]
      #source_address_prefix      = "10.187.18.128/29"
      #destination_address_prefix = "10.187.18.128/29"
      description                = "Module Testing"
    },
    {
      name = "RITM0086216-Outbound-DEV-Allow-DesttoSource"
      #or
      #source_name                  = "Source"
      #destination_name             = "Dest"
      priority                   = 140
      direction                  = "Outbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_ranges    = ["443"]
      source_address_prefix      = "10.187.18.128/29"
      destination_address_prefix = "10.187.18.128/29"
      description                = "Module Testing"
    }
  ]
}

vm_list = {
  vm1 = {
    name              = "azw-basevmwd01"
    size              = "Standard_B2s_v2"
    zone              = null
    image_os          = "windows"
    marketplace_image = false
    #\image_urn       = "center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l1-gen2:latest"
    image_urn     = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
    ip_allocation = "Static"
    ip_address    = "10.187.18.134"
    identity_type = "SystemAssigned, UserAssigned"
    #os_disk_name    = "OSDisk01-123456"
    os_disk_size = 128 #If this is smaller than the vm image it will fail
    os_disk_type = "Standard_LRS"
    os_disk_tier = null
    #data_disks = {
    #  1 = {
    #    name = "dataDisk01-123456"
    #    size = 150
    #    type = "Standard_LRS"
    #    tier = null
    #  }
    #  2 = {
    #    name = "dataDisk02-123456"
    #    size = 150
    #    type = "Standard_LRS"
    #    tier = null
    #  }
    #}
    data_disk_sizes = [50, 50]
    data_disk_type  = "Standard_LRS"
    snet_key        = "snet1"
    asg_key         = "asg_nic"
    tags = {
      "role"        = "Test",
      "patch-optin" = "NO"
    }
  }
  vm2 = {
    name              = "azw-basevmwd02"
    size              = "Standard_B2s_v2"
    zone              = null
    image_os          = "windows"
    marketplace_image = false
    source_image_id = "/subscriptions/6f5e4da6-a73e-4795-8e57-49bdfaed7724/resourceGroups/rg-packer-dev/providers/Microsoft.Compute/galleries/PackerDev/images/Packer-windows-cis-L1"
    #image_urn       = "center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l1-gen2:latest"
    #image_urn     = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
    ip_allocation = "Dynamic"
    identity_type = "SystemAssigned, UserAssigned"
    os_disk_size  = 128 #If this is smaller than the vm image it will fail
    os_disk_type  = "Standard_LRS"
    os_disk_tier  = null
    snet_key      = "snet1"
    asg_key       = "asg_nic"
    tags = {
      "role"        = "Test",
      "patch-optin" = "NO",
      "snow-item"   = "RITM000000"
    }
  }
}

common_tags = {
  "shared-service-name" = "NA",
  "app-name"            = "Terraform Cloud",
  "environment"         = "DEV",
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "Bronze",
  "snow-item"           = "RITM0086216",
  "it-cost-center"      = "5541",
  "it-domain"           = "Platform Engineering",
  #"notes"               = "",
  #"segment"             = "NA",
  "lineofbusiness"      = "Amerihome Mortgage",
  "department"          = "Cloud Engineering",
  "cost-center"         = "6500"
}

# Begin variables.tf

variable "spn" {
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

variable "existing_application_security_groups" {
  type = map(object({
    name                = string
    resource_group_name = optional(string)

  }))
  default     = {}
  description = <<-EOT
  map(object({
    name         = Name of the application security group 
  }))
  EOT
  nullable    = false
}

variable "application_security_groups" {
  type = map(object({
    name = string

  }))
  default     = {}
  description = <<-EOT
  map(object({
    name         = Name of the application security group 
  }))
  EOT
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
  description = <<-EOT
  name                          = The name of the vault
  sku_name                      = The name of the SKU used for this Key Vault. Possible values are standard and premium
  soft_delete_retention_days    = The number of days that items should be retained for once soft-deleted. This value can be between 7 and 90
  public_network_access_enabled = Whether public network access is allowed for this Key Vault.
  snet_key                      = Subnet key that this key vault should be in
  key_name                = The name of the key vault key
  EOT
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

variable "existing_subnets" {
  type = map(object({
    resource_group_name  = string
    virtual_network_name = string
    name                 = string
  }))
  default     = null
  description = <<-EOT
  map(object({
    resource_group_name         = Name of the resource group the vnet is in
    virtual_network_name        = Name of virtual network the subnet is will be attached to
    network_security_group_name = Name of the network security group to associate with the subnet
    route_table_name            = Name of the route table to associate with the subnet
    name                        = Name of the subnet
    prefixes                    = Address prefixes to use for the subnet
    service_endpoints           = List of Service endpoints to associate with the subnet
  }))
  EOT
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
  description = <<-EOT
  map(object({
    resource_group_name         = Name of the resource group the vnet is in
    virtual_network_name        = Name of virtual network the subnet is will be attached to
    network_security_group_name = Name of the network security group to associate with the subnet
    route_table_name            = Name of the route table to associate with the subnet
    name                        = Name of the subnet
    prefixes                    = Address prefixes to use for the subnet
    service_endpoints           = List of Service endpoints to associate with the subnet
  }))
  EOT
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
  description = <<-EOT
  map(object({
    name                           = (Required) Specifies the Name of the Private Endpoint.
    subresource_names              = (Optional) A list of subresource names which the Private Endpoint is able to connect to. subresource_names corresponds to group_id. Possible values are detailed in the product documentation in the Subresources column.
    private_connection_resource_id = (Optional) The ID of the Private Link Enabled Remote Resource which this Private Endpoint should be connected to.
    is_manual_connection           = (Required) Does the Private Endpoint require Manual Approval from the remote resource owner?
    private_dns_zone_group_name    = (Required) Specifies the Name of the Private Service Connection
    private_dns_zone_ids           = (Required) Specifies the list of Private DNS Zones to include within the private_dns_zone_group
  }))
  EOT
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
  description = <<-EOT
  map(object({
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
    data_disks = map(object({
      name = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
      size = The Size of the data Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you'll need to repartition the disk to use the remaining space.
      type = (optional) Storage type of the data disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
      tier = (optional) The disk performance tier to use. Possible values are documented here https://learn.microsoft.com/en-us/azure/virtual-machines/disks-change-performance. This feature is currently supported only for premium SSDs.
    }))
    tags = list(object({
      "role"             = 
      "patch-optin"      = (YES,NO)
      "snow-item"        = If the vm is part of a different ticket provide it
    }))
  }))
  EOT
  nullable    = true
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
  #default = {
  #  terraform           = true
  #  shared-service-name = "NA",
  #  app-name            = "NA",
  #  environment         = "NA",
  #  app-tier            = "NA",
  #  snow-item           = "NA",
  #  it-cost-center      = "NA",
  #  it-domain           = "NA",
  #  notes               = "NA",
  #  segment             = "NA",
  #  lineofbusiness      = "NA",
  #  department          = "NA",
  #  cost-center         = "NA"
  #}

  description = "Required tags on all resources."
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
  description = "These need to be on all resources. Some resources such as VMs will have values. Those tag values are controlled under that variable."
}

# Begin versions.tf

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
}

# Begin data.tf

data "azurerm_client_config" "current" {}

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


# Begin locals.tf

locals {
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

# Begin m-vm.tf

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

# Begin outputs.tf

#output "build_validation" {
#  value = {
#    snow_ticket_number    = lookup(local.common_tags, "wab:snow-item")
#    app_tier              = lookup(local.common_tags, "wab:app-tier")
#    location              = azurerm_resource_group.rg.location
#    environment           = lookup(local.common_tags, "wab:environment")
#    resource_group        = azurerm_resource_group.rg.name
#    vm_name               = tomap({ for n, name in module.vm : n => name.vm_name })
#    vm_ip_addresses       = tomap({ for a, address in module.vm : a => address.network_interface_private_ip })
#    subnet_rsg            = tomap({ for n, snet in azurerm_subnet.snet : n => snet.resource_group_name })
#    vnet_rsg              = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.resource_group_name })
#    vnet_name             = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.name })
#    vnet_ip_address_space = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.address_space })
#    subnet_name           = tomap({ for n, snet in azurerm_subnet.snet : n => snet.name })
#    subnet_address_space  = tomap({ for n, snet in azurerm_subnet.snet : n => snet.address_prefixes })
#    nsg_name              = tomap({ for n, nsg in data.azurerm_network_security_group.nsg : n => nsg.name })
#    route_table_name      = tomap({ for n, rt in data.azurerm_route_table.rt : n => rt.name })
#    #route_table           = [for route in data.azurerm_route_table.rt.route : route if route.name == "Default"]
#  }
#}

output "build_validation" {
  value = {
    "01-Subscription" = data.azurerm_subscription.subscription.display_name
    "02-Resource_groups" = {
      "01-Name"          = var.resource_group_name
      "02-Location"      = azurerm_resource_group.rg.location
      "03-Environment"   = lookup(local.common_tags, "wab:environment")
      "04-App_tier"      = lookup(local.common_tags, "wab:app-tier")
      "05-Ticket_number" = lookup(local.common_tags, "wab:snow-item")
      "06-Virtual_machines" = [for vm_key, vm_value in module.vm : {
        "01-Name"         = vm_value.vm_name
        "02-IP_Address"   = vm_value.network_interface_private_ip
        "03-SKU"          = var.vm_list[vm_key].size
        "04-Zone"         = coalesce(var.vm_list[vm_key].zone, "none")
        "05-OS"           = coalesce(var.vm_list[vm_key].image_urn, var.vm_list[vm_key].source_image_id)
        "06-OS_disk_size" = var.vm_list[vm_key].os_disk_size
        "07-OS_disk_type" = var.vm_list[vm_key].os_disk_type
        "08-Data_disks"   = try(join(", ", var.vm_list[vm_key].data_disk_sizes), "none")
        "09-Subnet" = coalesce(
          try(azurerm_subnet.snet[var.vm_list[vm_key].snet_key].name, null),
          try(data.azurerm_subnet.snet[var.vm_list[vm_key].snet_key].name, null)
        )
        "10-ASG" = can(coalesce(
          try(azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].id, null),
          try(data.azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].id, null)
          )) ? try(join(", ", [coalesce(
            try(azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].name, null),
            try(data.azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].name, null)
        )]), null) : null
      }]
    }
    "03-Network" = {
      "01-Subnets" = {
        for key, snet in merge(var.subnets, var.existing_subnets) :
        key => {
          "01-Resource Group"                = snet.resource_group_name
          "02-Network Security Group"        = try(data.azurerm_network_security_group.nsg[key].name, data.azurerm_network_security_group.nsg_id[key].name, split("/", data.azurerm_subnet.snet[key].network_security_group_id)[8], "none")
          "03-Route Table"                   = try(data.azurerm_route_table.rt[key].name, data.azurerm_route_table.rt_id[key].name, split("/", data.azurerm_subnet.snet[key].route_table_id)[8], "none")
          "04-Virtual Network"               = snet.virtual_network_name
          "05-Virtual Network Address Space" = join(", ", try(data.azurerm_virtual_network.vnet[key].address_space, []))
          "06-Subnet"                        = snet.name
          "07-Subnet Prefix"                 = join(", ", try(data.azurerm_subnet.snet[key].address_prefixes, snet.prefixes))
          #try(
          #  lookup(data.azurerm_subnet.existing_subnets[key].address_prefix, 0, ""),
          #  snet.prefix
          #)
          "08-Subnet Service Endpoints" = join(", ", try(data.azurerm_subnet.snet[key].service_endpoints, snet.service_endpoints))
          #try(
          #  join(", ", data.azurerm_subnet.existing_subnets[key].service_endpoints),
          #  join(", ", snet.service_endpoints)
          #)
        }
      }
      "02-NSG Rules" = {
        for key, rule in azurerm_network_security_rule.nsr :
        key => {
          "01-Direction"          = rule.direction
          "01-Access"             = rule.access 
          "01-Priority"           = rule.priority
          "01-Name"               = rule.name
          "01-Source_port_range"  = rule.source_port_range
          "01-Source_port_range"  = rule.destination_port_range
          "01-Protocol"           = rule.protocol
          "01-Source"             = try(rule.source_port_range, join(", ", rule.source_port_ranges), join(", ", rule.source_application_security_group_ids))
          "01-Destination"        = try(rule.destination_port_range, join(", ", rule.destination_port_ranges), join(", ", rule.destination_application_security_group_ids))
          "01-Description"        = rule.description  
        }
      }
    }
  }
}

output "resources" {
  value = {
    rg = azurerm_resource_group.rg.id
    asg = tomap({ for n, asg in azurerm_application_security_group.asg : n => asg.id })
    dsk = azurerm_disk_encryption_set.dsk.id #tomap({ for n, dsk in azurerm_disk_encryption_set.dsk : n => dsk.id })
    umid = azurerm_user_assigned_identity.umid.id #tomap({ for n, umid in azurerm_user_assigned_identity.umid : n => umid.id })
    kvlt = azurerm_key_vault.kvlt.id #tomap({ for n, kvlt in azurerm_key_vault.kvlt : n => kvlt.id })
    kvkey = azurerm_key_vault_key.kvkey.id #tomap({ for n, kvkey in azurerm_key_vault_key.kvkey : n => kvkey.id })
    nsr = tomap({ for n, nsr in azurerm_network_security_rule.nsr : n => nsr.id })
    pe = tomap({ for n, pe in azurerm_private_endpoint.pe : n => pe.id })
    snet = tomap({ for n, snet in azurerm_subnet.snet : n => snet.id })
  }
}

#output "build_validation_improved" {
#  value = {
#    tags           = merge(local.common_tags, local.resource_specific_tags)
#    location       = azurerm_resource_group.rg.location
#    resource_group = azurerm_resource_group.rg.name
#    vm_all         = tomap({ for n, name in module.vm : n => name })
#
#    vm_name         = tomap({ for n, name in module.vm : n => name.vm_name })
#    vm_ip_addresses = tomap({ for a, address in module.vm : a => address.network_interface_private_ip })
#
#    #Networking
#    subnet_rsg            = tomap({ for n, snet in azurerm_subnet.snet : n => snet.resource_group_name })
#    vnet_rsg              = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.resource_group_name })
#    vnet_name             = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.name })
#    vnet_ip_address_space = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.address_space })
#    subnet_name           = tomap({ for n, snet in azurerm_subnet.snet : n => snet.name })
#    subnet_address_space  = tomap({ for n, snet in azurerm_subnet.snet : n => snet.address_prefixes })
#    nsg_name              = tomap({ for n, nsg in data.azurerm_network_security_group.nsg : n => nsg.name })
#    route_table_name      = tomap({ for n, rt in data.azurerm_route_table.rt : n => rt.name })
#    #route_table           = [for route in data.azurerm_route_table.rt.route : route if route.name == "Default"]
#  }
#}

#output "network" {
#  value = [
#    for s, snet in azurerm_subnet.snet : {
#      resource_group_name      = snet.resource_group_name
#      vnet_name                = data.azurerm_virtual_network.vnet[snet].name
#      vnet_ip_address_space    = data.azurerm_virtual_network.vnet[snet].address_space
#      vnet_dns_servar          = data.azurerm_virtual_network.vnet[snet].dns_servers
#      nsg_name                 = data.azurerm_network_security_group.nsg[snet].name
#      route_table_name         = data.azurerm_route_table.rt[snet].name
#      subnet_name              = snet.name
#      subnet_address_space     = snet.address_prefixes
#      subnet_service_endpoints = snet.service_endpoints
#    }
#  ]
#}
#
#output "resource_group_name" {
#  description = "Resource group name"
#  value       = azurerm_resource_group.rg.name
#}
#
#output "resource_group_location" {
#  description = "Resource group region"
#  value       = azurerm_resource_group.rg.location
#}
#
#output "environment" {
#  description = "Environment tag"
#  value       = lookup(local.common_tags, "wab:environment")
#}
#
#output "tier" {
#  description = "Resource group region"
#  value       = lookup(local.resource_specific_tags, "wab:tier")
#}
#
#output "snow_ticket_number" {
#  description = "Resource group region"
#  value       = lookup(local.common_tags, "wab:snow-item")
#}
#
#output "application_security_group_name" {
#  description = "Application security group name"
#  value       = tomap({ for n, asg in azurerm_application_security_group.asg : n => asg.name })
#}
#
#output "disk_encryption_set_name" {
#  description = "Disk encryption_set name"
#  value       = azurerm_disk_encryption_set.dsk.name
#}
#
#output "user_assigned_identity_name" {
#  description = "User identity name"
#  value       = azurerm_user_assigned_identity.umid.name
#}
#
#output "key_vault_name" {
#  description = "Key vault name"
#  value       = azurerm_key_vault.kvlt.name
#}
#
#output "key_vault_uri" {
#  description = "Key vault uri"
#  value       = azurerm_key_vault.kvlt.vault_uri
#}
#
#output "subnets_name" {
#  description = "Subnet name"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.name })
#}
#
#output "subnets_service_endpoints" {
#  description = "Subnet service_endpoints"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.service_endpoints })
#}
#
#output "subnets_virtual_network" {
#  description = "Subnet virtual network"
#  value       = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.name })
#}
#
#output "subnets_address_prefixes" {
#  description = "Subnet address prefix"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.address_prefixes })
#}
#
#output "subnets_resource_group_name" {
#  description = "Subnet resource group name"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.resource_group_name })
#}
#
#output "route_table_name" {
#  description = "Route Table name"
#  value       = tomap({ for n, rt in data.azurerm_route_table.rt : n => rt.name })
#}
#
##output "route_table_default" {
##  description = "Route Table default"
##  value       = [for route in data.azurerm_route_table.rt.route : route if route.name == "Default"]
##}
#
#output "network_security_group_name" {
#  description = "NSG name"
#  value       = data.azurerm_network_security_group.nsg["snet1"].name
#}
#
#output "virtual_network_name" {
#  description = "Virtual Network name"
#  value       = data.azurerm_virtual_network.vnet["snet1"].name
#}
#
#output "virtual_network_address_space" {
#  description = "Virtual Network name"
#  value       = data.azurerm_virtual_network.vnet["snet1"].address_space
#}
#
#output "virtual_network_dns_servers" {
#  description = "Virtual Network dns servers"
#  value       = data.azurerm_virtual_network.vnet["snet1"].dns_servers
#}
#
#output "vm_name" {
#  description = "Virtual machine name"
#  value       = tomap({ for n, name in module.vm : n => name.vm_name })
#}
#
#output "vm_network_interface_private_ip" {
#  description = "Virtual machine network interface ip"
#  value       = tomap({ for a, address in module.vm : a => address.network_interface_private_ip })
#}


# Begin r-asg.tf

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

# Begin r-dcra.tf

resource "azurerm_monitor_data_collection_rule_association" "dcra" {
  for_each                = (local.common_tags["wab:environment"] == "PROD" || local.common_tags["wab:environment"] == "DR") && var.vm_list != null ? var.vm_list : {}
  name                    = module.vm[each.key].vm_name
  target_resource_id      = module.vm[each.key].vm_id
  data_collection_rule_id = var.vm_process_data_collection_rules[var.location].id
  description             = null
}

# Begin r-dsk.tf

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

  #lifecycle {
  #  ignore_changes = [tags]
  #}
}


# Begin r-kvlt.tf

resource "azurerm_key_vault" "kvlt" {
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

# Begin r-nsr.tf

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
}

locals {
  rules = length(try(var.network_security_rules.rules, {})) > 0 ? {
    for mapping in flatten([
      for priority, value in var.network_security_rules.rules : {
        name                         = value.name != null && value.name != "null" ? value.name : "${coalesce(value.snow-item, local.common_tags["wab:snow-item"])}-${value.direction}-${local.common_tags["wab:environment"]}-${value.access}-${value.source_name}to${value.destination_name}"
        #name = value.direction
        resource_group_name          = var.network_security_rules.resource_group_name
        network_security_group_name  = var.network_security_rules.network_security_group_name
        description                  = "Terraform Managed. ${coalesce(value.description, " ")}"
        priority                     = value.priority
        direction                    = try(value.direction, null)
        access                       = try(value.access, "Deny")
        protocol                     = try(title(value.protocol), "*")
        source_port_range            = try(value.source_port_range, null)
        source_port_ranges           = try(value.source_port_ranges, null)
        destination_port_range       = try(value.destination_port_range, null)
        destination_port_ranges      = try(value.destination_port_ranges, null)
        source_address_prefix        = try(value.source_address_prefix, null)
        destination_address_prefix   = try(value.destination_address_prefix, null)
        source_address_prefixes      = try(value.source_address_prefixes, null)
        destination_address_prefixes = try(value.destination_address_prefixes, null)

        #if an destination asg key is provided and it can be obtained from a resource or a data than get that value, else null
        source_application_security_group_ids = try(value.source_asg_keys, null) != null ? [for asg in value.source_asg_keys : can(coalesce(
          try(azurerm_application_security_group.asg[asg].id, null),
          try(data.azurerm_application_security_group.asg[asg].id, null)
          )) ? coalesce(
          try(azurerm_application_security_group.asg[asg].id, null),
          try(data.azurerm_application_security_group.asg[asg].id, null)
        ) : null] : []

        #if an destination asg key is provided and it can be obtained from a resource or a data than get that value, else null
        destination_application_security_group_ids = try(value.destination_asg_keys, null) != null ? [for asg in value.destination_asg_keys : can(coalesce(
          try(azurerm_application_security_group.asg[asg].id, null),
          try(data.azurerm_application_security_group.asg[asg].id, null)
          )) ? coalesce(
          try(azurerm_application_security_group.asg[asg].id, null),
          try(data.azurerm_application_security_group.asg[asg].id, null)
        ) : null] : []
      }
    ]) : mapping.name => mapping
  } : {}
}

# Begin r-pe.tf

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
}

# Begin r-rg.tf

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = merge(
    tomap(
      { "wab:resource-name" = var.resource_group_name }
    ),
    local.common_tags, local.resource_specific_tags
  )

  #lifecycle {
  #  ignore_changes = [tags]
  #}
}

# Begin r-rnd.tf

resource "random_password" "password" {
  #Create a random password if one is not given
  count            = var.admin_password != null ? 0 : 1
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Begin r-snet.tf

resource "azurerm_subnet" "snet" {
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

# Begin r-umid.tf

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

# Begin variables.tf

variable "spn" {
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
  validation {
    condition = contains(
      [
        "WEST US",
        "WEST US 2",
        "WEST US 3",
        "EAST US",
      ], var.location
    )
    error_message = format("A location value of '%s' is not allowed. Please use one of the following: \n %s", var.location,
      join("\n ",
        [
          "US WEST",
          "US WEST 2",
          "US WEST 3",
          "US EAST",
        ]
      )
    )
  }
}

variable "existing_application_security_groups" {
  type = map(object({
    name                = string
    resource_group_name = optional(string)

  }))
  default     = {}
  description = <<-EOT
  map(object({
    name         = Name of the application security group 
  }))
  EOT
  nullable    = false
}

variable "application_security_groups" {
  type = map(object({
    name = string

  }))
  default     = {}
  description = <<-EOT
  map(object({
    name         = Name of the application security group 
  }))
  EOT
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
  description = <<-EOT
  name                          = The name of the vault
  sku_name                      = The name of the SKU used for this Key Vault. Possible values are standard and premium
  soft_delete_retention_days    = The number of days that items should be retained for once soft-deleted. This value can be between 7 and 90
  public_network_access_enabled = Whether public network access is allowed for this Key Vault.
  snet_key                      = Subnet key that this key vault should be in
  key_name                = The name of the key vault key
  EOT
  nullable    = false

  validation {
    condition     = alltrue([can(regex("^([a-z])[a-z0-9-]*[a-z0-9]$", var.key_vault.name)) && !can(regex("--", var.key_vault.name)) && length(var.key_vault.name) <= 24])
    error_message = "The key vault name must contain only the following characters A-Z, a-z, 0-9, and '-' and must be 24 characters or less."
  }
  validation {
    condition     = alltrue([can(regex("^([a-z])[a-z0-9-]*[a-z0-9]$", var.key_vault.key_name)) && !can(regex("--", var.key_vault.name)) && length(var.key_vault.key_name) <= 127])
    error_message = "The key vault name must contain only the following characters A-Z, a-z, 0-9, and '-' and must be 127 characters or less."
  }
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

variable "existing_subnets" {
  type = map(object({
    resource_group_name  = string
    virtual_network_name = string
    name                 = string
  }))
  default     = null
  description = <<-EOT
  map(object({
    resource_group_name         = Name of the resource group the vnet is in
    virtual_network_name        = Name of virtual network the subnet is will be attached to
    network_security_group_name = Name of the network security group to associate with the subnet
    route_table_name            = Name of the route table to associate with the subnet
    name                        = Name of the subnet
    prefixes                    = Address prefixes to use for the subnet
    service_endpoints           = List of Service endpoints to associate with the subnet
  }))
  EOT
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
  description = <<-EOT
  map(object({
    resource_group_name         = Name of the resource group the vnet is in
    virtual_network_name        = Name of virtual network the subnet is will be attached to
    network_security_group_name = Name of the network security group to associate with the subnet
    route_table_name            = Name of the route table to associate with the subnet
    name                        = Name of the subnet
    prefixes                    = Address prefixes to use for the subnet
    service_endpoints           = List of Service endpoints to associate with the subnet
  }))
  EOT
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
  description = <<-EOT
  map(object({
    name                           = (Required) Specifies the Name of the Private Endpoint.
    subresource_names              = (Optional) A list of subresource names which the Private Endpoint is able to connect to. subresource_names corresponds to group_id. Possible values are detailed in the product documentation in the Subresources column.
    private_connection_resource_id = (Optional) The ID of the Private Link Enabled Remote Resource which this Private Endpoint should be connected to.
    is_manual_connection           = (Required) Does the Private Endpoint require Manual Approval from the remote resource owner?
    private_dns_zone_group_name    = (Required) Specifies the Name of the Private Service Connection
    private_dns_zone_ids           = (Required) Specifies the list of Private DNS Zones to include within the private_dns_zone_group
  }))
  EOT
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

variable "vm_process_data_collection_rules" {
  type = map(object({
    name = string
    id   = string
  }))
  default = {
    "WEST US 3" = {
      name = "dcr-vm-process-data-westus3"
      id   = "/subscriptions/5cb440c1-22d6-404e-a472-0fc1911fb361/resourceGroups/rg-infra-dcr-prod/providers/Microsoft.Insights/dataCollectionRules/dcr-vm-process-data-westus3"
    },
    "WEST US" = {
      name = "dcr-vm-process-data-westus"
      id   = "/subscriptions/5cb440c1-22d6-404e-a472-0fc1911fb361/resourceGroups/rg-infra-dcr-prod/providers/Microsoft.Insights/dataCollectionRules/dcr-vm-process-data-westus"
    },
    "EAST US" = {
      name = "dcr-vm-process-data-eastus"
      id   = "/subscriptions/5cb440c1-22d6-404e-a472-0fc1911fb361/resourceGroups/rg-infra-dcr-prod/providers/Microsoft.Insights/dataCollectionRules/dcr-vm-process-data-eastus"
    }
  }
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
  description = <<-EOT
  map(object({
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
    data_disks = map(object({
      name = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
      size = The Size of the data Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you'll need to repartition the disk to use the remaining space.
      type = (optional) Storage type of the data disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
      tier = (optional) The disk performance tier to use. Possible values are documented here https://learn.microsoft.com/en-us/azure/virtual-machines/disks-change-performance. This feature is currently supported only for premium SSDs.
    }))
    tags = list(object({
      "role"             = 
      "patch-optin"      = (YES,NO)
      "snow-item"        = If the vm is part of a different ticket provide it
    }))
  }))
  EOT
  nullable    = true

  validation {
    condition = var.vm_list != null ? alltrue([for k, v in var.vm_list :
    can(regex("[0-9A-Za-z-]", v.name)) && length(v.name) <= (v.image_os == "linux" ? 64 : 15)]) : true
    error_message = "The vm name must contain only the following characters A-Z, a-z, 0-9, and '-'. In addition windows vms must be 15 characters or less and linux vms must be 64 characters or less."
  }

  validation {
    condition = var.vm_list != null ? alltrue([for k, v in var.vm_list :
    contains(["windows", "linux"], v.image_os)]) : true
    error_message = "The image os value must be one of the following: windows, linux"
  }

  validation {
    condition = var.vm_list != null ? alltrue([for k, v in var.vm_list :
    contains(["Static", "Dynamic"], v.ip_allocation)]) : true
    error_message = "The ip allocation value must be one of the following: Static, Dynamic"
  }

  validation {
    condition = var.vm_list != null ? alltrue([for k, v in var.vm_list :
      contains(
        [
          "Standard_LRS",
          "StandardSSD_LRS",
          "StandardSSD_ZRS",
          "Premium_ZRS",
          "Premium_LRS",
          "PremiumV2_LRS",
          "UltraSSD_LRS"
      ], v.os_disk_type)]
    ) : true
    error_message = format("The os disk type value must be one of the following: \n %s",
      join("\n ",
        [
          "Standard_LRS",
          "StandardSSD_LRS",
          "StandardSSD_ZRS",
          "Premium_ZRS",
          "Premium_LRS",
          "PremiumV2_LRS",
          "UltraSSD_LRS"
        ]
      )
    )
  }

  validation {
    condition = var.vm_list != null ? alltrue([for k, v in var.vm_list : v.data_disk_type != null ?
      contains(
        [
          "Standard_LRS",
          "StandardSSD_LRS",
          "StandardSSD_ZRS",
          "Premium_ZRS",
          "Premium_LRS",
          "PremiumV2_LRS",
          "UltraSSD_LRS"
      ], v.data_disk_type) : true
    ]) : true

    error_message = format("The data disk type value must be one of the following: \n %s",
      join("\n ",
        [
          "Standard_LRS",
          "StandardSSD_LRS",
          "StandardSSD_ZRS",
          "Premium_ZRS",
          "Premium_LRS",
          "PremiumV2_LRS",
          "UltraSSD_LRS"
        ]
      )
    )
  }

  validation {
    condition = var.vm_list != null ? alltrue([for k, v in var.vm_list :
    contains(["YES", "NO", "NA"], v.tags.patch-optin)]) : true
    error_message = "A patch-optin tag value must be one of the following: YES, NO, NA"
  }
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

  validation {
    condition = contains(
      [
        "DEV",
        "QA",
        "UAT",
        "PROD",
        "DR"
      ], var.common_tags.environment
    )
    error_message = format("An environment tag value of '%s' is not allowed. Please use one of the following: \n %s", var.common_tags.environment,
      join("\n ",
        [
          "DEV",
          "QA",
          "UAT",
          "PROD",
          "DR"
        ]
      )
    )
  }

  validation {
    condition = contains(
      [
        "Platinum",
        "Gold",
        "Iron",
        "Silver",
        "Bronze",
      ], var.common_tags.app-tier
    )
    error_message = format("A app-tier tag value of '%s' is not allowed. Please use one of the following: \n %s", var.common_tags.app-tier,
      join("\n ",
        [
          "Platinum",
          "Gold",
          "Iron",
          "Silver",
          "Bronze",
        ]
      )
    )
  }

  validation {
    condition     = var.common_tags.it-cost-center == "NA" || can(var.common_tags.it-cost-center * 1)
    error_message = format("An it-cost-center tag value of '%s' is not allowed. Please use NA or a whole number", var.common_tags.it-cost-center)
  }

  #validation {
  #  condition     = var.common_tags.cost-center == "NA" || can(var.common_tags.cost-center * 1)
  #  error_message = format("A cost-center tag value of '%s' is not allowed. Please use NA or a whole number", var.common_tags.cost-center)
  #}
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
  description = "These need to be on all resources. Some resources such as VMs will have values. Those tag values are controlled under that variable."

  validation {
    condition     = contains(["YES", "NO", "NA"], var.resource_specific_tags.patch-optin)
    error_message = format("A patch-optin tag value of '%s' is not allowed. Please use one of the following: YES, NO, NA", var.resource_specific_tags.patch-optin)
  }
}