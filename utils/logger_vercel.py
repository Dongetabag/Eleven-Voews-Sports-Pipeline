#!/usr/bin/env python3
"""
Serverless-compatible logging for Vercel deployment
Falls back to stdout/stderr only (no file logging)
"""

import logging
import sys
import os

def get_logger(name: str) -> logging.Logger:
    """Get a serverless-compatible logger instance"""
    logger = logging.getLogger(f'eleven_views.{name}')

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # Console handler only (Vercel captures stdout/stderr)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Stub functions for compatibility
def log_lead_generation(**kwargs):
    """Stub for lead generation logging"""
    logger = get_logger('lead_generation')
    logger.info(f"Lead generation: {kwargs}")

def log_api_call(**kwargs):
    """Stub for API call logging"""
    logger = get_logger('api')
    logger.info(f"API call: {kwargs}")

def log_ai_request(**kwargs):
    """Stub for AI request logging"""
    logger = get_logger('ai')
    logger.info(f"AI request: {kwargs}")
