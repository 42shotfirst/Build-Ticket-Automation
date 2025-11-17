resource "azurerm_subnet" "snet" {
  for_each = coalesce(var.subnets, {})

  name                 = each.value.name
  address_prefixes     = each.value.prefixes
  resource_group_name  = each.value.resource_group_name
  service_endpoints    = each.value.service_endpoints
  virtual_network_name = each.value.virtual_network_name
}

resource "azurerm_subnet_network_security_group_association" "nsg" {
  for_each  = coalesce(var.subnets, {})
  subnet_id = azurerm_subnet.snet[each.key].id
  network_security_group_id = coalesce(
    try(each.value.network_security_group_id, null),
    try(data.azurerm_network_security_group.nsg[each.key].id, null)
  )
}

resource "azurerm_subnet_route_table_association" "rta" {
  for_each  = coalesce(var.subnets, {})
  subnet_id = azurerm_subnet.snet[each.key].id
  route_table_id = coalesce(
    try(each.value.route_table_id, null),
    try(data.azurerm_route_table.rt[each.key].id, null)
  )
}
