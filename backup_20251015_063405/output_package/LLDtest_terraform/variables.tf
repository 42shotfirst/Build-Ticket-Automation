# Variables for project1
# Generated from Excel data on 2025-10-07 10:32:38

# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "project1"
}

variable "application_name" {
  description = "Name of the application"
  type        = string
  default     = "myapp"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

# Build Environment (from Build_ENV sheet)
variable "subscription" {
  description = "Azure subscription"
  type        = string
  default     = "subscription"
}

variable "resource_group_key" {
  description = "Resource group key"
  type        = string
  default     = "key"
}

# Application Details
variable "app_owner" {
  description = "Application owner"
  type        = string
  default     = "Morgan"
}

variable "business_owner" {
  description = "Business owner"
  type        = string
  default     = "Morgan"
}

variable "admin_username" {
  description = "Admin username for VMs"
  type        = string
  default     = "azureuser"
}

# Infrastructure Configuration
variable "vm_count" {
  description = "Number of VMs to create"
  type        = number
  default     = 23
}

variable "vm_names" {
  description = "List of VM names"
  type        = list(string)
  default     = ["vm-001", "vm-002", "vm-003", "vm-004", "vm-005", "vm-006", "vm-007", "vm-008", "vm-009", "vm-010", "vm-011", "vm-012", "vm-013", "vm-014", "vm-015", "vm-016", "vm-017", "vm-018", "vm-019", "vm-020", "vm-021", "vm-022", "vm-023"]
}

variable "vm_size" {
  description = "Size of the VMs"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "vm_os_disk_type" {
  description = "OS disk type for VMs"
  type        = string
  default     = "Premium_LRS"
}

variable "vm_os_disk_size" {
  description = "OS disk size in GB"
  type        = number
  default     = 30
}

variable "vm_image_publisher" {
  description = "VM image publisher"
  type        = string
  default     = "Canonical"
}

variable "vm_image_offer" {
  description = "VM image offer"
  type        = string
  default     = "0001-com-ubuntu-server-jammy"
}

variable "vm_image_sku" {
  description = "VM image SKU"
  type        = string
  default     = "22_04-lts"
}

variable "vm_image_version" {
  description = "VM image version"
  type        = string
  default     = "latest"
}

variable "vm_private_ip_allocation" {
  description = "Private IP allocation method"
  type        = string
  default     = "Dynamic"
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

# Network Configuration
variable "vnet_address_space" {
  description = "VNet address space"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_address_prefixes" {
  description = "Subnet address prefixes"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

# Network Security Group Rules
variable "nsg_rules" {
  description = "List of NSG rules"
  type = list(object({
    name                       = string
    priority                   = number
    direction                  = string
    access                     = string
    protocol                   = string
    source_port_range          = string
    destination_port_range     = string
    source_address_prefix      = string
    destination_address_prefix = string
  }))
  default = [{
    name                       = "one"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "1"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }, {
    name                       = "two"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "2"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }]
}

# Application Gateway Configuration (from APGW sheet)
variable "app_gateway_sku" {
  description = "Application Gateway SKU"
  type        = string
  default     = "Standard_v2"
}

variable "app_gateway_capacity" {
  description = "Application Gateway capacity"
  type        = number
  default     = 2
}

variable "app_gateway_port" {
  description = "Application Gateway port"
  type        = number
  default     = 80
}

variable "app_gateway_protocol" {
  description = "Application Gateway protocol"
  type        = string
  default     = "Http"
}

# Container Registry Configuration (from ACR NRS sheet)
variable "acr_sku" {
  description = "Container Registry SKU"
  type        = string
  default     = "Basic"
}

# Storage Configuration
variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "storage_replication_type" {
  description = "Storage replication type"
  type        = string
  default     = "LRS"
}

# Resource Naming Patterns (from Resource Options sheet)
variable "resource_naming_patterns" {
  description = "Resource naming patterns from Excel"
  type        = map(string)
  default = {
    Resource_Group = "rg-appname-env"
    Subnet = "Subnet"
    Network_Security_Group = "Network_Security_Group"
    Application_Gateway = "Application_Gateway"
    Azure_Container_Registry = "Azure_Container_Registry"
    Storage_Account = "Storage_Account"
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "project1"
    Application = "myapp"
    Environment = "dev"
    Owner       = "Morgan"
    CreatedBy   = "Excel-to-Terraform-Generator"
  }
}
