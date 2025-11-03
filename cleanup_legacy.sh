#!/bin/bash
# Cleanup Legacy Run Material
# Removes old JSON outputs, output directories, and automation artifacts
# Keeps source Excel file and Python scripts

echo "=========================================="
echo "CLEANING UP LEGACY RUN MATERIAL"
echo "=========================================="
echo ""

# Count before
JSON_COUNT=$(ls -1 *comprehensive*.json *complete*.json *extract*.json 2>/dev/null | wc -l)
OUTPUT_COUNT=$(ls -d output_package/subscription_* 2>/dev/null | wc -l)
BACKUP_COUNT=$(ls -d backup_* 2>/dev/null | wc -l)
RESULTS_COUNT=$(ls -1 automation_results_*.json 2>/dev/null | wc -l)

echo "Current artifacts:"
echo "  JSON files: $JSON_COUNT"
echo "  Output directories: $OUTPUT_COUNT"
echo "  Backup directories: $BACKUP_COUNT"
echo "  Automation results: $RESULTS_COUNT"
echo ""

read -p "Remove these artifacts? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

echo ""
echo "Removing..."

# Remove old JSON conversion outputs
echo "  - Old JSON conversion files..."
rm -f LLDtest_comprehensive*.json 2>/dev/null
rm -f LLDtest_complete*.json 2>/dev/null
rm -f LLDtest_comprehensive_extract.json 2>/dev/null
rm -f comprehensive_excel_data.json 2>/dev/null
rm -f terraform_ready_data.json 2>/dev/null
rm -f demo_terraform_data.json 2>/dev/null

# Remove old output directories
echo "  - Old output directories..."
rm -rf output_package/subscription_* 2>/dev/null
rm -rf output_package/LLDtest_terraform 2>/dev/null

# Remove backup directories
echo "  - Backup directories..."
rm -rf backup_* 2>/dev/null

# Remove old automation results (keep last 5)
echo "  - Old automation results (keeping last 5)..."
ls -t automation_results_*.json 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null

# Remove old log files (keep latest)
echo "  - Old log files (keeping latest)..."
ls -t automation_*.log 2>/dev/null | tail -n +2 | xargs rm -f 2>/dev/null

# Remove temporary files
echo "  - Temporary files..."
find . -name "*.tmp" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo ""
echo "=========================================="
echo "CLEANUP COMPLETE!"
echo "=========================================="
echo ""
echo "Remaining files:"
echo "  - Source Excel: LLDtest.xlsm ✓"
echo "  - Python scripts: All preserved ✓"
echo "  - Configuration files: All preserved ✓"
echo ""
echo "Ready for new sheet processing!"

