import json
import datetime
import os
from typing import Dict, Any, List, Optional

def create_terraform_json(data: Dict[str, Any], output_filename: str = "terraform_variables.json") -> bool:
    """
    Translates build data into structured JSON suitable for Terraform variable files.
    
    Args:
        data (dict): The dictionary containing build data extracted from Excel.
        output_filename (str): The name of the output JSON file.
        
    Returns:
        bool: True if the file is created successfully, False otherwise.
    """
    print(f"Translating build data into Terraform JSON format...")
    
    try:
        # Import config here to avoid circular imports
        import config
        
        # Generate metadata
        current_time = datetime.datetime.now().isoformat()
        
        # --- Build the main Terraform variables structure ---
        terraform_variables = {
            # Metadata section (if enabled in config)
            "metadata": {
                "generated_at": current_time,
                "source_file": config.EXCEL_FILE_PATH,
                "generator_version": "1.0.0",
                "project_name": data.get('project_name', 'Unknown Project'),
                "application_name": data.get('application_name', 'Unknown Application')
            } if config.INCLUDE_METADATA else {},
            
            # Global configuration
            "project_name": config.normalize_resource_name(data.get('project_name', 'default-project')),
            "application_name": config.normalize_resource_name(data.get('application_name', 'default-app')),
            "environment": extract_primary_environment(data.get('environments', 'dev')),
            "location": config.DEFAULT_AZURE_REGION,
            
            # Resource group configuration
            "resource_group_name": generate_resource_group_name(data),
            
            # Application metadata
            "application_config": {
                "description": data.get('app_description', 'No description provided'),
                "tier": data.get('app_tier', 'Bronze').lower(),
                "owner": data.get('app_owner', 'TBD'),
                "business_owner": data.get('business_owner', 'TBD'),
                "service_now_ticket": data.get('service_now_ticket', 'TBD'),
                "environments": parse_environments(data.get('environments', 'dev'))
            },
            
            # Virtual machines configuration
            "virtual_machines": process_vm_instances(data.get('vm_instances', []), data),
            
            # Resource tagging strategy
            "default_tags": generate_resource_tags(data),
            
            # Networking configuration (if VM data includes network info)
            "networking": extract_networking_config(data.get('vm_instances', [])),
        }
        
        # Remove empty metadata section if not including metadata
        if not config.INCLUDE_METADATA or not terraform_variables["metadata"]:
            terraform_variables.pop("metadata", None)
        
        # Convert to formatted JSON
        json_output = json.dumps(
            terraform_variables, 
            indent=config.JSON_INDENT,
            sort_keys=config.JSON_SORT_KEYS,
            ensure_ascii=False
        )
        
        # Save JSON to specified output file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(json_output)
        
        print(f"Successfully generated Terraform variables file: '{output_filename}'")
        
        # Show preview if debug mode is enabled
        if hasattr(config, 'DEBUG_MODE') and config.DEBUG_MODE:
            print("\n--- Terraform JSON Preview (first 50 lines) ---")
            preview_lines = json_output.split('\n')[:50]
            print('\n'.join(preview_lines))
            if len(json_output.split('\n')) > 50:
                print("... (truncated)")
            print("--- End Preview ---")
        
        # Print summary
        print(f"\nGeneration Summary:")
        print(f"  Project: {terraform_variables['project_name']}")
        print(f"  Application: {terraform_variables['application_name']}")
        print(f"  Environment: {terraform_variables['environment']}")
        print(f"  Virtual Machines: {len(terraform_variables['virtual_machines'])}")
        print(f"  Output file size: {len(json_output):,} characters")
        
        return True
        
    except Exception as e:
        print(f"An error occurred while generating the Terraform JSON file: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_resource_group_name(data: Dict[str, Any]) -> str:
    """Generate a standardized resource group name."""
    import config
    
    app_name = config.normalize_resource_name(data.get('application_name', 'default-app'))
    env = extract_primary_environment(data.get('environments', 'dev'))
    
    # Standard Azure resource group naming: rg-{app}-{env}
    rg_name = f"rg-{app_name}-{env}"
    
    return rg_name

def extract_primary_environment(environments_str: str) -> str:
    """Extract the primary environment from a comma-separated string."""
    if not environments_str:
        return 'dev'
    
    # Split by common delimiters and take the first one
    env_list = environments_str.lower().replace(' ', '').split(',')
    primary_env = env_list[0] if env_list else 'dev'
    
    # Normalize common environment names
    env_mapping = {
        'development': 'dev',
        'testing': 'test', 
        'staging': 'stage',
        'production': 'prod',
        'qa': 'test',
        'uat': 'uat'
    }
    
    return env_mapping.get(primary_env, primary_env)

def parse_environments(environments_str: str) -> List[str]:
    """Parse comma-separated environments into a list."""
    if not environments_str:
        return ['dev']
    
    return [env.strip().lower() for env in environments_str.split(',') if env.strip()]

def process_vm_instances(vm_instances: List[Dict], global_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process VM instances from Excel data into Terraform format."""
    import config
    
    processed_vms = []
    
    for i, vm in enumerate(vm_instances):
        # Skip empty VMs if configured to do so
        if config.SKIP_EMPTY_VMS and not vm.get('Hostname', '').strip():
            continue
        
        # Extract and normalize VM data
        hostname = config.normalize_resource_name(vm.get('Hostname', f'vm-{i+1}'))
        
        vm_config = {
            "name": hostname,
            "hostname": hostname,
            "resource_group": vm.get('App RG', generate_resource_group_name(global_data)),
            "vm_size": vm.get('Recommended SKU', config.DEFAULT_VM_SIZE),
            "os_image": vm.get('OS Image*', config.DEFAULT_OS_IMAGE),
            "admin_username": vm.get('Admin Username', config.DEFAULT_ADMIN_USERNAME),
            "environment": extract_vm_environment(vm, global_data),
            "location": vm.get('Location', config.DEFAULT_AZURE_REGION),
            
            # Optional fields (only include if present)
            **{k: v for k, v in {
                "subscription_name": vm.get('Subscription Name'),
                "network_security_group": vm.get('Network Security Group'),
                "subnet_name": vm.get('Subnet'),
                "virtual_network": vm.get('Virtual Network'),
                "availability_zone": vm.get('Availability Zone'),
                "disk_type": vm.get('Disk Type'),
                "disk_size_gb": parse_disk_size(vm.get('Disk Size')),
            }.items() if v}
        }
        
        # Add VM-specific tags
        vm_config["tags"] = generate_vm_tags(vm, global_data, hostname)
        
        processed_vms.append(vm_config)
    
    return processed_vms

def extract_vm_environment(vm_data: Dict, global_data: Dict[str, Any]) -> str:
    """Extract environment for a specific VM."""
    # Try to get environment from VM data first
    vm_env = vm_data.get('Environment', '').strip().lower()
    if vm_env:
        return vm_env
    
    # Fall back to inferring from hostname
    hostname = vm_data.get('Hostname', '').lower()
    if any(env in hostname for env in ['prod', 'production']):
        return 'prod'
    elif any(env in hostname for env in ['dev', 'development']):
        return 'dev'
    elif any(env in hostname for env in ['test', 'qa', 'testing']):
        return 'test'
    elif any(env in hostname for env in ['stage', 'staging']):
        return 'stage'
    
    # Fall back to primary environment from global data
    return extract_primary_environment(global_data.get('environments', 'dev'))

def parse_disk_size(disk_size_str: Optional[str]) -> Optional[int]:
    """Parse disk size from string to integer GB."""
    if not disk_size_str:
        return None
    
    # Extract number from string like "128 GB", "256GB", "1TB", etc.
    import re
    match = re.search(r'(\d+)', str(disk_size_str))
    if match:
        size = int(match.group(1))
        # Convert TB to GB if needed
        if 'tb' in str(disk_size_str).lower():
            size *= 1024
        return size
    
    return None

def generate_resource_tags(data: Dict[str, Any]) -> Dict[str, str]:
    """Generate standardized resource tags."""
    import config
    
    tags = dict(config.DEFAULT_TAGS)  # Copy default tags
    
    # Add dynamic tags
    tags.update({
        "Project": data.get('project_name', 'Unknown'),
        "Application": data.get('application_name', 'Unknown'),
        "ApplicationTier": data.get('app_tier', 'Bronze'),
        "Owner": data.get('app_owner', 'TBD'),
        "BusinessOwner": data.get('business_owner', 'TBD'),
        "Environment": extract_primary_environment(data.get('environments', 'dev')),
        "ServiceNowTicket": data.get('service_now_ticket', 'TBD'),
    })
    
    # Add generation timestamp if enabled
    if config.INCLUDE_GENERATION_TIMESTAMP:
        tags["GeneratedAt"] = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Remove empty tags
    return {k: v for k, v in tags.items() if v and v != 'TBD'}

def generate_vm_tags(vm_data: Dict, global_data: Dict[str, Any], hostname: str) -> Dict[str, str]:
    """Generate VM-specific tags."""
    tags = generate_resource_tags(global_data)  # Start with global tags
    
    # Add VM-specific tags
    tags.update({
        "Name": hostname,
        "Role": infer_vm_role(hostname),
        "Environment": extract_vm_environment(vm_data, global_data),
    })
    
    # Add optional VM-specific information
    if vm_data.get('Subscription Name'):
        tags["Subscription"] = vm_data['Subscription Name']
    
    return tags

def infer_vm_role(hostname: str) -> str:
    """Infer VM role from hostname."""
    hostname_lower = hostname.lower()
    
    if any(role in hostname_lower for role in ['web', 'www', 'frontend', 'ui']):
        return 'web'
    elif any(role in hostname_lower for role in ['api', 'app', 'application', 'backend']):
        return 'application'
    elif any(role in hostname_lower for role in ['db', 'database', 'sql', 'mysql', 'postgres']):
        return 'database'
    elif any(role in hostname_lower for role in ['cache', 'redis', 'memcache']):
        return 'cache'
    elif any(role in hostname_lower for role in ['lb', 'loadbalancer', 'proxy']):
        return 'loadbalancer'
    else:
        return 'compute'

def extract_networking_config(vm_instances: List[Dict]) -> Dict[str, Any]:
    """Extract networking configuration from VM instances."""
    networking_config = {
        "virtual_networks": set(),
        "subnets": set(), 
        "network_security_groups": set()
    }
    
    for vm in vm_instances:
        if vm.get('Virtual Network'):
            networking_config["virtual_networks"].add(vm['Virtual Network'])
        if vm.get('Subnet'):
            networking_config["subnets"].add(vm['Subnet'])
        if vm.get('Network Security Group'):
            networking_config["network_security_groups"].add(vm['Network Security Group'])
    
    # Convert sets to sorted lists for JSON serialization
    return {
        "virtual_networks": sorted(list(networking_config["virtual_networks"])),
        "subnets": sorted(list(networking_config["subnets"])),
        "network_security_groups": sorted(list(networking_config["network_security_groups"]))
    }

# Test and utility functions
def validate_terraform_json(json_data: Dict[str, Any]) -> List[str]:
    """Validate the generated Terraform JSON structure."""
    errors = []
    
    required_fields = ['project_name', 'application_name', 'virtual_machines']
    for field in required_fields:
        if field not in json_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate VM configurations
    for i, vm in enumerate(json_data.get('virtual_machines', [])):
        vm_errors = []
        if not vm.get('name'):
            vm_errors.append(f"VM {i}: Missing name")
        if not vm.get('vm_size'):
            vm_errors.append(f"VM {i}: Missing vm_size")
        
        errors.extend(vm_errors)
    
    return errors

if __name__ == '__main__':
    """Test the terraform JSON generator with sample data."""
    print("Testing Terraform JSON Generator...")
    
    # Sample test data matching the Excel structure
    test_data = {
        'project_name': 'Infrastructure Modernization Project',
        'application_name': 'WebApp-Production',
        'app_description': 'Production web application infrastructure',
        'app_tier': 'Gold',
        'app_owner': 'infrastructure@company.com',
        'business_owner': 'product@company.com',
        'service_now_ticket': 'RITM0012345',
        'environments': 'dev, staging, production',
        'vm_instances': [
            {
                'Hostname': 'webapp-prod-web01',
                'App RG': 'rg-webapp-prod',
                'OS Image*': 'Ubuntu 22.04 LTS',
                'Recommended SKU': 'Standard_D4s_v3',
                'Subscription Name': 'prod-subscription',
                'Environment': 'production',
                'Virtual Network': 'vnet-prod-web',
                'Subnet': 'subnet-web',
                'Network Security Group': 'nsg-web-prod'
            },
            {
                'Hostname': 'webapp-prod-app01',
                'App RG': 'rg-webapp-prod', 
                'OS Image*': 'Ubuntu 22.04 LTS',
                'Recommended SKU': 'Standard_D2s_v3',
                'Subscription Name': 'prod-subscription',
                'Environment': 'production',
                'Virtual Network': 'vnet-prod-app',
                'Subnet': 'subnet-app',
                'Network Security Group': 'nsg-app-prod'
            }
        ]
    }
    
    # Test the generation
    output_file = "test_terraform_variables.json"
    success = create_terraform_json(test_data, output_file)
    
    if success:
        print(f"\nTest completed successfully!")
        print(f"Generated file: {output_file}")
        
        # Validate the generated JSON
        with open(output_file, 'r') as f:
            generated_data = json.load(f)
        
        validation_errors = validate_terraform_json(generated_data)
        if validation_errors:
            print("Validation errors found:")
            for error in validation_errors:
                print(f"  - {error}")
        else:
            print("Generated JSON passed validation!")
    else:
        print("Test failed!")
        