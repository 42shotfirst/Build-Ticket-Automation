#output "build_validation" {
#  value = {
#    snow_ticket_number    = lookup(local.common_tags, "wab:snow-item")
#    app_tier              = lookup(local.common_tags, "wab:app-tier")
#    location              = azurerm_resource_group.rg.location
#    environment           = lookup(local.common_tags, "wab:environment")
#    resource_group        = azurerm_resource_group.rg.name
#    vm_name               = tomap({ for n, name in module.vm : n => name.vm_name })
#    vm_ip_addresses       = tomap({ for a, address in module.vm : a => address.network_interface_private_ip })
#    subnet_rsg            = tomap({ for n, snet in azurerm_subnet.snet : n => snet.resource_group_name })
#    vnet_rsg              = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.resource_group_name })
#    vnet_name             = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.name })
#    vnet_ip_address_space = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.address_space })
#    subnet_name           = tomap({ for n, snet in azurerm_subnet.snet : n => snet.name })
#    subnet_address_space  = tomap({ for n, snet in azurerm_subnet.snet : n => snet.address_prefixes })
#    nsg_name              = tomap({ for n, nsg in data.azurerm_network_security_group.nsg : n => nsg.name })
#    route_table_name      = tomap({ for n, rt in data.azurerm_route_table.rt : n => rt.name })
#    #route_table           = [for route in data.azurerm_route_table.rt.route : route if route.name == "Default"]
#  }
#}

output "build_validation" {
  value = {
    "01-Subscription" = data.azurerm_subscription.subscription.display_name
    "02-Resource_groups" = {
      "01-Name"          = var.resource_group_name
      "02-Location"      = azurerm_resource_group.rg.location
      "03-Environment"   = lookup(local.common_tags, "wab:environment")
      "04-App_tier"      = lookup(local.common_tags, "wab:app-tier")
      "05-Ticket_number" = lookup(local.common_tags, "wab:snow-item")
      "06-Virtual_machines" = [for vm_key, vm_value in module.vm : {
        "01-Name"         = vm_value.vm_name
        "02-IP_Address"   = vm_value.network_interface_private_ip
        "03-SKU"          = var.vm_list[vm_key].size
        "04-Zone"         = coalesce(var.vm_list[vm_key].zone, "none")
        "05-OS"           = coalesce(var.vm_list[vm_key].image_urn, var.vm_list[vm_key].source_image_id)
        "06-OS_disk_size" = var.vm_list[vm_key].os_disk_size
        "07-OS_disk_type" = var.vm_list[vm_key].os_disk_type
        "08-Data_disks"   = try(join(", ", var.vm_list[vm_key].data_disk_sizes), "none")
        "09-Subnet" = coalesce(
          try(azurerm_subnet.snet[var.vm_list[vm_key].snet_key].name, null),
          try(data.azurerm_subnet.snet[var.vm_list[vm_key].snet_key].name, null)
        )
        "10-ASG" = can(coalesce(
          try(azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].id, null),
          try(data.azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].id, null)
          )) ? try(join(", ", [coalesce(
            try(azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].name, null),
            try(data.azurerm_application_security_group.asg[var.vm_list[vm_key].asg_key].name, null)
        )]), null) : null
      }]
    }
    "03-Network" = {
      "01-Subnets" = {
        for key, snet in merge(var.subnets, var.existing_subnets) :
        key => {
          "01-Resource Group"                = snet.resource_group_name
          "02-Network Security Group"        = try(data.azurerm_network_security_group.nsg[key].name, data.azurerm_network_security_group.nsg_id[key].name, split("/", data.azurerm_subnet.snet[key].network_security_group_id)[8], "none")
          "03-Route Table"                   = try(data.azurerm_route_table.rt[key].name, data.azurerm_route_table.rt_id[key].name, split("/", data.azurerm_subnet.snet[key].route_table_id)[8], "none")
          "04-Virtual Network"               = snet.virtual_network_name
          "05-Virtual Network Address Space" = join(", ", try(data.azurerm_virtual_network.vnet[key].address_space, []))
          "06-Subnet"                        = snet.name
          "07-Subnet Prefix"                 = join(", ", try(data.azurerm_subnet.snet[key].address_prefixes, snet.prefixes))
          #try(
          #  lookup(data.azurerm_subnet.existing_subnets[key].address_prefix, 0, ""),
          #  snet.prefix
          #)
          "08-Subnet Service Endpoints" = join(", ", try(data.azurerm_subnet.snet[key].service_endpoints, snet.service_endpoints))
          #try(
          #  join(", ", data.azurerm_subnet.existing_subnets[key].service_endpoints),
          #  join(", ", snet.service_endpoints)
          #)
        }
      }
      "02-NSG Rules" = {
        for key, rule in azurerm_network_security_rule.nsr :
        key => {
          "01-Direction"          = rule.direction
          "01-Access"             = rule.access 
          "01-Priority"           = rule.priority
          "01-Name"               = rule.name
          "01-Source_port_range"  = rule.source_port_range
          "01-Source_port_range"  = rule.destination_port_range
          "01-Protocol"           = rule.protocol
          "01-Source"             = try(rule.source_port_range, join(", ", rule.source_port_ranges), join(", ", rule.source_application_security_group_ids))
          "01-Destination"        = try(rule.destination_port_range, join(", ", rule.destination_port_ranges), join(", ", rule.destination_application_security_group_ids))
          "01-Description"        = rule.description  
        }
      }
    }
  }
}

