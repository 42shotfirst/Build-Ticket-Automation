# Deployment Guide for project1

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
scripts\deploy.bat
```

## Infrastructure Overview

### Resources Created
- **Resource Group**: 1
- **Virtual Network**: 1 (10.0.0.0/16)
- **Subnet**: 1 (10.0.1.0/24)
- **Network Security Group**: 1
- **Security Rules**: 13
- **Virtual Machines**: 2

### VM Details
- **myapp-01**: Standard_D2s_v3 - Ubuntu 22.04 LTS
- **myapp-02**: Standard_D2s_v3 - Ubuntu 22.04 LTS

### Security Rules
- **one**: Inbound Allow Tcp
- **two**: Inbound Allow Tcp
- **rule-2**: Inbound Allow Tcp
- **rule-3**: Inbound Allow Tcp
- **rule-4**: Inbound Allow Tcp
- ... and 8 more rules

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
Generated on: 2025-10-02 14:30:36
Project: project1
Application: myapp
