#!/usr/bin/env python3
"""
Enhanced Terraform Generator
============================
Generates proper Terraform files from Excel data with column referencing and structured output.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from data_accessor import ExcelDataAccessor

class EnhancedTerraformGenerator:
    """Generate Terraform files from Excel data with proper structure and formatting."""
    
    def __init__(self, json_file_path: str):
        """Initialize with JSON file from comprehensive extraction."""
        self.accessor = ExcelDataAccessor(json_file_path)
        self.terraform_data = self.accessor.get_terraform_ready_data()
        
    def generate_terraform_files(self, output_dir: str = "output_package") -> Dict[str, str]:
        """Generate complete deployment package with all necessary files."""
        
        # Create output directory structure
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "docs"), exist_ok=True)
        
        generated_files = {}
        
        # Generate main.tf
        main_tf = self._generate_main_tf()
        main_tf_path = os.path.join(output_dir, "main.tf")
        with open(main_tf_path, 'w', encoding='utf-8') as f:
            f.write(main_tf)
        generated_files['main.tf'] = main_tf_path
        
        # Generate variables.tf
        variables_tf = self._generate_variables_tf()
        variables_tf_path = os.path.join(output_dir, "variables.tf")
        with open(variables_tf_path, 'w', encoding='utf-8') as f:
            f.write(variables_tf)
        generated_files['variables.tf'] = variables_tf_path
        
        # Generate terraform.tfvars
        tfvars = self._generate_tfvars()
        tfvars_path = os.path.join(output_dir, "terraform.tfvars")
        with open(tfvars_path, 'w', encoding='utf-8') as f:
            f.write(tfvars)
        generated_files['terraform.tfvars'] = tfvars_path
        
        # Generate outputs.tf
        outputs_tf = self._generate_outputs_tf()
        outputs_tf_path = os.path.join(output_dir, "outputs.tf")
        with open(outputs_tf_path, 'w', encoding='utf-8') as f:
            f.write(outputs_tf)
        generated_files['outputs.tf'] = outputs_tf_path
        
        # Generate provider.tf
        provider_tf = self._generate_provider_tf()
        provider_tf_path = os.path.join(output_dir, "provider.tf")
        with open(provider_tf_path, 'w', encoding='utf-8') as f:
            f.write(provider_tf)
        generated_files['provider.tf'] = provider_tf_path
        
        # Generate validation script only (for ADO pipeline validation)
        validate_script = self._generate_validate_script()
        validate_script_path = os.path.join(output_dir, "scripts", "validate.sh")
        with open(validate_script_path, 'w', encoding='utf-8') as f:
            f.write(validate_script)
        os.chmod(validate_script_path, 0o755)  # Make executable
        generated_files['scripts/validate.sh'] = validate_script_path
        
        # Generate README.md
        readme = self._generate_readme()
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        generated_files['README.md'] = readme_path
        
        # Generate deployment guide
        deployment_guide = self._generate_deployment_guide()
        deployment_guide_path = os.path.join(output_dir, "docs", "DEPLOYMENT_GUIDE.md")
        with open(deployment_guide_path, 'w', encoding='utf-8') as f:
            f.write(deployment_guide)
        generated_files['docs/DEPLOYMENT_GUIDE.md'] = deployment_guide_path
        
        # Generate .gitignore
        gitignore = self._generate_gitignore()
        gitignore_path = os.path.join(output_dir, ".gitignore")
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore)
        generated_files['.gitignore'] = gitignore_path
        
        # Generate terraform.auto.tfvars.example
        tfvars_example = self._generate_tfvars_example()
        tfvars_example_path = os.path.join(output_dir, "terraform.auto.tfvars.example")
        with open(tfvars_example_path, 'w', encoding='utf-8') as f:
            f.write(tfvars_example)
        generated_files['terraform.auto.tfvars.example'] = tfvars_example_path
        
        return generated_files
    
    def _generate_main_tf(self) -> str:
        """Generate main.tf file with all resources."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        security_groups = self.terraform_data.get('security_groups', [])
        comprehensive_data = self.terraform_data.get('comprehensive_data', {})
        
        print(f"GENERATING COMPREHENSIVE TERRAFORM MAIN.TF")
        print(f"  VM instances: {len(vm_instances)}")
        print(f"  Security groups: {len(security_groups)}")
        print(f"  Comprehensive data sheets: {len(comprehensive_data)}")
        
        # Get project details
        project_name = project_info.get('project_name', 'default-project')
        app_name = project_info.get('application_name', 'default-app')
        location = "East US"  # Default location
        
        # Generate resource group
        main_tf = f'''# Main Terraform configuration
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Resource Group
resource "azurerm_resource_group" "main" {{
  name     = "rg-${{var.project_name}}-${{var.environment}}"
  location = var.location

  tags = {{
    Project     = var.project_name
    Application = var.application_name
    Environment = var.environment
    Owner       = var.app_owner
    CreatedBy   = "Excel-to-Terraform-Generator"
  }}
}}

# Virtual Network
resource "azurerm_virtual_network" "main" {{
  name                = "vnet-${{var.project_name}}-${{var.environment}}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = azurerm_resource_group.main.tags
}}

# Subnet
resource "azurerm_subnet" "main" {{
  name                 = "subnet-${{var.project_name}}-${{var.environment}}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}}

# Network Security Group
resource "azurerm_network_security_group" "main" {{
  name                = "nsg-${{var.project_name}}-${{var.environment}}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = azurerm_resource_group.main.tags
}}

# Network Security Group Rules
'''
        
        # Add NSG rules from Excel data with proper Terraform format
        for i, rule in enumerate(security_groups):
            if rule.get('name') and rule.get('direction'):
                # Sanitize rule name for Terraform
                rule_name = self._sanitize_resource_name(rule.get('name', f'rule_{i}'))
                
                main_tf += f'''
resource "azurerm_network_security_rule" "{rule_name}" {{
  name                        = var.nsg_rules[{i}].name
  priority                    = var.nsg_rules[{i}].priority
  direction                   = var.nsg_rules[{i}].direction
  access                      = var.nsg_rules[{i}].access
  protocol                    = var.nsg_rules[{i}].protocol
  source_port_range           = var.nsg_rules[{i}].source_port_range
  destination_port_range      = var.nsg_rules[{i}].destination_port_range
  source_address_prefix       = var.nsg_rules[{i}].source_address_prefix
  destination_address_prefix  = var.nsg_rules[{i}].destination_address_prefix
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.main.name
}}
'''
        
        # Add Application Gateway if configured
        app_gateway = self.terraform_data.get('application_gateway', {})
        if app_gateway:
            main_tf += self._generate_application_gateway(app_gateway)
        
        # Add Container Registry if configured
        container_registry = self.terraform_data.get('container_registry', {})
        if container_registry:
            main_tf += self._generate_container_registry(container_registry)
        
        # Add Storage Account if configured
        main_tf += self._generate_storage_account()
        
        # Add VM instances - COMPREHENSIVE VM GENERATION
        if vm_instances:
            main_tf += f'''

# Virtual Machines - Comprehensive Generation
# Generated from {len(vm_instances)} VM instances found in Excel data
'''
            
            print(f"  Generating {len(vm_instances)} VM resources...")
            
            for i, vm in enumerate(vm_instances):
                # Extract VM details with comprehensive field mapping
                vm_name = self._extract_vm_name(vm, i)
                vm_size = self._extract_vm_size(vm)
                os_image = self._extract_os_image(vm)
                vm_owner = self._extract_vm_owner(vm)
                vm_environment = self._extract_vm_environment(vm)
                
                # Generate unique resource names
                vm_resource_name = self._sanitize_resource_name(vm_name)
                
                main_tf += f'''
# VM {i+1}: {vm_name}
resource "azurerm_linux_virtual_machine" "{vm_resource_name}" {{
  name                = var.vm_names[{i}]
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  disable_password_authentication = true

  admin_ssh_key {{
    username   = var.admin_username
    public_key = var.ssh_public_key
  }}

  network_interface_ids = [
    azurerm_network_interface.{vm_resource_name}.id,
  ]

  os_disk {{
    caching              = "ReadWrite"
    storage_account_type = var.vm_os_disk_type
    disk_size_gb        = var.vm_os_disk_size
  }}

  source_image_reference {{
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = var.vm_image_version
  }}

  tags = merge(azurerm_resource_group.main.tags, {{
    Name        = var.vm_names[{i}]
    Owner       = var.app_owner
    Environment = var.environment
    Index       = {i+1}
    Type        = "Virtual Machine"
  }})
}}

resource "azurerm_network_interface" "{vm_resource_name}" {{
  name                = "nic-${{var.vm_names[{i}]}}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {{
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = var.vm_private_ip_allocation
  }}

  tags = merge(azurerm_resource_group.main.tags, {{
    Name        = "nic-${{var.vm_names[{i}]}}"
    Owner       = var.app_owner
    Environment = var.environment
    Type        = "Network Interface"
  }})
}}
'''
            
            print(f"  Generated {len(vm_instances)} VM resources with comprehensive tagging")
        
        return main_tf
    
    def _generate_variables_tf(self) -> str:
        """Generate variables.tf file."""
        
        project_info = self.terraform_data.get('project_info', {})
        build_env = self.terraform_data.get('build_environment', {})
        naming_patterns = self.terraform_data.get('naming_patterns', {})
        app_gateway = self.terraform_data.get('application_gateway', {})
        container_registry = self.terraform_data.get('container_registry', {})
        
        variables_tf = f'''# Variables for {project_info.get('project_name', 'default-project')}
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Project Configuration
variable "project_name" {{
  description = "Name of the project"
  type        = string
  default     = "{project_info.get('project_name', 'default-project')}"
}}

variable "application_name" {{
  description = "Name of the application"
  type        = string
  default     = "{project_info.get('application_name', 'default-app')}"
}}

variable "environment" {{
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}}

variable "location" {{
  description = "Azure region"
  type        = string
  default     = "East US"
}}

# Build Environment (from Build_ENV sheet)
variable "subscription" {{
  description = "Azure subscription"
  type        = string
  default     = "{build_env.get('key_value_pairs', {}).get('Subscription', 'subscription1')}"
}}

variable "resource_group_key" {{
  description = "Resource group key"
  type        = string
  default     = "{build_env.get('key_value_pairs', {}).get('Key', 'rsg1')}"
}}

# Application Details
variable "app_owner" {{
  description = "Application owner"
  type        = string
  default     = "{project_info.get('app_owner', 'TBD')}"
}}

variable "business_owner" {{
  description = "Business owner"
  type        = string
  default     = "{project_info.get('business_owner', 'TBD')}"
}}

variable "admin_username" {{
  description = "Admin username for VMs"
  type        = string
  default     = "azureuser"
}}

# Infrastructure Configuration
variable "vm_count" {{
  description = "Number of VMs to create"
  type        = number
  default     = {len(self.terraform_data.get('vm_instances', []))}
}}

variable "vm_names" {{
  description = "List of VM names"
  type        = list(string)
  default     = {self._generate_vm_names_list()}
}}

variable "vm_size" {{
  description = "Size of the VMs"
  type        = string
  default     = "Standard_D2s_v3"
}}

variable "vm_os_disk_type" {{
  description = "OS disk type for VMs"
  type        = string
  default     = "Premium_LRS"
}}

variable "vm_os_disk_size" {{
  description = "OS disk size in GB"
  type        = number
  default     = 30
}}

variable "vm_image_publisher" {{
  description = "VM image publisher"
  type        = string
  default     = "Canonical"
}}

variable "vm_image_offer" {{
  description = "VM image offer"
  type        = string
  default     = "0001-com-ubuntu-server-jammy"
}}

variable "vm_image_sku" {{
  description = "VM image SKU"
  type        = string
  default     = "22_04-lts"
}}

variable "vm_image_version" {{
  description = "VM image version"
  type        = string
  default     = "latest"
}}

variable "vm_private_ip_allocation" {{
  description = "Private IP allocation method"
  type        = string
  default     = "Dynamic"
}}

variable "ssh_public_key" {{
  description = "SSH public key for VM access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}}

# Network Configuration
variable "vnet_address_space" {{
  description = "VNet address space"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}}

variable "subnet_address_prefixes" {{
  description = "Subnet address prefixes"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}}

# Network Security Group Rules
variable "nsg_rules" {{
  description = "List of NSG rules"
  type = list(object({{
    name                       = string
    priority                   = number
    direction                  = string
    access                     = string
    protocol                   = string
    source_port_range          = string
    destination_port_range     = string
    source_address_prefix      = string
    destination_address_prefix = string
  }}))
  default = {self._generate_nsg_rules_list()}
}}

# Application Gateway Configuration (from APGW sheet)
variable "app_gateway_sku" {{
  description = "Application Gateway SKU"
  type        = string
  default     = "Standard_v2"
}}

variable "app_gateway_capacity" {{
  description = "Application Gateway capacity"
  type        = number
  default     = 2
}}

variable "app_gateway_port" {{
  description = "Application Gateway port"
  type        = number
  default     = {app_gateway.get('port', 80) if app_gateway.get('port') != 'False' else 80}
}}

variable "app_gateway_protocol" {{
  description = "Application Gateway protocol"
  type        = string
  default     = "{app_gateway.get('protocol', 'Http')}"
}}

# Container Registry Configuration (from ACR NRS sheet)
variable "acr_sku" {{
  description = "Container Registry SKU"
  type        = string
  default     = "Basic"
}}

# Storage Configuration
variable "storage_account_tier" {{
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}}

variable "storage_replication_type" {{
  description = "Storage replication type"
  type        = string
  default     = "LRS"
}}

# Resource Naming Patterns (from Resource Options sheet)
variable "resource_naming_patterns" {{
  description = "Resource naming patterns from Excel"
  type        = map(string)
  default = {{
    Resource_Group = "{naming_patterns.get('Resource_Group', 'rg-appname-env')}"
    Subnet = "{naming_patterns.get('Subnet', 'snet-appname-env')}"
    Network_Security_Group = "{naming_patterns.get('Network_Security_Group', 'nsg-appname-env')}"
    Application_Gateway = "{naming_patterns.get('Application_Gateway', 'appgw-appname-env')}"
    Azure_Container_Registry = "{naming_patterns.get('Azure_Container_Registry', 'acr-appname-env')}"
    Storage_Account = "{naming_patterns.get('Storage_Account', 'st-appname-env')}"
  }}
}}

variable "tags" {{
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {{
    Project     = "{project_info.get('project_name', 'default-project')}"
    Application = "{project_info.get('application_name', 'default-app')}"
    Environment = "dev"
    Owner       = "{project_info.get('app_owner', 'TBD')}"
    CreatedBy   = "Excel-to-Terraform-Generator"
  }}
}}
'''
        
        return variables_tf
    
    def _generate_tfvars(self) -> str:
        """Generate terraform.tfvars file."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        build_env = self.terraform_data.get('build_environment', {})
        app_gateway = self.terraform_data.get('application_gateway', {})
        container_registry = self.terraform_data.get('container_registry', {})
        naming_patterns = self.terraform_data.get('naming_patterns', {})
        
        # Get actual values from the first VM instance if available
        if vm_instances:
            first_vm = vm_instances[0]
            project_name = first_vm.get('Project Name', 'default-project')
            application_name = first_vm.get('Application Name', 'default-app')
            environment = first_vm.get('Environment', 'dev')
            vm_size = first_vm.get('Recommended SKU', 'Standard_D2s_v3')
            app_owner = first_vm.get('Application Owner', 'TBD')
            business_owner = first_vm.get('Business Owner', 'TBD')
            service_now_ticket = first_vm.get('Service Now Ticket', 'TBD')
        else:
            # Fallback to project_info or defaults
            project_name = project_info.get('project_name', 'default-project')
            application_name = project_info.get('application_name', 'default-app')
            environment = project_info.get('environment', 'dev')
            vm_size = project_info.get('vm_size', 'Standard_D2s_v3')
            app_owner = project_info.get('app_owner', 'TBD')
            business_owner = project_info.get('business_owner', 'TBD')
            service_now_ticket = project_info.get('service_now_ticket', 'TBD')
        
        # Get Build Environment values
        subscription = build_env.get('key_value_pairs', {}).get('Subscription', 'subscription1')
        resource_group_key = build_env.get('key_value_pairs', {}).get('Key', 'rsg1')
        
        # Get Application Gateway values
        app_gateway_port = app_gateway.get('port', 80) if app_gateway.get('port') != 'False' else 80
        app_gateway_protocol = app_gateway.get('protocol', 'Http')
        
        tfvars = f'''# Terraform variables file
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Project Configuration
project_name     = "{project_name}"
application_name = "{application_name}"
environment      = "{environment}"
location         = "East US"

# Build Environment (from Build_ENV sheet)
subscription         = "{subscription}"
resource_group_key   = "{resource_group_key}"

# Application Details
app_owner        = "{app_owner}"
business_owner   = "{business_owner}"
admin_username   = "azureuser"

# Infrastructure Configuration
vm_count         = {len(vm_instances)}
vm_names         = {self._generate_vm_names_list()}
vm_size          = "{vm_size}"
vm_os_disk_type  = "Premium_LRS"
vm_os_disk_size  = 30
vm_image_publisher = "Canonical"
vm_image_offer   = "0001-com-ubuntu-server-jammy"
vm_image_sku     = "22_04-lts"
vm_image_version = "latest"
vm_private_ip_allocation = "Dynamic"
ssh_public_key   = "~/.ssh/id_rsa.pub"

# Network Configuration
vnet_address_space      = ["10.0.0.0/16"]
subnet_address_prefixes = ["10.0.1.0/24"]

# Application Gateway Configuration (from APGW sheet)
app_gateway_sku      = "Standard_v2"
app_gateway_capacity = 2
app_gateway_port     = {app_gateway_port}
app_gateway_protocol = "{app_gateway_protocol}"

# Container Registry Configuration (from ACR NRS sheet)
acr_sku = "Basic"

# Storage Configuration
storage_account_tier        = "Standard"
storage_replication_type    = "LRS"

# Resource Naming Patterns (from Resource Options sheet)
resource_naming_patterns = {{
  Resource_Group            = "{naming_patterns.get('Resource_Group', 'rg-appname-env')}"
  Subnet                   = "{naming_patterns.get('Subnet', 'snet-appname-env')}"
  Network_Security_Group   = "{naming_patterns.get('Network_Security_Group', 'nsg-appname-env')}"
  Application_Gateway      = "{naming_patterns.get('Application_Gateway', 'appgw-appname-env')}"
  Azure_Container_Registry = "{naming_patterns.get('Azure_Container_Registry', 'acr-appname-env')}"
  Storage_Account          = "{naming_patterns.get('Storage_Account', 'st-appname-env')}"
}}

tags = {{
  Project     = "{project_name}"
  Application = "{application_name}"
  Environment = "{environment}"
  Owner       = "{app_owner}"
  CreatedBy   = "Excel-to-Terraform-Generator"
  ServiceNow  = "{service_now_ticket}"
}}
'''
        
        return tfvars
    
    def _generate_outputs_tf(self) -> str:
        """Generate outputs.tf file."""
        
        project_info = self.terraform_data.get('project_info', {})
        
        outputs_tf = f'''# Outputs for {project_info.get('project_name', 'default-project')}
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

output "resource_group_name" {{
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}}

output "resource_group_location" {{
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}}

output "virtual_network_name" {{
  description = "Name of the virtual network"
  value       = azurerm_virtual_network.main.name
}}

output "virtual_network_id" {{
  description = "ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}}

output "subnet_name" {{
  description = "Name of the subnet"
  value       = azurerm_subnet.main.name
}}

output "subnet_id" {{
  description = "ID of the subnet"
  value       = azurerm_subnet.main.id
}}

output "network_security_group_name" {{
  description = "Name of the network security group"
  value       = azurerm_network_security_group.main.name
}}

output "network_security_group_id" {{
  description = "ID of the network security group"
  value       = azurerm_network_security_group.main.id
}}
'''
        
        # Add VM outputs
        vm_instances = self.terraform_data.get('vm_instances', [])
        if vm_instances:
            outputs_tf += f'''

# Virtual Machine Outputs
'''
            for i, vm in enumerate(vm_instances):
                vm_name = vm.get('Hostname', f'vm-{i+1}')
                outputs_tf += f'''
output "{vm_name.replace('-', '_')}_name" {{
  description = "Name of {vm_name}"
  value       = azurerm_linux_virtual_machine.{vm_name.replace('-', '_')}.name
}}

output "{vm_name.replace('-', '_')}_id" {{
  description = "ID of {vm_name}"
  value       = azurerm_linux_virtual_machine.{vm_name.replace('-', '_')}.id
}}

output "{vm_name.replace('-', '_')}_private_ip" {{
  description = "Private IP of {vm_name}"
  value       = azurerm_linux_virtual_machine.{vm_name.replace('-', '_')}.private_ip_address
}}
'''
        
        return outputs_tf
    
    def _generate_provider_tf(self) -> str:
        """Generate provider.tf file."""
        
        provider_tf = f'''# Terraform provider configuration
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{
    resource_group {{
      prevent_deletion_if_contains_resources = false
    }}
  }}
}}
'''
        
        return provider_tf
    
    def _generate_readme(self) -> str:
        """Generate README.md file."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_count = len(self.terraform_data.get('vm_instances', []))
        security_rule_count = len(self.terraform_data.get('security_groups', []))
        
        readme = f'''# {project_info.get('project_name', 'Default Project')} Infrastructure

This is a complete Terraform package generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for Azure DevOps deployment.

## 🚀 Quick Start

### Prerequisites
- Azure DevOps pipeline configured
- Terraform task in ADO pipeline
- Appropriate Azure service connection

### Deploy via Azure DevOps
This package is designed to be deployed through Azure DevOps pipelines. The Terraform files are ready for use with ADO Terraform tasks.

### Local Development/Testing
```bash
# Initialize Terraform
terraform init

# Validate configuration
./scripts/validate.sh

# Plan deployment
terraform plan

# Apply (if testing locally)
terraform apply
```

## 📋 Project Information

- **Project Name**: {project_info.get('project_name', 'default-project')}
- **Application Name**: {project_info.get('application_name', 'default-app')}
- **Application Owner**: {project_info.get('app_owner', 'TBD')}
- **Business Owner**: {project_info.get('business_owner', 'TBD')}
- **ServiceNow Ticket**: {project_info.get('service_now_ticket', 'TBD')}

## 🏗️ Infrastructure Components

- **Resource Group**: 1
- **Virtual Network**: 1 (10.0.0.0/16)
- **Subnet**: 1 (10.0.1.0/24)
- **Network Security Group**: 1
- **Security Rules**: {security_rule_count}
- **Virtual Machines**: {vm_count}

## 📁 Package Contents

### Core Terraform Files
- `main.tf` - Main resource definitions
- `variables.tf` - Variable declarations
- `terraform.tfvars` - Variable values (customize these!)
- `outputs.tf` - Output definitions
- `provider.tf` - Provider configuration
- `terraform.auto.tfvars.example` - Example variables file

### Validation Scripts
- `scripts/validate.sh` - Configuration validation script (for ADO pipeline)

### Documentation
- `README.md` - This file
- `docs/DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `.gitignore` - Git ignore rules for Terraform

## ⚙️ Configuration

### Before Deploying
1. **Review Variables**: Edit `terraform.tfvars` with your specific values
2. **Check Permissions**: Ensure you have Azure Contributor role
3. **Verify Subscription**: Confirm you're targeting the correct Azure subscription

### Key Variables to Customize
- `project_name` - Your project name
- `application_name` - Your application name
- `environment` - Environment (dev, staging, prod)
- `location` - Azure region
- `vm_count` - Number of VMs
- `vm_size` - VM size

## 🚀 Deployment Options

### Azure DevOps Pipeline (Recommended)
This package is designed for Azure DevOps deployment:
1. **Terraform Init Task**: Initialize Terraform
2. **Terraform Plan Task**: Plan the deployment
3. **Terraform Apply Task**: Deploy the infrastructure
4. **Terraform Destroy Task**: Clean up resources (if needed)

### Local Development/Testing
```bash
# Initialize
terraform init

# Validate
./scripts/validate.sh

# Plan
terraform plan

# Apply (for testing)
terraform apply
```

## 📖 Documentation

- **Quick Start**: This README
- **Detailed Guide**: See `docs/DEPLOYMENT_GUIDE.md`
- **Terraform Docs**: https://terraform.io/docs
- **Azure Docs**: https://docs.microsoft.com/azure

## 🔧 Customization

### Adding Resources
- Edit `main.tf` to add new Azure resources
- Update `variables.tf` for new variables
- Add outputs in `outputs.tf`

### Modifying VMs
- Change VM sizes in `terraform.tfvars`
- Add/remove VMs by editing the VM resources in `main.tf`
- Modify security rules in the NSG section

## 🛡️ Security Notes

- Review all security group rules before deployment
- Ensure SSH keys are properly configured
- Consider using Azure Key Vault for sensitive data
- Enable Azure Security Center recommendations

## 📊 Monitoring

After deployment:
- Check Azure Portal for resource status
- Monitor costs in Azure Cost Management
- Set up alerts for resource health
- Review Terraform outputs for connection information

## 🧹 Cleanup

To destroy all resources:
```bash
./scripts/destroy.sh
```

**⚠️ Warning**: This will permanently delete all resources and data!

## 🆘 Support

- **Terraform Issues**: Check [Terraform documentation](https://terraform.io/docs)
- **Azure Issues**: Check [Azure documentation](https://docs.microsoft.com/azure)
- **This Package**: Review logs and configuration files

---

**Generated by Excel-to-Terraform-Generator v1.0.0**  
**Source**: Excel data from {project_info.get('project_name', 'Unknown Project')}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
        
        return readme
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of what will be created."""
        
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        security_groups = self.terraform_data.get('security_groups', [])
        
        summary = {
            'project_name': project_info.get('project_name', 'default-project'),
            'application_name': project_info.get('application_name', 'default-app'),
            'resources': {
                'resource_groups': 1,
                'virtual_networks': 1,
                'subnets': 1,
                'network_security_groups': 1,
                'network_security_rules': len(security_groups),
                'virtual_machines': len(vm_instances),
                'network_interfaces': len(vm_instances)
            },
            'vm_details': [
                {
                    'name': vm.get('Hostname', f'vm-{i+1}'),
                    'size': vm.get('Recommended SKU', 'Standard_D2s_v3'),
                    'os': vm.get('OS Image*', 'Ubuntu 22.04 LTS')
                }
                for i, vm in enumerate(vm_instances)
            ],
            'security_rules': [
                {
                    'name': rule.get('name', f'rule-{i}'),
                    'direction': rule.get('direction', 'Inbound'),
                    'access': rule.get('access', 'Allow'),
                    'protocol': rule.get('protocol', 'Tcp')
                }
                for i, rule in enumerate(security_groups)
            ]
        }
        
        return summary
    
    def _generate_deploy_script(self) -> str:
        """Generate deployment script for Linux/Mac."""
        project_info = self.terraform_data.get('project_info', {})
        project_name = project_info.get('project_name', 'default-project')
        
        deploy_script = f'''#!/bin/bash
