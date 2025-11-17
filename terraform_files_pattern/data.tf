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
