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
}