# Deployment Script for {project_name}
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

set -e  # Exit on any error

echo "=========================================="
echo "Deploying {project_name} Infrastructure"
echo "=========================================="

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform is not installed or not in PATH"
    echo "Please install Terraform from https://terraform.io/downloads"
    exit 1
fi

# Check Terraform version
terraform_version=$(terraform version -json | jq -r '.terraform_version')
echo "Using Terraform version: $terraform_version"

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "Planning deployment..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
echo "Review the plan above. Do you want to proceed with deployment? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Applying Terraform configuration..."
    terraform apply tfplan
    
    echo ""
    echo "=========================================="
    echo "Deployment completed successfully!"
    echo "=========================================="
    
    # Show outputs
    echo "Infrastructure outputs:"
    terraform output
    
    # Clean up plan file
    rm -f tfplan
    
else
    echo "Deployment cancelled."
    rm -f tfplan
    exit 0
fi
'''
        return deploy_script
    
    def _generate_destroy_script(self) -> str:
        """Generate destroy script for Linux/Mac."""
        project_info = self.terraform_data.get('project_info', {})
        project_name = project_info.get('project_name', 'default-project')
        
        destroy_script = f'''#!/bin/bash
# Destroy Script for {project_name}
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

set -e  # Exit on any error

echo "=========================================="
echo "DESTROYING {project_name} Infrastructure"
echo "=========================================="
echo "WARNING: This will destroy all resources!"
echo ""

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform is not installed or not in PATH"
    exit 1
