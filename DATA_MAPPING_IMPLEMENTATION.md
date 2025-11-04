# Data Mapping Implementation

## Overview
This document describes the data mappings between Terraform configuration (Source) and Excel spreadsheet structure (Target) that have been implemented.

---

## 1. Network Security Group (NSG) Rules Mapping

### Source Structure
```hcl
network_security_rules = {
  rules = [
    {
      name = "rule1"
      priority = 100
      direction = "Inbound"
      access = "Allow"
      protocol = "Tcp"
      source_port_range = "*"
      destination_port_ranges = ["443"]
      source_asg_keys = ["asg_nic"]
      destination_asg_keys = ["asg_pe"]
      description = "Rule description"
    }
  ]
}
```

### Target Structure (Excel NSG Sheet)
```
sheets.NSG.structured_data.header_row_0.data
```

### Field Mappings

| Source (Terraform) | Target (Excel) | Implementation |
|-------------------|----------------|----------------|
| `rules.name` | `name` | Direct mapping |
| `rules.priority` | `priority` | Direct mapping (converted to int) |
| `rules.direction` | `direction` | Direct mapping |
| `rules.access` | `access` | Direct mapping |
| `rules.protocol` | `protocol` | Direct mapping |
| `rules.source_port_range` | `source_port_range` | Direct mapping |
| `rules.destination_port_ranges` | `destination_port_ranges` | Direct mapping (handles both singular/plural) |
| `rules.source_asg_keys` | `source_asg` | Excel uses `source_asg`, Terraform expects `source_asg_keys` (list) |
| `rules.destination_asg_keys` | `destination_asg` | Excel uses `destination_asg`, Terraform expects `destination_asg_keys` (list) |
| `rules.description` | `description` | Direct mapping |

### Implementation Details

**Location:** `enhanced_terraform_generator_v2.py` → `_generate_nsg_rules_for_tfvars()`

**Key Features:**
- Handles both `source_asg` (Excel) and `source_asg_keys` (Terraform)
- Converts port ranges from string to list format
- Validates priority as integer
- Preserves all original fields for backward compatibility

---

## 2. Virtual Machines (VMs) Mapping

### Source Structure
```hcl
vm_list = {
  vm1 = {
    name = "vm-name"
    size = "Standard_B2s_v2"
    image_os = "windows"
    image_urn = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
    os_disk_size = 128
    os_disk_type = "Standard_LRS"
    ip_allocation = "Dynamic"
    ip_address = "10.0.1.5"
    snet_key = "snet1"
    asg_key = "asg_nic"
    tags = {
      role = "Application"
      patch-optin = "YES"
    }
  }
}
```

### Target Structure (Excel Resources Sheet)
```
sheets.Resources.structured_data.header_row_1.data
```

### Field Mappings

| Source (Terraform) | Target (Excel Path) | Implementation |
|-------------------|---------------------|----------------|
| `vm_list.vmX` (key) | `vm_list.key` | VM identifier |
| `vm_list.vmX.name` | `vm_list.vm1.name` | Extracted via `_get_raw_value('vm_list.vm1.name', 'Resources')` |
| `vm_list.vmX.image_os` | `vm_list.vm1.image_os` | Extracted via `_get_raw_value('vm_list.vm1.image_os', 'Resources')` |
| `vm_list.vmX.image_urn` | `vm_list.vm1.image_urn` | Extracted via `_get_raw_value('vm_list.vm1.image_urn', 'Resources')` |
| `vm_list.vmX.size` | `vm_list.vm1.size` | Extracted via `_get_raw_value('vm_list.vm1.size', 'Resources')` |
| `vm_list.vmX.os_disk_size` | `vm_list.vm1.os_disk_size` | Extracted via `_get_raw_value('vm_list.vm1.os_disk_size', 'Resources')` |
| `vm_list.vmX.os_disk_type` | `vm_list.vm1.os_disk_type` | Extracted via `_get_raw_value('vm_list.vm1.os_disk_type', 'Resources')` |
| `vm_list.vmX.ip_allocation` | `vm_list.vm1.ip_allocation` | Extracted via `_get_raw_value('vm_list.vm1.ip_allocation', 'Resources')` |
| `vm_list.vmX.ip_address` | `vm_list.vm1.ip_address` | Extracted via `_get_raw_value('vm_list.vm1.ip_address', 'Resources')` |
| `vm_list.vmX.snet_key` | `vm_list.vm1.snet_key` | Extracted via `_get_raw_value('vm_list.vm1.snet_key', 'Resources')` |
| `vm_list.vmX.asg_key` | `vm_list.vm1.asg_key` | Extracted via `_get_raw_value('vm_list.vm1.asg_key', 'Resources')` |
| `vm_list.vmX.tags.role` | `vm_list.vm1.tags.wab:role` | Excel uses `wab:role`, Terraform uses `role` |
| `vm_list.vmX.tags.patch-optin` | `vm_list.vm1.tags.wab:patch-optin` | Excel uses `wab:patch-optin`, Terraform uses `patch-optin` |

