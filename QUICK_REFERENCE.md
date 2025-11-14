# Build Ticket Automation - Quick Reference Card

## Files at a Glance

### PRODUCTION CORE (7 files - DO NOT REMOVE)
```
main.py (142 lines)
  ↓ calls
automation_pipeline.py (800+ lines)
  ├→ comprehensive_excel_extractor.py (500+ lines) - Data extraction
  ├→ data_accessor.py (740+ lines) - Data interface  
  └→ terraform_generator_clean.py (750+ lines) - Terraform output
       └→ excel_data_mapper.py (275+ lines) - Mapping

config.py (167 lines) - Configuration & utilities
```

### UTILITY TOOLS (6 files - optional, can run standalone)
```
vba_macro_extractor.py (248 lines)
  - Extract VBA macros from Excel
  - Called by comprehensive_extractor
  - Can run: python vba_macro_extractor.py <file>

production_readiness_validator.py (411 lines)
  - Validate Terraform for production
  - Can run: python production_readiness_validator.py

terraform_structure_validator.py (452 lines)
  - Validate Terraform structure
  - Can run: python terraform_structure_validator.py

validate_terraform_commas.py (128 lines)
  - Validate comma syntax in Terraform maps
  - Can run: python validate_terraform_commas.py

read_build_data.py (397 lines)
  - Legacy Excel reading utility
  - NOT called from pipeline
  - Status: Possibly redundant

config.py (167 lines)
  - Configuration constants
  - Utility functions
```

### BROKEN (1 file - DELETE)
```
convert_excel.py
  - ERROR: Depends on missing excel_to_json_converter
  - Not used in pipeline
  - Action: git rm convert_excel.py
```

---

## Entry Points

### Main Pipeline Execution
```bash
python main.py                          # Use defaults
python main.py --excel-file data.xlsx   # Single file mode
python main.py --input-dir ./files      # Batch mode
python main.py --dry-run                # Validate only
python main.py --verbose                # Debug output
```

### Standalone Utilities
```bash
python vba_macro_extractor.py <file>
python production_readiness_validator.py
python terraform_structure_validator.py
python validate_terraform_commas.py
```

---

## Data Flow Overview

```
Excel Input (.xlsx/.xlsm)
          ↓
ComprehensiveExcelExtractor
          ↓
    JSON Output
          ↓
ExcelDataAccessor + ExcelDataMapper
          ↓
   Terraform Data
          ↓
TerraformGeneratorClean
          ↓
  Terraform Files (.tf)
   (main.tf, variables.tf,
    terraform.tfvars, etc.)
```

---

## File Dependencies

### No Circular Dependencies Found ✓

### Import Chain
```
main.py
  ↓
AutomationPipeline
  ├→ ComprehensiveExcelExtractor
  │   └→ VBAMacroExtractor
  ├→ ExcelDataAccessor
  └→ TerraformGeneratorClean
      └→ ExcelDataMapper
```

### Unused Dependencies
- config.py only used by read_build_data.py (which is unused)

---

## What Each File Does

| File | Purpose | Type | Status |
|------|---------|------|--------|
| **main.py** | CLI entry point | Core | Active |
| **automation_pipeline.py** | Orchestrate pipeline | Core | Active |
| **comprehensive_excel_extractor.py** | Extract Excel data | Core | Active |
| **data_accessor.py** | Query extracted data | Core | Active |
| **excel_data_mapper.py** | Map to Terraform format | Core | Active |
| **terraform_generator_clean.py** | Generate .tf files | Core | Active |
| **config.py** | Configuration constants | Core | Active |
| **vba_macro_extractor.py** | Extract VBA macros | Utility | Optional |
| **production_readiness_validator.py** | Production checks | Utility | Optional |
| **terraform_structure_validator.py** | Structure validation | Utility | Optional |
| **validate_terraform_commas.py** | Syntax checking | Utility | Optional |
| **read_build_data.py** | Excel reading (legacy) | Utility | Unused |
| **convert_excel.py** | [BROKEN] | Utility | Remove |

