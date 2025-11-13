# terraform.tfvars
# Generated from Excel data extraction

# Service Principal
spn = "spn-bob-uat"

# Location
location = "West US 3"

# Resource Group
resource_group_name = "rsg1"

# Application Security Groups
application_security_groups = {
  asg_nic = {
    name = "asg-bob-nic-uat"
  },
  asg_pe = {
    name = "asg-bob-pe-uat"
  }
}

# Key Vault Configuration
key_vault = {
  name                       = "kv-bob-uat"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-bob-uat"
}

# Identity and Encryption
user_assigned_identity_name = "id-bob-uat"
disk_encryption_set_name    = "des-bob-uat"

# Admin credentials
admin_username = "cisadmin"
# admin_password = "CHANGE-ME-IN-KEYVAULT"  # Store in Key Vault, not in code

# Subnet Configuration
subnets = {
  snet1 = {
    resource_group_name  = "rsg1-network"
    virtual_network_name = "vnet-bob-uat"
    network_security_group_id = "/subscriptions/YOUR-AZURE-SUBSCRIPTION-ID/resourceGroups/rsg1-network/providers/Microsoft.Network/networkSecurityGroups/nsg-bob-uat"  # TODO: Update with actual Azure subscription ID
    route_table_id            = "/subscriptions/YOUR-AZURE-SUBSCRIPTION-ID/resourceGroups/rsg1-network/providers/Microsoft.Network/routeTables/rt-bob-uat"  # TODO: Update with actual Azure subscription ID
    name              = "snet-bob-uat"
    prefixes          = ["10.0.1.0/24"]
    service_endpoints = ["Microsoft.KeyVault"]
  }
}

# Private Endpoints
private_endpoints = {
  pe_kvlt = {
    name              = "pe-kv-bob-uat"
    subresource_names = ["vault"]
    snet_key          = "snet1"
    asg_key           = "asg_pe"
  }
}

# Virtual Machines
vm_list = {
  vm1 = {
    name              = "vm-rsg1-01"
    size              = "Standard_B2s"
    zone              = null
    image_os          = "windows"
    marketplace_image = false
    image_urn         = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
    ip_allocation     = "Static"
    identity_type     = "SystemAssigned, UserAssigned"
    os_disk_size      = 10
    os_disk_type      = "StandardSSD_LRS"
    os_disk_tier      = null
    data_disk_sizes   = [50, 50]
    data_disk_type    = "Standard_LRS"
    snet_key          = "snet1"
    asg_key           = "asg_nic"
    tags = {
      "role"        = "Application",
      "patch-optin" = "YES",
      "snow-item"   = "1"
    }
  }
}

# Network Security Rules
network_security_rules = {
  resource_group_name         = "rsg1-network"
  network_security_group_name = "nsg-bob-uat"
  rules = [
    {
      name                    = "one"
      priority                = 100
      direction               = "Inbound"
      access                  = "Allow"
      protocol                = "Tcp"
      source_port_range       = "1"
      destination_port_ranges = ["5"]
      source_asg              = "9"
      destination_asg         = "13"
      description             = "25"
    },
    {
      name                    = "two"
      priority                = 110
      direction               = "Inbound"
      access                  = "Allow"
      protocol                = "Tcp"
      source_port_range       = "2"
      destination_port_ranges = ["6"]
      source_asg              = "10"
      destination_asg         = "14"
      description             = "26"
    },
    {
      name                    = "three"
      priority                = 120
      direction               = "Outbound"
      access                  = "Allow"
      protocol                = "Tcp"
      source_port_range       = "3"
      destination_port_ranges = ["7"]
      source_asg              = "11"
      destination_asg         = "15"
      description             = "27"
    },
    {
      name                    = "four"
      priority                = 130
      direction               = "Outbound"
      access                  = "Allow"
      protocol                = "Tcp"
      source_port_range       = "4"
      destination_port_ranges = ["8"]
      source_asg              = "12"
      destination_asg         = "16"
      description             = "28"
    }
  ]
}

# Common Tags
common_tags = {
  "app-name"            = "bob",
  "environment"         = "UAT",
  "snow-item"           = "1",
  "managed-by"          = "terraform",
  "cost-center"         = "TBD",
  "department"          = "TBD",
  "line-of-business"    = "TBD"
}

# Resource-specific tags (customize as needed)
resource_specific_tags = {}