fi

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init
fi

# Show what will be destroyed
echo "Resources that will be destroyed:"
terraform plan -destroy

# Ask for confirmation
echo ""
echo "Are you sure you want to destroy all resources? Type 'yes' to confirm:"
read -r response
if [ "$response" = "yes" ]; then
    echo "Destroying infrastructure..."
    terraform destroy -auto-approve
    
    echo ""
    echo "=========================================="
    echo "Infrastructure destroyed successfully!"
    echo "=========================================="
else
    echo "Destroy cancelled."
    exit 0
fi
'''
        return destroy_script
    
    def _generate_deploy_bat(self) -> str:
        """Generate deployment script for Windows."""
        project_info = self.terraform_data.get('project_info', {})
        project_name = project_info.get('project_name', 'default-project')
        
        deploy_bat = f'''@echo off
REM Deployment Script for {project_name}
REM Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo ==========================================
echo Deploying {project_name} Infrastructure
echo ==========================================

REM Check if Terraform is installed
terraform version >nul 2>&1
if errorlevel 1 (
    echo Error: Terraform is not installed or not in PATH
    echo Please install Terraform from https://terraform.io/downloads
    pause
    exit /b 1
)

REM Initialize Terraform
echo Initializing Terraform...
terraform init

REM Validate configuration
echo Validating Terraform configuration...
terraform validate

