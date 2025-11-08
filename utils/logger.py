#!/usr/bin/env python3
"""
Enterprise-grade logging system for Eleven Views Opportunity Engine
Supports structured logging, file rotation, and multiple handlers
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)

class ElevenViewsLogger:
    """Centralized logging system"""
    
    _instance: Optional['ElevenViewsLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create root logger
        self.logger = logging.getLogger('eleven_views')
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler (human-readable)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (rotating, human-readable)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'eleven_views.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        self.logger.addHandler(file_handler)
        
        # JSON handler (for log aggregation systems)
        json_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'eleven_views.json.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=10
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(json_handler)
        
        # Error handler (separate file for errors)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'errors.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=20
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(console_formatter)
        self.logger.addHandler(error_handler)
        
        self._initialized = True
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific module"""
        return self.logger.getChild(name)
    
    def log_lead_generation(
        self,
        search_query: str,
        leads_found: int,
        leads_saved: int,
        leads_qualified: int,
        duration_seconds: float,
        errors: int = 0
    ):
        """Log lead generation metrics"""
        self.logger.info(
            "Lead generation completed",
            extra={
                'event_type': 'lead_generation',
                'search_query': search_query,
                'leads_found': leads_found,
                'leads_saved': leads_saved,
                'leads_qualified': leads_qualified,
                'duration_seconds': duration_seconds,
                'errors': errors,
                'success_rate': (leads_saved / leads_found * 100) if leads_found > 0 else 0
            }
        )
    
    def log_api_call(
        self,
        service: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        error: Optional[str] = None
    ):
        """Log API call metrics"""
        level = logging.ERROR if error else logging.INFO
        self.logger.log(
            level,
            f"API call: {service} {endpoint}",
            extra={
                'event_type': 'api_call',
                'service': service,
                'endpoint': endpoint,
                'status_code': status_code,
                'duration_ms': duration_ms,
                'error': error
            }
        )
    
    def log_ai_request(
        self,
        model: str,
        tokens_used: int,
        duration_ms: float,
        cost: float,
        error: Optional[str] = None
    ):
        """Log AI API usage"""
        level = logging.ERROR if error else logging.INFO
        self.logger.log(
            level,
            f"AI request: {model}",
            extra={
                'event_type': 'ai_request',
                'model': model,
                'tokens_used': tokens_used,
                'duration_ms': duration_ms,
                'cost': cost,
                'error': error
            }
        )

# Global logger instance
_logger_instance = ElevenViewsLogger()

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return _logger_instance.get_logger(name)

def log_lead_generation(**kwargs):
    """Convenience function for lead generation logging"""
    _logger_instance.log_lead_generation(**kwargs)

def log_api_call(**kwargs):
    """Convenience function for API call logging"""
    _logger_instance.log_api_call(**kwargs)

def log_ai_request(**kwargs):
    """Convenience function for AI request logging"""
    _logger_instance.log_ai_request(**kwargs)


# Backwards compatibility alias
RecipeLabsLogger = ElevenViewsLogger


