# Excel to JSON Converter

A comprehensive Python tool that extracts **ALL** data from Excel files and converts it to JSON format, including:

- ✅ All sheet data (tables, key-value pairs, raw data)
- ✅ VBA macros and code
- ✅ Formulas and calculated values
- ✅ Workbook properties and metadata
- ✅ Named ranges and data validation
- ✅ Comments and formatting information
- ✅ Charts and images (metadata)

## Features

### Complete Data Extraction
- **All Sheets**: Extracts data from every sheet in the Excel file
- **Multiple Data Types**: Handles tables, key-value pairs, and raw cell data
- **Smart Detection**: Automatically detects data structures and patterns
- **Formula Support**: Extracts formulas and their calculated values
- **VBA Macros**: Detects and extracts VBA project information and code patterns

### Column Referencing & Data Access
- **Keyword-based Search**: Find columns and data using keywords
- **Easy Data Access**: Simple API for accessing specific data points
- **Cross-sheet Search**: Search for data across all sheets
- **Table Filtering**: Find tables by header keywords
- **DataFrame Support**: Convert tables to pandas DataFrames for analysis

### Terraform Generation
- **Complete Terraform Files**: Generates main.tf, variables.tf, outputs.tf, etc.
- **Proper Structure**: Well-formatted, production-ready Terraform code
- **Resource Mapping**: Automatically maps Excel data to Terraform resources
- **VM Generation**: Creates virtual machines from Excel VM data
- **Security Groups**: Generates NSG rules from Excel security data
- **Networking**: Creates VNets, subnets, and network interfaces

### Flexible Output
- **Comprehensive JSON**: Complete data extraction in structured JSON format
- **Terraform Files**: Ready-to-deploy Terraform configuration
- **Configurable**: Customizable extraction and output options
- **Multiple Formats**: Supports .xlsx, .xlsm, .xls files

## Installation

### Prerequisites
- Python 3.7 or higher
- Required packages: `pandas`, `openpyxl`

### Install Dependencies
```bash
pip install pandas openpyxl
```

## Usage

### Quick Start
```bash
# Convert Excel to comprehensive JSON (default)
python main.py

# Convert Excel to complete Terraform files
python main.py --terraform-complete

# Run column referencing demo
python main.py --demo

# Show help
python main.py --help
```

### Command Line Options

```bash
# Comprehensive JSON conversion (default)
python main.py
python main.py --comprehensive

# Complete Terraform conversion with column referencing
python main.py --terraform-complete

# Legacy Terraform JSON conversion
python main.py --terraform

# Run column referencing and Terraform demo
python main.py --demo

# Show help
python main.py --help

# Show configuration
python main.py --config

# Test with sample data
python main.py --test
```

### Direct Usage
```bash
# Using the standalone converter
python excel_to_json_converter.py LLDtest.xlsm

# Using the simple converter
python convert_excel.py LLDtest.xlsm output.json

# Using the complete Excel to Terraform converter
python excel_to_terraform.py LLDtest.xlsm

# Using the data accessor for column referencing
python data_accessor.py comprehensive_excel_data.json
```

## Column Referencing & Data Access

The tool provides powerful column referencing capabilities for easy data access:

### Basic Data Access
```python
from data_accessor import ExcelDataAccessor

# Load data
accessor = ExcelDataAccessor("comprehensive_excel_data.json")

# Get project information using keywords
project_name = accessor.get_value_by_keywords("Resources", ["project", "name"])
app_owner = accessor.get_value_by_keywords("Resources", ["app", "owner"])

# Get column data using keywords
vm_sizes = accessor.get_column_data("Resources", "Recommended SKU", 0)
hostnames = accessor.get_column_data("Resources", "Hostname", 0)

# Find tables by header keywords
vm_table = accessor.get_table_by_headers("Resources", ["hostname", "vm", "server"])
nsg_table = accessor.get_table_by_headers("NSG", ["name", "direction", "access"])
```

### Advanced Data Access
```python
# Search across all sheets
search_results = accessor.search_across_sheets("Morgan")

# Get table as pandas DataFrame
df = accessor.get_table_as_dataframe("Resources", 0)

# Export Terraform-ready data
accessor.export_terraform_data("terraform_data.json")
```

### Terraform Generation with Column Referencing
```python
from enhanced_terraform_generator import EnhancedTerraformGenerator

# Generate complete Terraform files
generator = EnhancedTerraformGenerator("comprehensive_excel_data.json")
terraform_files = generator.generate_terraform_files("terraform_output")

# Get generation summary
summary = generator.generate_summary()
print(f"VMs: {summary['resources']['virtual_machines']}")
print(f"Security Rules: {summary['resources']['network_security_rules']}")
```

## File Structure

```
Build Ticket Automation/
├── main.py                          # Main entry point
├── excel_to_json_converter.py       # Comprehensive converter
├── comprehensive_excel_extractor.py # Excel data extractor
├── vba_macro_extractor.py          # VBA macro extractor
├── convert_excel.py                # Simple usage script
├── config.py                       # Configuration settings
├── read_build_data.py              # Legacy data reader
├── terraform_json_generator.py     # Legacy Terraform generator
├── LLDtest.xlsm                    # Example Excel file
└── README.md                       # This file
```

