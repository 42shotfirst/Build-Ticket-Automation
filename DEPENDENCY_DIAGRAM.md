# Build Ticket Automation - Dependency Diagram

## Production Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  USER EXECUTION                                                             │
│  ===============                                                            │
│                                                                             │
│  python main.py [options]                                                  │
│         │                                                                   │
│         └──> main.py (entry point)                                         │
│              │                                                              │
│              └──> AutomationPipeline.run()                                 │
│                   │                                                         │
│                   ├─────────────────────────────────────────────────────┐  │
│                   │                                                     │  │
│                   ▼                                                     │  │
│         ┌──────────────────────┐                                      │  │
│         │ Load Configuration   │                                      │  │
│         │ & Validate Inputs    │                                      │  │
│         └──────────────────────┘                                      │  │
│                   │                                                    │  │
│                   ▼                                                    │  │
│         ┌──────────────────────┐                                      │  │
│         │ Discover Excel Files │                                      │  │
│         │ (single or batch)    │                                      │  │
│         └──────────────────────┘                                      │  │
│                   │                                                    │  │
│         ┌─────────┴────────────────────────────────┐                  │  │
│         │ For Each Excel File                      │                  │  │
│         │                                          │                  │  │
│         ▼                                          │                  │  │
│    ┌────────────────────────────────────────┐     │                  │  │
│    │ ComprehensiveExcelExtractor            │     │                  │  │
│    ├────────────────────────────────────────┤     │                  │  │
│    │ • Extract all sheets                   │     │                  │  │
│    │ • Extract VBA macros                   │     │                  │  │
│    │ • Extract formulas                     │     │                  │  │
│    │ • Extract comments & metadata          │     │                  │  │
│    │ • Extract formatting & styles          │     │                  │  │
│    │ • Extract named ranges & connections  │     │                  │  │
│    │                                        │     │                  │  │
│    │ Output: JSON with complete data        │     │                  │  │
│    └────────────────────────────────────────┘     │                  │  │
│         │                                         │                  │  │
│         └────────────▶ JSON File                  │                  │  │
│                       (.../comprehensive_*.json) │                  │  │
│                       │                          │                  │  │
│                       ▼                          │                  │  │
│         ┌────────────────────────────────────────┐│                  │  │
│         │ ExcelDataAccessor                      ││                  │  │
│         ├────────────────────────────────────────┤│                  │  │
│         │ • Load JSON data                       ││                  │  │
│         │ • Provide typed interface              ││                  │  │
│         │ • Sheet/table/cell access              ││                  │  │
│         │ • Data filtering & searching           ││                  │  │
│         └────────────────────────────────────────┘│                  │  │
│                       │                          │                  │  │
│                       ▼                          │                  │  │
│         ┌────────────────────────────────────────┐│                  │  │
│         │ ExcelDataMapper                        ││                  │  │
│         ├────────────────────────────────────────┤│                  │  │
│         │ • Map Build_ENV data                   ││                  │  │
│         │ • Map Resources (VMs, storage)         ││                  │  │
│         │ • Map NSG rules                        ││                  │  │
│         │ • Map Key Vault settings               ││                  │  │
│         │ • Map Subnets & networking             ││                  │  │
│         │ • Clean values for Terraform output    ││                  │  │
│         └────────────────────────────────────────┘│                  │  │
│                       │                          │                  │  │
│                       ▼                          │                  │  │
│         ┌────────────────────────────────────────┐│                  │  │
│         │ TerraformGeneratorClean                ││                  │  │
│         ├────────────────────────────────────────┤│                  │  │
│         │ • Generate main.tf                     ││                  │  │
│         │   (resource definitions)               ││                  │  │
│         │ • Generate variables.tf                ││                  │  │
│         │   (variable declarations)              ││                  │  │
│         │ • Generate terraform.tfvars            ││                  │  │
│         │   (variable values)                    ││                  │  │
│         │ • Generate outputs.tf                  ││                  │  │
│         │ • Generate provider.tf                 ││                  │  │
│         │                                        ││                  │  │
│         │ Output: Clean, production-ready .tf   ││                  │  │
│         └────────────────────────────────────────┘│                  │  │
│                       │                          │                  │  │
│         ┌─────────────┴──────────────────────────┘                  │  │
│         │                                                            │  │
│    ┌────▼─────────────────────────────────────────────────────────┐ │  │
│    │ Per-File Output Directory                                   │ │  │
│    │ terraform_clean_<subscription>_<timestamp>/                 │ │  │
│    │  ├── main.tf                                                │ │  │
│    │  ├── variables.tf                                           │ │  │
│    │  ├── terraform.tfvars                                       │ │  │
│    │  ├── outputs.tf                                             │ │  │
│    │  └── provider.tf                                            │ │  │
│    └────────────────────────────────────────────────────────────┘ │  │
│         │                                                           │  │
│         └──────────────────────────────────────────────────────────┘  │
│                   │                                                     │
│                   ▼                                                     │
│         ┌──────────────────────────────────────────┐                   │
│         │ Validate Outputs                         │                   │
│         │ • Check JSON validity                    │                   │
│         │ • Check required Terraform files exist   │                   │
│         │ • Report warnings if any                 │                   │
│         └──────────────────────────────────────────┘                   │
│                   │                                                     │
│                   ▼                                                     │
│         ┌──────────────────────────────────────────┐                   │
│         │ Generate Summary Report                  │                   │
│         │ • Total files processed                  │                   │
│         │ • Files generated                        │                   │
│         │ • Execution duration                     │                   │
│         │ • Errors/warnings                        │                   │
│         └──────────────────────────────────────────┘                   │
│                   │                                                     │
│                   ▼                                                     │
│         Return to main.py with results                                 │
│         Print summary and exit                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Module Dependency Graph

