# Terraform Default Values Accuracy Report

**Date:** October 10, 2025  
**Analysis:** Comprehensive comparison between Excel source → JSON → Terraform files

## Critical Issues Found

### 1. **Location Field - CRITICAL ERROR**
- **JSON Source (raw_data):** `"here"` (Line 106)
- **Terraform variables.tf default:** `"WEST US 3"`
- **Terraform terraform.tfvars:** `"here"`
- **Issue:** The value "here" is NOT a valid Azure location and will cause deployment failures
- **Expected valid values:** "WEST US", "WEST US 2", "WEST US 3", "EAST US"
- **Recommendation:** This must be corrected in the Excel file source data before generating terraform files

### 2. **Key Vault soft_delete_retention_days - MISMATCH**
- **JSON Source (raw_data line 4119):** `90`
- **Terraform variables.tf default:** `90` ✓
- **Terraform terraform.tfvars:** `7` ❌
- **Issue:** terraform.tfvars has wrong value - should be 90 to match source data
- **Impact:** Non-compliance with retention policy requirements

### 3. **Key Vault public_network_access - INCONSISTENCY**
- **JSON Source (raw_data line 4166):** `1` (represents TRUE/enabled)
- **Terraform variables.tf default:** `false` ❌
- **Terraform terraform.tfvars:** `true` ✓
- **Issue:** variables.tf default contradicts the source data. The JSON shows `1` which should map to `true`
- **Impact:** Default behavior doesn't match documented requirements

### 4. **VM os_disk_size - MAJOR MISMATCH**
- **JSON Source (raw_data line 5435):** `10` GB
- **Terraform terraform.tfvars (all VMs):** `128` GB
- **Issue:** ALL VMs in terraform.tfvars have os_disk_size of 128 GB, but source data shows 10 GB
- **Impact:** Significant cost implications - provisioning much larger disks than specified

###  5. **VM ip_allocation - WRONG ALLOCATION METHOD**
- **JSON Source (raw_data line 5529):** `"Static"`
- **Terraform terraform.tfvars (all VMs):** `"Dynamic"`
- **Issue:** ALL VMs configured with Dynamic IPs instead of Static as specified in source
- **Impact:** Could cause networking issues if static IPs are required for the application

### 6. **admin_username - CORRECT**
- **JSON Source (raw_data line 5811):** `"cisadmin"` ✓
- **Terraform variables.tf default:** `"cisadmin"` ✓  
- **Terraform terraform.tfvars:** Not explicitly set (uses default) ✓
- **Status:** This field is correct

### 7. **Key Vault sku_name - CORRECT**
- **JSON Source (raw_data line 4025):** `"standard"` ✓
- **Terraform variables.tf default:** `"standard"` ✓
- **Terraform terraform.tfvars:** `"standard"` ✓
- **Status:** This field is correct

## Summary Statistics

| Category | Count |
|----------|-------|
| **Critical Errors** | 5 |
| **Correct Values** | 2 |
| **Fields Checked** | 7 |
| **Accuracy Rate** | 28.6% |

## Root Cause Analysis

### Likely causes of inaccuracies:

1. **Hard-coded fallback values:** The terraform generator appears to use hard-coded defaults when it can't properly extract values from JSON (e.g., "128" for os_disk_size, "Dynamic" for ip_allocation)

2. **Type conversion issues:** The value `1` in JSON for public_network_access may not be correctly converted to boolean `true`

3. **Invalid source data:** The location field contains "here" in the Excel source, which should never have been accepted

4. **Incomplete data mapping:** The generator may not be correctly traversing the nested JSON structure to extract raw_data values

## Recommendations

### Immediate Actions Required:

1. **Fix Excel Source Data:**
   - Change location from "here" to a valid Azure region (e.g., "WEST US 3")
   - Verify all other fields in Excel have valid values

2. **Fix Terraform Generator:**
   - Update `enhanced_terraform_generator_v2.py` to properly extract values from `raw_data` structure
   - Fix type conversion for boolean fields (1 → true, 0 → false)
   - Remove hard-coded fallback values or add warnings when fallbacks are used
   - Add validation to reject invalid values before writing to terraform files

3. **Regenerate All Terraform Files:**
   - After fixing generator, regenerate all subscription packages
   - Verify all fields match source data

4. **Add Validation Layer:**
   - Add pre-generation validation of JSON data
   - Add post-generation verification comparing terraform outputs to source
   - Implement automated testing

## Detailed Field-by-Field Comparison

### Fields from raw_data (column "1" = variable name, column "2" = value):

```json
Line 106:  {"1": "location", "2": "here"}  → INVALID VALUE
Line 4025: {"1": "sku_name", "2": "standard"}  → CORRECT
Line 4119: {"1": "soft_delete_retention_days", "2": 90}  → MISMATCH in tfvars (shows 7)
Line 4166: {"1": "public_network_access", "2": 1}  → Should be true, variables.tf shows false
Line 5435: {"1": "vm_list.vm1.os_disk_size", "2": 10}  → MISMATCH in tfvars (shows 128)
Line 5529: {"1": "vm_list.vm1.ip_allocation", "2": "Static"}  → MISMATCH in tfvars (shows Dynamic)
Line 5811: {"1": "admin_username", "2": "cisadmin"}  → CORRECT
```

## Next Steps

1. Review and approve fixes to Excel source data
2. Update terraform generator to correctly read raw_data structure  
3. Add comprehensive validation and testing
4. Regenerate all terraform packages
5. Perform final verification before deployment