REM Plan deployment
echo Planning deployment...
terraform plan -out=tfplan

REM Ask for confirmation
echo.
echo Review the plan above. Do you want to proceed with deployment? (y/N)
set /p response=
if /i "%response%"=="y" (
    echo Applying Terraform configuration...
    terraform apply tfplan
    
    echo.
    echo ==========================================
    echo Deployment completed successfully!
    echo ==========================================
    
    REM Show outputs
    echo Infrastructure outputs:
    terraform output
    
    REM Clean up plan file
    del tfplan
    
) else (
    echo Deployment cancelled.
    del tfplan
)

pause
'''
        return deploy_bat
    
    def _generate_validate_script(self) -> str:
        """Generate validation script."""
        project_info = self.terraform_data.get('project_info', {})
        project_name = project_info.get('project_name', 'default-project')
        
        validate_script = f'''#!/bin/bash
# Validation Script for {project_name}
# Generated from Excel data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

set -e  # Exit on any error

echo "=========================================="
echo "Validating {project_name} Infrastructure"
echo "=========================================="

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform is not installed or not in PATH"
    exit 1
fi

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init
fi

# Format check
echo "Checking Terraform formatting..."
terraform fmt -check -diff

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

# Security scan (if tfsec is available)
if command -v tfsec &> /dev/null; then
    echo "Running security scan..."
    tfsec .
