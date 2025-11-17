resource "random_password" "password" {
  #Create a random password if one is not given
  count            = var.admin_password != null ? 0 : 1
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}
