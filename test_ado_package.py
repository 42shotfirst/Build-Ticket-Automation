#!/usr/bin/env python3
"""
Test script to demonstrate the Azure DevOps-focused deployment package functionality.
This script will create a complete Terraform package optimized for ADO deployment.
"""

import os
import sys
from automation_pipeline import AutomationPipeline

def test_ado_package():
    """Test the Azure DevOps-focused deployment package functionality."""
    
    print("=" * 80)
    print("TESTING AZURE DEVOPS DEPLOYMENT PACKAGE GENERATION")
    print("=" * 80)
    
    # Check if we have Excel files in sourcefiles directory
    sourcefiles_dir = "sourcefiles"
    if not os.path.exists(sourcefiles_dir):
        print(f"Creating {sourcefiles_dir} directory...")
        os.makedirs(sourcefiles_dir)
        print(f"Please place your Excel files in the {sourcefiles_dir} directory and run again.")
        return False
    
    # Check for Excel files
    import glob
    excel_files = glob.glob(os.path.join(sourcefiles_dir, "*.xls*"))
    if not excel_files:
        print(f"No Excel files found in {sourcefiles_dir} directory.")
        print("Please place your Excel files in the sourcefiles directory and run again.")
        return False
    
    print(f"Found {len(excel_files)} Excel file(s) in {sourcefiles_dir}:")
    for file in excel_files:
        print(f"  - {os.path.basename(file)}")
    
    # Create automation pipeline
    print("\nInitializing automation pipeline...")
    pipeline = AutomationPipeline()
    
    # Run the pipeline
    print("Running automation pipeline...")
    results = pipeline.run()
    
    if results['success']:
        print("\n" + "=" * 80)
        print("✅ AZURE DEVOPS PACKAGE GENERATED SUCCESSFULLY!")
        print("=" * 80)
        
        print(f"\n📁 Output Package Location: output_package/")
        print(f"📊 Files Generated: {len(results['files_generated'])}")
        print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
        
        print(f"\n📋 Package Contents:")
        if os.path.exists("output_package"):
            for root, dirs, files in os.walk("output_package"):
                level = root.replace("output_package", "").count(os.sep)
                indent = "  " * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = "  " * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        
        print(f"\n🚀 Azure DevOps Integration:")
        print(f"1. Copy the output_package contents to your ADO repository")
        print(f"2. Configure Terraform tasks in your ADO pipeline:")
        print(f"   - Terraform Init")
        print(f"   - Terraform Plan") 
        print(f"   - Terraform Apply")
        print(f"3. Use terraform.tfvars for variable configuration")
        print(f"4. Run validation with: ./scripts/validate.sh")
        
        print(f"\n📖 Documentation:")
        print(f"- README.md - Azure DevOps integration guide")
        print(f"- docs/DEPLOYMENT_GUIDE.md - Comprehensive deployment guide")
        
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ PACKAGE GENERATION FAILED!")
        print("=" * 80)
        
        print(f"\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
        
        return False

def show_ado_package_structure():
    """Show the expected ADO package structure."""
    print("\n" + "=" * 80)
    print("AZURE DEVOPS PACKAGE STRUCTURE")
    print("=" * 80)
    
    structure = """
output_package/
├── main.tf                          # Main Terraform resources
├── variables.tf                     # Variable definitions
├── terraform.tfvars                 # Variable values (customize these!)
├── terraform.auto.tfvars.example    # Example variables file
├── outputs.tf                       # Output definitions
├── provider.tf                      # Provider configuration
├── .gitignore                       # Git ignore rules
├── README.md                        # Azure DevOps integration guide
├── scripts/
│   └── validate.sh                  # Configuration validation script
└── docs/
    └── DEPLOYMENT_GUIDE.md          # Comprehensive deployment guide
"""
    
    print(structure)
    
    print("\n🎯 Azure DevOps Integration Features:")
    print("  ✅ Complete Terraform configuration ready for ADO")
    print("  ✅ Terraform tasks compatible (Init, Plan, Apply, Destroy)")
    print("  ✅ Variable files for easy configuration")
    print("  ✅ Validation script for pipeline validation")
    print("  ✅ Comprehensive documentation for ADO setup")
    print("  ✅ Git-ready with proper .gitignore")
    
    print("\n🔧 ADO Pipeline Tasks:")
    print("  1. Terraform Init Task")
    print("  2. Terraform Plan Task")
    print("  3. Terraform Apply Task")
    print("  4. Terraform Destroy Task (optional)")

if __name__ == "__main__":
    print("Excel to Terraform Azure DevOps Package Generator")
    print("=" * 55)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--structure":
        show_ado_package_structure()
    else:
        success = test_ado_package()
        
        if success:
            print(f"\n🎉 Test completed successfully!")
            print(f"Your Azure DevOps package is ready in the 'output_package' directory.")
        else:
            print(f"\n💥 Test failed!")
            print(f"Please check the errors above and try again.")
        
        sys.exit(0 if success else 1)
