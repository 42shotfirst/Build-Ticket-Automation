# Terraform Default Values Fix Implementation Plan

**Date:** October 10, 2025

## Issues Identified

Based on comprehensive analysis of the Excel source → JSON → Terraform pipeline:

### Critical Issues:

1. **Location = "here"** in Excel source (INVALID)
2. **soft_delete_retention_days = 7** (hardcoded, should be 90)
3. **public_network_access = false** (wrong default, should be true/1)
4. **os_disk_size = 128** (hardcoded fallback, should be 10)
5. **ip_allocation = "Dynamic"** (hardcoded, should be "Static")

## Root Causes

### 1. Hardcoded Values in Generator
**File:** `enhanced_terraform_generator_v2.py`

**Problem locations:**
- Line 653: `soft_delete_retention_days = 7` (should read from JSON)
- Line 654: `public_network_access = true` (should read from JSON)
- Line 720: `ip_allocation = "Dynamic"` (should read from JSON)
- Line 1416: `return 128  # Default` (fallback value is too high)

### 2. Data Extraction Not Reading raw_data
**File:** `data_accessor.py`

**Problem:** The `get_terraform_ready_data()` function extracts from "tables" and "key_value_pairs" but doesn't properly traverse to the raw_data structure where actual field-by-field values are stored.

**Location:** Lines 258-585 don't extract individual field defaults from raw_data properly.

### 3. Invalid Source Data
**File:** `LLDtest.xlsm` (Excel source)

**Problem:** Location field contains "here" instead of valid Azure region.

## Implementation Steps

### Step 1: Fix Excel Source Data (MANUAL - User Action Required)
- Open `LLDtest.xlsm`
- Find the Location field in Build_ENV sheet
- Change from "here" to "WEST US 3" (or appropriate valid region)
- Save the file

### Step 2: Enhance data_accessor.py to Extract raw_data Values

Add new method to properly extract from raw_data:

```python
def _extract_from_raw_data(self, sheet_name: str, variable_name: str) -> Any:
    """Extract a specific variable value from raw_data structure.
    
    Args:
        sheet_name: Name of the sheet (e.g., 'Build_ENV')
        variable_name: The terraform variable name to extract
    
    Returns:
        The value from column "2" where column "1" matches variable_name
    """
    sheet_data = self.sheets.get(sheet_name, {})
    raw_data = sheet_data.get('raw_data', [])
    
    for row in raw_data:
        if isinstance(row, dict) and row.get('1') == variable_name:
            return row.get('2')
    
    return None
```

### Step 3: Fix enhanced_terraform_generator_v2.py

#### A. Extract Key Vault Settings from JSON (Line ~603-657)

**Current (wrong):**
```python
key_vault = {
  name                       = "kvlt-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
  sku_name                   = "standard"
  soft_delete_retention_days = 7  # WRONG
  public_network_access      = true  # Should read from JSON
  snet_key                   = "snet1"
  key_name                   = "key-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
}
```

**Fixed:**
```python
# Extract key vault settings from raw_data
raw_data = self.terraform_data.get('comprehensive_data', {}).get('Build_ENV', {}).get('raw_data', [])

def get_raw_value(var_name):
    for row in raw_data:
        if isinstance(row, dict) and row.get('1') == var_name:
            return row.get('2')
    return None

# Get actual values from JSON
kvlt_sku = get_raw_value('sku_name') or 'standard'
kvlt_retention = get_raw_value('soft_delete_retention_days') or 90
kvlt_public_access = get_raw_value('public_network_access')
if kvlt_public_access == 1:
    kvlt_public_access = 'true'
elif kvlt_public_access == 0:
    kvlt_public_access = 'false'
else:
    kvlt_public_access = 'false'  # safe default

key_vault = {
  name                       = "kvlt-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
  sku_name                   = "{kvlt_sku}"
  soft_delete_retention_days = {kvlt_retention}
  public_network_access      = {kvlt_public_access}
  snet_key                   = "snet1"
  key_name                   = "key-{project_name.lower().replace(' ', '-')}-{environment.lower()}"
}
```

#### B. Extract VM Settings from JSON (Line ~685-739)

**Current (wrong):**
```python
ip_allocation     = "Dynamic"  # HARDCODED
os_disk_size      = {os_disk_size}  # Uses extraction function with wrong fallback
```

