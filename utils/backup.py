#!/usr/bin/env python3
"""
Database backup and restore utilities
"""

import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
from utils.logger import get_logger
from config import DATABASE_PATH

logger = get_logger('backup')

class DatabaseBackup:
    """Database backup manager"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.db_path = Path(DATABASE_PATH)
    
    def create_backup(self, suffix: Optional[str] = None) -> Path:
        """
        Create a backup of the database
        
        Args:
            suffix: Optional suffix for backup filename
        
        Returns:
            Path to backup file
        """
        if not self.db_path.exists():
            logger.warning(f"Database not found at {self.db_path}")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"leads_backup_{timestamp}"
        if suffix:
            backup_name += f"_{suffix}"
        backup_name += ".db"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Use SQLite backup API for safe backup
            source = sqlite3.connect(self.db_path)
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
            source.close()
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            return None
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            True if successful
        """
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Create backup of current database first
            current_backup = self.create_backup("pre_restore")
            if current_backup:
                logger.info(f"Current database backed up to {current_backup}")
            
            # Restore
            backup = sqlite3.connect(backup_path)
            restored = sqlite3.connect(self.db_path)
            backup.backup(restored)
            restored.close()
            backup.close()
            
            logger.info(f"Database restored from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            return False
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = sorted(
            self.backup_dir.glob("*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                backup.unlink()
                logger.info(f"Removed old backup: {backup}")






