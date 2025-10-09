# Main Entry Points

## Overview

The automation system has two primary entry points with distinct purposes:

## 1. main.py - Primary Entry Point

**Purpose:** Direct automation execution with full features

**Use Cases:**
- Manual execution
- Development and testing
- Direct command-line usage
- One-off automation runs

**Features:**
- Kicks off complete automation pipeline
- Dynamic output folders (subscription + timestamp)
- Enhanced Terraform generator v2
- Multi-file processing
- Comprehensive validation
- Backup management

**Usage:**
```bash
# process all files in sourcefiles directory
python3 main.py

# process specific file
python3 main.py --excel-file data.xlsx

# process custom directory
python3 main.py --input-dir /path/to/files

# dry run validation
python3 main.py --dry-run

# verbose logging
python3 main.py --verbose

# custom config
python3 main.py --config my_config.json
```

**Command-Line Options:**
```
--config, -c       Configuration file
--excel-file, -e   Excel file to process
--input-dir, -d    Directory with Excel files
--output-dir, -o   Terraform output directory
--dry-run          Validate without processing
--verbose, -v      Enable verbose logging
--no-backup        Skip backup of previous outputs
```

## 2. run_automation.sh - Control-M Wrapper

**Purpose:** External scheduler integration (Control-M, cron, etc.)

**Use Cases:**
- Scheduled automation (Control-M)
- Cron job execution
- Production environments
- External triggering systems
- Automated workflows

**Features:**
- Colored logging with timestamps
- Environment validation
- Python package checking
- Automatic dependency installation
- Exit code handling for schedulers
- Comprehensive log files
- Error tracking for monitoring

**Usage:**
```bash
# default mode (uses automation_config.json)
./run_automation.sh

# with specific config
./run_automation.sh custom_config.json

# with specific excel file
./run_automation.sh automation_config.json data.xlsx

# with custom output dir
./run_automation.sh automation_config.json data.xlsx terraform_out

# Control-M job configuration
./run_automation.sh automation_config.json "" ""
```

**Control-M Integration:**
- Exit code 0 = Success
- Exit code 1 = Environment/dependency error
- Exit code 2 = Processing error
- Log file: `automation_YYYYMMDD_HHMMSS.log`

## Workflow

### main.py Flow:
```
main.py
  └─> AutomationPipeline
       ├─> Validate inputs
       ├─> Backup previous outputs
       ├─> Extract Excel data
       ├─> Generate Terraform files (v2 generator)
       ├─> Validate outputs
       ├─> Generate summary
       └─> Cleanup
```

### run_automation.sh Flow:
```
run_automation.sh
  ├─> Validate environment
  ├─> Check Python/packages
  ├─> Build command
  └─> Execute main.py
       └─> (see main.py flow above)
```

## Relationship

```
┌─────────────────────────┐
│   run_automation.sh     │  ← Control-M/Scheduler
│  (Control-M Wrapper)    │
└───────────┬─────────────┘
            │ calls
            ▼
┌─────────────────────────┐
│       main.py           │  ← Direct Usage
│  (Primary Entry Point)  │
└───────────┬─────────────┘
            │ uses
            ▼
┌─────────────────────────┐
│  automation_pipeline.py │
│  (Core Pipeline Logic)  │
└─────────────────────────┘
```

## When to Use Each

### Use main.py when:
- Running manually
- Development/testing
- Need command-line options
- Want direct control
- Interactive usage

### Use run_automation.sh when:
- Scheduled automation (Control-M)
- Cron jobs
- Production environments
- Need colored logging
- Want environment validation
- External system triggering

## Output Structure

Both create the same output structure:
```
output_package/
├── {subscription}_{timestamp}/
│   ├── m-basevm.tf
│   ├── r-asg.tf
│   ├── r-kvlt.tf
│   ├── r-nsr.tf
│   ├── r-pe.tf
│   ├── r-rg.tf
│   ├── r-snet.tf
│   ├── r-umid.tf
│   ├── r-dsk.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   ├── outputs.tf
│   ├── versions.tf
│   ├── data.tf
│   ├── locals.tf
│   ├── scripts/validate.sh
│   ├── README.md
│   └── .gitignore
└── backup_YYYYMMDD_HHMMSS/
```

## Examples

### Manual Execution:
```bash
# simple run
python3 main.py

# with options
python3 main.py --excel-file sourcefiles/project.xlsx --verbose
```

### Control-M Job:
```bash
# job configuration
Command: /path/to/run_automation.sh
Parameters: automation_config.json
Working Dir: /Users/morganreed/StudioProjects/Build Ticket Automation
On Success: Check exit code = 0
On Failure: Check exit code != 0
Log File: automation_*.log
```

### Cron Job:
```bash
# crontab entry - run daily at 2 AM
0 2 * * * cd /path/to/automation && ./run_automation.sh >> cron.log 2>&1
```

## Configuration

Both use the same configuration file (`automation_config.json`):
```json
{
  "input": {
    "input_directory": "sourcefiles",
    "process_multiple_files": true
  },
  "output": {
    "dynamic_folder_naming": true,
    "folder_naming_pattern": "{subscription}_{timestamp}"
  },
  "terraform": {
    "use_enhanced_generator_v2": true
  }
}
```

## Logs

### main.py logs:
- Console output with timestamps
- Saved to `automation.log` (configured in automation_config.json)
- Python logging module format

### run_automation.sh logs:
- Colored console output
- Saved to `automation_YYYYMMDD_HHMMSS.log` (unique per run)
- Bash logging with timestamps
- Suitable for Control-M monitoring

## Summary

| Feature | main.py | run_automation.sh |
|---------|---------|-------------------|
| **Purpose** | Direct automation | Control-M wrapper |
| **Use** | Manual/Dev | Scheduled/Production |
| **Options** | Full CLI args | Positional args |
| **Logging** | Python logging | Colored bash logging |
| **Validation** | Built-in | Environment + packages |
| **Exit Codes** | Standard | Scheduler-friendly |

**Recommendation:**
- **Development**: Use `main.py`
- **Production/Control-M**: Use `run_automation.sh`
- **Both call the same automation_pipeline.py underneath**

