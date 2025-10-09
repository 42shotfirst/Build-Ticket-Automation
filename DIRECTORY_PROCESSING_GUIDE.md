# Directory Processing Guide

This guide explains how to use the updated automation pipeline to process multiple Excel files from a directory.

## Overview

The automation pipeline now supports two modes:
1. **Single File Mode** (default): Process one Excel file at a time
2. **Multi-File Mode**: Process all Excel files in a specified directory

## Usage Examples

### Using automation_pipeline.py

#### Single File Mode (Default)
```bash
# Process the default file (LLDtest.xlsm)
python automation_pipeline.py

# Process a specific file
python automation_pipeline.py --excel-file myfile.xlsx

# Process with custom output directory
python automation_pipeline.py --excel-file myfile.xlsx --output-dir my_terraform_output
```

#### Multi-File Mode
```bash
# Process all Excel files in a directory
python automation_pipeline.py --input-dir /path/to/excel/files --multi-file

# Process with custom file pattern
python automation_pipeline.py --input-dir /path/to/excel/files --file-pattern "*.xlsx" --multi-file

# Process with custom output directory
python automation_pipeline.py --input-dir /path/to/excel/files --multi-file --output-dir my_terraform_output
```

#### Using Configuration File
```bash
# Use a custom configuration file
python automation_pipeline.py --config automation_config_directory.json
```

### Using main.py

#### Single File Mode
```bash
# Process default file
python main.py

# Process specific file
python main.py --comprehensive
```

#### Directory Mode
```bash
# Process all Excel files in a directory
python main.py --directory /path/to/excel/files

# Process with custom file pattern
python main.py --directory /path/to/excel/files "*.xlsx"
```

## Configuration

### Multi-File Configuration
Create a configuration file (e.g., `automation_config_directory.json`) with:

```json
{
  "input": {
    "process_multiple_files": true,
    "input_directory": "/path/to/excel/files",
    "file_pattern": "*.xls*",
    "required_sheets": ["Resources", "NSG", "Build_ENV"]
  },
  "output": {
    "terraform_dir": "terraform_output"
  }
}
```

### Key Configuration Options

- `process_multiple_files`: Enable/disable multi-file processing
- `input_directory`: Directory containing Excel files to process
- `file_pattern`: Glob pattern to match Excel files (default: "*.xls*")
- `terraform_dir`: Base output directory for Terraform files

## Output Structure

### Single File Mode
```
terraform_output/
├── main.tf
├── variables.tf
├── terraform.tfvars
├── provider.tf
└── outputs.tf
```

### Multi-File Mode
```
terraform_output/
├── file1_terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   ├── provider.tf
│   └── outputs.tf
├── file2_terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   ├── provider.tf
│   └── outputs.tf
└── ...
```

## JSON Output Files

Each Excel file processed will generate a corresponding JSON file:
- `filename_comprehensive_data.json` - Contains all extracted data from the Excel file

## Command Line Options

### automation_pipeline.py
- `--excel-file, -e`: Excel file to process (single file mode)
- `--input-dir, -d`: Directory containing Excel files (multi-file mode)
- `--file-pattern, -p`: File pattern for Excel files (default: "*.xls*")
- `--multi-file`: Enable multi-file processing mode
- `--output-dir, -o`: Terraform output directory
- `--config, -c`: Configuration file
- `--dry-run`: Validate configuration without processing
- `--verbose, -v`: Enable verbose logging

### main.py
- `--directory`: Process all Excel files in specified directory
- `--comprehensive`: Convert Excel to comprehensive JSON
- `--terraform-complete`: Convert Excel to complete Terraform files
- `--help, -h`: Show help information

## Error Handling

The pipeline will:
- Continue processing other files if one file fails
- Log detailed error information for failed files
- Provide a summary of successful vs failed processing
- Generate separate output directories for each file

## Best Practices

1. **Use descriptive file names**: Excel files with clear names will generate more readable output directories
2. **Organize input files**: Keep Excel files in a dedicated directory for easier management
3. **Monitor output**: Check the generated JSON and Terraform files for accuracy
4. **Use configuration files**: For repeated processing, use configuration files instead of command-line arguments
5. **Test with dry-run**: Use `--dry-run` to validate configuration before processing

## Troubleshooting

### Common Issues

1. **No files found**: Check that the input directory exists and contains Excel files matching the pattern
2. **Permission errors**: Ensure write permissions for the output directory
3. **File format errors**: Verify that Excel files are not corrupted and are in supported formats (.xlsx, .xlsm, .xls)

### Debug Mode

Enable verbose logging to see detailed processing information:
```bash
python automation_pipeline.py --input-dir /path/to/files --multi-file --verbose
```
