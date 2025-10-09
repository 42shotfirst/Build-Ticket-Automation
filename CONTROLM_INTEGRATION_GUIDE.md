# Control-M Integration Guide
## Excel to Terraform Automation Pipeline

This guide explains how to integrate the Excel to Terraform automation pipeline with Control-M for automated, repeatable execution.

## Overview

The automation pipeline provides:
- **Complete Excel data extraction** (all sheets, macros, formulas, metadata)
- **JSON conversion** for easy data processing
- **Terraform file generation** (ready for deployment)
- **External trigger support** (Control-M, cron, etc.)
- **Comprehensive logging and error handling**
- **Repeatable execution** with backup and validation

## Control-M Integration

### 1. Job Definition

Create a Control-M job with the following parameters:

```json
{
  "job_name": "Excel_To_Terraform_Automation",
  "application": "Infrastructure_Automation",
  "job_type": "Command",
  "command": "/path/to/run_automation.sh",
  "arguments": "automation_config.json LLDtest.xlsm terraform_output",
  "working_directory": "/path/to/Build Ticket Automation",
  "description": "Automated Excel to Terraform conversion pipeline",
  "schedule": {
    "frequency": "daily",
    "time": "02:00",
    "timezone": "UTC"
  },
  "retry": {
    "max_attempts": 3,
    "delay_minutes": 15
  },
  "timeout_minutes": 60,
  "notifications": {
    "on_success": true,
    "on_failure": true,
    "email_recipients": ["admin@company.com", "devops@company.com"]
  }
}
```

### 2. Windows Control-M Integration

For Windows environments, use the batch file:

```json
{
  "job_name": "Excel_To_Terraform_Automation_Windows",
  "application": "Infrastructure_Automation",
  "job_type": "Command",
  "command": "C:\\path\\to\\run_automation.bat",
  "arguments": "automation_config.json LLDtest.xlsm terraform_output",
  "working_directory": "C:\\path\\to\\Build Ticket Automation",
  "description": "Automated Excel to Terraform conversion pipeline (Windows)",
  "schedule": {
    "frequency": "daily",
    "time": "02:00",
    "timezone": "UTC"
  }
}
```

### 3. Environment-Specific Configurations

#### Development Environment
```bash
./run_automation.sh controlm_config.json LLDtest.xlsm terraform_dev
```

#### Staging Environment
```bash
./run_automation.sh controlm_config.json LLDtest.xlsm terraform_staging
```

#### Production Environment
```bash
./run_automation.sh controlm_config.json LLDtest.xlsm terraform_prod
```

## Configuration Files

### 1. automation_config.json
Main configuration file for the automation pipeline:
- Input settings (Excel file, required sheets)
- Processing options (macros, formulas, validation)
- Output settings (directories, backup, cleanup)
- Terraform settings (provider version, defaults)
- Logging and notification settings

### 2. controlm_config.json
Control-M specific configuration:
- Control-M job settings
- Environment-specific configurations
- Monitoring and performance settings
- Enhanced validation rules

## File Structure

After successful execution, the following structure is created:

```
Build Ticket Automation/
├── automation_pipeline.py          # Main automation pipeline
├── run_automation.sh               # Linux/Unix runner script
├── run_automation.bat              # Windows runner script
├── automation_config.json          # Main configuration
├── controlm_config.json            # Control-M configuration
├── comprehensive_excel_data.json   # Extracted Excel data
├── terraform_output/               # Generated Terraform files
│   ├── main.tf                     # Main Terraform configuration
│   ├── variables.tf                # Variable definitions
│   ├── terraform.tfvars            # Variable values
│   ├── outputs.tf                  # Output definitions
│   ├── provider.tf                 # Provider configuration
│   ├── README.md                   # Documentation
│   └── deploy.sh                   # Deployment script
├── backup_YYYYMMDD_HHMMSS/         # Backup of previous run
├── automation.log                  # Detailed execution log
└── automation_results_*.json       # Execution results
```

## Exit Codes

The automation pipeline returns specific exit codes for Control-M integration:

- **0**: Success - All steps completed successfully
- **1**: Configuration error - Invalid configuration or missing files
- **2**: Processing error - Failed during Excel extraction or Terraform generation
- **3**: Validation error - Output validation failed

## Monitoring and Alerting

### Success Notifications
- Email notification with summary
- File count and generation details
- Execution duration
- Resource summary (VMs, security rules)

### Failure Notifications
- Detailed error messages
- Step where failure occurred
- Log file location
- Retry information

### Log Files
- **automation.log**: Detailed execution log
- **automation_results_*.json**: Structured results
- **Control-M logs**: Integration with Control-M logging

## Scheduling Options

### Daily Execution
```json
"schedule": {
  "frequency": "daily",
  "time": "02:00",
  "timezone": "UTC"
}
```

### Weekly Execution
```json
"schedule": {
  "frequency": "weekly",
  "day": "monday",
  "time": "01:00",
  "timezone": "UTC"
}
```

### On-Demand Execution
Trigger manually through Control-M interface or API.

## Dependencies

### System Requirements
- Python 3.7 or higher
- Required packages (auto-installed): pandas, openpyxl
- Sufficient disk space for backups and outputs
- Write permissions to output directories

### File Dependencies
- Excel file (.xlsx, .xlsm, .xls)
- Configuration files (JSON format)
- Sufficient memory for large Excel files

## Troubleshooting

### Common Issues

1. **Excel file not found**
   - Verify file path in configuration
   - Check file permissions
   - Ensure file is not locked

2. **Python packages missing**
   - Script auto-installs required packages
   - Check Python installation
   - Verify network connectivity

3. **Output directory issues**
   - Check write permissions
   - Verify disk space
   - Ensure directory path is valid

4. **Terraform generation failures**
   - Check Excel data format
   - Verify configuration settings
   - Review log files for details

### Log Analysis

Check the following log files for troubleshooting:
- `automation.log` - Detailed execution log
- `automation_results_*.json` - Structured results
- Control-M job logs - Integration logs

## Performance Considerations

### Large Excel Files
- Files > 50MB may require more memory
- Consider increasing Python memory limits
- Monitor execution time

### Multiple Environments
- Run environments sequentially to avoid conflicts
- Use separate output directories
- Consider resource scheduling

## Security Considerations

### File Access
- Secure Excel files with sensitive data
- Limit access to automation directories
- Use appropriate file permissions

### Network Security
- Secure Control-M communication
- Use encrypted channels for notifications
- Validate input files

## Best Practices

1. **Test First**: Always test with sample data before production
2. **Backup Strategy**: Enable backup of previous outputs
3. **Monitoring**: Set up proper monitoring and alerting
4. **Documentation**: Keep configuration files documented
5. **Version Control**: Track changes to configuration files
6. **Environment Separation**: Use separate configurations per environment

## Example Control-M Job Flow

```
Excel_To_Terraform_Automation
├── Pre_Validation_Job (optional)
├── Excel_To_Terraform_Conversion
│   ├── Input Validation
│   ├── Excel Data Extraction
│   ├── JSON Conversion
│   ├── Terraform Generation
│   ├── Output Validation
│   └── Cleanup
├── Post_Processing_Job (optional)
└── Notification_Job
```

## Support and Maintenance

### Regular Maintenance
- Review log files weekly
- Update configurations as needed
- Monitor disk space usage
- Update Python packages periodically

### Updates
- Test automation pipeline updates in development
- Update Control-M job definitions as needed
- Maintain configuration file versions
- Document any changes

---

**Note**: This automation pipeline is designed for enterprise use with Control-M. Ensure proper testing in your environment before production deployment.
