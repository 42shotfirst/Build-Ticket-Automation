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
    error_message = format("A location value of "%s" is not allowed. Please use one of the following: \n %s", var.location,
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
    public_network_access      = true
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
    zone              = (optional) The Availability Zone which the Virtual Machine should be allocated in, only one zone would be accepted. If set then this module will not create "azurerm_availability_set" resource. Changing this forces a new resource to be created.
    image_os          = Enum flag of virtual machine os system. windows or linux
    image_urn         = Azure urn Publisher:Offer:SKU:Version
    ip_allocation     = The allocation method used for the Private IP Address. Possible values are Dynamic and Static
    os_disk_name      = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
    os_disk_size      = The Size of the Internal OS Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you will need to repartition the disk to use the remaining space.
    os_disk_type      = (optional) Storage type of the OS disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
    os_disk_tier      = (optional) The disk performance tier to use. Possible values are documented here https://learn.microsoft.com/en-us/azure/virtual-machines/disks-change-performance. This feature is currently supported only for premium SSDs.
    data_disk_sizes   = (optional) Specifies the size of the managed disk to create in gigabytes. If create_option is Copy or FromImage, then the value must be equal to or greater than the source size. The size can only be increased. Changing this value may be disruptive if the disk is attached to a Virtual Machine.
    data_disk_type    = (optional) Storage type of the data disk. Standard_LRS, StandardSSD_LRS, StandardSSD_ZRS, Premium_ZRS, Premium_LRS, PremiumV2_LRS or UltraSSD_LRS
    data_disks = map(object({
      name = (optional) The name which should be used for the Internal OS Disk. Changing this forces a new resource to be created. By default will be based off the vm name.
      size = The Size of the data Disk in GB, if you wish to vary from the size used in the image this Virtual Machine is sourced from. If specified this must be equal to or larger than the size of the Image the Virtual Machine is based on. When creating a larger disk than exists in the image you will need to repartition the disk to use the remaining space.
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
    error_message = format("An environment tag value of "%s" is not allowed. Please use one of the following: \n %s", var.common_tags.environment,
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
    error_message = format("A app-tier tag value of "%s" is not allowed. Please use one of the following: \n %s", var.common_tags.app-tier,
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
    error_message = format("An it-cost-center tag value of "%s" is not allowed. Please use NA or a whole number", var.common_tags.it-cost-center)
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
  description = "These need to be on all resources. Some resources such as VMs will have values. Those tag values are controlled under that variable."

  validation {
    condition     = contains(["YES", "NO", "NA"], var.resource_specific_tags.patch-optin)
    error_message = format("A patch-optin tag value of "%s" is not allowed. Please use one of the following: YES, NO, NA", var.resource_specific_tags.patch-optin)
  }
}