```
┌──────────────────────────────────────────────────────────────────────┐
│ PRODUCTION PIPELINE (Direct Usage)                                   │
│                                                                      │
│  main.py                                                             │
│    └─→ AutomationPipeline (automation_pipeline.py)                  │
│         ├─→ ComprehensiveExcelExtractor                             │
│         │   (comprehensive_excel_extractor.py)                      │
│         │   └─→ VBAMacroExtractor (vba_macro_extractor.py)          │
│         │                                                            │
│         ├─→ ExcelDataAccessor (data_accessor.py)                    │
│         │                                                            │
│         └─→ TerraformGeneratorClean                                 │
│             (terraform_generator_clean.py)                          │
│             └─→ ExcelDataMapper (excel_data_mapper.py)              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STANDALONE TOOLS (Optional/Manual Usage)                             │
│                                                                      │
│  production_readiness_validator.py                                   │
│    (No local dependencies - can run independently)                  │
│                                                                      │
│  terraform_structure_validator.py                                    │
│    (No local dependencies - can run independently)                  │
│                                                                      │
│  validate_terraform_commas.py                                        │
│    (No local dependencies - can run independently)                  │
│                                                                      │
│  read_build_data.py                                                  │
│    └─→ config.py                                                     │
│    (Not used in production pipeline)                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ BROKEN/DEPRECATED                                                    │
│                                                                      │
│  convert_excel.py [BROKEN]                                           │
│    └─→ excel_to_json_converter (MISSING - removed in cleanup)       │
│    (Cannot run - missing dependency)                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Reverse Dependency Map (Who Uses What)

```
main.py
  ↓
automation_pipeline.py
  ├─← Uses: comprehensive_excel_extractor.py
  ├─← Uses: data_accessor.py
  └─← Uses: terraform_generator_clean.py

terraform_generator_clean.py
  └─← Uses: excel_data_mapper.py

excel_data_mapper.py
  └─← Uses: JSON data from ComprehensiveExcelExtractor

comprehensive_excel_extractor.py
  └─← Uses: vba_macro_extractor.py (optionally, for macro extraction)

data_accessor.py
  └─← No local dependencies

config.py
  └─← Used by: read_build_data.py

read_build_data.py
  └─← Used by: Nothing (standalone)

vba_macro_extractor.py
  └─← Called by: comprehensive_excel_extractor.py
  └─← Can run standalone: python vba_macro_extractor.py <file.xlsx>

production_readiness_validator.py
  └─← No local dependencies
  └─← Can run standalone: python production_readiness_validator.py

terraform_structure_validator.py
  └─← No local dependencies
  └─← Can run standalone: python terraform_structure_validator.py

validate_terraform_commas.py
  └─← No local dependencies
  └─← Can run standalone: python validate_terraform_commas.py

convert_excel.py
  └─← BROKEN: Depends on missing excel_to_json_converter
```

## Data Flow

```
Excel File (.xlsx/.xlsm)
    │
    ▼
ComprehensiveExcelExtractor
    │ (extracts all data)
    ▼
JSON File (comprehensive_*.json)
    │
    ├──────────────────────┬──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
ExcelDataAccessor   ExcelDataMapper      (Analysis/Debugging)
    │                      │
    │          (maps to Terraform structure)
    │                      │
    ▼                      ▼
(Typed access)     Terraform Data Dict
                           │
                           ▼
                   TerraformGeneratorClean
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    main.tf          variables.tf      terraform.tfvars
(Resources)        (Declarations)        (Values)
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
        terraform_clean_<subscription>_<timestamp>/
                    (Output Directory)
```

## Critical Dependencies Summary

### MUST HAVE (Cannot Remove):
- main.py
- automation_pipeline.py
- comprehensive_excel_extractor.py
- data_accessor.py
- excel_data_mapper.py
- terraform_generator_clean.py
- config.py

### OPTIONAL (Can Remove/Archive):
- production_readiness_validator.py
- terraform_structure_validator.py
- validate_terraform_commas.py
- vba_macro_extractor.py (used optionally in extraction)

### SAFE TO DELETE:
- convert_excel.py (broken, not used)

### NEED REVIEW:
- read_build_data.py (appears unused, possibly redundant)

## Circular Dependency Check: NONE FOUND ✓

The dependency tree is acyclic and clean. No circular references detected.

