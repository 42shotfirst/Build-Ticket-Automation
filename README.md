# Build Ticket Automation (BTA)

A comprehensive automation pipeline that extracts infrastructure configuration from Excel build tickets and generates production-ready Terraform configurations for Azure deployments.

## Overview

The Build Ticket Automation (BTA) system converts standardized Excel build tickets into complete Terraform configurations. It supports:

- Virtual Machine deployments with custom images
- Key Vault with diagnostic settings
- Network Security Groups (NSG)
- Application Security Groups (ASG)
- Private Endpoints with DNS zone integration
- Disk Encryption Sets
- User Assigned Identities

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AUTOMATION PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │ Excel File   │───▶│ Extractors   │───▶│ EnhancedTerraformGen V2  │  │
│  │ (Build_ENV)  │    │              │    │                          │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│         │                   │                        │                  │
│         ▼                   ▼                        ▼                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │ sourcefiles/ │    │ JSON Data    │    │ terraform_output/        │  │
│  │ *.xlsm       │    │ Extract      │    │ ├── terraform.tfvars     │  │
│  └──────────────┘    └──────────────┘    │ ├── variables.tf         │  │
│                                          │ ├── main.tf              │  │
│                                          │ ├── m-vm.tf              │  │
│                                          │ └── ...                  │  │
│                                          └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Prerequisites

```bash
# Python 3.7+
pip install pandas openpyxl

# Terraform (optional, for validation)
# https://www.terraform.io/downloads
```

### 2. Place Excel File

Place your Excel build ticket (`.xlsm` or `.xlsx`) in the `sourcefiles/` directory.

### 3. Run the Pipeline

```bash
python3 automation_pipeline.py
```

### 4. Output

Generated Terraform files are placed in `terraform_output/{timestamp}/`:
- `terraform.tfvars` - Variable values from Excel
- `variables.tf` - Variable definitions
- `main.tf` - Provider configuration
- `m-vm.tf` - VM module configuration
- `r-*.tf` - Resource files (ASG, Key Vault, etc.)

---

## Excel File Structure

### Required Sheet: Build_ENV

The `Build_ENV` sheet contains the core infrastructure configuration in a key-value format:

| Column A (Label) | Column B (Terraform Variable) | Column C (Value) |
|-----------------|------------------------------|------------------|
| Resource Group | resource_group_name | rg-myapp-prod |
| Location | location | EAST US |
| Key Vault | key_vault_name | kvlt-myapp-prod |
| ... | ... | ... |

### Sections in Build_ENV

1. **Project Information** - ServiceNow ticket, application name, environment
2. **Resource Group** - Name and location
3. **Key Vault** - Name, SKU, retention days, public access
4. **Disk Encryption Set** - Name and key reference
5. **User Assigned Identity** - Managed identity name
6. **Subnet** - VNET details, NSG, Route Table
7. **Application Security Groups** - ASG keys and names
8. **Private Endpoints** - PE configuration for Key Vault
9. **Virtual Machines** - VM specifications (vm1, vm2, etc.)
10. **Network Security Rules** - HCL-formatted NSG rules (optional)

### Example VM Configuration in Excel

```
vm_list.vm1.name          = aze-myapp01
vm_list.vm1.size          = Standard_D8as_v5
vm_list.vm1.image_os      = windows
vm_list.vm1.os_disk_size  = 128
vm_list.vm1.snet_key      = snet1
vm_list.vm1.asg_key       = asg_app
```

---

## Generated Output

### terraform.tfvars

The generated `terraform.tfvars` includes all infrastructure configuration:

```hcl
# Begin terraform.tfvars

spn      = "spn-terraform-mysubscription"
location = "EAST US"
resource_group_name = "rg-myapp-prod"

application_security_groups = {
  asg_app = {
    name = "asg-myapp-prod"
  }
}

disk_encryption_set_name    = "dsk-myapp-prod"
user_assigned_identity_name = "umid-myapp-prod"

key_vault = {
  name                       = "kvlt-myapp-prod"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  public_network_access      = true
  snet_key                   = "snet1"
  key_name                   = "key-myapp-prod"
}

diagnostic_setting = {
  name                           = "diag-smc_cis"
  eventhub_authorization_rule_id = "/subscriptions/.../evh-sec-eus-prod/..."
  eventhub_name                  = "evhub-keyvault-001"
}

existing_subnets = {
  snet1 = {
    resource_group_name  = "rg-networking-prod"
    virtual_network_name = "vnet-core-prod"
    name                 = "snet-myapp-prod"
  }
}

private_endpoints = {
  pe1 = {
    name                           = "pvep-myapp-kvlt-prod"
    subresource_names              = ["vault"]
    private_connection_resource_id = null
    is_manual_connection           = "false"
    private_dns_zone_group_name    = "default"
    private_dns_zone_ids           = ["/subscriptions/.../privatelink.vaultcore.azure.net"]
    snet_key                       = "snet1"
    asg_key                        = "asg_kvlt"
  }
}

vm_list = {
  vm1 = {
    name              = "aze-myapp01"
    size              = "Standard_D8as_v5"
    zone              = 1
    image_os          = "windows"
    marketplace_image = false
    source_image_id   = "/subscriptions/.../galleries/PackerDev/images/windows-server-2019-cis-L1"
    ip_allocation     = "Static"
    os_disk_size      = 128
    os_disk_type      = "Premium_LRS"
    data_disk_sizes   = [64]
    data_disk_type    = "Premium_LRS"
    snet_key          = "snet1"
    vtpm_enabled      = true
    asg_key           = "asg_app"
    tags = {
      "role"        = "App",
      "patch-optin" = "YES"
    }
  }
}

common_tags = {
  "shared-service-name" = "NA",
  "app-name"            = "Microsoft Active Directory",
  "environment"         = "prod",
  "data-classification" = "Internal",
  "criticality"         = "4-Very Minor to Operations",
  "app-tier"            = "Platinum",
  "it-cost-center"      = "55410",
  "it-domain"           = "Identity and Access Management",
  "notes"               = "NA",
  "segment"             = "NA",
  "lineofbusiness"      = "NA",
  "department"          = "NA",
  "cost-center"         = "NA",
  "wab:terraform"       = "True"
}
```

---

## Region-Based Configuration

### Event Hub Namespaces

The `diagnostic_setting` block automatically selects the Event Hub namespace based on region:

| Region | Event Hub Namespace |
|--------|-------------------|
| East US, East US 2 | `evh-sec-eus-prod` |
| West US, West US 2, West US 3 | `evh-sec-wus3-prod` |

### Source Image IDs

VM images are resolved to full Azure resource paths based on region:

| Region | Resource Group | Gallery |
|--------|---------------|---------|
| East regions | `rg-packer-dev` | `PackerDev` |
| West regions | `rg-packer-prod-wus3` | `PackerWUS3` |

Example resolved path:
```
/subscriptions/6f5e4da6-a73e-4795-8e57-49bdfaed7724/resourceGroups/rg-packer-dev/providers/Microsoft.Compute/galleries/PackerDev/images/windows-server-2019-cis-L1
```

---

## Configuration

### automation_config.json

```json
{
  "input": {
    "excel_file": null,
    "input_directory": "sourcefiles",
    "file_pattern": "*.xls*",
    "required_sheets": ["Resources", "NSG", "Build_ENV"],
    "process_multiple_files": true
  },
  "terraform": {
    "provider_version": "~> 4.14",
    "default_location": "WEST US 3",
    "use_enhanced_generator_v2": true,
    "module_source": "app.terraform.io/wab-cloudengineering-org/base-vm/iac"
  },
  "output": {
    "terraform_dir": "terraform_output",
    "backup_previous": true
  }
}
```

---

## Project Structure

