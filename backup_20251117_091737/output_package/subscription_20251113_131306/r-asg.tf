# Begin r-asg.tf

resource "azurerm_application_security_group" "asg" {
  for_each            = var.application_security_groups
  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tags = merge(
    tomap(
      { "wab:resource-name" = "${each.value.name}" }
    ),
    local.common_tags, local.resource_specific_tags
  )
}