#!/bin/bash
# Excel to Terraform Automation Runner
# designed for Control-M and other external schedulers
# usage: ./run_automation.sh [config_file] [excel_file] [output_dir]

set -e

# config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${1:-automation_config.json}"
EXCEL_FILE="${2:-}"
OUTPUT_DIR="${3:-}"
LOG_FILE="automation_$(date +%Y%m%d_%H%M%S).log"
PYTHON_CMD="python3"

# colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# logging functions
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# main execution
main() {
    log_info "=========================================="
    log_info "Excel to Terraform Automation (Control-M)"
    log_info "=========================================="
    log_info "Script Dir: $SCRIPT_DIR"
    log_info "Config: $CONFIG_FILE"
    log_info "Log: $LOG_FILE"
    log_info "Python: $PYTHON_CMD"
    log_info "=========================================="
    
    cd "$SCRIPT_DIR"
    
    # check python
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        log_error "Python3 not found"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_info "Python Version: $PYTHON_VERSION"
    
    # check packages
    log_info "Checking Python packages..."
    if ! $PYTHON_CMD -c "import pandas, openpyxl" 2>/dev/null; then
        log_error "Required packages not found"
        log_info "Installing: pandas, openpyxl"
        $PYTHON_CMD -m pip install pandas openpyxl
        if [ $? -ne 0 ]; then
            log_error "Failed to install packages"
            exit 1
        fi
        log_success "Packages installed"
    else
        log_success "Packages available"
    fi
    
    # build command for main.py
    CMD="$PYTHON_CMD main.py"
    
    if [ -n "$CONFIG_FILE" ] && [ -f "$CONFIG_FILE" ]; then
        CMD="$CMD --config $CONFIG_FILE"
    fi
    
    if [ -n "$EXCEL_FILE" ]; then
        CMD="$CMD --excel-file $EXCEL_FILE"
    fi
    
    if [ -n "$OUTPUT_DIR" ]; then
        CMD="$CMD --output-dir $OUTPUT_DIR"
    fi
    
    log_info "Executing: $CMD"
    log_info "=========================================="
    
    # run main.py and capture exit code
    if $CMD 2>&1 | tee -a "$LOG_FILE"; then
        EXIT_CODE=${PIPESTATUS[0]}
        
        if [ $EXIT_CODE -eq 0 ]; then
            log_success "Automation completed successfully"
            
            # check for generated files
            if [ -d "output_package" ]; then
                TERRAFORM_DIRS=$(find output_package -mindepth 1 -maxdepth 1 -type d | wc -l)
                log_info "Generated $TERRAFORM_DIRS output folder(s)"
                
                # list output directories
                find output_package -mindepth 1 -maxdepth 1 -type d | while read dir; do
                    log_info "  - $(basename "$dir")"
                done
            fi
            
            log_info "Log saved to: $LOG_FILE"
            exit 0
        else
            log_error "Automation failed (exit code: $EXIT_CODE)"
            log_info "Check log for details: $LOG_FILE"
            exit $EXIT_CODE
        fi
    else
        log_error "Automation failed"
        log_info "Check log for details: $LOG_FILE"
        exit 2
    fi
}

# cleanup handler
cleanup() {
    if [ $? -ne 0 ]; then
        log_warning "Script terminated with errors"
    fi
}

# signal handlers
trap cleanup EXIT INT TERM

# run
main "$@"
