#!/usr/bin/env python3
"""
Module 5: Automation Pipeline
==============================
Main orchestration pipeline for the entire automation process.
Consolidates: automation_pipeline.py
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .extractor import ExcelExtractor
from .generator import TerraformGenerator
from .validator import TerraformValidator


class AutomationPipeline:
    """End-to-end automation pipeline for Excel to Terraform conversion."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the automation pipeline.

        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or self._default_config()
        self.logger = self._setup_logger()
        self.results = {}

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'input': {
                'excel_file': None,
                'input_directory': 'sourcefiles'
            },
            'output': {
                'json_file': 'extracted_data.json',
                'terraform_dir': 'terraform_output',
                'timestamp_dirs': True
            },
            'validation': {
                'enabled': True,
                'strict_mode': False
            },
            'logging': {
                'level': 'INFO',
                'file': 'automation.log'
            }
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('automation_pipeline')
        logger.setLevel(self.config['logging']['level'])

        # Clear existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler(self.config['logging']['file'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def run(self, excel_file: str) -> Dict[str, Any]:
        """
        Run the complete automation pipeline.

        Args:
            excel_file: Path to the Excel file to process

        Returns:
            Results dictionary with status and output paths
        """
        self.logger.info("=" * 80)
        self.logger.info("STARTING AUTOMATION PIPELINE")
        self.logger.info("=" * 80)

        try:
            # Step 1: Extract
            self.logger.info(f"Step 1: Extracting data from {excel_file}")
            json_file = self._run_extraction(excel_file)
            self.results['extraction'] = {'status': 'success', 'output': json_file}

            # Step 2: Generate
            self.logger.info("Step 2: Generating Terraform files")
            terraform_dir = self._run_generation(json_file)
            self.results['generation'] = {'status': 'success', 'output': terraform_dir}

            # Step 3: Validate
            if self.config['validation']['enabled']:
                self.logger.info("Step 3: Validating Terraform configuration")
                validation_report = self._run_validation(terraform_dir)
                self.results['validation'] = validation_report

            self.results['overall_status'] = 'success'
            self.logger.info("Pipeline completed successfully")

        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            self.results['overall_status'] = 'failed'
            self.results['error'] = str(e)

        self.logger.info("=" * 80)
        return self.results

    def _run_extraction(self, excel_file: str) -> str:
        """Run the extraction step."""
        extractor = ExcelExtractor(excel_file)
        data = extractor.extract()

        # Save to JSON
        json_file = self.config['output']['json_file']
        extractor.save_to_json(json_file)

        self.logger.info(f"Extracted data saved to {json_file}")
        return json_file

    def _run_generation(self, json_file: str) -> str:
        """Run the generation step."""
        # Create output directory with timestamp if configured
        output_dir = self.config['output']['terraform_dir']

        if self.config['output']['timestamp_dirs']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.join(output_dir, timestamp)

        generator = TerraformGenerator(json_file)
        files = generator.generate(output_dir)

        self.logger.info(f"Generated {len(files)} Terraform files in {output_dir}")
        return output_dir

    def _run_validation(self, terraform_dir: str) -> Dict[str, Any]:
        """Run the validation step."""
        validator = TerraformValidator(terraform_dir)
        report = validator.validate_all()

        # Print report
        validator.print_report(report)

        # Check if validation passed
        if report['summary']['overall_status'] == 'FAILED':
            if self.config['validation']['strict_mode']:
                raise ValueError("Validation failed in strict mode")
            else:
                self.logger.warning("Validation failed but continuing (non-strict mode)")

        return report