```
Build Ticket Automation/
├── automation_pipeline.py          # Main entry point
├── automation_config.json          # Pipeline configuration
├── enhanced_terraform_generator_v2.py  # Core Terraform generator
├── comprehensive_excel_extractor.py    # Excel data extraction
├── data_accessor.py                    # Data access utilities
│
├── src/
│   ├── extractors/
│   │   ├── build_env_extractor.py  # Build_ENV sheet extraction
│   │   ├── resources_extractor.py  # Resources sheet extraction
│   │   ├── nsg_extractor.py        # NSG sheet extraction
│   │   ├── apgw_extractor.py       # Application Gateway extraction
│   │   └── acr_extractor.py        # Container Registry extraction
│   │
│   ├── generators/
│   │   ├── core_infrastructure_generator.py  # Key Vault, Identity, etc.
│   │   ├── networking_generator.py           # Subnets, ASG, PE
│   │   ├── vm_generator.py                   # Virtual Machine config
│   │   └── nsg_generator.py                  # NSG rules
│   │
│   └── core/
│       ├── orchestrator.py         # Pipeline orchestration
│       ├── hcl_formatter.py        # HCL formatting utilities
│       └── validator.py            # Data validation
│
├── sourcefiles/                    # Input Excel files
│   └── *.xlsm
│
├── terraform_output/               # Generated Terraform files
│   └── {timestamp}/
│       ├── terraform.tfvars
│       ├── variables.tf
│       ├── main.tf
│       └── ...
│
└── terraform_files_pattern/        # Template files
    └── *.tf
```

---

## Key Components

### 1. EnhancedTerraformGeneratorV2

The main generator class (`enhanced_terraform_generator_v2.py`) handles:

- Reading extracted Excel data
- Generating all Terraform resource files
- Creating `terraform.tfvars` with proper HCL formatting
- Region-based configuration (Event Hub, Image galleries)
- VM tag management

**Key methods:**
| Method | Purpose |
|--------|---------|
| `_generate_tfvars()` | Main terraform.tfvars generation |
| `_generate_vm_list_for_tfvars()` | VM configuration with all attributes |
| `_generate_subnets_for_tfvars()` | Subnet configuration (existing vs new) |
| `_generate_diagnostic_setting()` | Event Hub diagnostics with region logic |
| `_resolve_source_image_id()` | Region-based image gallery resolution |
| `_generate_private_endpoints_for_tfvars()` | Private endpoint with DNS zones |
| `_generate_asg_for_tfvars()` | Application Security Groups |

### 2. Build_ENV Extractor

The `build_env_extractor.py` extracts data from the Build_ENV sheet including:

- Key-value pairs (terraform variable -> value)
- VM configurations (vm_list.vm1.*, vm_list.vm2.*, etc.)
- NSG rules from HCL literals
- ASG definitions
- Private endpoint configurations

**Sheet fallback logic:** Build_ENV -> BTA5 -> Active sheet

### 3. Data Accessor

The `data_accessor.py` provides utilities for:

- Searching data across sheets
- Getting values by terraform variable name
- Extracting section-specific data
- NSG metadata extraction from HCL

---

## NSG Rules from HCL

The system can parse NSG rules directly from HCL format in the Excel sheet:

```hcl
network_security_rules = {
  resource_group_name         = "rg-networking-prod"
  network_security_group_name = "nsg-myapp-prod"
  rules = [
    {
      name                       = "Allow_HTTPS"
      priority                   = 100
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_ranges    = ["443"]
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    },
  ]
}
```

---

## Usage Examples

### Basic Pipeline Execution

```bash
# Run the full pipeline
python3 automation_pipeline.py

# Output will be in terraform_output/{timestamp}/
```

### Using the Orchestrator (Alternative)

```python
from src.core.orchestrator import TerraformOrchestrator

# Initialize with Excel file
orchestrator = TerraformOrchestrator("sourcefiles/build_ticket.xlsm")

# Extract all data
data = orchestrator.extract_all()

# Generate Terraform files
files = orchestrator.generate_terraform("output_dir")
```

