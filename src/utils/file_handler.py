#!/usr/bin/env python3
"""
Module 7: File Handler Utility
===============================
File operations and backup management.
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
import glob


class FileHandler:
    """Handle file operations and backup management."""

    @staticmethod
    def create_backup(
        source_path: str,
        backup_dir: str = 'backups',
        include_timestamp: bool = True
    ) -> str:
        """
        Create a backup of a file or directory.

        Args:
            source_path: Path to backup
            backup_dir: Directory to store backups
            include_timestamp: Whether to add timestamp to backup name

        Returns:
            Path to the backup
        """
        os.makedirs(backup_dir, exist_ok=True)

        base_name = os.path.basename(source_path)

        if include_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{base_name}_{timestamp}"
        else:
            backup_name = base_name

        backup_path = os.path.join(backup_dir, backup_name)

        if os.path.isfile(source_path):
            shutil.copy2(source_path, backup_path)
        elif os.path.isdir(source_path):
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(source_path, backup_path)

        return backup_path

    @staticmethod
    def cleanup_old_backups(
        backup_dir: str = 'backups',
        max_age_days: Optional[int] = None,
        max_count: Optional[int] = None
    ) -> List[str]:
        """
        Clean up old backup files.

        Args:
            backup_dir: Directory containing backups
            max_age_days: Maximum age of backups to keep (days)
            max_count: Maximum number of backups to keep (keeps newest)

        Returns:
            List of deleted backup paths
        """
        if not os.path.exists(backup_dir):
            return []

        deleted = []

        # Get all items in backup directory
        items = []
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isdir(item_path) or os.path.isfile(item_path):
                mtime = os.path.getmtime(item_path)
                items.append((item_path, mtime))

        # Sort by modification time (newest first)
        items.sort(key=lambda x: x[1], reverse=True)

        # Delete by age
        if max_age_days is not None:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            cutoff_timestamp = cutoff_date.timestamp()

            for item_path, mtime in items:
                if mtime < cutoff_timestamp:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                    deleted.append(item_path)

        # Delete by count (keep only max_count newest)
        if max_count is not None and len(items) > max_count:
            for item_path, _ in items[max_count:]:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                deleted.append(item_path)

        return deleted

    @staticmethod
    def ensure_directory(directory: str):
        """
        Ensure a directory exists, create if it doesn't.

        Args:
            directory: Directory path to ensure
        """
        os.makedirs(directory, exist_ok=True)

    @staticmethod
    def find_files(pattern: str, directory: str = '.') -> List[str]:
        """
        Find files matching a pattern.

        Args:
            pattern: Glob pattern to match
            directory: Directory to search in

        Returns:
            List of matching file paths
        """
        search_pattern = os.path.join(directory, pattern)
        return glob.glob(search_pattern)

    @staticmethod
    def copy_directory_contents(source_dir: str, dest_dir: str):
        """
        Copy all contents from source directory to destination.

        Args:
            source_dir: Source directory
            dest_dir: Destination directory
        """
        os.makedirs(dest_dir, exist_ok=True)

        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            dest_path = os.path.join(dest_dir, item)

            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
