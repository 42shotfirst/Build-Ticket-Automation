# Begin terraform.tfvars

spn      = "spn-terraform-bob"
location = "WEST US 3"
resource_group_name = "rsg1"

application_security_groups = {
  asg_nic = {
    name = "asg-bob-nic-uat"
  }
  asg_pe = {
    name = "asg-bob-pe-uat"
  }
}

disk_encryption_set_name    = "dsk-bob-uat"
user_assigned_identity_name = "umid-bob-uat"

key_vault = {
  name                       = "kvlt-bob-uat"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-bob-uat"
}

subnets = {
  snet1 = {
    resource_group_name  = "rsg1-networking"
    virtual_network_name = "vnet-bob-uat"
    network_security_group_id   = "/subscriptions/YOUR-AZURE-SUBSCRIPTION-ID/resourceGroups/rsg1-networking/providers/Microsoft.Network/networkSecurityGroups/nsg-bob-uat"  # TODO: Update with actual Azure subscription ID
    route_table_id              = "/subscriptions/YOUR-AZURE-SUBSCRIPTION-ID/resourceGroups/rsg1-networking/providers/Microsoft.Network/routeTables/rt-bob-uat"  # TODO: Update with actual Azure subscription ID
    name              = "snet-bob-uat"
    prefixes          = ["10.0.1.0/24"]
    service_endpoints = ["Microsoft.KeyVault"]
  }
}

private_endpoints = {
  pe_kvlt = {
    name                           = "pvep-kvlt-bob-uat"
    subresource_names              = ["vault"]
    snet_key                       = "snet1"
    asg_key                        = "asg_pe"
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
      "patch-optin" = "NO",
      "snow-item"   = "1"
    }
  }
}

network_security_rules = {
  resource_group_name         = "rsg1-networking"
  network_security_group_name = "nsg-bob-uat"
  rules = [
    {
      name                       = "one"
      source_name                = "Source"
      destination_name           = "Destination"
      priority                   = 100
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "1"
      destination_port_ranges    = ["5"]
      source_asg_keys            = ["asg_nic"]
      destination_asg_keys       = ["asg_pe"]
      description                = "25"
    },
    {
      name                       = "two"
      source_name                = "Source"
      destination_name           = "Destination"
      priority                   = 110
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "2"
      destination_port_ranges    = ["6"]
      source_asg_keys            = ["asg_nic"]
      destination_asg_keys       = ["asg_pe"]
      description                = "26"
    },
    {
      name                       = "three"
      source_name                = "Source"
      destination_name           = "Destination"
      priority                   = 120
      direction                  = "Outbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "3"
      destination_port_ranges    = ["7"]
      source_asg_keys            = ["asg_nic"]
      destination_asg_keys       = ["asg_pe"]
      description                = "27"
    },
    {
      name                       = "four"
      source_name                = "Source"
      destination_name           = "Destination"
      priority                   = 130
      direction                  = "Outbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "4"
      destination_port_ranges    = ["8"]
      source_asg_keys            = ["asg_nic"]
      destination_asg_keys       = ["asg_pe"]
      description                = "28"
    }
  ]
}

common_tags = {
  "shared-service-name" = "NA",
  "app-name"            = "bob",
  "environment"         = "UAT",
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "Bronze",
  "snow-item"           = "1",
  "it-cost-center"      = "NA",
  "it-domain"           = "Platform Engineering",
  "lineofbusiness"      = "TBD",
  "department"          = "Cloud Engineering",
  "cost-center"         = "TBD"
}
