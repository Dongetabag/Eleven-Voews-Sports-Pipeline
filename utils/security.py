#!/usr/bin/env python3
"""
Security utilities for authentication, authorization, and input validation
"""

import re
import hashlib
import secrets
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify
from utils.logger import get_logger

logger = get_logger('security')

class SecurityValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        # Check if it's digits with optional + prefix
        return bool(re.match(r'^\+?[1-9]\d{9,14}$', cleaned))
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>]', '', text)
        
        return text.strip()
    
    @staticmethod
    def validate_search_query(query: str) -> tuple[bool, Optional[str]]:
        """
        Validate search query
        
        Returns:
            (is_valid, error_message)
        """
        if not query or len(query.strip()) == 0:
            return False, "Search query cannot be empty"
        
        if len(query) > 200:
            return False, "Search query too long (max 200 characters)"
        
        # Check for SQL injection patterns
        dangerous_patterns = [
            r'(\bOR\b|\bAND\b).*?=.*?',
            r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b)',
            r'[;\'"]',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, "Invalid characters in search query"
        
        return True, None

class APIKeyAuth:
    """Simple API key authentication"""
    
    def __init__(self):
        self.api_keys = set()
        # Load from environment
        import os
        master_key = os.getenv('API_MASTER_KEY')
        if master_key:
            self.api_keys.add(master_key)
    
    def validate_key(self, api_key: Optional[str]) -> bool:
        """Validate API key"""
        if not api_key:
            return False
        return api_key in self.api_keys
    
    def require_auth(self, f):
        """Decorator to require API key authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if not self.validate_key(api_key):
                logger.warning(f"Unauthorized API access attempt from {request.remote_addr}")
                return jsonify({'error': 'Unauthorized'}), 401
            
            return f(*args, **kwargs)
        return decorated_function

# Global instances
_validator = SecurityValidator()
_auth = APIKeyAuth()

def validate_input(data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate input data against schema
    
    Args:
        data: Input data dictionary
        schema: Validation schema
    
    Returns:
        (is_valid, error_message)
    """
    for field, rules in schema.items():
        value = data.get(field)
        
        # Check required
        if rules.get('required') and not value:
            return False, f"Field '{field}' is required"
        
        if value:
            # Check type
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                return False, f"Field '{field}' must be of type {expected_type.__name__}"
            
            # Check min/max length
            if 'min_length' in rules and len(str(value)) < rules['min_length']:
                return False, f"Field '{field}' is too short (min {rules['min_length']})"
            
            if 'max_length' in rules and len(str(value)) > rules['max_length']:
                return False, f"Field '{field}' is too long (max {rules['max_length']})"
            
            # Custom validation
            if 'validator' in rules:
                if not rules['validator'](value):
                    return False, f"Field '{field}' failed validation"
    
    return True, None