else
    echo "tfsec not found - skipping security scan"
    echo "Install tfsec for security analysis: https://aquasecurity.github.io/tfsec/"
fi

echo ""
echo "=========================================="
echo "Validation completed successfully!"
echo "=========================================="
'''
        return validate_script
    
    def _generate_deployment_guide(self) -> str:
        """Generate comprehensive deployment guide."""
        project_info = self.terraform_data.get('project_info', {})
        vm_instances = self.terraform_data.get('vm_instances', [])
        security_groups = self.terraform_data.get('security_groups', [])
        
        deployment_guide = f'''# Deployment Guide for {project_info.get('project_name', 'Default Project')}

This guide will help you deploy the infrastructure defined in this Terraform configuration.

## Prerequisites

### Required Software
- **Terraform**: Version 1.0 or higher
  - Download from: https://terraform.io/downloads
  - Verify installation: `terraform version`

- **Azure CLI**: For authentication
  - Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
  - Verify installation: `az version`

### Required Permissions
- Azure subscription with appropriate permissions
- Ability to create resource groups, virtual networks, VMs, and security groups

## Authentication

### Option 1: Azure CLI (Recommended)
```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "your-subscription-id"
```

### Option 2: Service Principal
```bash
# Set environment variables
export ARM_CLIENT_ID="your-client-id"
export ARM_CLIENT_SECRET="your-client-secret"
export ARM_SUBSCRIPTION_ID="your-subscription-id"
export ARM_TENANT_ID="your-tenant-id"
```

