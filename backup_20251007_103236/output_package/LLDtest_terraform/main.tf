# Main Terraform configuration
# Generated from Excel data on 2025-10-02 15:56:50

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

resource "azurerm_network_security_rule" "rule_0" {
  name                        = "one"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "1"
  destination_port_range      = "5"
  source_address_prefix       = "17"
  destination_address_prefix  = "21"
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.main.name
}

resource "azurerm_network_security_rule" "rule_1" {
  name                        = "two"
  priority                    = 110
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "2"
  destination_port_range      = "6"
  source_address_prefix       = "18"
  destination_address_prefix  = "22"
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
  name                = "vm-001"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-001.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-001"
    VMOwner       = "Application Owner"
    VMEnvironment = "dev"
    VMIndex       = "1"
  })
}

resource "azurerm_network_interface" "vm-001" {
  name                = "nic-vm-001"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-001"
    VMOwner       = "Application Owner"
    VMEnvironment = "dev"
  })
}

# VM 2: vm-002
resource "azurerm_linux_virtual_machine" "vm-002" {
  name                = "vm-002"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-002.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-002"
    VMOwner       = "Business Owner"
    VMEnvironment = "dev"
    VMIndex       = "2"
  })
}

resource "azurerm_network_interface" "vm-002" {
  name                = "nic-vm-002"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-002"
    VMOwner       = "Business Owner"
    VMEnvironment = "dev"
  })
}

# VM 3: vm-003
resource "azurerm_linux_virtual_machine" "vm-003" {
  name                = "vm-003"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-003.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-003"
    VMOwner       = "TRB Approval Date"
    VMEnvironment = "dev"
    VMIndex       = "3"
  })
}

resource "azurerm_network_interface" "vm-003" {
  name                = "nic-vm-003"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-003"
    VMOwner       = "TRB Approval Date"
    VMEnvironment = "dev"
  })
}

# VM 4: vm-004
resource "azurerm_linux_virtual_machine" "vm-004" {
  name                = "vm-004"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-004.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-004"
    VMOwner       = "TRB Approval Link"
    VMEnvironment = "dev"
    VMIndex       = "4"
  })
}

resource "azurerm_network_interface" "vm-004" {
  name                = "nic-vm-004"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-004"
    VMOwner       = "TRB Approval Link"
    VMEnvironment = "dev"
  })
}

# VM 5: vm-005
resource "azurerm_linux_virtual_machine" "vm-005" {
  name                = "vm-005"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-005.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-005"
    VMOwner       = "Diagram"
    VMEnvironment = "dev"
    VMIndex       = "5"
  })
}

resource "azurerm_network_interface" "vm-005" {
  name                = "nic-vm-005"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-005"
    VMOwner       = "Diagram"
    VMEnvironment = "dev"
  })
}

# VM 6: vm-006
resource "azurerm_linux_virtual_machine" "vm-006" {
  name                = "vm-006"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-006.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-006"
    VMOwner       = "Built in"
    VMEnvironment = "dev"
    VMIndex       = "6"
  })
}

resource "azurerm_network_interface" "vm-006" {
  name                = "nic-vm-006"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-006"
    VMOwner       = "Built in"
    VMEnvironment = "dev"
  })
}

# VM 7: vm-007
resource "azurerm_linux_virtual_machine" "vm-007" {
  name                = "vm-007"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-007.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-007"
    VMOwner       = "DR Setup"
    VMEnvironment = "dev"
    VMIndex       = "7"
  })
}

resource "azurerm_network_interface" "vm-007" {
  name                = "nic-vm-007"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-007"
    VMOwner       = "DR Setup"
    VMEnvironment = "dev"
  })
}

# VM 8: vm-008
resource "azurerm_linux_virtual_machine" "vm-008" {
  name                = "vm-008"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-008.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-008"
    VMOwner       = "Recovery Type"
    VMEnvironment = "dev"
    VMIndex       = "8"
  })
}

resource "azurerm_network_interface" "vm-008" {
  name                = "nic-vm-008"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-008"
    VMOwner       = "Recovery Type"
    VMEnvironment = "dev"
  })
}

# VM 9: vm-009
resource "azurerm_linux_virtual_machine" "vm-009" {
  name                = "vm-009"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-009.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-009"
    VMOwner       = "Will it house Personally Identifiable Information (PII)"
    VMEnvironment = "dev"
    VMIndex       = "9"
  })
}

resource "azurerm_network_interface" "vm-009" {
  name                = "nic-vm-009"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-009"
    VMOwner       = "Will it house Personally Identifiable Information (PII)"
    VMEnvironment = "dev"
  })
}

# VM 10: vm-010
resource "azurerm_linux_virtual_machine" "vm-010" {
  name                = "vm-010"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-010.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-010"
    VMOwner       = "Is Remote desktop or SSH access required"
    VMEnvironment = "dev"
    VMIndex       = "10"
  })
}

resource "azurerm_network_interface" "vm-010" {
  name                = "nic-vm-010"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-010"
    VMOwner       = "Is Remote desktop or SSH access required"
    VMEnvironment = "dev"
  })
}

# VM 11: vm-011
resource "azurerm_linux_virtual_machine" "vm-011" {
  name                = "vm-011"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-011.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-011"
    VMOwner       = "Comments"
    VMEnvironment = "dev"
    VMIndex       = "11"
  })
}

resource "azurerm_network_interface" "vm-011" {
  name                = "nic-vm-011"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-011"
    VMOwner       = "Comments"
    VMEnvironment = "dev"
  })
}

