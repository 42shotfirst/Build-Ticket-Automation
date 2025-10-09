#!/usr/bin/env python3
"""
Configuration file for Excel to JSON Converter
=============================================
Contains all configuration settings for the Excel to JSON conversion process.
"""

import os

# paths
EXCEL_FILE_PATH = None  # Will be determined from sourcefiles directory
EXCEL_INPUT_DIRECTORY = "sourcefiles"  # Directory containing Excel files to process
TERRAFORM_JSON_PATH = "terraform_variables.json"  # Output path for Terraform JSON

# options
DEBUG_MODE = True  # Enable debug output and verbose logging
INCLUDE_METADATA = True  # Include metadata in generated JSON
INCLUDE_GENERATION_TIMESTAMP = True  # Include generation timestamp in tags
JSON_INDENT = 2  # JSON indentation level
JSON_SORT_KEYS = False  # Sort JSON keys alphabetically
SKIP_EMPTY_VMS = True  # Skip VM entries that don't have hostnames

# azure defaults
DEFAULT_AZURE_REGION = "East US"
DEFAULT_VM_SIZE = "Standard_D2s_v3"
DEFAULT_OS_IMAGE = "Ubuntu 22.04 LTS"
DEFAULT_ADMIN_USERNAME = "azureuser"

# default tags
DEFAULT_TAGS = {
    "CreatedBy": "Excel-to-JSON-Converter",
    "Environment": "Development",
    "Project": "Infrastructure-Automation",
    "ManagedBy": "Terraform"
}

# field mappings
EXCEL_TO_TERRAFORM_MAPPING = {
    # overview mappings
    "Project Name": "project_name",
    "Abbreviated App Name": "application_name", 
    "Application Description": "app_description",
    "Application Tier": "app_tier",
    "App Owner": "app_owner",
    "Business Owner": "business_owner",
    "Service Now Ticket": "service_now_ticket",
    "Environments": "environments"
}

# defaults
DEFAULT_VALUES = {
    "project_name": "Default Project",
    "application_name": "default-app",
    "app_description": "No description provided",
    "app_tier": "Bronze",
    "app_owner": "TBD",
    "business_owner": "TBD",
    "service_now_ticket": "TBD",
    "environments": "dev"
}

# required fields
REQUIRED_OVERVIEW_FIELDS = [
    "project_name",
    "application_name", 
    "app_owner"
]

def normalize_resource_name(name: str) -> str:
    """
    Normalize a resource name to be compatible with Azure naming conventions.
    
    Args:
        name: The name to normalize
        
    Returns:
        Normalized name suitable for Azure resources
    """
    if not name:
        return "default-resource"
    
    # normalize to lowercase with hyphens
    normalized = str(name).lower().strip()
    normalized = normalized.replace(' ', '-')
    normalized = normalized.replace('_', '-')
    
    # strip special chars
    import re
    normalized = re.sub(r'[^a-z0-9-]', '', normalized)
    
    # remove duplicate hyphens
    normalized = re.sub(r'-+', '-', normalized)
    
    # trim hyphens
    normalized = normalized.strip('-')
    
    # validate length
    if not normalized:
        normalized = "default-resource"
    elif len(normalized) > 60:  # Azure resource name limit
        normalized = normalized[:60].rstrip('-')
    
    return normalized

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # validate input dir
    if not os.path.exists(EXCEL_INPUT_DIRECTORY):
        errors.append(f"Excel input directory not found: {EXCEL_INPUT_DIRECTORY}")
    elif not os.path.isdir(EXCEL_INPUT_DIRECTORY):
        errors.append(f"Excel input path is not a directory: {EXCEL_INPUT_DIRECTORY}")
    
    # validate output dir
    output_dir = os.path.dirname(TERRAFORM_JSON_PATH) or '.'
    if not os.access(output_dir, os.W_OK):
        errors.append(f"Cannot write to output directory: {output_dir}")
    
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

if __name__ == "__main__":
    """Test configuration."""
    print("Configuration Test")
    print("=" * 50)
    print(f"Excel input directory: {EXCEL_INPUT_DIRECTORY}")
    print(f"Output file: {TERRAFORM_JSON_PATH}")
    print(f"Debug mode: {DEBUG_MODE}")
    print(f"Include metadata: {INCLUDE_METADATA}")
    print()
    
    if validate_config():
        print("SUCCESS: Configuration is valid")
        # list excel files
        if os.path.exists(EXCEL_INPUT_DIRECTORY):
            excel_files = [f for f in os.listdir(EXCEL_INPUT_DIRECTORY) 
                          if f.endswith(('.xlsx', '.xlsm', '.xls')) and not f.startswith('~$')]
            if excel_files:
                print(f"\nFound {len(excel_files)} Excel file(s):")
                for f in excel_files:
                    print(f"  - {f}")
            else:
                print("\nWARNING: No Excel files found in the input directory")
    else:
        print("ERROR: Configuration has errors")
