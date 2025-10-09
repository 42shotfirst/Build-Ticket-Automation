# Main Terraform configuration
# Generated from Excel data on 2025-10-07 10:32:38

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location

  tags = {
    Project     = var.project_name
    Application = var.application_name
    Environment = var.environment
    Owner       = var.app_owner
    CreatedBy   = "Excel-to-Terraform-Generator"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "vnet-${var.project_name}-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = azurerm_resource_group.main.tags
}

# Subnet
resource "azurerm_subnet" "main" {
  name                 = "subnet-${var.project_name}-${var.environment}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Network Security Group
resource "azurerm_network_security_group" "main" {
  name                = "nsg-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = azurerm_resource_group.main.tags
}

# Network Security Group Rules

resource "azurerm_network_security_rule" "one" {
  name                        = var.nsg_rules[0].name
  priority                    = var.nsg_rules[0].priority
  direction                   = var.nsg_rules[0].direction
  access                      = var.nsg_rules[0].access
  protocol                    = var.nsg_rules[0].protocol
  source_port_range           = var.nsg_rules[0].source_port_range
  destination_port_range      = var.nsg_rules[0].destination_port_range
  source_address_prefix       = var.nsg_rules[0].source_address_prefix
  destination_address_prefix  = var.nsg_rules[0].destination_address_prefix
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.main.name
}

resource "azurerm_network_security_rule" "two" {
  name                        = var.nsg_rules[1].name
  priority                    = var.nsg_rules[1].priority
  direction                   = var.nsg_rules[1].direction
  access                      = var.nsg_rules[1].access
  protocol                    = var.nsg_rules[1].protocol
  source_port_range           = var.nsg_rules[1].source_port_range
  destination_port_range      = var.nsg_rules[1].destination_port_range
  source_address_prefix       = var.nsg_rules[1].source_address_prefix
  destination_address_prefix  = var.nsg_rules[1].destination_address_prefix
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.main.name
}


# Application Gateway
resource "azurerm_public_ip" "appgw" {
  name                = "pip-${var.project_name}-${var.environment}-appgw"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                = "Standard"

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_application_gateway" "main" {
  name                = "appgw-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku {
    name     = "Standard_v2"
    tier     = "Standard_v2"
    capacity = 2
  }

  gateway_ip_configuration {
    name      = "gateway-ip-configuration"
    subnet_id = azurerm_subnet.main.id
  }

  frontend_port {
    name = "frontend-port"
    port = False
  }

  frontend_ip_configuration {
    name                 = "frontend-ip-configuration"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }

  backend_address_pool {
    name = "Value"
  }

  backend_http_settings {
    name                  = "Value"
    cookie_based_affinity = "Disabled"
    port                  = False
    protocol              = "Http"
    request_timeout       = 30
  }

  http_listener {
    name                           = "listener"
    frontend_ip_configuration_name = "frontend-ip-configuration"
    frontend_port_name             = "frontend-port"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "listener"
    backend_address_pool_name  = "Value"
    backend_http_settings_name = "Value"
    priority                   = 100
  }

  tags = azurerm_resource_group.main.tags
}


# Container Registry
resource "azurerm_container_registry" "main" {
  name                = "acr${{var.project_name}}${{var.environment}}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = azurerm_resource_group.main.tags
}


# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "st${var.project_name}${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_storage_container" "main" {
  name                  = "container"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}


# Virtual Machines - Comprehensive Generation
# Generated from 23 VM instances found in Excel data

