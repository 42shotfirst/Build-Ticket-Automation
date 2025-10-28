# Data Flow: Excel → JSON → Terraform

## Complete Data Pipeline

```
Excel File (LLDtest.xlsm)
    ↓
Python Extractor (comprehensive_excel_extractor.py)
    ↓
JSON File (LLDtest_comprehensive_data.json)
    ↓
Data Accessor (data_accessor.py)
    ↓
Terraform Generator (enhanced_terraform_generator_v2.py)
    ↓
Terraform Files (output_package/subscription_*/)
```

---

## Detailed Flow

### 1️⃣ **Excel Source File**
**File:** `LLDtest.xlsm` (122KB)
**Location:** Root directory or `sourcefiles/` folder

**Contents:**
- Build_ENV sheet (environment configuration)
- Resources sheet (project info, VMs)
- NSG sheet (security rules)
- APGW sheet (application gateway)
- ACR NRS sheet (container registry)
- Resource Options sheet
- VBA macros

---

### 2️⃣ **Excel to JSON Conversion**

**Main File:** `excel_to_json_converter.py`
- **Calls:** `comprehensive_excel_extractor.py`
- **Calls:** `vba_macro_extractor.py`
- **Output:** `{base_name}_comprehensive_data.json` (4.6MB)

**What gets extracted:**
```python
comprehensive_data = {
    "conversion_metadata": {...},
    "file_info": {...},
    "workbook_properties": {...},
    "sheets": {
        "Build_ENV": {
            "raw_data": [...],           # ← Excel rows as dicts
            "structured_data": {...},
            "tables": [...],             # ← Parsed table structures
            "key_value_pairs": {...},     # ← Key-value mappings
            "dimensions": {...},
            "cell_formats": {...},
            "data_validation": {...}
        },
        "Resources": {...},
        "NSG": {...},
        # ... all sheets
    },
    "vba_macros": {...},
    "formulas": {...}
}
```

**Raw Data Format:**
```json
{
  "0": "Resource_Group",      // Column A
  "1": "",                     // Column B
  "2": "To add resources...", // Column C
  "3": "",                     // Column D
  ...
}
```

This is where your Excel values like `"here"`, `"project1"`, `"myapp"` are stored!

---

### 3️⃣ **JSON File (Intermediate)**

**File:** `LLDtest_comprehensive_data.json` (4.6MB)
**Location:** Project root
**Generated:** Every time automation runs

**Structure:**
```json
{
  "sheets": {
    "Build_ENV": {
      "raw_data": [
        {"0": "Resource_Group", "1": "", "2": "To add resources..."},
        {"0": "Key", "1": "key", "2": "rsg1"},          // ← Your actual data
        {"0": "Name", "1": "resource_group_name", "2": "rsg1"},
        {"0": "Subscription", "1": "subscription", "2": "subscription1"},
        {"0": "Location", "1": "location", "2": "here"} // ← "here" from Excel!
      ],
      "tables": [...],
      "key_value_pairs": {...}
    },
    "Resources": {
      "raw_data": [
        {"0": "Project Name", "1": "project1"},        // ← From Excel!
        {"0": "Abbreviated App Name", "1": "myapp"},    // ← From Excel!
        {"0": "Application Description", "1": "stuff"},
        ...
      ],
      "tables": [...],
      "key_value_pairs": {...}
    }
  }
}
```

---

### 4️⃣ **Data Accessor (Reads JSON)**

**File:** `data_accessor.py`
**Purpose:** Extract and structure data from JSON for Terraform generation

**Key Methods:**
```python
class ExcelDataAccessor:
    def __init__(self, json_file_path: str):
        self.json_file_path = "LLDtest_comprehensive_data.json"
        self.data = self._load_data()  # Load JSON
        self.sheets = self.data.get('sheets', {})
    
    def get_terraform_ready_data(self) -> Dict[str, Any]:
        """Extract data in format ready for Terraform generation."""
        # Extracts:
        # - project_info
        # - vm_instances
        # - build_environment
        # - security_groups
        # - ... all structured data
```

**What it does:**
1. Reads `LLDtest_comprehensive_data.json`
2. Extracts structured data from `sheets`
3. Builds `terraform_data` dictionary
4. Returns structured data for generator

---

### 5️⃣ **Terraform Generator (Uses Data)**

**File:** `enhanced_terraform_generator_v2.py`
**Purpose:** Generate Terraform files from structured JSON data

