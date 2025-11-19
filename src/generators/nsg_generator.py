"""
NSG Generator

Generates network security group rules section for terraform.tfvars from NSG sheet data.
"""

from typing import Dict, Any, List, Optional


class NSGGenerator:
    """Generates NSG rules configuration for terraform.tfvars."""

    def __init__(self, nsg_data: Dict[str, Any], build_env_data: Dict[str, Any]):
        """
        Initialize generator with extracted data.

        Args:
            nsg_data: Data from NSGExtractor
            build_env_data: Data from BuildEnvExtractor (for RG and NSG names)
        """
        self.nsg_data = nsg_data
        self.build_env = build_env_data

    def get_tfvars_content(self) -> Dict[str, Any]:
        """
        Get terraform.tfvars content for NSG rules.

        Returns:
            Dictionary with 'network_security_rules' key
        """
        tfvars = {}

        rules = self.nsg_data.get('rules', [])
        if not rules:
            return tfvars

        # Get resource group and NSG names from build_env
        # These might come from metadata or need to be calculated
        rg_name = self.build_env.get('resource_group', {}).get('name')

        # Try to find NSG name from subnets
        nsg_name = None
        subnets = self.build_env.get('subnets', [])
        if subnets and len(subnets) > 0:
            nsg_name = subnets[0].get('network_security_group_name')

        # Format rules for terraform
        formatted_rules = []
        for idx, rule in enumerate(rules):
            formatted_rule = {
                'name': rule.get('name', f'rule_{idx}'),
                'priority': self._to_int(rule.get('priority', 100 + idx * 10)),
                'direction': rule.get('direction', 'Inbound'),
                'access': rule.get('access', 'Allow'),
                'protocol': rule.get('protocol', 'Tcp'),
            }

            # Description
            desc = rule.get('description')
            if desc:
                formatted_rule['description'] = desc

            # Source port
            src_port = rule.get('source_port_range') or rule.get('source_port_ranges')
            if isinstance(src_port, list):
                if len(src_port) == 1:
                    formatted_rule['source_port_range'] = str(src_port[0])
                else:
                    formatted_rule['source_port_ranges'] = [str(p) for p in src_port]
            elif src_port:
                formatted_rule['source_port_range'] = str(src_port)
            else:
                formatted_rule['source_port_range'] = '*'

            # Destination port
            dst_port = rule.get('destination_port_range') or rule.get('destination_port_ranges')
            if isinstance(dst_port, list):
                if len(dst_port) == 1:
                    formatted_rule['destination_port_range'] = str(dst_port[0])
                else:
                    formatted_rule['destination_port_ranges'] = [str(p) for p in dst_port]
            elif dst_port:
                formatted_rule['destination_port_range'] = str(dst_port)

            # Source address/prefix
            src_addr = rule.get('source_address_prefix') or rule.get('source_address_prefixes')
            if isinstance(src_addr, list):
                formatted_rule['source_address_prefixes'] = [str(a) for a in src_addr]
            elif src_addr:
                formatted_rule['source_address_prefix'] = str(src_addr)

            # Destination address/prefix
            dst_addr = rule.get('destination_address_prefix') or rule.get('destination_address_prefixes')
            if isinstance(dst_addr, list):
                formatted_rule['destination_address_prefixes'] = [str(a) for a in dst_addr]
            elif dst_addr:
                formatted_rule['destination_address_prefix'] = str(dst_addr)

            # Application Security Groups
            src_asg = rule.get('source_asg_keys')
            if src_asg:
                if not isinstance(src_asg, list):
                    src_asg = [src_asg]
                formatted_rule['source_asg_keys'] = src_asg
                formatted_rule['source_name'] = src_asg[0] if src_asg else None

            dst_asg = rule.get('destination_asg_keys')
            if dst_asg:
                if not isinstance(dst_asg, list):
                    dst_asg = [dst_asg]
                formatted_rule['destination_asg_keys'] = dst_asg
                formatted_rule['destination_name'] = dst_asg[0] if dst_asg else None

            # SNOW item
            snow_item = rule.get('snow-item') or rule.get('snow_item')
            if snow_item:
                formatted_rule['snow-item'] = snow_item

            formatted_rules.append(formatted_rule)

        # Build the network_security_rules object
        if formatted_rules:
            tfvars['network_security_rules'] = {
                'resource_group_name': rg_name,
                'network_security_group_name': nsg_name,
                'rules': formatted_rules
            }

        return tfvars

    def _to_int(self, value: Any) -> int:
        """Convert value to int, handling strings and None."""
        if value is None:
            return 100
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 100
        return 100
