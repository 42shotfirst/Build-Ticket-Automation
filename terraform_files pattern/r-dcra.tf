resource "azurerm_monitor_data_collection_rule_association" "dcra" {
  for_each                = (local.common_tags["wab:environment"] == "PROD" || local.common_tags["wab:environment"] == "DR") && var.vm_list != null ? var.vm_list : {}
  name                    = module.vm[each.key].vm_name
  target_resource_id      = module.vm[each.key].vm_id
  data_collection_rule_id = var.vm_process_data_collection_rules[var.location].id
  description             = null
}
