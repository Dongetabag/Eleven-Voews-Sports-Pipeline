#!/usr/bin/env python3
"""
Production launch script for the Eleven Views Opportunity Engine
Performs pre-flight checks and launches the system
"""

import os
import sys
import time
from pathlib import Path
from utils.logger import get_logger, ElevenViewsLogger
from utils.monitoring import get_monitor
from utils.backup import DatabaseBackup
from config import validate_config
from database import Database

logger = get_logger('launch')

def preflight_checks():
    """Perform pre-flight system checks"""
    logger.info("="*60)
    logger.info("🚀 ELEVEN VIEWS OPPORTUNITY ENGINE - PRE-FLIGHT CHECKS")
    logger.info("="*60)
    
    checks_passed = True
    
    # Check 1: Python version
    logger.info("✓ Checking Python version...")
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required")
        checks_passed = False
    else:
        logger.info(f"✅ Python {sys.version.split()[0]}")
    
    # Check 2: Environment variables
    logger.info("✓ Checking environment variables...")
    try:
        validate_config()
        logger.info("✅ Configuration valid")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        checks_passed = False
    
    # Check 3: Required directories
    logger.info("✓ Checking directories...")
    required_dirs = ['data', 'logs', 'cache', 'exports', 'backups']
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"✅ {dir_name}/")
    
    # Check 4: Database
    logger.info("✓ Checking database...")
    try:
        db = Database()
        stats = db.get_stats()
        logger.info(f"✅ Database initialized ({stats['total_leads']} leads)")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        checks_passed = False
    
    # Check 5: System resources
    logger.info("✓ Checking system resources...")
    monitor = get_monitor()
    health = monitor.check_health()
    
    if health['status'] == 'healthy':
        logger.info("✅ System resources OK")
    else:
        logger.warning(f"⚠️  System issues: {health.get('issues', [])}")
    
    # Check 6: Create initial backup
    logger.info("✓ Creating initial backup...")
    try:
        backup = DatabaseBackup()
        backup_path = backup.create_backup("pre_launch")
        if backup_path:
            logger.info(f"✅ Backup created: {backup_path}")
    except Exception as e:
        logger.warning(f"⚠️  Backup creation failed: {e}")
    
    logger.info("="*60)
    
    if checks_passed:
        logger.info("✅ ALL PRE-FLIGHT CHECKS PASSED")
        logger.info("="*60)
        return True
    else:
        logger.error("❌ PRE-FLIGHT CHECKS FAILED")
        logger.error("Please fix the issues above before launching")
        logger.info("="*60)
        return False

def launch_dashboard():
    """Launch the dashboard"""
    import socket
    
    # Try to find an available port
    port = 5000
    for p in range(5000, 5010):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', p))
        sock.close()
        if result != 0:
            port = p
            break
    
    logger.info("\n" + "="*60)
    logger.info("🌐 LAUNCHING DASHBOARD")
    logger.info("="*60)
    logger.info(f"Dashboard: http://localhost:{port}")
    logger.info(f"API: http://localhost:{port}/api/v1")
    logger.info(f"Health: http://localhost:{port}/api/v1/health")
    logger.info("\nPress Ctrl+C to stop")
    logger.info("="*60 + "\n")
    
    # Import and run dashboard
    from dashboard import app
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    """Main launch function"""
    # Initialize logging first
    ElevenViewsLogger()
    
    logger.info("Eleven Views Opportunity Engine - Production Launch")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Run pre-flight checks
    if not preflight_checks():
        sys.exit(1)
    
    # Launch
    try:
        launch_dashboard()
    except KeyboardInterrupt:
        logger.info("\n\n⏹️  Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

