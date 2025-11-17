spn      = "spn-terraform-devops_dev_qa"
location = "WEST US 3"
#abbreviated_app_name                             = "terra" #15 characters or less
resource_group_name = "rg-base-vm-module-test"
application_security_groups = {
  asg_nic = {
    name = "asg-base-vm-module-nic-test"
  }
  asg_pe = {
    name = "asg-base-vm-module-pe-test"
  }
}

disk_encryption_set_name    = "dsk-base-vm-module-test"
user_assigned_identity_name = "umid-base-vm-module-test"
key_vault = {
  name                       = "kvlt-base-vm-module-test"
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-base-vm-test"
}

#existing_subnets = {
#  snet1 = {
#    resource_group_name         = "rg-devops_dev_qa-networking"
#    virtual_network_name        = "vnet-devops_dev_qa"
#    name                        = "snet-base-vm-module-test"
#  }
#}

subnets = {
  snet1 = {
    resource_group_name  = "rg-devops_dev_qa-networking"
    virtual_network_name = "vnet-devops_dev_qa"
    network_security_group_id   = "/subscriptions/6f5e4da6-a73e-4795-8e57-49bdfaed7724/resourceGroups/rg-devops_dev_qa-networking/providers/Microsoft.Network/networkSecurityGroups/nsg-devops_dev_qa"
    #network_security_group_name = "nsg-devops_dev_qa"
    route_table_id              = "/subscriptions/6f5e4da6-a73e-4795-8e57-49bdfaed7724/resourceGroups/rg-devops_dev_qa-networking/providers/Microsoft.Network/routeTables/rt-devops_dev_qa"
    #route_table_name  = "rt-devops_dev_qa"
    name              = "snet-base-vm-module-test"
    prefixes          = ["10.187.18.128/29"]
    service_endpoints = ["Microsoft.KeyVault"]
  }
}
private_endpoints = {
  pe_kvlt = {
    name                           = "pvep-kvlt-base-vm-module-test"
    subresource_names              = ["vault"]
    snet_key                       = "snet1"
    asg_key                        = "asg_pe"
  }
}

network_security_rules = {
  resource_group_name         = "rg-devops_dev_qa-networking"
  network_security_group_name = "nsg-devops_dev_qa"
  rules = [
    {
      #name                         = ""
      #or
      source_name                = "Source"
      destination_name           = "Dest"
      priority                   = 140
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_ranges    = ["443"]
      source_asg_keys            = ["asg_nic"]
      destination_asg_keys       = ["asg_pe"]
      #source_address_prefix      = "10.187.18.128/29"
      #destination_address_prefix = "10.187.18.128/29"
      description                = "Module Testing"
    },
    {
      name = "RITM0086216-Outbound-DEV-Allow-DesttoSource"
      #or
      #source_name                  = "Source"
      #destination_name             = "Dest"
      priority                   = 140
      direction                  = "Outbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_ranges    = ["443"]
      source_address_prefix      = "10.187.18.128/29"
      destination_address_prefix = "10.187.18.128/29"
      description                = "Module Testing"
    }
  ]
}

vm_list = {
  vm1 = {
    name              = "azw-basevmwd01"
    size              = "Standard_B2s_v2"
    zone              = null
    image_os          = "windows"
    marketplace_image = false
    #\image_urn       = "center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l1-gen2:latest"
    image_urn     = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
    ip_allocation = "Static"
    ip_address    = "10.187.18.134"
    identity_type = "SystemAssigned, UserAssigned"
    #os_disk_name    = "OSDisk01-123456"
    os_disk_size = 128 #If this is smaller than the vm image it will fail
    os_disk_type = "Standard_LRS"
    os_disk_tier = null
    #data_disks = {
    #  1 = {
    #    name = "dataDisk01-123456"
    #    size = 150
    #    type = "Standard_LRS"
    #    tier = null
    #  }
    #  2 = {
    #    name = "dataDisk02-123456"
    #    size = 150
    #    type = "Standard_LRS"
    #    tier = null
    #  }
    #}
    data_disk_sizes = [50, 50]
    data_disk_type  = "Standard_LRS"
    snet_key        = "snet1"
    asg_key         = "asg_nic"
    tags = {
      "role"        = "Test",
      "patch-optin" = "NO"
    }
  }
  vm2 = {
    name              = "azw-basevmwd02"
    size              = "Standard_B2s_v2"
    zone              = null
    image_os          = "windows"
    marketplace_image = false
    source_image_id = "/subscriptions/6f5e4da6-a73e-4795-8e57-49bdfaed7724/resourceGroups/rg-packer-dev/providers/Microsoft.Compute/galleries/PackerDev/images/Packer-windows-cis-L1"
    #image_urn       = "center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l1-gen2:latest"
    #image_urn     = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
    ip_allocation = "Dynamic"
    identity_type = "SystemAssigned, UserAssigned"
    os_disk_size  = 128 #If this is smaller than the vm image it will fail
    os_disk_type  = "Standard_LRS"
    os_disk_tier  = null
    snet_key      = "snet1"
    asg_key       = "asg_nic"
    tags = {
      "role"        = "Test",
      "patch-optin" = "NO",
      "snow-item"   = "RITM000000"
    }
  }
}

common_tags = {
  "shared-service-name" = "NA",
  "app-name"            = "Terraform Cloud",
  "environment"         = "DEV",
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "Bronze",
  "snow-item"           = "RITM0086216",
  "it-cost-center"      = "5541",
  "it-domain"           = "Platform Engineering",
  #"notes"               = "",
  #"segment"             = "NA",
  "lineofbusiness"      = "Amerihome Mortgage",
  "department"          = "Cloud Engineering",
  "cost-center"         = "6500"
}