## Configuration

### Review Variables
Before deploying, review and modify the variables in `terraform.tfvars`:

- **project_name**: Name of your project
- **application_name**: Name of your application
- **environment**: Environment (dev, staging, prod)
- **location**: Azure region
- **vm_count**: Number of VMs to create
- **vm_size**: Size of the VMs

### Customize Resources
You can modify the following files to customize your infrastructure:
- `main.tf`: Main resource definitions
- `variables.tf`: Variable declarations
- `outputs.tf`: Output definitions

## Deployment

### Quick Start
```bash
# Make scripts executable (Linux/Mac)
chmod +x scripts/*.sh

# Deploy infrastructure
./scripts/deploy.sh
```

### Manual Deployment
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

### Windows Deployment
```cmd
# Run the Windows deployment script
scripts\\deploy.bat
```

## Infrastructure Overview

### Resources Created
- **Resource Group**: 1
- **Virtual Network**: 1 (10.0.0.0/16)
- **Subnet**: 1 (10.0.1.0/24)
- **Network Security Group**: 1
- **Security Rules**: {len(security_groups)}
- **Virtual Machines**: {len(vm_instances)}

### VM Details
'''
        
        # Add VM details
        for i, vm in enumerate(vm_instances[:10]):  # Show first 10 VMs
            vm_name = vm.get('Hostname', f'vm-{i+1}')
            vm_size = vm.get('Recommended SKU', 'Standard_D2s_v3')
            os_image = vm.get('OS Image*', 'Ubuntu 22.04 LTS')
            deployment_guide += f"- **{vm_name}**: {vm_size} - {os_image}\n"
        
        if len(vm_instances) > 10:
            deployment_guide += f"- ... and {len(vm_instances) - 10} more VMs\n"
        
        deployment_guide += f'''