### Data Accessor Usage

```python
from data_accessor import ExcelDataAccessor

# Load extracted JSON data
accessor = ExcelDataAccessor("comprehensive_excel_data.json")

# Get specific values
rg_name = accessor.get_value_by_keywords("Build_ENV", ["resource_group", "name"])
location = accessor.get_value_by_keywords("Build_ENV", ["location"])

# Search across all sheets
results = accessor.search_across_sheets("production")
```

---

## Validation

### Built-in Validation

The pipeline includes validation for:

- Excel file format and required sheets
- Data extraction completeness
- VM configuration requirements
- Terraform syntax (via `terraform fmt`)

### Manual Validation

```bash
cd terraform_output/{timestamp}
terraform init
terraform validate
terraform plan
```

---

## Troubleshooting

### Common Issues

1. **Sheet not found error**
   - Ensure the Excel file has a `Build_ENV` or `BTA5` sheet
   - The system falls back to: Build_ENV -> BTA5 -> Active sheet

2. **Missing VM data**
   - Check that VM entries use the format: `vm_list.vm1.name`, `vm_list.vm1.size`, etc.
   - Verify Column B contains the terraform variable name

3. **Region detection issues**
   - Ensure the `location` field is properly set in Excel
   - Valid values: "EAST US", "WEST US 3", etc.

4. **Image resolution problems**
   - The system defaults to `windows-server-2019-cis-L1` if no image is specified
   - Check that region mapping is correct for your subscription

### Debug Mode

Enable detailed logging in `automation_config.json`:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

---

## Extending the System

### Adding New Resource Types

1. Create an extractor in `src/extractors/`
2. Create a generator in `src/generators/`
3. Update `enhanced_terraform_generator_v2.py` to include the new resource
4. Add variable definitions to `variables.tf` template

### Custom Tag Configuration

Modify the `common_tags` block in `_generate_tfvars()` method of `enhanced_terraform_generator_v2.py`:

```python
common_tags = {{
  "app-name"    = "Your App Name",
  "environment" = {fmt(environment)},
  "custom-tag"  = "custom-value",
}}
```

### Adding New Region Mappings

Update `_generate_diagnostic_setting()` and `_resolve_source_image_id()` methods:

```python
def _resolve_source_image_id(self, source_image_id: str, region: str) -> str:
    region_upper = region.upper() if region else 'WEST US 3'
    if 'EAST' in region_upper:
        rg_name = 'rg-packer-dev'
        gallery_name = 'PackerDev'
    elif 'CENTRAL' in region_upper:  # Add new region
        rg_name = 'rg-packer-central'
        gallery_name = 'PackerCentral'
    else:
        rg_name = 'rg-packer-prod-wus3'
        gallery_name = 'PackerWUS3'
    # ...
```

---

## Performance

| File Size | Processing Time |
|-----------|----------------|
| < 1MB | < 5 seconds |
| 1-10MB | 5-30 seconds |
| > 10MB | 30+ seconds |

---

## File Output Reference

### Generated Files

| File | Description |
|------|-------------|
| `terraform.tfvars` | All variable values from Excel |
| `variables.tf` | Variable definitions with types and validation |
| `main.tf` | Provider configuration and backend |
| `m-vm.tf` | VM module instantiation |
| `r-asg.tf` | Application Security Group resources |
| `r-kvlt.tf` | Key Vault resource |
| `r-umid.tf` | User Assigned Identity |
| `r-dsk.tf` | Disk Encryption Set |
| `r-snet.tf` | Subnet data sources |
| `data.tf` | Data source lookups |
| `locals.tf` | Local values |
| `outputs.tf` | Output definitions |

---

## License

Internal use only. Contact the Cloud Engineering team for support.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review generated `automation_results.json` for errors
3. Enable debug logging for detailed output
4. Contact the Platform Engineering team

---

**Note**: This tool extracts infrastructure configuration from Excel files. Ensure you handle the generated Terraform files securely and in accordance with your organization's security policies.
