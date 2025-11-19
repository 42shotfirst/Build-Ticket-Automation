#!/usr/bin/env python3
"""
Module 3: Terraform Generator
==============================
Generates Terraform files from extracted Excel data.
Consolidates: enhanced_terraform_generator_v2.py, terraform_generator_clean.py
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .data_accessor import DataAccessor


class TerraformGenerator:
    """Generate Terraform configuration files from Excel data."""

    def __init__(self, json_file_path: str, template_dir: str = "terraform_files_pattern"):
        """
        Initialize the Terraform generator.

        Args:
            json_file_path: Path to the extracted JSON data
            template_dir: Directory containing Terraform templates
        """
        self.accessor = DataAccessor(json_file_path)
        self.template_dir = template_dir
        self.terraform_data = self.accessor.get_terraform_ready_data()

    def generate(self, output_dir: str) -> Dict[str, str]:
        """
        Generate all Terraform files.

        Args:
            output_dir: Directory to write Terraform files

        Returns:
            Dictionary of filename -> content
        """
        os.makedirs(output_dir, exist_ok=True)

        files = {}

        # Copy template files
        files.update(self._copy_template_files())

        # Generate terraform.tfvars from data
        files['terraform.tfvars'] = self._generate_tfvars()

        # Write all files
        for filename, content in files.items():
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return files

    def _copy_template_files(self) -> Dict[str, str]:
        """Copy template files to output."""
        files = {}

        template_files = [
            'main.tf', 'variables.tf', 'data.tf', 'locals.tf',
            'outputs.tf', 'networking.tf', 'm-vm.tf',
            'r-asg.tf', 'r-dcra.tf', 'r-dsk.tf', 'r-kvlt.tf',
            'r-rnd.tf', 'r-snet.tf', 'r-umid.tf', 's3.tf'
        ]

        for filename in template_files:
            template_path = os.path.join(self.template_dir, filename)
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    files[filename] = f.read()

        return files

    def _generate_tfvars(self) -> str:
        """Generate terraform.tfvars content from Excel data."""

        # Get key data points from Excel
        spn = self.accessor.get_value_by_keywords('Build_ENV', ['spn', 'service principal']) or 'spn-terraform'
        rg_name = self.accessor.get_value_by_keywords('Resources', ['resource group', 'rg']) or 'rg-default'
        location = self.accessor.get_value_by_keywords('Build_ENV', ['location', 'region']) or 'WEST US 3'

        tfvars_content = f"""# Begin terraform.tfvars

spn      = "{spn}"
location = "{location}"
resource_group_name = "{rg_name}"

application_security_groups = {{
  asg_nic = {{
    name = "asg-app-nic"
  }},
  asg_pe = {{
    name = "asg-app-pe"
  }}
}}

disk_encryption_set_name    = "dsk-encryption"
user_assigned_identity_name = "umid-identity"

key_vault = {{
  name                       = "kvlt-app"
  sku_name                   = "Standard"
  soft_delete_retention_days = 90
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-app"
}}

subnets = {{
  snet1 = {{
    resource_group_name  = "rg-networking"
    virtual_network_name = "vnet-app"
    network_security_group_id   = null
    route_table_id              = null
    name              = "snet-app"
    prefixes          = []
    service_endpoints = ["Microsoft.KeyVault"]
  }}
}}

common_tags = {{
  "shared-service-name" = "NA",
  "app-name"            = "Application",
  "environment"         = "PROD",
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "Bronze",
  "snow-item"           = "RITM0000000",
  "it-cost-center"      = "0000",
  "it-domain"           = "Platform Engineering",
  "lineofbusiness"      = "Organization",
  "department"          = "Engineering",
  "cost-center"         = "0000"
}}
"""
        return tfvars_content