# VM 1: vm-001
resource "azurerm_linux_virtual_machine" "vm-001" {
  name                = var.vm_names[0]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-001.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[0]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 1
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-001" {
  name                = "nic-${var.vm_names[0]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[0]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 2: vm-002
resource "azurerm_linux_virtual_machine" "vm-002" {
  name                = var.vm_names[1]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-002.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[1]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 2
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-002" {
  name                = "nic-${var.vm_names[1]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[1]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 3: vm-003
resource "azurerm_linux_virtual_machine" "vm-003" {
  name                = var.vm_names[2]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-003.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[2]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 3
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-003" {
  name                = "nic-${var.vm_names[2]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[2]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 4: vm-004
resource "azurerm_linux_virtual_machine" "vm-004" {
  name                = var.vm_names[3]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-004.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[3]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 4
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-004" {
  name                = "nic-${var.vm_names[3]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[3]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 5: vm-005
resource "azurerm_linux_virtual_machine" "vm-005" {
  name                = var.vm_names[4]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-005.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[4]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 5
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-005" {
  name                = "nic-${var.vm_names[4]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[4]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 6: vm-006
resource "azurerm_linux_virtual_machine" "vm-006" {
  name                = var.vm_names[5]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-006.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[5]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 6
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-006" {
  name                = "nic-${var.vm_names[5]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[5]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 7: vm-007
resource "azurerm_linux_virtual_machine" "vm-007" {
  name                = var.vm_names[6]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-007.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[6]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 7
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-007" {
  name                = "nic-${var.vm_names[6]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[6]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 8: vm-008
resource "azurerm_linux_virtual_machine" "vm-008" {
  name                = var.vm_names[7]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-008.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[7]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 8
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-008" {
  name                = "nic-${var.vm_names[7]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[7]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 9: vm-009
resource "azurerm_linux_virtual_machine" "vm-009" {
  name                = var.vm_names[8]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-009.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[8]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 9
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-009" {
  name                = "nic-${var.vm_names[8]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[8]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 10: vm-010
resource "azurerm_linux_virtual_machine" "vm-010" {
  name                = var.vm_names[9]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-010.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[9]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 10
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-010" {
  name                = "nic-${var.vm_names[9]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[9]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 11: vm-011
resource "azurerm_linux_virtual_machine" "vm-011" {
  name                = var.vm_names[10]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-011.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[10]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 11
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-011" {
  name                = "nic-${var.vm_names[10]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[10]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 12: vm-012
resource "azurerm_linux_virtual_machine" "vm-012" {
  name                = var.vm_names[11]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-012.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[11]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 12
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-012" {
  name                = "nic-${var.vm_names[11]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[11]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 13: vm-013
resource "azurerm_linux_virtual_machine" "vm-013" {
  name                = var.vm_names[12]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-013.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[12]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 13
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-013" {
  name                = "nic-${var.vm_names[12]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[12]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 14: vm-014
resource "azurerm_linux_virtual_machine" "vm-014" {
  name                = var.vm_names[13]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-014.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[13]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 14
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-014" {
  name                = "nic-${var.vm_names[13]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[13]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 15: vm-015
resource "azurerm_linux_virtual_machine" "vm-015" {
  name                = var.vm_names[14]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-015.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[14]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 15
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-015" {
  name                = "nic-${var.vm_names[14]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[14]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 16: vm-016
resource "azurerm_linux_virtual_machine" "vm-016" {
  name                = var.vm_names[15]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-016.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[15]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 16
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-016" {
  name                = "nic-${var.vm_names[15]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[15]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 17: vm-017
resource "azurerm_linux_virtual_machine" "vm-017" {
  name                = var.vm_names[16]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-017.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[16]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 17
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-017" {
  name                = "nic-${var.vm_names[16]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[16]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 18: vm-018
resource "azurerm_linux_virtual_machine" "vm-018" {
  name                = var.vm_names[17]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-018.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[17]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 18
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-018" {
  name                = "nic-${var.vm_names[17]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[17]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 19: vm-019
resource "azurerm_linux_virtual_machine" "vm-019" {
  name                = var.vm_names[18]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-019.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[18]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 19
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-019" {
  name                = "nic-${var.vm_names[18]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[18]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 20: vm-020
resource "azurerm_linux_virtual_machine" "vm-020" {
  name                = var.vm_names[19]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-020.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[19]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 20
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-020" {
  name                = "nic-${var.vm_names[19]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[19]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 21: vm-021
resource "azurerm_linux_virtual_machine" "vm-021" {
  name                = var.vm_names[20]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-021.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[20]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 21
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-021" {
  name                = "nic-${var.vm_names[20]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[20]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 22: vm-022
resource "azurerm_linux_virtual_machine" "vm-022" {
  name                = var.vm_names[21]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-022.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[21]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 22
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-022" {
  name                = "nic-${var.vm_names[21]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[21]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}

# VM 23: vm-023
resource "azurerm_linux_virtual_machine" "vm-023" {
  name                = var.vm_names[22]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  network_interface_ids = [
    azurerm_network_interface.vm-023.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = var.vm_names[22]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = 23
    Type        = "Virtual Machine"
  })
}

resource "azurerm_network_interface" "vm-023" {
  name                = "nic-${var.vm_names[22]}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }

  tags = merge(azurerm_resource_group.main.tags, {
    Name        = "nic-${var.vm_names[22]}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  })
}