### Implementation Details

**Location:** `enhanced_terraform_generator_v2.py` → `_generate_vm_list_for_tfvars()`

**Key Features:**
- Uses `_get_raw_value()` with full path (e.g., `vm_list.vm1.name`)
- Falls back to VM-specific path (e.g., `vm_list.vm2.name`) if available
- Handles `wab:` prefix for tags (Excel) vs no prefix (Terraform)
- Converts disk sizes to integers
- Handles optional fields like `ip_address`

**Extraction Logic:**
```python
# Try VM-specific value first
value = self._get_raw_value(f'vm_list.{vm_key}.field', 'Resources')
# Fall back to vm1 template
value = value or self._get_raw_value('vm_list.vm1.field', 'Resources')
# Fall back to extraction function
value = value or self._extract_field(vm)
```

---

## Excel Structure Reference

### NSG Sheet Structure
```
Column 0: name
Column 1: priority
Column 2: direction
Column 3: access
Column 4: protocol
Column 5: source_port_range
Column 6: destination_port_ranges
Column 7: source_asg
Column 8: destination_asg
Column 9: description
```

### Resources Sheet Structure (VM Section)
```
Row: "vm_list.vm1.name" = "vm-name"
Row: "vm_list.vm1.size" = "Standard_B2s_v2"
Row: "vm_list.vm1.image_os" = "windows"
Row: "vm_list.vm1.image_urn" = "MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest"
Row: "vm_list.vm1.os_disk_size" = "128"
Row: "vm_list.vm1.os_disk_type" = "Standard_LRS"
Row: "vm_list.vm1.ip_allocation" = "Dynamic"
Row: "vm_list.vm1.ip_address" = "10.0.1.5"
Row: "vm_list.vm1.snet_key" = "snet1"
Row: "vm_list.vm1.asg_key" = "asg_nic"
Row: "vm_list.vm1.tags.wab:role" = "Application"
Row: "vm_list.vm1.tags.wab:patch-optin" = "YES"
```

---

## Implementation Files

1. **`enhanced_terraform_generator_v2.py`**
   - `_generate_nsg_rules_for_tfvars()` - NSG rule generation with correct mappings
   - `_generate_vm_list_for_tfvars()` - VM list generation with correct path mappings

2. **`data_accessor.py`**
   - `get_terraform_ready_data()` - NSG extraction with field name mapping

3. **`enhanced_terraform_generator_v2.py`**
   - `_build_raw_data_cache()` - Builds cache from Excel raw_data
   - `_get_raw_value()` - Retrieves values using Excel path structure

---

## Usage

When Excel data is processed:
1. NSG rules are extracted with correct field names (`source_asg` → `source_asg_keys`)
2. VMs are extracted using full paths (`vm_list.vm1.name`, etc.)
3. Tags are handled with `wab:` prefix conversion
4. All values flow correctly from Excel → JSON → Terraform

---

## Testing

To verify mappings:
```bash
# Run automation
python3 automation_pipeline.py

# Check generated Terraform
cat output_package/subscription_*/terraform.tfvars

# Verify:
# - NSG rules have correct field names
# - VMs use correct vm_list paths
# - Tags use correct format
```

---

**Status:** ✅ Implemented and ready for use

