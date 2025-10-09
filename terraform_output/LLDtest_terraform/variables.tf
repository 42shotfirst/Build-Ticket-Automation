# Variables for default-project
# Generated from Excel data on 2025-09-25 18:10:49

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

variable "vm_count" {
  description = "Number of VMs to create"
  type        = number
  default     = 23
}

variable "vm_size" {
  description = "Size of the VMs"
  type        = string
  default     = "Standard_D2s_v3"
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