**Initialization:**
```python
class EnhancedTerraformGeneratorV2:
    def __init__(self, json_file_path: str):
        self.accessor = ExcelDataAccessor(json_file_path)  # ← Reads JSON!
        self.terraform_data = self.accessor.get_terraform_ready_data()
        
        # Your new code: Build raw_data cache
        self.raw_data_cache = {}
        self._build_raw_data_cache()  # ← Extracts raw_data from JSON
    
    def _build_raw_data_cache(self):
        """Build a cache of raw_data values for quick lookup."""
        comprehensive_data = self.terraform_data.get('comprehensive_data', {})
        
        for sheet_name, sheet_data in comprehensive_data.items():
            raw_data = sheet_data.get('raw_data', [])
            # Parses raw_data from JSON to create lookup cache
            for row in raw_data:
                var_name = row.get('1')  # Column B (variable name)
                value = row.get('2')      # Column C (actual value)
```

**Your New Code:**
```python
def _get_raw_value(self, var_name: str, sheet_name: str = 'Build_ENV', default: Any = None):
    """Get a value from raw_data cache.
    
    This reads directly from the JSON's raw_data structure.
    For example:
    - var_name='location' → Returns 'here'
    - var_name='sku_name' → Returns value from Excel column 2 where column 1='sku_name'
    """
    return self.raw_data_cache.get(sheet_name, {}).get(var_name, default)
```

---

### 6️⃣ **How Your New Code Works**

**JSON Structure It Uses:**
```json
{
  "sheets": {
    "Build_ENV": {
      "raw_data": [
        {"0": "Location", "1": "location", "2": "here"},
        {"0": "sku_name", "1": "sku_name", "2": "standard"},
        {"0": "soft_delete_retention_days", "1": "soft_delete_retention_days", "2": "90"}
      ]
    }
  }
}
```

**Your Code:**
```python
# In _build_raw_data_cache():
for row in raw_data:
    var_name = row.get('1')  # Gets "location", "sku_name", etc.
    value = row.get('2')     # Gets "here", "standard", "90", etc.
    self.raw_data_cache[sheet_name][var_name] = value

# In _generate_tfvars():
kvlt_sku = self._get_raw_value('sku_name', 'Build_ENV', 'standard')
# Looks up: row['1']='sku_name' → row['2']='standard'
```

---

## File Locations Summary

| Component | File | Size | Purpose |
|-----------|------|------|---------|
| **Excel Source** | `LLDtest.xlsm` | 122KB | Original Excel file |
| **JSON Output** | `LLDtest_comprehensive_data.json` | 4.6MB | Parsed Excel data |
| **Python Extractors** | `excel_to_json_converter.py` | 11KB | Excel → JSON |
| | `comprehensive_excel_extractor.py` | 20KB | Main extraction logic |
| **Python Accessor** | `data_accessor.py` | 30KB | JSON → Structured data |
| **Terraform Generator** | `enhanced_terraform_generator_v2.py` | 145KB | Generates .tf files |
| **Terraform Output** | `output_package/subscription_*/` | ~70KB | Final .tf files |

---

## Key Insight: raw_data Structure

The JSON stores Excel data in a **raw format** where:
- **Column indices** are dictionary keys (`"0"`, `"1"`, `"2"`, etc.)
- **Column 0** = Field names/labels
- **Column 1** = Terraform variable names
- **Column 2** = Actual values ← **This is what you're extracting!**

**Your code accesses this via:**
1. `self.raw_data_cache` - Caches column 1→column 2 mappings
2. `_get_raw_value(var_name, sheet_name)` - Looks up values
3. Returns actual Excel values like `"here"`, `"standard"`, `"90"`

---

## Why This Matters

**Before your changes:**
```python
kvlt_sku = "standard"  # Hardcoded!
```

**After your changes:**
```python
kvlt_sku = self._get_raw_value('sku_name', 'Build_ENV', 'standard')
# Now reads from Excel JSON: "standard" from raw_data!
```

**Result:** Terraform files now use **actual Excel values** instead of hardcoded defaults!

---

## Generation Command

When you run:
```bash
python3 automation_pipeline.py
```

It internally:
1. Calls `convert_excel_to_json()` → Creates `LLDtest_comprehensive_data.json`
2. Loads JSON into `ExcelDataAccessor`
3. Extracts structured data
4. Your code builds `raw_data_cache`
5. `_get_raw_value()` reads from cache
6. Terraform files get actual Excel values!

---

**Your `raw_data` approach is extracting values directly from the Excel→JSON conversion at the most granular level!** 🎯

