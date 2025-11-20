"""
HCL Formatter for Terraform tfvars files.
Formats output to match the exact style with aligned = signs.
"""

from typing import Any, Dict, List


class HCLFormatter:
    """Format Python dictionaries as HCL with proper alignment and spacing."""

    def __init__(self):
        # Alignment width for top-level variables (before the = sign)
        self.top_level_align = 28
        # Alignment width for nested variables
        self.nested_align = 35

    def format(self, data: Dict[str, Any]) -> str:
        """
        Format dictionary as HCL terraform.tfvars content.

        Args:
            data: Dictionary of variable names to values

        Returns:
            HCL-formatted string
        """
        lines = []

        # Order of variables
        var_order = [
            'spn',
            'location',
            'resource_group_name',
            'application_security_groups',
            'disk_encryption_set_name',
            'user_assigned_identity_name',
            'key_vault',
            'diagnostic_setting',
            'existing_subnets',
            'private_endpoints',
            'network_security_rules',
            'vm_list',
            'common_tags',
            'resource_specific_tags',
        ]

        for var_name in var_order:
            if var_name in data:
                value = data[var_name]
                formatted = self._format_variable(var_name, value, is_top_level=True)
                lines.append(formatted)

        # Add any remaining variables not in the order list
        for var_name, value in data.items():
            if var_name not in var_order:
                formatted = self._format_variable(var_name, value, is_top_level=True)
                lines.append(formatted)

        return "\n".join(lines)

    def _format_variable(self, name: str, value: Any, indent: int = 0, is_top_level: bool = False) -> str:
        """Format a single variable with proper alignment."""
        indent_str = "  " * indent

        # Determine alignment width
        if is_top_level:
            # Top-level variables - align at position 28 (or less for short names)
            if isinstance(value, dict):
                # For dict values at top level, no padding needed
                return self._format_dict(name, value, indent)
            else:
                # For simple values, pad the name
                padded_name = name.ljust(self.top_level_align)
                return f"{indent_str}{padded_name}= {self._format_value(value)}"
        else:
            # Nested variables - align at position 35
            if isinstance(value, dict):
                return self._format_dict(name, value, indent)
            else:
                padded_name = name.ljust(self.nested_align)
                return f"{indent_str}{padded_name}= {self._format_value(value)}"

    def _format_dict(self, name: str, value: Dict, indent: int = 0) -> str:
        """Format a dictionary value."""
        indent_str = "  " * indent
        lines = [f"{indent_str}{name} = {{"]

        for key, val in value.items():
            if isinstance(val, dict):
                # Nested dict
                lines.append(f"  {indent_str}{key} = {{")
                for sub_key, sub_val in val.items():
                    formatted = self._format_nested_field(sub_key, sub_val, indent + 2)
                    lines.append(formatted)
                lines.append(f"  {indent_str}}}")
            else:
                # Simple value in dict
                formatted = self._format_nested_field(key, val, indent + 1)
                lines.append(formatted)

        lines.append(f"{indent_str}}}")
        return "\n".join(lines)

    def _format_nested_field(self, name: str, value: Any, indent: int) -> str:
        """Format a nested field with alignment."""
        indent_str = "  " * indent

        if value is None:
            padded = name.ljust(self.nested_align)
            return f"{indent_str}{padded}= null"

        if isinstance(value, bool):
            padded = name.ljust(self.nested_align)
            return f"{indent_str}{padded}= {str(value).lower()}"

        if isinstance(value, (int, float)):
            padded = name.ljust(self.nested_align)
            return f"{indent_str}{padded}= {value}"

        if isinstance(value, str):
            padded = name.ljust(self.nested_align)
            escaped = value.replace('"', '\\"')
            return f"{indent_str}{padded}= \"{escaped}\""

        if isinstance(value, list):
            padded = name.ljust(self.nested_align)
            return f"{indent_str}{padded}= {self._format_list(value)}"

        if isinstance(value, dict):
            # For nested dicts within dicts
            return self._format_dict(name, value, indent)

        # Fallback
        padded = name.ljust(self.nested_align)
        return f"{indent_str}{padded}= {str(value)}"

    def _format_value(self, value: Any) -> str:
        """Format a value without the variable name."""
        if value is None:
            return "null"

        if isinstance(value, bool):
            return str(value).lower()

        if isinstance(value, (int, float)):
            return str(value)

        if isinstance(value, str):
            # Special handling for location - uppercase
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'

        if isinstance(value, list):
            return self._format_list(value)

        return str(value)

    def _format_list(self, items: List) -> str:
        """Format a list value."""
        if not items:
            return "[]"

        formatted_items = []
        for item in items:
            if isinstance(item, str):
                formatted_items.append(f'"{item}"')
            elif isinstance(item, bool):
                formatted_items.append(str(item).lower())
            elif item is None:
                formatted_items.append('null')
            else:
                formatted_items.append(str(item))

        return f"[{', '.join(formatted_items)}]"
