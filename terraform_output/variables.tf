# variables.tf
# Generated from Excel data

variable "spn" {
  type        = string
  description = "Service Principal Name"
}

variable "location" {
  type        = string
  default     = "West US 3"
  description = "Azure region for resources"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name"
}

variable "application_security_groups" {
  type = map(object({
    name = string
  }))
  description = "Application security groups"
}

variable "key_vault" {
  type = object({
    name                       = string
    sku_name                   = string
    soft_delete_retention_days = number
    public_network_access      = bool
    snet_key                   = string
    key_name                   = string
  })
  description = "Key vault configuration"
}

variable "user_assigned_identity_name" {
  type        = string
  description = "User assigned identity name"
}

variable "disk_encryption_set_name" {
  type        = string
  description = "Disk encryption set name"
}

variable "subnets" {
  type = map(object({
    resource_group_name         = string
    virtual_network_name        = string
    network_security_group_id   = string
    route_table_id              = string
    name                        = string
    prefixes                    = list(string)
    service_endpoints           = list(string)
  }))
  description = "Subnet configurations"
}

variable "private_endpoints" {
  type = map(object({
    name              = string
    subresource_names = list(string)
    snet_key          = string
    asg_key           = string
  }))
  description = "Private endpoint configurations"
}

variable "admin_username" {
  type        = string
  default     = "azureadmin"
  description = "VM admin username"
}

variable "admin_password" {
  type        = string
  sensitive   = true
  description = "VM admin password"
}

variable "vm_list" {
  type = map(object({
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
  }))
  description = "Virtual machine configurations"
}

variable "network_security_rules" {
  type = object({
    resource_group_name         = string
    network_security_group_name = string
    rules = list(object({
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
    }))
  })
  description = "Network security rules"
}

variable "common_tags" {
  type        = map(string)
  description = "Common tags for all resources"
}

variable "resource_specific_tags" {
  type        = map(map(string))
  default     = {}
  description = "Resource-specific tags"
}
