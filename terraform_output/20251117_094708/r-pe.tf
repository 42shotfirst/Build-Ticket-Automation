# Begin r-pe.tf

resource "azurerm_private_endpoint" "pe" {
  for_each            = var.private_endpoints
  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id = coalesce(
    try(azurerm_subnet.snet[each.value.snet_key].id, null),
    try(data.azurerm_subnet.snet[each.value.snet_key].id, null)
  )
  private_dns_zone_group {
    name                 = coalesce(each.value.private_dns_zone_group_name, "default")
    private_dns_zone_ids = coalesce(each.value.private_dns_zone_ids, ["/subscriptions/f3b58ef2-13a2-492a-b3b5-8688d74fd868/resourceGroups/rg-privatedns-prod-001/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net"])
  }
  private_service_connection {
    name                           = each.value.name
    is_manual_connection           = coalesce(each.value.is_manual_connection, "false")
    subresource_names              = each.value.subresource_names
    private_connection_resource_id = coalesce(each.value.private_connection_resource_id, azurerm_key_vault.kvlt.id)
  }
  custom_network_interface_name = "nic01-${each.value.name}"
  tags = merge(
    tomap(
      { "wab:resource-name" = "${each.value.name}" }
    ),
    local.common_tags, local.resource_specific_tags
  )
}