# VM 12: vm-012
resource "azurerm_linux_virtual_machine" "vm-012" {
  name                = "vm-012"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-012.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-012"
    VMOwner       = "Application Name"
    VMEnvironment = "dev"
    VMIndex       = "12"
  })
}

resource "azurerm_network_interface" "vm-012" {
  name                = "nic-vm-012"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-012"
    VMOwner       = "Application Name"
    VMEnvironment = "dev"
  })
}

# VM 13: vm-013
resource "azurerm_linux_virtual_machine" "vm-013" {
  name                = "vm-013"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-013.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-013"
    VMOwner       = "Service Now Ticket"
    VMEnvironment = "dev"
    VMIndex       = "13"
  })
}

resource "azurerm_network_interface" "vm-013" {
  name                = "nic-vm-013"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-013"
    VMOwner       = "Service Now Ticket"
    VMEnvironment = "dev"
  })
}

# VM 14: vm-014
resource "azurerm_linux_virtual_machine" "vm-014" {
  name                = "vm-014"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-014.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-014"
    VMOwner       = "Environment"
    VMEnvironment = "dev"
    VMIndex       = "14"
  })
}

resource "azurerm_network_interface" "vm-014" {
  name                = "nic-vm-014"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-014"
    VMOwner       = "Environment"
    VMEnvironment = "dev"
  })
}

# VM 15: vm-015
resource "azurerm_linux_virtual_machine" "vm-015" {
  name                = "vm-015"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-015.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-015"
    VMOwner       = "App Tier"
    VMEnvironment = "dev"
    VMIndex       = "15"
  })
}

resource "azurerm_network_interface" "vm-015" {
  name                = "nic-vm-015"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-015"
    VMOwner       = "App Tier"
    VMEnvironment = "dev"
  })
}

# VM 16: vm-016
resource "azurerm_linux_virtual_machine" "vm-016" {
  name                = "vm-016"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-016.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-016"
    VMOwner       = "Shared Service Name"
    VMEnvironment = "dev"
    VMIndex       = "16"
  })
}

resource "azurerm_network_interface" "vm-016" {
  name                = "nic-vm-016"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-016"
    VMOwner       = "Shared Service Name"
    VMEnvironment = "dev"
  })
}

# VM 17: vm-017
resource "azurerm_linux_virtual_machine" "vm-017" {
  name                = "vm-017"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-017.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-017"
    VMOwner       = "IT Cost Center ID"
    VMEnvironment = "dev"
    VMIndex       = "17"
  })
}

resource "azurerm_network_interface" "vm-017" {
  name                = "nic-vm-017"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-017"
    VMOwner       = "IT Cost Center ID"
    VMEnvironment = "dev"
  })
}

# VM 18: vm-018
resource "azurerm_linux_virtual_machine" "vm-018" {
  name                = "vm-018"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-018.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-018"
    VMOwner       = "IT Domain"
    VMEnvironment = "dev"
    VMIndex       = "18"
  })
}

resource "azurerm_network_interface" "vm-018" {
  name                = "nic-vm-018"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-018"
    VMOwner       = "IT Domain"
    VMEnvironment = "dev"
  })
}

# VM 19: vm-019
resource "azurerm_linux_virtual_machine" "vm-019" {
  name                = "vm-019"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-019.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-019"
    VMOwner       = "Notes"
    VMEnvironment = "dev"
    VMIndex       = "19"
  })
}

resource "azurerm_network_interface" "vm-019" {
  name                = "nic-vm-019"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-019"
    VMOwner       = "Notes"
    VMEnvironment = "dev"
  })
}

# VM 20: vm-020
resource "azurerm_linux_virtual_machine" "vm-020" {
  name                = "vm-020"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-020.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-020"
    VMOwner       = "Segment"
    VMEnvironment = "dev"
    VMIndex       = "20"
  })
}

resource "azurerm_network_interface" "vm-020" {
  name                = "nic-vm-020"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-020"
    VMOwner       = "Segment"
    VMEnvironment = "dev"
  })
}

# VM 21: vm-021
resource "azurerm_linux_virtual_machine" "vm-021" {
  name                = "vm-021"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-021.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-021"
    VMOwner       = "Line of Business"
    VMEnvironment = "dev"
    VMIndex       = "21"
  })
}

resource "azurerm_network_interface" "vm-021" {
  name                = "nic-vm-021"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-021"
    VMOwner       = "Line of Business"
    VMEnvironment = "dev"
  })
}

# VM 22: vm-022
resource "azurerm_linux_virtual_machine" "vm-022" {
  name                = "vm-022"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-022.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-022"
    VMOwner       = "Department"
    VMEnvironment = "dev"
    VMIndex       = "22"
  })
}

resource "azurerm_network_interface" "vm-022" {
  name                = "nic-vm-022"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-022"
    VMOwner       = "Department"
    VMEnvironment = "dev"
  })
}

# VM 23: vm-023
resource "azurerm_linux_virtual_machine" "vm-023" {
  name                = "vm-023"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [
    azurerm_network_interface.vm-023.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-023"
    VMOwner       = "Cost Center ID"
    VMEnvironment = "dev"
    VMIndex       = "23"
  })
}

resource "azurerm_network_interface" "vm-023" {
  name                = "nic-vm-023"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(azurerm_resource_group.main.tags, {
    VMName        = "vm-023"
    VMOwner       = "Cost Center ID"
    VMEnvironment = "dev"
  })
}
