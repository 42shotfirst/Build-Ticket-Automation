locals {
  merge_common_tags = merge(var.default_common_tags, { for key, value in var.common_tags : key => coalesce(value, lookup(var.default_common_tags, key, "")) })
}

locals {
  common_tags = {
    for tag, value in local.merge_common_tags : "wab:${tag}" => value
  }
}

locals {
  resource_specific_tags = {
    for tag, value in var.resource_specific_tags : "wab:${tag}" => value
  }
}
