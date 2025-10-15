# Begin m-basevm.tf

module "base-vm" {
  source = "app.terraform.io/wab-cloudengineering-org/base-vm/iac"

  # Using a variable for the module version is not supported yet: https://github.com/hashicorp/terraform/issues/28912
  #version                     = var.test_module_version
  version                              = "__DYNAMIC_MODULE_VERSION__"
  spn                                  = var.spn
  location                             = var.location
  resource_group_name                  = var.resource_group_name
  existing_application_security_groups = var.existing_application_security_groups
  application_security_groups          = var.application_security_groups
  key_vault                            = var.key_vault
  user_assigned_identity_name          = var.user_assigned_identity_name
  disk_encryption_set_name             = var.disk_encryption_set_name
  subnets                              = var.subnets
  existing_subnets                     = var.existing_subnets
  private_endpoints                    = var.private_endpoints
  admin_username                       = var.admin_username
  admin_password                       = var.admin_password
  vm_list                              = var.vm_list
  network_security_rules               = var.network_security_rules
  common_tags                          = var.common_tags
  resource_specific_tags               = var.resource_specific_tags
}
