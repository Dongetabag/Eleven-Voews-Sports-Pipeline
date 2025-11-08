#!/usr/bin/env python3
"""
System monitoring and health checks
"""

import time
from typing import Dict, Any
from pathlib import Path
from utils.logger import get_logger
from database import Database
from config import DATABASE_PATH

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = get_logger('monitoring')

class SystemMonitor:
    """Monitor system health and performance"""
    
    def __init__(self):
        self.db = Database()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        return {
            'timestamp': time.time(),
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage(),
            'database': self.get_database_health(),
            'logs': self.get_log_stats()
        }
    
    def get_cpu_usage(self) -> Dict[str, float]:
        """Get CPU usage metrics"""
        if PSUTIL_AVAILABLE:
            return {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count()
            }
        return {'percent': 0, 'count': 0, 'note': 'psutil not available'}
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage metrics"""
        if PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            return {
                'total_gb': round(mem.total / (1024**3), 2),
                'available_gb': round(mem.available / (1024**3), 2),
                'used_gb': round(mem.used / (1024**3), 2),
                'percent': mem.percent
            }
        return {'note': 'psutil not available'}
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage metrics"""
        if PSUTIL_AVAILABLE:
            disk = psutil.disk_usage('/')
            return {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent': disk.percent
            }
        return {'note': 'psutil not available'}
    
    def get_database_health(self) -> Dict[str, Any]:
        """Get database health metrics"""
        try:
            db_path = Path(DATABASE_PATH)
            if not db_path.exists():
                return {'status': 'error', 'message': 'Database file not found'}
            
            stats = self.db.get_stats()
            db_size_mb = db_path.stat().st_size / (1024 * 1024)
            
            return {
                'status': 'healthy',
                'size_mb': round(db_size_mb, 2),
                'total_leads': stats.get('total_leads', 0),
                'avg_score': stats.get('avg_score', 0)
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get log file statistics"""
        log_dir = Path("logs")
        if not log_dir.exists():
            return {'status': 'no_logs'}
        
        log_files = list(log_dir.glob("*.log"))
        total_size = sum(f.stat().st_size for f in log_files)
        
        return {
            'file_count': len(log_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': [f.name for f in log_files[:5]]  # First 5 files
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Perform health check"""
        health = self.get_system_health()
        
        # Determine overall status
        issues = []
        
        if PSUTIL_AVAILABLE:
            if health['cpu'].get('percent', 0) > 90:
                issues.append('High CPU usage')
            
            if health['memory'].get('percent', 0) > 90:
                issues.append('High memory usage')
            
            if health['disk'].get('percent', 0) > 90:
                issues.append('Low disk space')
        
        if health['database'].get('status') != 'healthy':
            issues.append('Database issues')
        
        health['status'] = 'healthy' if not issues else 'degraded'
        health['issues'] = issues
        
        return health

# Global instance
_monitor = None

def get_monitor() -> SystemMonitor:
    """Get monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = SystemMonitor()
    return _monitor

