# main.tf
# Generated from Excel data

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

module "base-vm" {
  source  = "app.terraform.io/wab-cloudengineering-org/base-vm/iac"
  version = "1.0.0"

  # Core configuration
  spn                 = var.spn
  location            = var.location
  resource_group_name = var.resource_group_name

  # Security groups
  application_security_groups = var.application_security_groups

  # Key vault and identity
  key_vault                   = var.key_vault
  user_assigned_identity_name = var.user_assigned_identity_name
  disk_encryption_set_name    = var.disk_encryption_set_name

  # Networking
  subnets           = var.subnets
  private_endpoints = var.private_endpoints

  # VM configuration
  admin_username = var.admin_username
  admin_password = var.admin_password
  vm_list        = var.vm_list

  # Security rules
  network_security_rules = var.network_security_rules

  # Tags
  common_tags            = var.common_tags
  resource_specific_tags = var.resource_specific_tags
}
