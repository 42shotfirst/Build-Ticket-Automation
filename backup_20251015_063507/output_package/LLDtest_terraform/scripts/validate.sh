#!/bin/bash
# Validation Script for project1
# Generated from Excel data on 2025-10-07 10:32:38

set -e  # Exit on any error

echo "=========================================="
echo "Validating project1 Infrastructure"
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
