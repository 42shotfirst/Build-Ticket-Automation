@echo off
REM Deployment Script for default-project
REM Generated from Excel data on 2025-09-25 18:10:49

echo ==========================================
echo Deploying default-project Infrastructure
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