output "resources" {
  value = {
    rg = azurerm_resource_group.rg.id
    asg = tomap({ for n, asg in azurerm_application_security_group.asg : n => asg.id })
    dsk = azurerm_disk_encryption_set.dsk.id #tomap({ for n, dsk in azurerm_disk_encryption_set.dsk : n => dsk.id })
    umid = azurerm_user_assigned_identity.umid.id #tomap({ for n, umid in azurerm_user_assigned_identity.umid : n => umid.id })
    kvlt = azurerm_key_vault.kvlt.id #tomap({ for n, kvlt in azurerm_key_vault.kvlt : n => kvlt.id })
    kvkey = azurerm_key_vault_key.kvkey.id #tomap({ for n, kvkey in azurerm_key_vault_key.kvkey : n => kvkey.id })
    nsr = tomap({ for n, nsr in azurerm_network_security_rule.nsr : n => nsr.id })
    pe = tomap({ for n, pe in azurerm_private_endpoint.pe : n => pe.id })
    snet = tomap({ for n, snet in azurerm_subnet.snet : n => snet.id })
  }
}

#output "build_validation_improved" {
#  value = {
#    tags           = merge(local.common_tags, local.resource_specific_tags)
#    location       = azurerm_resource_group.rg.location
#    resource_group = azurerm_resource_group.rg.name
#    vm_all         = tomap({ for n, name in module.vm : n => name })
#
#    vm_name         = tomap({ for n, name in module.vm : n => name.vm_name })
#    vm_ip_addresses = tomap({ for a, address in module.vm : a => address.network_interface_private_ip })
#
#    #Networking
#    subnet_rsg            = tomap({ for n, snet in azurerm_subnet.snet : n => snet.resource_group_name })
#    vnet_rsg              = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.resource_group_name })
#    vnet_name             = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.name })
#    vnet_ip_address_space = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.address_space })
#    subnet_name           = tomap({ for n, snet in azurerm_subnet.snet : n => snet.name })
#    subnet_address_space  = tomap({ for n, snet in azurerm_subnet.snet : n => snet.address_prefixes })
#    nsg_name              = tomap({ for n, nsg in data.azurerm_network_security_group.nsg : n => nsg.name })
#    route_table_name      = tomap({ for n, rt in data.azurerm_route_table.rt : n => rt.name })
#    #route_table           = [for route in data.azurerm_route_table.rt.route : route if route.name == "Default"]
#  }
#}

