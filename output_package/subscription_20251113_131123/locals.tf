# Begin locals.tf

locals {
  common_tags = {
    for tag, value in var.common_tags : "wab:${tag}" => value
  }
}

locals {
  resource_specific_tags = {
    for tag, value in var.resource_specific_tags : "wab:${tag}" => value
  }
}