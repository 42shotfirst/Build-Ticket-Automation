# Dynamic Output Directory Implementation

## Overview

This document describes the implementation of dynamic output folder creation based on the Subscription field from Excel data and timestamp. This feature prevents output folders from being overwritten and creates unique, organized directories for each automation run.

## Implementation Details

### 1. Dynamic Folder Naming Logic

The automation pipeline now creates output directories using the following pattern:
```
{Subscription}_{YYYYMMDD_HHMMSS}
```

**Example:**
- Subscription: `subscription-dev-001`
- Timestamp: `20251007_230153`
- Result: `subscription-dev-001_20251007_230153`

### 2. Subscription Field Extraction

The system searches for the Subscription field in multiple locations within the Excel data:

1. **Build_ENV sheet key-value pairs**
2. **Resources sheet key-value pairs**
3. **Comprehensive data across all sheets**
4. **VM instance data**

**Search Keywords:**
- `subscription`
- `Subscription`
- `SUBSCRIPTION`

### 3. Fallback Mechanism

If no Subscription field is found, the system falls back to using the Excel filename:
```
{ExcelFilename}_{YYYYMMDD_HHMMSS}
```

**Example:**
- Excel file: `my_project_data.xlsx`
- Timestamp: `20251007_230153`
- Result: `my_project_data_20251007_230153`

### 4. Directory Name Sanitization

The system sanitizes directory names to ensure compatibility:
- Replaces spaces and special characters with underscores
- Removes multiple consecutive underscores
- Trims leading/trailing underscores
- Limits length to 50 characters
- Handles empty values with "unknown" fallback

**Examples:**
```
'My Test Subscription' -> 'My_Test_Subscription'
'sub@#$%^&*()script' -> 'sub_script'
'very-long-name...' -> 'very-long-subscription-name-that-exceeds-fifty-cha'
'' -> 'unknown'
```

## Configuration Options

### automation_config.json

```json
{
  "output": {
    "dynamic_folder_naming": true,
    "folder_naming_pattern": "{subscription}_{timestamp}",
    "fallback_folder_naming": "{excel_filename}_{timestamp}"
  }
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dynamic_folder_naming` | boolean | `true` | Enable/disable dynamic folder naming |
| `folder_naming_pattern` | string | `{subscription}_{timestamp}` | Pattern for subscription-based naming |
| `fallback_folder_naming` | string | `{excel_filename}_{timestamp}` | Pattern for fallback naming |

### Supported Pattern Variables

- `{subscription}` - Extracted subscription value
- `{timestamp}` - Current timestamp (YYYYMMDD_HHMMSS)
- `{excel_filename}` - Excel filename without extension

### Example Patterns

```json
{
  "folder_naming_pattern": "terraform_{subscription}_{timestamp}",
  "fallback_folder_naming": "terraform_{excel_filename}_{timestamp}"
}
```

**Results:**
- `terraform_subscription-dev-001_20251007_230153`
- `terraform_my_project_data_20251007_230153`

## Code Implementation

### Key Methods

#### `_create_dynamic_output_directory()`
- Main method for creating dynamic output directories
- Handles configuration checking and pattern application
- Returns the full path to the output directory

#### `_extract_subscription_from_json()`
- Extracts Subscription value from JSON data
- Searches multiple data locations
- Returns the first valid subscription found

#### `_sanitize_directory_name()`
- Sanitizes names for directory compatibility
- Handles special characters and length limits
- Ensures valid directory names

### Integration Points

The dynamic output functionality is integrated into:
- `automation_pipeline.py` - Main automation pipeline
- `automation_config.json` - Configuration file
- `test_dynamic_output.py` - Test suite

## Usage Examples

### Basic Usage
```bash
# Run automation with dynamic folder naming (default)
python automation_pipeline.py

# Output will be in: output_package/{subscription}_{timestamp}/
```

### Custom Configuration
```json
{
  "output": {
    "dynamic_folder_naming": true,
    "folder_naming_pattern": "deployment_{subscription}_{timestamp}",
    "fallback_folder_naming": "deployment_{excel_filename}_{timestamp}"
  }
}
```

### Legacy Mode
```json
{
  "output": {
    "dynamic_folder_naming": false
  }
}
```

## Generated Directory Structure

```
output_package/
├── subscription-dev-001_20251007_230153/
│   ├── m-basevm.tf
│   ├── r-asg.tf
│   ├── r-kvlt.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── ...
├── subscription-prod-002_20251007_231045/
│   ├── m-basevm.tf
│   ├── r-asg.tf
│   ├── r-kvlt.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── ...
└── ...
```

## Testing

### Test Suite
The implementation includes a comprehensive test suite (`test_dynamic_output.py`) that tests:

1. **Subscription extraction** from various data locations
2. **Directory name sanitization** with various inputs
3. **Pattern application** with different configurations
4. **Fallback mechanisms** when subscription is not found
5. **Configuration options** validation

### Test Results
```
✅ Dynamic output directory creation
✅ Subscription field extraction
✅ Directory name sanitization
✅ Pattern application
✅ Fallback mechanisms
✅ Configuration options
```

## Benefits

### 1. **No Overwriting**
- Each automation run creates a unique directory
- Previous outputs are preserved
- Easy to track different deployments

### 2. **Organized Output**
- Clear naming convention based on subscription
- Timestamp-based ordering
- Easy identification of deployment time

### 3. **Flexible Configuration**
- Configurable naming patterns
- Support for different organizational needs
- Backward compatibility with legacy mode

### 4. **Robust Fallback**
- Handles missing subscription gracefully
- Uses Excel filename as fallback
- Ensures unique directory creation

## Logging

The system provides detailed logging for troubleshooting:

```
INFO - Creating dynamic output directory: output_package/subscription-dev-001_20251007_230153
INFO - Based on subscription: subscription-dev-001
INFO - Timestamp: 20251007_230153
INFO - Found subscription in Build_ENV: subscription-dev-001
INFO - Using subscription-based naming: subscription-dev-001_20251007_230153
```

## Error Handling

The system handles various error conditions:

1. **Missing Subscription Field**
   - Logs warning message
   - Falls back to Excel filename
   - Continues processing

2. **Invalid Directory Names**
   - Sanitizes problematic characters
   - Ensures valid directory creation
   - Handles empty values

3. **Configuration Errors**
   - Uses default patterns if configuration is invalid
   - Logs configuration issues
   - Maintains functionality

## Future Enhancements

Potential future improvements:

1. **Environment-based Naming**
   - Include environment (DEV, PROD, etc.) in directory names
   - Pattern: `{subscription}_{environment}_{timestamp}`

2. **Project-based Organization**
   - Group outputs by project name
   - Pattern: `{project}/{subscription}_{timestamp}`

3. **Custom Timestamp Formats**
   - Configurable timestamp formats
   - Support for different date/time formats

4. **Retention Policies**
   - Automatic cleanup of old output directories
   - Configurable retention periods

## Conclusion

The dynamic output directory implementation provides a robust, configurable solution for organizing Terraform automation outputs. It prevents overwriting, ensures unique directory creation, and provides flexibility for different organizational needs while maintaining backward compatibility.

The implementation has been thoroughly tested and provides comprehensive logging for troubleshooting and monitoring automation runs.
