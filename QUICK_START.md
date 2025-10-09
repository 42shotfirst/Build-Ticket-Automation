# Quick Start Guide

## Simple Usage

### For Manual Execution:
```bash
# place Excel files in sourcefiles/ folder, then run:
python3 main.py
```

### For Control-M/Scheduled Jobs:
```bash
./run_automation.sh
```

## What Happens

1. Finds all Excel files in `sourcefiles/` directory
2. Extracts comprehensive data to JSON
3. Generates Terraform files in dynamic folders:
   - Pattern: `output_package/{subscription}_{timestamp}/`
   - Example: `output_package/subscription-dev-001_20251008_181844/`

## Output

Each run creates a new folder with complete Terraform configuration:
```
output_package/
└── subscription-dev-001_20251008_181844/
    ├── m-basevm.tf              # module call
    ├── r-rg.tf                  # resource group
    ├── r-asg.tf                 # application security groups
    ├── r-snet.tf                # subnets
    ├── r-nsr.tf                 # network security rules
    ├── r-kvlt.tf                # key vault
    ├── r-umid.tf                # user identity
    ├── r-dsk.tf                 # disk encryption
    ├── r-pe.tf                  # private endpoints
    ├── variables.tf             # variable declarations
    ├── terraform.tfvars         # variable values
    ├── outputs.tf               # outputs
    ├── versions.tf              # provider versions
    ├── data.tf                  # data sources
    ├── locals.tf                # locals
    ├── scripts/validate.sh      # validation script
    ├── README.md                # documentation
    └── .gitignore               # git ignore
```

## Options

### main.py options:
```bash
python3 main.py --dry-run              # validate only
python3 main.py --verbose              # detailed logging
python3 main.py --excel-file data.xlsx # specific file
python3 main.py --no-backup            # skip backup
```

### run_automation.sh options:
```bash
./run_automation.sh                              # default
./run_automation.sh config.json                  # custom config
./run_automation.sh config.json file.xlsx        # specific file
./run_automation.sh config.json file.xlsx outdir # custom output
```

## Entry Points

- **main.py** - Primary entry point for all automation
- **run_automation.sh** - Control-M wrapper with enhanced logging
- Both call **automation_pipeline.py** underneath

## Configuration

Edit `automation_config.json` to customize behavior.

Default settings already configured for:
- sourcefiles directory input
- dynamic folder naming
- enhanced generator v2
- module.md patterns
- subscription-based organization

## Requirements

- Python 3.7+
- pandas
- openpyxl

Install: `pip install pandas openpyxl`

## That's It

Just run `python3 main.py` and it handles everything else.

