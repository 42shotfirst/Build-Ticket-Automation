# Variables for default-project
# Generated from Excel data on 2025-09-30 17:56:49

# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "default-project"
}

variable "application_name" {
  description = "Name of the application"
  type        = string
  default     = "default-app"
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
  default     = "TBD"
}

variable "business_owner" {
  description = "Business owner"
  type        = string
  default     = "TBD"
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
  default     = 2
}

variable "vm_size" {
  description = "Size of the VMs"
  type        = string
  default     = "Standard_D2s_v3"
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
    Project     = "default-project"
    Application = "default-app"
    Environment = "dev"
    Owner       = "TBD"
    CreatedBy   = "Excel-to-Terraform-Generator"
  }
}
