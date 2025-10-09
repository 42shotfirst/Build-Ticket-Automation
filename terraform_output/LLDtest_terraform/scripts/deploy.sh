#!/bin/bash
# Deployment Script for default-project
# Generated from Excel data on 2025-09-25 18:10:49

set -e  # Exit on any error

echo "=========================================="
echo "Deploying default-project Infrastructure"
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