### Security Rules
'''
        
        # Add security rule details
        for i, rule in enumerate(security_groups[:5]):  # Show first 5 rules
            rule_name = rule.get('name', f'rule-{i}')
            direction = rule.get('direction', 'Inbound')
            access = rule.get('access', 'Allow')
            protocol = rule.get('protocol', 'Tcp')
            deployment_guide += f"- **{rule_name}**: {direction} {access} {protocol}\n"
        
        if len(security_groups) > 5:
            deployment_guide += f"- ... and {len(security_groups) - 5} more rules\n"
        
        deployment_guide += f'''
## Post-Deployment

### Accessing VMs
After deployment, you can access your VMs using SSH:

```bash
# Get VM public IPs
terraform output

# SSH to a VM
ssh azureuser@<vm-public-ip>
```

### Monitoring
- Check Azure Portal for resource status
- Monitor costs in Azure Cost Management
- Set up alerts for resource health

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure you're logged in: `az login`
   - Check subscription: `az account show`

2. **Permission Errors**
   - Verify you have Contributor role on the subscription
   - Check resource group permissions

3. **Resource Conflicts**
   - Ensure resource names are unique
   - Check for existing resources with same names

4. **Terraform State Issues**
   - Never manually edit terraform.tfstate
   - Use `terraform refresh` if resources changed outside Terraform

### Getting Help
- Check Terraform logs: `TF_LOG=DEBUG terraform apply`
- Review Azure activity logs in the portal
- Check resource-specific documentation

## Cleanup

To destroy all resources:

```bash
# Using script
./scripts/destroy.sh

# Or manually
terraform destroy
```

**Warning**: This will permanently delete all resources and data!

## Support

For issues related to:
- **Terraform**: Check [Terraform documentation](https://terraform.io/docs)
- **Azure**: Check [Azure documentation](https://docs.microsoft.com/azure)
- **This Project**: Review the generated logs and configuration files

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: {project_info.get('project_name', 'Default Project')}
Application: {project_info.get('application_name', 'Default Application')}
'''
        
        return deployment_guide
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file for Terraform."""
        gitignore = '''# Terraform files
*.tfstate
*.tfstate.*
*.tfplan
*.tfplan.*
.terraform/
.terraform.lock.hcl

# Crash log files
crash.log
crash.*.log

# Exclude all .tfvars files, which are likely to contain sensitive data
*.tfvars
*.tfvars.json

# Ignore override files as they are usually used to override resources locally
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Include override files you do wish to add to version control using negated pattern
# !example_override.tf

# Include tfplan files to ignore the plan output of command: terraform plan -out=tfplan
# example: *tfplan*

# Ignore CLI configuration files
.terraformrc
terraform.rc

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Log files
*.log

# Temporary files
*.tmp
*.temp
'''
        return gitignore
    
    def _generate_application_gateway(self, app_gateway_data: Dict[str, Any]) -> str:
        """Generate Application Gateway resources."""
        gateway_name = app_gateway_data.get('name', 'pr-')
        backend_pool = app_gateway_data.get('backend_address_pool', 'Value')
        backend_settings = app_gateway_data.get('backend_http_settings', 'Value')
        protocol = app_gateway_data.get('protocol', 'Http')
        port = app_gateway_data.get('port', '80')
        
        return f'''

# Application Gateway
resource "azurerm_public_ip" "appgw" {{
  name                = "pip-${{var.project_name}}-${{var.environment}}-appgw"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                = "Standard"

  tags = azurerm_resource_group.main.tags
}}

resource "azurerm_application_gateway" "main" {{
  name                = "appgw-${{var.project_name}}-${{var.environment}}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku {{
    name     = "Standard_v2"
    tier     = "Standard_v2"
    capacity = 2
  }}

  gateway_ip_configuration {{
    name      = "gateway-ip-configuration"
    subnet_id = azurerm_subnet.main.id
  }}

  frontend_port {{
    name = "frontend-port"
    port = {port}
  }}

  frontend_ip_configuration {{
    name                 = "frontend-ip-configuration"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }}

  backend_address_pool {{
    name = "{backend_pool}"
  }}

  backend_http_settings {{
    name                  = "{backend_settings}"
    cookie_based_affinity = "Disabled"
    port                  = {port}
    protocol              = "{protocol}"
    request_timeout       = 30
  }}

  http_listener {{
    name                           = "listener"
    frontend_ip_configuration_name = "frontend-ip-configuration"
    frontend_port_name             = "frontend-port"
    protocol                       = "{protocol}"
  }}

  request_routing_rule {{
    name                       = "routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "listener"
    backend_address_pool_name  = "{backend_pool}"
    backend_http_settings_name = "{backend_settings}"
    priority                   = 100
  }}

  tags = azurerm_resource_group.main.tags
}}
'''
    
    def _generate_container_registry(self, acr_data: Dict[str, Any]) -> str:
        """Generate Container Registry resources."""
        acr_name = acr_data.get('name', 'acr${{var.project_name}}${{var.environment}}')
        sku = acr_data.get('sku', 'Basic')
        
        return f'''

# Container Registry
resource "azurerm_container_registry" "main" {{
  name                = "{acr_name}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "{sku}"
  admin_enabled       = true

  tags = azurerm_resource_group.main.tags
}}
'''
    
    def _generate_storage_account(self) -> str:
        """Generate Storage Account resources."""
        return f'''

# Storage Account
resource "azurerm_storage_account" "main" {{
  name                     = "st${{var.project_name}}${{var.environment}}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = azurerm_resource_group.main.tags
}}

resource "azurerm_storage_container" "main" {{
  name                  = "container"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}}
'''
    
    def _generate_tfvars_example(self) -> str:
        """Generate example tfvars file."""
        project_info = self.terraform_data.get('project_info', {})
        
        tfvars_example = f'''# Example Terraform variables file
