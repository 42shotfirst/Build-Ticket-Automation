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
  #lifecycle {
  #  ignore_changes = [tags]
  #}
}

resource "azurerm_network_interface_application_security_group_association" "asg_nic" {
  #For each vm that is created attach the nic of the vm to an asg. Use the asg key in the list of vm to find the asg to attach it to
  for_each                      = module.vm
  network_interface_id          = each.value.network_interface_id
  application_security_group_id = azurerm_application_security_group.asg[var.vm_list[each.key].asg_key].id
}

resource "azurerm_private_endpoint_application_security_group_association" "asg_pe" {
  #For each private endpoint attach an asg. Use the asg key in the list of private endpoints to find the asg to attach it to
  for_each                      = var.private_endpoints
  private_endpoint_id           = azurerm_private_endpoint.pe[each.key].id
  application_security_group_id = azurerm_application_security_group.asg[var.private_endpoints[each.key].asg_key].id
}
