# Main Terraform configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Azure Provider configuration
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "azuread" {}

provider "random" {}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = merge(
    tomap(
      { "wab:resource-name" = var.resource_group_name }
    ),
    local.common_tags, local.resource_specific_tags
  )
}
