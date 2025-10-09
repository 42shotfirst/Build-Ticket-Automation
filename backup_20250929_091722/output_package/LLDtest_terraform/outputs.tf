# Outputs for default-project
# Generated from Excel data on 2025-09-29 09:16:32

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

output "virtual_network_name" {
  description = "Name of the virtual network"
  value       = azurerm_virtual_network.main.name
}

output "virtual_network_id" {
  description = "ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = azurerm_subnet.main.name
}

output "subnet_id" {
  description = "ID of the subnet"
  value       = azurerm_subnet.main.id
}

output "network_security_group_name" {
  description = "Name of the network security group"
  value       = azurerm_network_security_group.main.name
}

output "network_security_group_id" {
  description = "ID of the network security group"
  value       = azurerm_network_security_group.main.id
}


# Virtual Machine Outputs

output "myapp_01_name" {
  description = "Name of myapp-01"
  value       = azurerm_linux_virtual_machine.myapp_01.name
}

output "myapp_01_id" {
  description = "ID of myapp-01"
  value       = azurerm_linux_virtual_machine.myapp_01.id
}

output "myapp_01_private_ip" {
  description = "Private IP of myapp-01"
  value       = azurerm_linux_virtual_machine.myapp_01.private_ip_address
}

output "myapp_02_name" {
  description = "Name of myapp-02"
  value       = azurerm_linux_virtual_machine.myapp_02.name
}

output "myapp_02_id" {
  description = "ID of myapp-02"
  value       = azurerm_linux_virtual_machine.myapp_02.id
}

output "myapp_02_private_ip" {
  description = "Private IP of myapp-02"
  value       = azurerm_linux_virtual_machine.myapp_02.private_ip_address
}