#output "network" {
#  value = [
#    for s, snet in azurerm_subnet.snet : {
#      resource_group_name      = snet.resource_group_name
#      vnet_name                = data.azurerm_virtual_network.vnet[snet].name
#      vnet_ip_address_space    = data.azurerm_virtual_network.vnet[snet].address_space
#      vnet_dns_servar          = data.azurerm_virtual_network.vnet[snet].dns_servers
#      nsg_name                 = data.azurerm_network_security_group.nsg[snet].name
#      route_table_name         = data.azurerm_route_table.rt[snet].name
#      subnet_name              = snet.name
#      subnet_address_space     = snet.address_prefixes
#      subnet_service_endpoints = snet.service_endpoints
#    }
#  ]
#}
#
#output "resource_group_name" {
#  description = "Resource group name"
#  value       = azurerm_resource_group.rg.name
#}
#
#output "resource_group_location" {
#  description = "Resource group region"
#  value       = azurerm_resource_group.rg.location
#}
#
#output "environment" {
#  description = "Environment tag"
#  value       = lookup(local.common_tags, "wab:environment")
#}
#
#output "tier" {
#  description = "Resource group region"
#  value       = lookup(local.resource_specific_tags, "wab:tier")
#}
#
#output "snow_ticket_number" {
#  description = "Resource group region"
#  value       = lookup(local.common_tags, "wab:snow-item")
#}
#
#output "application_security_group_name" {
#  description = "Application security group name"
#  value       = tomap({ for n, asg in azurerm_application_security_group.asg : n => asg.name })
#}
#
#output "disk_encryption_set_name" {
#  description = "Disk encryption_set name"
#  value       = azurerm_disk_encryption_set.dsk.name
#}
#
#output "user_assigned_identity_name" {
#  description = "User identity name"
#  value       = azurerm_user_assigned_identity.umid.name
#}
#
#output "key_vault_name" {
#  description = "Key vault name"
#  value       = azurerm_key_vault.kvlt.name
#}
#
#output "key_vault_uri" {
#  description = "Key vault uri"
#  value       = azurerm_key_vault.kvlt.vault_uri
#}
#
#output "subnets_name" {
#  description = "Subnet name"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.name })
#}
#
#output "subnets_service_endpoints" {
#  description = "Subnet service_endpoints"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.service_endpoints })
#}
#
#output "subnets_virtual_network" {
#  description = "Subnet virtual network"
#  value       = tomap({ for n, vnet in data.azurerm_virtual_network.vnet : n => vnet.name })
#}
#
#output "subnets_address_prefixes" {
#  description = "Subnet address prefix"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.address_prefixes })
#}
#
#output "subnets_resource_group_name" {
#  description = "Subnet resource group name"
#  value       = tomap({ for n, snet in azurerm_subnet.snet : n => snet.resource_group_name })
#}
#
#output "route_table_name" {
#  description = "Route Table name"
#  value       = tomap({ for n, rt in data.azurerm_route_table.rt : n => rt.name })
#}
#
##output "route_table_default" {
##  description = "Route Table default"
##  value       = [for route in data.azurerm_route_table.rt.route : route if route.name == "Default"]
##}
#
#output "network_security_group_name" {
#  description = "NSG name"
#  value       = data.azurerm_network_security_group.nsg["snet1"].name
#}
#
#output "virtual_network_name" {
#  description = "Virtual Network name"
#  value       = data.azurerm_virtual_network.vnet["snet1"].name
#}
#
#output "virtual_network_address_space" {
#  description = "Virtual Network name"
#  value       = data.azurerm_virtual_network.vnet["snet1"].address_space
#}
#
#output "virtual_network_dns_servers" {
#  description = "Virtual Network dns servers"
#  value       = data.azurerm_virtual_network.vnet["snet1"].dns_servers
#}
#
#output "vm_name" {
#  description = "Virtual machine name"
#  value       = tomap({ for n, name in module.vm : n => name.vm_name })
#}
#
#output "vm_network_interface_private_ip" {
#  description = "Virtual machine network interface ip"
#  value       = tomap({ for a, address in module.vm : a => address.network_interface_private_ip })
#}