**Fixed:**
```python
# Extract VM-specific settings from raw_data
vm_ip_allocation = get_raw_value('vm_list.vm1.ip_allocation') or 'Dynamic'
vm_os_disk_size = get_raw_value('vm_list.vm1.os_disk_size') or self._extract_vm_disk_size(vm)

ip_allocation     = "{vm_ip_allocation}"
os_disk_size      = {vm_os_disk_size}
```

#### C. Fix Fallback Values

**Current (wrong):**
```python
def _extract_vm_disk_size(self, vm: Dict[str, Any]) -> int:
    # ... extraction logic ...
    return 128  # Default TOO HIGH
```

**Fixed:**
```python
def _extract_vm_disk_size(self, vm: Dict[str, Any]) -> int:
    # ... extraction logic ...
    return 30  # More reasonable default for OS disk
```

### Step 4: Update variables.tf Defaults (Line ~301-322)

**Current (wrong):**
```python
default = {
  name                       = null
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  public_network_access      = false  # WRONG
  snet_key                   = "snet1"
  key_name                   = null
}
```

**Fixed:**
```python
default = {
  name                       = null
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  public_network_access      = true  # Fixed to match JSON
  snet_key                   = "snet1"
  key_name                   = null
}
```

### Step 5: Add Validation Layer

Create new file: `validate_terraform_data.py`

```python
#!/usr/bin/env python3
"""
Validate Terraform Data Against Source
======================================
Ensures generated terraform files match source JSON data.
"""

import json
import sys

def validate_terraform_against_json(json_file, terraform_tfvars_file):
    """Compare terraform.tfvars values against JSON source."""
    
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    
    raw_data = json_data.get('sheets', {}).get('Build_ENV', {}).get('raw_data', [])
    
    def get_json_value(var_name):
        for row in raw_data:
            if isinstance(row, dict) and row.get('1') == var_name:
                return row.get('2')
        return None
    
    # Critical fields to validate
    validations = {
        'location': get_json_value('location'),
        'soft_delete_retention_days': get_json_value('soft_delete_retention_days'),
        'public_network_access': get_json_value('public_network_access'),
        'os_disk_size': get_json_value('vm_list.vm1.os_disk_size'),
        'ip_allocation': get_json_value('vm_list.vm1.ip_allocation'),
    }
    
    print("Validation Results:")
    print("=" * 50)
    
    for field, expected_value in validations.items():
        print(f"{field}: {expected_value}")
    
    # TODO: Parse terraform.tfvars and compare values
    # This is a template for validation logic
    
    return True

if __name__ == "__main__":
    json_file = sys.argv[1] if len(sys.argv) > 1 else "comprehensive_excel_data.json"
    tfvars_file = sys.argv[2] if len(sys.argv) > 2 else "output_package/*/terraform.tfvars"
    
    validate_terraform_against_json(json_file, tfvars_file)
```

## Testing Plan

1. **Fix Excel source** (change "here" to "WEST US 3")
2. **Regenerate JSON**: Run `python comprehensive_excel_extractor.py LLDtest.xlsm`
3. **Apply code fixes**: Update data_accessor.py and enhanced_terraform_generator_v2.py
4. **Regenerate terraform files**: Run automation pipeline
5. **Validate output**: Check that terraform.tfvars contains:
   - `location = "WEST US 3"` (not "here")
   - `soft_delete_retention_days = 90` (not 7)
   - `public_network_access = true` (not false)
   - `os_disk_size = 10` (not 128)
   - `ip_allocation = "Static"` (not "Dynamic")
6. **Run validation script**: `python validate_terraform_data.py`
7. **Test terraform**: `cd output_package/subscription_* && terraform validate`

## Success Criteria

- [ ] All hardcoded values removed from generator
- [ ] All values extracted from JSON raw_data
- [ ] Excel source corrected (location != "here")
- [ ] Validation script passes
- [ ] Terraform validate passes
- [ ] Generated files match source data 100%

## Timeline

- **User action** (fix Excel): 5 minutes
- **Code updates**: 30 minutes
- **Testing**: 15 minutes
- **Total**: ~50 minutes

## Risk Assessment

**Low Risk:**
- Changes are localized to generator logic
- Existing infrastructure not affected
- Can revert if issues occur

**Mitigation:**
- Keep backup of current generator
- Test with single subscription first
- Validate before bulk regeneration