## Output Format

The comprehensive JSON output includes:

```json
{
  "conversion_metadata": {
    "source_file": "LLDtest.xlsm",
    "conversion_timestamp": "2025-09-18T19:10:31.122053",
    "converter_version": "1.0.0",
    "extraction_methods": ["comprehensive_excel_extractor", "vba_macro_extractor"]
  },
  "file_info": {
    "filename": "LLDtest.xlsm",
    "extraction_timestamp": "2025-09-18T19:10:31.122053"
  },
  "workbook_properties": {
    "creator": "Travis Paskey",
    "created": "2024-03-05T17:47:47",
    "modified": "2025-09-19T01:14:40",
    "sheet_count": 7,
    "sheet_names": ["Build_ENV", "Resources", "NSG", "APGW", "ACR NRS", "Resource Options", "Issue and blockers "]
  },
  "sheets": {
    "Build_ENV": {
      "name": "Build_ENV",
      "raw_data": [...],
      "structured_data": {...},
      "tables": [...],
      "key_value_pairs": {...},
      "dimensions": {"rows": 6, "columns": 10}
    }
  },
  "vba_macros": {
    "project_info": {
      "filename": "xl/vbaProject.bin",
      "size_bytes": 24576,
      "detected_keywords": {"Sub ": 1, "Dim ": 1, "For ": 1},
      "detected_module_types": ["Module", "Sheet", "Workbook", "Form"]
    }
  },
  "formulas": {
    "Resources": [
      {
        "cell": "B100",
        "formula": "=\"vm_list.\" & C98 & \".name\"",
        "calculated_value": "f",
        "row": 100,
        "column": 2
      }
    ]
  },
  "processing_summary": {
    "sheets_processed": 7,
    "total_tables_extracted": 30,
    "total_key_value_pairs": 296,
    "total_formulas_found": 16,
    "has_vba_macros": true,
    "vba_project_size_bytes": 24576
  }
}
```

## Configuration

Edit `config.py` to customize:

```python
# File paths
EXCEL_FILE_PATH = "LLDtest.xlsm"
TERRAFORM_JSON_PATH = "terraform_variables.json"

# Processing options
DEBUG_MODE = True
INCLUDE_METADATA = True
JSON_INDENT = 2

# Default values
DEFAULT_AZURE_REGION = "East US"
DEFAULT_VM_SIZE = "Standard_D2s_v3"
```

## Examples

### Basic Conversion
```bash
# Convert the example file
python main.py

# Output: comprehensive_excel_data.json (4.8MB)
```

### Specific File Conversion
```bash
# Convert your own Excel file
python convert_excel.py my_data.xlsx my_output.json
```

### Legacy Terraform Conversion
```bash
# Generate Terraform variables (legacy mode)
python main.py --terraform
```

## Supported Excel Features

| Feature | Status | Notes |
|---------|--------|-------|
| Multiple Sheets | ✅ | All sheets extracted |
| Tables | ✅ | Auto-detected and structured |
| Key-Value Pairs | ✅ | Extracted from any sheet |
| Formulas | ✅ | Formula text and calculated values |
| VBA Macros | ✅ | Project info and code patterns |
| Named Ranges | ✅ | Range definitions |
| Comments | ✅ | Cell comments (where supported) |
| Data Validation | ✅ | Validation rules |
| Charts | ✅ | Metadata extraction |
| Images | ✅ | Metadata extraction |
| Formatting | ✅ | Style information |

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install pandas openpyxl
   ```

2. **File Not Found**
   - Ensure the Excel file exists in the specified path
   - Check file permissions

3. **Large File Processing**
   - Large Excel files may take time to process
   - Monitor memory usage for very large files

4. **VBA Macro Extraction**
   - VBA code is in binary format and cannot be directly read
   - The tool extracts project info and detects code patterns

### Debug Mode
Enable debug mode in `config.py` for detailed output:
```python
DEBUG_MODE = True
```

## Performance

- **Small files** (< 1MB): < 5 seconds
- **Medium files** (1-10MB): 5-30 seconds  
- **Large files** (10-50MB): 30 seconds - 2 minutes
- **Very large files** (> 50MB): 2+ minutes

## Limitations

- VBA source code cannot be directly extracted (binary format)
- Some Excel features may not be fully preserved
- Very large files may require significant memory
- Comments extraction is limited by openpyxl capabilities

## Contributing

This tool is designed to be comprehensive and extensible. To add new features:

1. Extend the `ComprehensiveExcelExtractor` class
2. Add new extraction methods
3. Update the JSON output structure
4. Test with various Excel file formats

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Enable debug mode for detailed output
3. Review the generated JSON structure
4. Check file permissions and dependencies

---

**Note**: This tool extracts ALL data from Excel files, including sensitive information. Ensure you handle the output JSON files securely and in accordance with your organization's data policies.
