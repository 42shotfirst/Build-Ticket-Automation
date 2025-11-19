# Backups Directory

This directory contains all backup files for the Build Ticket Automation system.

## Structure

```
backups/
├── archived_runs/     # Historical backup runs from previous versions
├── terraform/         # Terraform output backups (auto-managed)
├── excel/            # Excel file backups
└── configs/          # Configuration file backups
```

## Retention Policy

- **Terraform outputs**: 30 days, max 5 backups
- **Excel files**: 90 days, no limit
- **Configs**: 90 days, max 10 backups

## Auto-Cleanup

The system automatically cleans up old backups based on the retention policy.
To manually trigger cleanup:

```bash
python -m src.cli --cleanup-backups
```

## Archived Runs

The `archived_runs/` directory contains historical backups from the previous system.
These are preserved for reference but are not actively managed.

Date: 2025-11-19
Migration: Legacy backup_* directories consolidated into single location
