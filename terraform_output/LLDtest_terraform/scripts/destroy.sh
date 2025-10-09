#!/bin/bash
# Destroy Script for default-project
# Generated from Excel data on 2025-09-25 18:10:49

set -e  # Exit on any error

echo "=========================================="
echo "DESTROYING default-project Infrastructure"
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