---

## Recent Changes (Nov 13-14, 2025)

### Cleanup Commit (5dfc729)
Removed 11 old files:
- enhanced_terraform_generator.py (superseded)
- enhanced_terraform_generator_v2.py (superseded)
- terraform_generator_final.py
- terraform_json_generator.py
- excel_to_terraform.py
- excel_to_json_converter.py (broke convert_excel.py)
- test_*.py (5 files)
- demo_column_referencing.py

Result: Cleaner codebase, but convert_excel.py now broken

---

## Recommended Actions

### IMMEDIATE (Do Now)
```bash
# 1. Delete broken file
git rm convert_excel.py
git commit -m "Remove obsolete convert_excel.py with broken import"

# 2. Verify read_build_data.py isn't used elsewhere
grep -r "read_build_data" /path/to/project --include="*.py"
# If no results outside of this file, archive or remove it

# 3. Test pipeline still works
python main.py --dry-run
```

### FUTURE (Code Quality)
- Split automation_pipeline.py (800+ lines) into smaller modules
- Add consistent type hints to all files
- Add comprehensive docstrings
- Document external integrations (Control-M, cron, etc.)
- Create integration tests
- Document manual validator usage

---

## Production Readiness Checklist

- [x] All production files present
- [x] No circular dependencies
- [x] No syntax errors
- [x] Clean git history
- [x] Recent cleanup removed obsolete code
- [ ] convert_excel.py removed (TODO)
- [ ] read_build_data.py status clarified (TODO)
- [ ] Unit tests added (Future)
- [ ] Integration with Control-M documented (Future)

---

## Critical Files for Backup/Version Control

These 7 files are essential and must be version controlled:
1. main.py
2. automation_pipeline.py
3. comprehensive_excel_extractor.py
4. data_accessor.py
5. excel_data_mapper.py
6. terraform_generator_clean.py
7. config.py

Removing any of these breaks the entire pipeline.

---

## Validation Tools

### For Production Release
```bash
# Check syntax
python -m py_compile *.py

# Check imports
python -c "import automation_pipeline"

# Dry run
python main.py --dry-run

# Optional: Production validation
python production_readiness_validator.py
python terraform_structure_validator.py
python validate_terraform_commas.py
```

---

## File Sizes (Approximate)

| File | Size | Lines |
|------|------|-------|
| automation_pipeline.py | 35 KB | 800+ |
| terraform_generator_clean.py | 26 KB | 750+ |
| data_accessor.py | 34 KB | 740+ |
| comprehensive_excel_extractor.py | 20 KB | 500+ |
| terraform_structure_validator.py | 17 KB | 452+ |
| production_readiness_validator.py | 16 KB | 411+ |
| read_build_data.py | 16 KB | 397+ |
| excel_data_mapper.py | 9 KB | 275+ |
| vba_macro_extractor.py | 9 KB | 248+ |
| validate_terraform_commas.py | 5 KB | 128+ |
| main.py | 4 KB | 142 |
| config.py | 5 KB | 167 |
| convert_excel.py | 2 KB | 66 |
| **TOTAL** | **~213 KB** | **~5,800** |

(Excluding convert_excel.py: 211 KB, 5,734 lines)

---

## Contact Points for External Systems

- Control-M: Calls `python main.py` (main.py)
- Cron jobs: Can call `python main.py [options]`
- Validators: Can be called separately for manual verification
- Output: Terraform files in terraform_clean_*/ directories

---

## Known Issues

1. **convert_excel.py is broken** - Missing dependency excel_to_json_converter
   - Impact: None - not used in pipeline
   - Solution: Delete the file

2. **read_build_data.py possibly unused** - Not called from automation_pipeline
   - Impact: Minimal (only uses config.py)
   - Solution: Verify usage, then archive/delete

3. **automation_pipeline.py is large** - 800+ lines
   - Impact: Hard to maintain/test
   - Solution: Future refactoring opportunity

---

Generated: 2025-11-14
