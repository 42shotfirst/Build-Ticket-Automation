#!/usr/bin/env python3
"""
Module 3: Terraform Generator
==============================
Wrapper for the existing enhanced_terraform_generator_v2.py functionality.
This module provides a clean interface while using the proven generator logic.
"""

import os
import sys
from typing import Dict, Any

# Add parent directory to path to import the existing generator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from enhanced_terraform_generator_v2 import EnhancedTerraformGeneratorV2


class TerraformGenerator:
    """
    Wrapper for Terraform file generation.

    This class provides a clean interface to the existing enhanced_terraform_generator_v2.py
    which contains all the proven logic for SPN calculation, resource group naming,
    and complete Terraform file generation.

    The enhanced generator properly:
    - Calculates SPN from Excel Build_ENV sheet or subscription
    - Calculates resource_group_name as "rg-{resource_prefix}-{environment}"
    - References ALL other fields as variables (not hardcoded)
    - Handles null values correctly (keeps them as null when appropriate)
    """

    def __init__(self, json_file_path: str, template_dir: str = "terraform_files_pattern"):
        """
        Initialize the Terraform generator.

        Args:
            json_file_path: Path to the extracted JSON data
            template_dir: Directory containing Terraform templates
        """
        # Use the proven enhanced generator that has all the correct logic
        self.generator = EnhancedTerraformGeneratorV2(json_file_path)
        self.json_file_path = json_file_path

    def generate(self, output_dir: str) -> Dict[str, str]:
        """
        Generate all Terraform files.

        This uses the existing enhanced_terraform_generator_v2.py logic which:
        - Extracts SPN from Build_ENV sheet (keys: 'SPN', 'Service Principal')
        - Falls back to constructing from subscription: 'spn-terraform-{subscription}'
        - Calculates resource_group_name as: 'rg-{resource_prefix}-{environment}'
        - Properly references var.spn in data.tf for service principal lookup
        - Properly references var.resource_group_name in main.tf and other resources
        - All other resources reference these variables, not hardcoded values

        Args:
            output_dir: Directory to write Terraform files

        Returns:
            Dictionary of filename -> content
        """
        files = self.generator.generate_terraform_files(output_dir)
        return files
