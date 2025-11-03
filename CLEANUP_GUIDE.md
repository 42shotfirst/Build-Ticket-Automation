# Cleanup Legacy Run Material

## Purpose
Remove old run artifacts to make room for processing a new Excel sheet.

---

## What Gets Removed

### ✅ Safe to Remove (Generated Files)

1. **JSON Conversion Outputs:**
   - `LLDtest_comprehensive_data.json` (will be regenerated)
   - `LLDtest_complete_conversion.json`
   - `LLDtest_comprehensive_extract.json`
   - `comprehensive_excel_data.json`
   - `terraform_ready_data.json`
   - `demo_terraform_data.json`

2. **Output Directories:**
   - `output_package/subscription_*/` (old Terraform outputs)
   - `output_package/LLDtest_terraform/` (legacy output)

3. **Backup Directories:**
   - `backup_YYYYMMDD_HHMMSS/` (all old backups)

4. **Automation Results:**
   - Old `automation_results_*.json` files (keeps last 5)

5. **Log Files:**
   - Old `automation_*.log` files (keeps latest)

6. **Temporary Files:**
   - `*.tmp` files
   - `.DS_Store` files
   - `__pycache__/` directories

### ✅ Preserved (Source Files)

- ✓ `LLDtest.xlsm` (your Excel source - **DO NOT DELETE**)
- ✓ All Python scripts (`.py` files)
- ✓ Configuration files (`automation_config.json`, etc.)
- ✓ Documentation files (`.md` files)

---

## How to Clean

### Option 1: Automated Script (Recommended)

```bash
./cleanup_legacy.sh
```

This script will:
1. Show you what will be removed
2. Ask for confirmation
3. Clean up systematically
4. Preserve source files

### Option 2: Manual Cleanup

```bash
# Remove JSON outputs
rm -f LLDtest_comprehensive*.json
rm -f LLDtest_complete*.json
rm -f comprehensive_excel_data.json
rm -f terraform_ready_data.json

# Remove output directories
rm -rf output_package/subscription_*
rm -rf output_package/LLDtest_terraform

# Remove backups
rm -rf backup_*

# Remove old automation results (keep last 5)
ls -t automation_results_*.json | tail -n +6 | xargs rm -f

# Remove temporary files
find . -name "*.tmp" -delete
find . -name ".DS_Store" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

---

## Before Cleaning Up

### Check Your Current Artifacts

```bash
# Count artifacts
echo "JSON files: $(ls -1 *comprehensive*.json 2>/dev/null | wc -l)"
echo "Output dirs: $(ls -d output_package/subscription_* 2>/dev/null | wc -l)"
echo "Backups: $(ls -d backup_* 2>/dev/null | wc -l)"
```

### Important Notes

1. **Excel Source:** Always preserve `LLDtest.xlsm` or `sourcefiles/LLDtest.xlsm`
2. **Latest Output:** Consider keeping the most recent output if you need to reference it
3. **Automation Results:** The script keeps the last 5 results automatically

---

## After Cleanup

Once cleaned, you can:

1. **Insert your new sheet** into `LLDtest.xlsm` (or replace it)
2. **Run automation:**
   ```bash
   python3 automation_pipeline.py
   ```
3. **New artifacts will be generated:**
   - Fresh `LLDtest_comprehensive_data.json`
   - New `output_package/subscription_<timestamp>/`
   - New automation results

---

## Verification

After cleanup, verify:

```bash
# Check what remains
ls -lh *.json           # Should show minimal JSON files
ls -d output_package/*  # Should be empty or minimal
ls -d backup_*          # Should be empty

# Source files still exist
ls -lh *.xlsm           # Your Excel file ✓
ls -lh *.py             # Python scripts ✓
```

---

## Quick Command

For a quick one-liner cleanup (use with caution):

```bash
rm -f LLDtest*.json comprehensive_excel_data.json terraform_ready_data.json demo_terraform_data.json && \
rm -rf output_package/subscription_* output_package/LLDtest_terraform && \
rm -rf backup_* && \
find . -name "*.tmp" -o -name ".DS_Store" | xargs rm -f && \
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

---

## Troubleshooting

**Problem:** "Permission denied"  
**Solution:** Make script executable: `chmod +x cleanup_legacy.sh`

**Problem:** Accidentally deleted source Excel  
**Solution:** Restore from git or backup (if version controlled)

**Problem:** Need to keep specific outputs  
**Solution:** Manually move them before running cleanup, or modify the script

---

**Ready to clean up? Run:** `./cleanup_legacy.sh`