# Copy this file to terraform.auto.tfvars and customize the values

# Project Configuration
project_name     = "{project_info.get('project_name', 'your-project-name')}"
application_name = "{project_info.get('application_name', 'your-application-name')}"
environment      = "dev"  # dev, staging, prod
location         = "East US"  # Azure region

# Application Details
app_owner        = "{project_info.get('app_owner', 'your-email@company.com')}"
business_owner   = "{project_info.get('business_owner', 'business-owner@company.com')}"
admin_username   = "azureuser"

# Infrastructure Configuration
vm_count         = {len(self.terraform_data.get('vm_instances', []))}
vm_size          = "Standard_D2s_v3"  # VM size

# Tags
tags = {{
  Project     = "{project_info.get('project_name', 'your-project-name')}"
  Application = "{project_info.get('application_name', 'your-application-name')}"
  Environment = "dev"
  Owner       = "{project_info.get('app_owner', 'your-email@company.com')}"
  CreatedBy   = "Excel-to-Terraform-Generator"
  ServiceNow  = "{project_info.get('service_now_ticket', 'TBD')}"
}}
'''
        return tfvars_example
    
    def _extract_vm_name(self, vm: Dict[str, Any], index: int) -> str:
        """Extract VM name from various possible fields."""
        # Try different field names for VM name
        name_fields = ['Hostname', 'hostname', 'VM Name', 'vm_name', 'Server Name', 'server_name', 'Name', 'name']
        
        for field in name_fields:
            if field in vm and vm[field]:
                return str(vm[field]).strip()
        
        # Fallback to index-based name
        return f"vm-{index+1:03d}"
    
    def _extract_vm_size(self, vm: Dict[str, Any]) -> str:
        """Extract VM size from various possible fields."""
        size_fields = ['Recommended SKU', 'SKU', 'Size', 'size', 'VM Size', 'vm_size', 'Instance Type', 'instance_type']
        
        for field in size_fields:
            if field in vm and vm[field]:
                return str(vm[field]).strip()
        
        return "Standard_D2s_v3"
    
    def _extract_os_image(self, vm: Dict[str, Any]) -> str:
        """Extract OS image from various possible fields."""
        os_fields = ['OS Image*', 'OS Image', 'os_image', 'Image', 'image', 'OS', 'os']
        
        for field in os_fields:
            if field in vm and vm[field]:
                return str(vm[field]).strip()
        
        return "Ubuntu 22.04 LTS"
    
    def _extract_vm_owner(self, vm: Dict[str, Any]) -> str:
        """Extract VM owner from various possible fields."""
        owner_fields = ['Server Owner', 'server_owner', 'Owner', 'owner', 'Application Owner', 'app_owner']
        
        for field in owner_fields:
            if field in vm and vm[field]:
                return str(vm[field]).strip()
        
        return "TBD"
    
    def _extract_vm_environment(self, vm: Dict[str, Any]) -> str:
        """Extract VM environment from various possible fields."""
        env_fields = ['Environment', 'environment', 'Env', 'env', 'Stage', 'stage']
        
        for field in env_fields:
            if field in vm and vm[field]:
                return str(vm[field]).strip()
        
        return "dev"
    
    def _sanitize_resource_name(self, name: str) -> str:
        """Sanitize resource name for Terraform."""
        # Remove special characters and replace with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', str(name))
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'vm_' + sanitized
        return sanitized
    
    def _generate_vm_names_list(self) -> str:
        """Generate a list of VM names for variables.tf."""
        vm_instances = self.terraform_data.get('vm_instances', [])
        vm_names = []
        
        for i, vm in enumerate(vm_instances):
            vm_name = self._extract_vm_name(vm, i)
            vm_names.append(f'"{vm_name}"')
        
        return f'[{", ".join(vm_names)}]'
    
    def _generate_nsg_rules_list(self) -> str:
        """Generate a list of NSG rules for variables.tf."""
        security_groups = self.terraform_data.get('security_groups', [])
        nsg_rules = []
        
        for i, rule in enumerate(security_groups):
            if rule.get('name') and rule.get('direction'):
                rule_obj = f'''{{
    name                       = "{rule.get('name', f'rule_{i}')}"
    priority                   = {rule.get('priority', 100 + i * 10)}
    direction                  = "{rule.get('direction', 'Inbound')}"
    access                     = "{rule.get('access', 'Allow')}"
    protocol                   = "{rule.get('protocol', 'Tcp')}"
    source_port_range          = "{rule.get('source_port_range', '*')}"
    destination_port_range     = "{rule.get('destination_port_range', '*')}"
    source_address_prefix      = "{rule.get('source_address_prefix', '*')}"
    destination_address_prefix = "{rule.get('destination_address_prefix', '*')}"
  }}'''
                nsg_rules.append(rule_obj)
        
        return f'[{", ".join(nsg_rules)}]'


def main():
    """Main function for testing the enhanced Terraform generator."""
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else "comprehensive_excel_data.json"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "terraform_output"
    
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return False
    
    # Create generator
    generator = EnhancedTerraformGenerator(json_file)
    
    # Generate summary
    summary = generator.generate_summary()
    print("Terraform Generation Summary:")
    print(f"  Project: {summary['project_name']}")
    print(f"  Application: {summary['application_name']}")
    print(f"  VMs: {summary['resources']['virtual_machines']}")
    print(f"  Security Rules: {summary['resources']['network_security_rules']}")
    
    # Generate Terraform files
    print(f"\nGenerating Terraform files in: {output_dir}")
    generated_files = generator.generate_terraform_files(output_dir)
    
    print("\nGenerated files:")
    for filename, filepath in generated_files.items():
        print(f"  {filename}: {filepath}")
    
    print(f"\nSUCCESS: Terraform files generated successfully!")
    print(f"  To deploy: cd {output_dir} && terraform init && terraform plan")
    
    return True


if __name__ == "__main__":
    main()
