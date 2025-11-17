# Begin data.tf

data "azurerm_client_config" "current" {}

data "azurerm_subscription" "subscription" {
  subscription_id = data.azurerm_client_config.current.subscription_id
}

data "azuread_service_principal" "spn" {
  display_name = var.spn
}