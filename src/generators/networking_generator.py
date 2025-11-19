"""
Networking Generator

Generates networking terraform files from Build_ENV data:
- networking.tf (general networking resources)
- r-snet.tf (subnet resources)
- r-asg.tf (application security groups)
- Adds subnet/ASG sections to terraform.tfvars
"""

from typing import Dict, Any, List, Optional
import os


class NetworkingGenerator:
    """Generates networking terraform files."""

    def __init__(self, build_env_data: Dict[str, Any]):
        """
        Initialize generator with extracted data.

        Args:
            build_env_data: Data from BuildEnvExtractor
        """
        self.build_env = build_env_data

    def generate(self, output_dir: str) -> Dict[str, str]:
        """
        Generate all networking files.

        Args:
            output_dir: Directory to write files to

        Returns:
            Dictionary mapping filenames to their content
        """
        os.makedirs(output_dir, exist_ok=True)

        files = {
            'r-snet.tf': self._generate_r_snet_tf(),
            'r-asg.tf': self._generate_r_asg_tf(),
            'networking.tf': self._generate_networking_tf(),
        }

        # Write files
        for filename, content in files.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)

        return files

    def _generate_r_snet_tf(self) -> str:
        """Generate r-snet.tf for subnet resources."""
        content = '''resource "azurerm_subnet" "snet" {
  for_each = coalesce(var.subnets, {})

  name                 = each.value.name
  address_prefixes     = each.value.prefixes
  resource_group_name  = each.value.resource_group_name
  service_endpoints    = each.value.service_endpoints
  virtual_network_name = each.value.virtual_network_name
}

resource "azurerm_subnet_network_security_group_association" "nsg" {
  for_each  = coalesce(var.subnets, {})
  subnet_id = azurerm_subnet.snet[each.key].id
  network_security_group_id = coalesce(
    try(each.value.network_security_group_id, null),
    try(data.azurerm_network_security_group.nsg[each.key].id, null)
  )
}

resource "azurerm_subnet_route_table_association" "rta" {
  for_each  = coalesce(var.subnets, {})
  subnet_id = azurerm_subnet.snet[each.key].id
  route_table_id = coalesce(
    try(each.value.route_table_id, null),
    try(data.azurerm_route_table.rt[each.key].id, null)
  )
}
'''
        return content

    def _generate_r_asg_tf(self) -> str:
        """Generate r-asg.tf for application security groups."""
        content = '''resource "azurerm_application_security_group" "asg" {
  for_each            = var.application_security_groups
  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tags = merge(
    tomap(
      { "wab:resource-name" = "${each.value.name}" }
    ),
    local.common_tags, local.resource_specific_tags
  )
}

resource "azurerm_network_interface_application_security_group_association" "asg_nic" {
  #For each vm that is created attach the nic of the vm to an asg. Use the asg key in the list of vm to find the asg to attach it to
  for_each                      = module.vm
  network_interface_id          = each.value.network_interface_id
  application_security_group_id = azurerm_application_security_group.asg[var.vm_list[each.key].asg_key].id
}

resource "azurerm_private_endpoint_application_security_group_association" "asg_pe" {
  #For each private endpoint attach an asg. Use the asg key in the list of private endpoints to find the asg to attach it to
  for_each                      = var.private_endpoints
  private_endpoint_id           = azurerm_private_endpoint.pe[each.key].id
  application_security_group_id = azurerm_application_security_group.asg[var.private_endpoints[each.key].asg_key].id
}
'''
        return content

    def _generate_networking_tf(self) -> str:
        """Generate networking.tf for general networking resources."""
        content = '''# Networking resources

resource "azurerm_private_endpoint" "pe" {
  for_each            = var.private_endpoints
  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  subnet_id = coalesce(
    try(azurerm_subnet.snet[each.value.snet_key].id, null),
    try(data.azurerm_subnet.snet[each.value.snet_key].id, null)
  )

  private_service_connection {
    name                           = "${each.value.name}-connection"
    private_connection_resource_id = coalesce(each.value.private_connection_resource_id, azurerm_key_vault.kvlt.id)
    is_manual_connection           = false
    subresource_names              = each.value.subresource_names
  }

  dynamic "private_dns_zone_group" {
    for_each = each.value.private_dns_zone_ids != null ? [1] : []
    content {
      name                 = coalesce(each.value.private_dns_zone_group_name, "default")
      private_dns_zone_ids = each.value.private_dns_zone_ids
    }
  }

  tags = merge(
    tomap(
      { "wab:resource-name" = each.value.name }
    ),
    local.common_tags, local.resource_specific_tags
  )
}
'''
        return content

    def get_tfvars_content(self) -> Dict[str, Any]:
        """
        Get terraform.tfvars content for networking resources.

        Returns:
            Dictionary of variable names to values
        """
        tfvars = {}

        # Application Security Groups
        asgs = self.build_env.get('application_security_groups', [])
        if asgs:
            asg_map = {}
            for idx, asg in enumerate(asgs, 1):
                # Use keys like asg_nic, asg_pe, asg1, asg2, etc.
                asg_name = asg.get('name', '')
                if 'nic' in asg_name.lower():
                    key = 'asg_nic'
                elif 'pe' in asg_name.lower() or 'kvlt' in asg_name.lower():
                    key = 'asg_pe'
                else:
                    key = f'asg{idx}'

                asg_map[key] = {
                    'name': asg_name
                }

            if asg_map:
                tfvars['application_security_groups'] = asg_map

        # Subnets
        subnets = self.build_env.get('subnets', [])
        if subnets:
            subnet_map = {}
            for idx, subnet in enumerate(subnets, 1):
                key = f'snet{idx}'

                # Get prefixes and ensure it's a list
                prefixes = subnet.get('prefixes', [])
                if isinstance(prefixes, str):
                    prefixes = [prefixes] if prefixes else []

                # Get service endpoints and ensure it's a list
                service_endpoints = subnet.get('service_endpoints', [])
                if isinstance(service_endpoints, str):
                    service_endpoints = [service_endpoints] if service_endpoints else []

                subnet_config = {
                    'resource_group_name': subnet.get('resource_group_name'),
                    'virtual_network_name': subnet.get('virtual_network_name'),
                    'name': subnet.get('name'),
                    'prefixes': prefixes,
                    'service_endpoints': service_endpoints,
                }

                # Optional fields
                nsg_name = subnet.get('network_security_group_name')
                nsg_id = subnet.get('network_security_group_id')
                rt_name = subnet.get('route_table_name')
                rt_id = subnet.get('route_table_id')

                if nsg_name:
                    subnet_config['network_security_group_name'] = nsg_name
                if nsg_id:
                    subnet_config['network_security_group_id'] = nsg_id
                if rt_name:
                    subnet_config['route_table_name'] = rt_name
                if rt_id:
                    subnet_config['route_table_id'] = rt_id

                subnet_map[key] = subnet_config

            if subnet_map:
                tfvars['subnets'] = subnet_map

        # Private Endpoints
        private_endpoints = self.build_env.get('private_endpoints', [])
        if private_endpoints:
            pe_map = {}
            for idx, pe in enumerate(private_endpoints, 1):
                # Use key like pe_kvlt, pe1, pe2, etc.
                pe_name = pe.get('name', '')
                if 'kvlt' in pe_name.lower():
                    key = 'pe_kvlt'
                else:
                    key = f'pe{idx}'

                # Get subresource_names and ensure it's a list
                subresource_names = pe.get('subresource_names', [])
                if isinstance(subresource_names, str):
                    subresource_names = [subresource_names] if subresource_names else []

                pe_config = {
                    'name': pe_name,
                    'subresource_names': subresource_names,
                    'snet_key': pe.get('snet_key', 'snet1'),
                    'asg_key': pe.get('asg_key', 'asg_pe'),
                }

                # Optional fields
                resource_id = pe.get('private_connection_resource_id')
                is_manual = pe.get('is_manual_connection')
                dns_group = pe.get('private_dns_zone_group_name')
                dns_zones = pe.get('private_dns_zone_ids')

                if resource_id:
                    pe_config['private_connection_resource_id'] = resource_id
                if is_manual:
                    pe_config['is_manual_connection'] = is_manual
                if dns_group:
                    pe_config['private_dns_zone_group_name'] = dns_group
                if dns_zones:
                    pe_config['private_dns_zone_ids'] = dns_zones

                pe_map[key] = pe_config

            if pe_map:
                tfvars['private_endpoints'] = pe_map

        return tfvars
