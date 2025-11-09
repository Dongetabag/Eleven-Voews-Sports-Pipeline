#!/usr/bin/env python3
"""
Flask dashboard for the Eleven Views Opportunity Engine
"""

from flask import Flask, render_template_string, jsonify, request, send_file
from database import Database
from ai_personalizer import AIPersonalizer
import json
from datetime import datetime
import csv
import io
import os

# Use serverless-compatible logger for Vercel
try:
    from utils.logger_vercel import get_logger
except ImportError:
    from utils.logger import get_logger

# Optional imports for enhanced features
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False

try:
    from api.routes import api_bp
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

app = Flask(__name__)

# Enable CORS if available
if CORS_AVAILABLE:
    CORS(app)

# Rate limiting if available
if LIMITER_AVAILABLE:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per hour"]
    )

# Register API blueprint if available
if API_AVAILABLE:
    try:
        from api.routes import init_limiter
        init_limiter(app)
        app.register_blueprint(api_bp)
        
        # Register HubSpot API routes
        try:
            from api.hubspot_routes import hubspot_bp
            app.register_blueprint(hubspot_bp)
        except Exception as e:
            logger.warning(f"HubSpot API routes not available: {e}")
    except Exception as e:
        logger = get_logger('dashboard')
        logger.warning(f"API routes not available: {e}")

# Initialize services
db = Database()
personalizer = AIPersonalizer()
logger = get_logger('dashboard')

# Security
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# HTML template for dashboard - Eleven Views Luxe Style
DASHBOARD_HTML = """
<!DOCTYPE html>
<html class="dark">
<head>
    <title>Eleven Views Opportunity Engine</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            /* Eleven Views Brand Palette */
            --brand-rich-black: #050505;
            --brand-charcoal: #121212;
            --brand-onyx: #1c1c1c;
            --brand-gold: #d4af37;
            --brand-deep-gold: #b88a1a;
            --brand-light-gold: #f2e4c0;
            
            /* UI Colors */
            --bg-primary: var(--brand-rich-black);
            --bg-secondary: rgba(18, 18, 18, 0.7);
            --surface: rgba(255, 255, 255, 0.04);
            --surface-hover: rgba(255, 255, 255, 0.08);
            --text-primary: #F8F5ED;
            --text-secondary: rgba(248, 245, 237, 0.65);
            --border: rgba(212, 175, 55, 0.18);
            --accent-color: var(--brand-gold);
            --accent-color-rgb: 212, 175, 55;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            padding: 0;
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            position: relative;
            overflow-x: auto;
        }
        
        /* Hexagonal Grid Background */
        .hex-background {
            position: fixed;
            inset: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
            background: var(--bg-primary);
        }
        
        .hex-background svg {
            width: 100%;
            height: 100%;
        }
        
        .hex-background .hex-pattern {
            stroke: rgba(var(--accent-color-rgb), 0.2);
            stroke-opacity: 0.35;
            fill: transparent;
        }
        
        .hex-background .glow-gradient {
            fill: url(#glow-gradient);
            animation: pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.6; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .animate-fadeIn {
            animation: fadeIn 0.5s ease-out;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 24px;
            position: relative;
            z-index: 10;
        }
        
        /* Eleven Views Header */
        header {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            padding: 32px 40px;
            border-radius: 16px;
            margin-bottom: 32px;
            color: var(--text-primary);
            position: relative;
            overflow: hidden;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 12px;
        }
        
        .logo {
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, var(--brand-gold) 0%, var(--brand-deep-gold) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 18px;
            letter-spacing: 1px;
            color: var(--brand-rich-black);
            font-family: 'Orbitron', sans-serif;
            box-shadow: 0 6px 18px rgba(var(--accent-color-rgb), 0.35);
        }
        
        h1 {
            color: var(--text-primary);
            margin: 0;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
            font-family: 'Orbitron', sans-serif;
            background: linear-gradient(135deg, var(--brand-light-gold) 0%, var(--brand-gold) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 16px;
            font-weight: 400;
            margin-top: 8px;
        }
        
        /* Stats Cards - Eleven Views */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: var(--surface);
            backdrop-filter: blur(12px);
            padding: 28px;
            border-radius: 16px;
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(135deg, rgba(var(--accent-color-rgb), 0.6) 0%, rgba(var(--accent-color-rgb), 0.95) 100%);
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            background: var(--surface-hover);
            box-shadow: 0 8px 24px rgba(var(--accent-color-rgb), 0.25);
            border-color: rgba(var(--accent-color-rgb), 0.4);
        }
        
        .stat-value {
            font-size: 42px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;
            letter-spacing: -1px;
            background: linear-gradient(135deg, rgba(var(--accent-color-rgb), 0.35) 0%, rgba(var(--accent-color-rgb), 1) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-family: 'Orbitron', sans-serif;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        
        /* Filters - Eleven Views */
        .filters {
            background: var(--surface);
            backdrop-filter: blur(12px);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid var(--border);
            margin-bottom: 24px;
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filters select, .filters input {
            padding: 12px 16px;
            border: 1px solid var(--border);
            border-radius: 10px;
            font-size: 14px;
            font-family: 'Inter', sans-serif;
            background: rgba(0, 0, 0, 0.3);
            color: var(--text-primary);
            transition: all 0.2s ease;
            font-weight: 500;
        }
        
        .filters select:focus, .filters input:focus {
            outline: none;
            border-color: rgba(var(--accent-color-rgb), 0.5);
            box-shadow: 0 0 0 3px rgba(var(--accent-color-rgb), 0.15);
        }
        
        .filters button {
            padding: 12px 24px;
            background: linear-gradient(135deg, var(--brand-deep-gold) 0%, var(--brand-gold) 100%);
            color: var(--brand-rich-black);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(var(--accent-color-rgb), 0.3);
        }
        
        .filters button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(var(--accent-color-rgb), 0.35);
        }
        
        .filters button:active {
            transform: translateY(0);
        }
        
        .export-btn {
            background: linear-gradient(135deg, #0b8e54 0%, #09ad63 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 10px rgba(9, 173, 99, 0.28) !important;
        }
        
        .export-btn:hover {
            box-shadow: 0 4px 12px rgba(0, 200, 83, 0.4) !important;
        }
        
        .hubspot-btn {
            background: linear-gradient(135deg, #ff9c6a 0%, #ff7a45 100%) !important;
            box-shadow: 0 2px 10px rgba(255, 154, 107, 0.28) !important;
            color: #2a1a00 !important;
        }
        
        .hubspot-btn:hover {
            box-shadow: 0 4px 12px rgba(255, 122, 89, 0.4) !important;
        }
        
        /* Table - Eleven Views */
        .leads-table {
            background: var(--surface);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid var(--border);
            overflow: hidden;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .leads-table table {
            min-width: 860px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background: linear-gradient(135deg, var(--brand-onyx) 0%, rgba(212, 175, 55, 0.1) 100%);
            color: var(--text-primary);
            padding: 16px 20px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Inter', sans-serif;
            border-bottom: 1px solid var(--border);
        }
        
        td {
            padding: 18px 20px;
            border-bottom: 1px solid var(--border);
            font-size: 14px;
            color: var(--text-primary);
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        tr:hover {
            background: var(--surface-hover);
        }
        
        tr {
            transition: background 0.2s ease;
        }
        
        /* Score Badges - Dark Theme */
        .score {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.3px;
        }
        
        .score-high {
            background: rgba(var(--accent-color-rgb), 0.22);
            color: var(--brand-light-gold);
            border: 1px solid rgba(var(--accent-color-rgb), 0.5);
        }
        
        .score-medium {
            background: rgba(255, 193, 7, 0.2);
            color: #FFC107;
            border: 1px solid rgba(255, 193, 7, 0.5);
        }
        
        .score-low {
            background: rgba(244, 67, 54, 0.2);
            color: #F44336;
            border: 1px solid rgba(244, 67, 54, 0.5);
        }
        
        /* Status Badges - Dark Theme */
        .status-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-new { 
            background: rgba(33, 150, 243, 0.2);
            color: #2196F3;
            border: 1px solid rgba(33, 150, 243, 0.5);
        }
        .status-qualified { 
            background: rgba(76, 175, 80, 0.2);
            color: #4CAF50;
            border: 1px solid rgba(76, 175, 80, 0.5);
        }
        .status-contacted { 
            background: rgba(255, 193, 7, 0.2);
            color: #FFC107;
            border: 1px solid rgba(255, 193, 7, 0.5);
        }
        .status-converted { 
            background: rgba(156, 39, 176, 0.2);
            color: #9C27B0;
            border: 1px solid rgba(156, 39, 176, 0.5);
        }
        .status-rejected { 
            background: rgba(244, 67, 54, 0.2);
            color: #F44336;
            border: 1px solid rgba(244, 67, 54, 0.5);
        }
        
        /* Modal - Eleven Views */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: var(--surface);
            backdrop-filter: blur(12px);
            padding: 40px;
            border-radius: 20px;
            max-width: 700px;
            width: 90%;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border);
        }
        
        .modal-content h2 {
            color: var(--text-primary);
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            font-family: 'Orbitron', sans-serif;
            background: linear-gradient(135deg, rgba(var(--accent-color-rgb), 0.4) 0%, rgba(var(--accent-color-rgb), 1) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .modal-content h3 {
            color: var(--text-primary);
            font-size: 18px;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 12px;
            font-family: 'Inter', sans-serif;
        }
        
        .modal-close {
            float: right;
            font-size: 32px;
            cursor: pointer;
            color: var(--text-secondary);
            font-weight: 300;
            line-height: 1;
            transition: color 0.2s ease;
        }
        
        .modal-close:hover {
            color: var(--text-primary);
        }
        
        .outreach-message {
            background: rgba(0, 0, 0, 0.3);
            padding: 24px;
            border-radius: 12px;
            margin: 20px 0;
            white-space: pre-wrap;
            line-height: 1.8;
            border-left: 4px solid rgba(var(--accent-color-rgb), 0.7);
            font-size: 14px;
            color: var(--text-primary);
        }
        
        .copy-btn {
            background: linear-gradient(135deg, #00C853 0%, #00B045 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 200, 83, 0.3);
            margin-top: 12px;
        }
        
        .copy-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 200, 83, 0.4);
        }
        
        /* Loading State */
        .loading {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
            font-size: 16px;
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 80px 20px;
            color: var(--text-secondary);
        }
        
        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .empty-state-text {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--text-primary);
        }
        
        .empty-state-subtext {
            font-size: 14px;
            color: var(--text-secondary);
        }
        
        /* Action Buttons - Dark Theme */
        .action-btn {
            padding: 8px 16px;
            margin: 2px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, rgba(var(--accent-color-rgb), 0.35) 0%, rgba(var(--accent-color-rgb), 0.85) 100%);
            color: var(--brand-rich-black);
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(var(--accent-color-rgb), 0.25);
        }
        
        .action-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(var(--accent-color-rgb), 0.3);
        }
        
        .view-btn { 
            background: linear-gradient(135deg, rgba(255, 215, 128, 0.85) 0%, rgba(var(--accent-color-rgb), 0.95) 100%);
            box-shadow: 0 2px 6px rgba(var(--accent-color-rgb), 0.3);
        }
        .view-btn:hover { 
            box-shadow: 0 4px 12px rgba(var(--accent-color-rgb), 0.4);
        }
        
        a {
            color: rgba(var(--accent-color-rgb), 0.85);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }
        
        a:hover {
            color: var(--brand-light-gold);
            text-decoration: underline;
        }
        
        /* Search Panel Styles */
        .search-panel {
            background: var(--surface);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 32px;
            display: none;
        }
        
        .search-panel.active {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }
        
        .search-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        
        .search-header h2 {
            font-size: 20px;
            margin: 0;
        }
        
        .close-search-btn {
            background: transparent !important;
            border: none !important;
            color: var(--text-secondary) !important;
            font-size: 28px !important;
            cursor: pointer;
            padding: 0 !important;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s ease;
        }
        
        .close-search-btn:hover {
            background: var(--surface-hover) !important;
            color: var(--text-primary) !important;
        }
        
        .search-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        
        .search-field {
            display: flex;
            flex-direction: column;
        }
        
        .search-field label {
            color: var(--text-primary);
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .search-field input,
        .search-field select {
            padding: 12px 16px;
            border: 1px solid var(--border);
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.3);
            color: var(--text-primary);
            font-size: 14px;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease;
        }
        
        .search-field input:focus,
        .search-field select:focus {
            outline: none;
            border-color: rgba(var(--accent-color-rgb), 0.5);
            box-shadow: 0 0 0 3px rgba(var(--accent-color-rgb), 0.15);
        }
        
        .search-field small {
            color: var(--text-secondary);
            font-size: 11px;
            margin-top: 4px;
        }
        
        .filter-metrics {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            border: 1px solid var(--border);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
        }
        
        .metric-field {
            display: flex;
            flex-direction: column;
        }
        
        .metric-field label {
            color: var(--text-secondary);
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 6px;
        }
        
        .metric-field input[type="number"] {
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.3);
            color: var(--text-primary);
            font-size: 14px;
        }
        
        .metric-field input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: rgba(var(--accent-color-rgb), 1);
        }
        
        .search-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }
        
        .search-btn {
            padding: 14px 32px;
            background: linear-gradient(135deg, var(--brand-deep-gold) 0%, var(--brand-gold) 100%);
            color: var(--brand-rich-black);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(var(--accent-color-rgb), 0.3);
            min-width: 180px;
        }
        
        .search-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(var(--accent-color-rgb), 0.4);
        }
        
        .search-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .cancel-search-btn {
            padding: 14px 24px;
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease;
        }
        
        .cancel-search-btn:hover {
            background: var(--surface-hover);
            color: var(--text-primary);
        }
        
        .new-search-btn {
            margin-right: auto;
        }
        
        .new-search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(var(--accent-color-rgb), 0.4);
        }
        
        /* Search Status Message */
        .search-status {
            background: rgba(var(--accent-color-rgb), 0.12);
            border: 1px solid rgba(var(--accent-color-rgb), 0.4);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            display: none;
        }
        
        .search-status.active {
            display: block;
        }
        
        .search-status.success {
            background: rgba(76, 175, 80, 0.1);
            border-color: #4CAF50;
        }
        
        .search-status.error {
            background: rgba(244, 67, 54, 0.1);
            border-color: #F44336;
        }
        
        @media (max-width: 1024px) {
            .container {
                padding: 20px;
            }
            
            .stats {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }
            
            .filters {
                padding: 20px;
            }
        }
        
        @media (max-width: 768px) {
            body {
                font-size: 15px;
            }
            
            .hex-background {
                display: none;
            }
            
            .container {
                padding: 18px;
            }
            
            header {
                padding: 20px;
            }
            
            .logo-section {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .stats {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            
            .filters {
                flex-direction: column;
                align-items: stretch;
                gap: 12px;
            }
            
            .filters button,
            .filters select,
            .filters input,
            .filters .new-search-btn,
            .filters .nav-link-btn {
                width: 100%;
            }
            
            .search-actions {
                flex-direction: column;
                gap: 10px;
            }
            
            .search-actions button {
                width: 100%;
            }
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 16px;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .leads-table table {
                min-width: 640px;
            }
            
            .stat-card {
                padding: 22px;
            }
            
            .search-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 480px) {
            h1 {
                font-size: 26px;
            }
            
            .filters {
                padding: 16px;
            }
            
            .filters button,
            .search-btn {
                font-size: 14px;
                padding: 12px 18px;
            }
            
            .stat-value {
                font-size: 32px;
            }
            
            .modal-content {
                padding: 28px;
            }
        }
    </style>
</head>
<body>
    <!-- Hexagonal Grid Background -->
    <div class="hex-background">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="hex-pattern" patternUnits="userSpaceOnUse" width="100" height="115.47" x="50%" y="50%">
                    <g>
                        <path
                            d="M50 0 L100 28.8675 V86.6025 L50 115.47 L0 86.6025 V28.8675 Z"
                            stroke-width="1"
                            class="hex-pattern"
                        />
                    </g>
                </pattern>
                <radialGradient id="glow-gradient">
                    <stop offset="0%" stop-color="#00BFFF" stop-opacity="0.3" />
                    <stop offset="100%" stop-color="#00BFFF" stop-opacity="0" />
                </radialGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#hex-pattern)" />
            <rect width="100%" height="100%" fill="url(#glow-gradient)" class="glow-gradient" />
        </svg>
    </div>
    
    <div class="container animate-fadeIn">
        <header>
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo">EV</div>
                    <div>
                        <h1>ELEVEN VIEWS</h1>
                        <p class="subtitle">Luxury Production & Sports Management Pipeline</p>
                    </div>
                </div>
            </div>
        </header>
        
        <!-- Lead Search Form -->
        <div class="search-panel" id="search-panel">
            <div class="search-header">
                <h2 style="font-family: 'Orbitron', sans-serif; margin: 0; background: linear-gradient(135deg, var(--brand-light-gold) 0%, var(--brand-gold) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🔍 Curate New Opportunities</h2>
                <button class="close-search-btn" onclick="toggleSearchPanel()" style="background: transparent; border: none; color: var(--text-secondary); font-size: 24px; cursor: pointer; padding: 0; width: 32px; height: 32px;">×</button>
            </div>
            <form id="lead-search-form" onsubmit="runLeadSearch(event)">
                <div class="search-grid">
                    <div class="search-field">
                        <label>📍 Primary Market</label>
                        <input type="text" id="search-location" placeholder="e.g., Miami, FL or 33139" required>
                        <small>City, state, region, or ZIP</small>
                    </div>
                    
                    <div class="search-field">
                        <label>🏷️ Focus Segment</label>
                        <select id="search-industry" required>
                            <option value="">Select Industry</option>
                            <option value="professional sports teams">Professional sports teams</option>
                            <option value="minor league clubs">Minor league clubs</option>
                            <option value="college athletic departments">College athletic departments</option>
                            <option value="elite training facilities">Elite training facilities</option>
                            <option value="sports academies">Sports academies</option>
                            <option value="performance therapy centers">Performance therapy centers</option>
                            <option value="sports marketing agencies">Sports marketing agencies</option>
                            <option value="athlete management firms">Athlete management firms</option>
                            <option value="sports tech startups">Sports tech startups</option>
                            <option value="sports content studios">Sports content studios</option>
                            <option value="luxury event venues">Luxury event venues</option>
                            <option value="brand sponsorship teams">Brand sponsorship teams</option>
                            <option value="premium hospitality suites">Premium hospitality suites</option>
                            <option value="sports nonprofits">Sports nonprofits</option>
                            <option value="youth development programs">Youth development programs</option>
                            <option value="custom">Custom (enter below)</option>
                        </select>
                    </div>
                    
                    <div class="search-field" id="custom-industry-field" style="display: none;">
                        <label>✏️ Custom Industry</label>
                        <input type="text" id="search-custom-industry" placeholder="e.g., marketing agencies">
                    </div>
                    
                    <div class="search-field">
                        <label>📏 Catchment Radius</label>
                        <select id="search-radius">
                            <option value="city">City Only</option>
                            <option value="10mi" selected>10 Miles</option>
                            <option value="25mi">25 Miles</option>
                            <option value="50mi">50 Miles</option>
                            <option value="100mi">100 Miles</option>
                        </select>
                    </div>
                    
                    <div class="search-field">
                        <label>📊 Max Results</label>
                        <input type="number" id="search-limit" value="50" min="10" max="200" step="10">
                    </div>
                </div>
                
                <div class="filter-metrics">
                    <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text-primary);">🎯 Filter Metrics</h3>
                    <div class="metrics-grid">
                        <div class="metric-field">
                        <label>⭐ Min Reputation</label>
                            <input type="number" id="search-min-rating" value="4.0" min="1.0" max="5.0" step="0.1">
                        </div>
                        <div class="metric-field">
                        <label>💬 Min Public Signals</label>
                            <input type="number" id="search-min-reviews" value="10" min="0" max="1000" step="5">
                        </div>
                        <div class="metric-field">
                        <label>🎯 Min Fit Score</label>
                            <input type="number" id="search-min-score" value="60" min="0" max="100" step="5">
                        </div>
                        <div class="metric-field">
                            <label>✅ Auto-Qualify</label>
                            <input type="checkbox" id="search-auto-qualify" checked>
                        </div>
                    </div>
                </div>
                
                <div class="search-actions">
                    <button type="submit" class="search-btn" id="search-submit-btn">
                        <span id="search-btn-text">🚀 Generate Leads</span>
                        <span id="search-loading" style="display: none;">⏳ Generating...</span>
                    </button>
                    <button type="button" class="cancel-search-btn" onclick="toggleSearchPanel()">Cancel</button>
                </div>
            </form>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-leads">0</div>
                <div class="stat-label">Total Leads</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="qualified-leads">0</div>
                <div class="stat-label">Qualified</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-score">0</div>
                <div class="stat-label">Avg Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="contacted-leads">0</div>
                <div class="stat-label">Contacted</div>
            </div>
        </div>
        
        <div class="filters">
                    <button class="new-search-btn" onclick="toggleSearchPanel()" style="background: linear-gradient(135deg, var(--brand-deep-gold) 0%, var(--brand-gold) 100%); color: var(--brand-rich-black); padding: 12px 24px; border: none; border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 600; font-family: 'Inter', sans-serif; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(var(--accent-color-rgb), 0.3);">
                🔍 New Market Scan
            </button>
            <a href="/csv-viewer" class="nav-link-btn" style="background: linear-gradient(135deg, var(--brand-deep-gold) 0%, var(--brand-gold) 100%); color: var(--brand-rich-black); padding: 12px 24px; border: none; border-radius: 10px; text-decoration: none; font-size: 14px; font-weight: 600; font-family: 'Inter', sans-serif; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(var(--accent-color-rgb), 0.3); display: inline-block;">
                📊 Deal Room CSVs
            </a>
            <select id="status-filter">
                <option value="">All Statuses</option>
                <option value="new">New</option>
                <option value="qualified">Qualified</option>
                <option value="contacted">Contacted</option>
                <option value="converted">Converted</option>
                <option value="rejected">Rejected</option>
            </select>
            
            <input type="number" id="min-score" placeholder="Min Score" min="0" max="100">
            
            <input type="text" id="city-filter" placeholder="City">
            
            <button onclick="loadLeads()">Filter</button>
            <button onclick="refreshStats()">Refresh</button>
            <button class="export-btn" onclick="exportLeads()">Export to CSV</button>
            <button class="hubspot-btn" onclick="syncToHubSpot()" title="Sync qualified leads to HubSpot">Sync to HubSpot</button>
        </div>
        
        <div class="leads-table">
            <table>
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Business Name</th>
                        <th>Category</th>
                        <th>Location</th>
                        <th>Contact</th>
                        <th>Rating</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="leads-tbody">
                    <tr><td colspan="8" class="loading">Loading leads...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div id="lead-modal" class="modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div id="modal-body"></div>
        </div>
    </div>
    
    <script>
        // Load stats on page load
        refreshStats();
        loadLeads();
        
        function refreshStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total-leads').textContent = data.total_leads;
                    document.getElementById('qualified-leads').textContent = data.by_status.qualified || 0;
                    document.getElementById('avg-score').textContent = data.avg_score;
                    document.getElementById('contacted-leads').textContent = data.by_status.contacted || 0;
                });
        }
        
        function loadLeads() {
            const status = document.getElementById('status-filter').value;
            const minScore = document.getElementById('min-score').value;
            const city = document.getElementById('city-filter').value;
            
            let url = '/api/leads?';
            if (status) url += `status=${status}&`;
            if (minScore) url += `min_score=${minScore}&`;
            if (city) url += `city=${city}&`;
            
            fetch(url)
                .then(r => r.json())
                .then(leads => {
                    const tbody = document.getElementById('leads-tbody');
                    
                    if (leads.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><div class="empty-state-icon">📋</div><div class="empty-state-text">No leads found</div><div class="empty-state-subtext">Try adjusting filters or generate new leads</div></td></tr>';
                        return;
                    }
                    
                    tbody.innerHTML = leads.map(lead => {
                        const scoreClass = lead.ai_lead_score >= 75 ? 'score-high' : lead.ai_lead_score >= 50 ? 'score-medium' : 'score-low';
                        const statusClass = `status-${lead.status}`;
                        
                        return `
                            <tr>
                                <td><span class="score ${scoreClass}">${lead.ai_lead_score || 'N/A'}</span></td>
                                <td><strong>${lead.name}</strong></td>
                                <td>${lead.category || 'N/A'}</td>
                                <td>${lead.city || ''}, ${lead.state || ''}</td>
                                <td>
                                    ${lead.phone ? `📞 ${lead.phone}<br>` : ''}
                                    ${lead.email ? `📧 ${lead.email}<br>` : ''}
                                    ${lead.website ? `<a href="${lead.website}" target="_blank">🌐 Website</a>` : ''}
                                </td>
                                <td>${lead.rating ? `⭐ ${lead.rating}/5 (${lead.review_count})` : 'N/A'}</td>
                                <td><span class="status-badge ${statusClass}">${lead.status}</span></td>
                                <td>
                                    <button class="action-btn view-btn" onclick="viewLead(${lead.id})">View</button>
                                    <button class="action-btn" onclick="updateStatus(${lead.id}, 'qualified')">Qualify</button>
                                </td>
                            </tr>
                        `;
                    }).join('');
                });
        }
        
        function viewLead(leadId) {
            fetch(`/api/leads/${leadId}`)
                .then(r => r.json())
                .then(lead => {
                    const insights = JSON.parse(lead.ai_insights || '[]');
                    const concerns = JSON.parse(lead.ai_concerns || '[]');
                    
                    const modal = document.getElementById('lead-modal');
                    const modalBody = document.getElementById('modal-body');
                    
                    modalBody.innerHTML = `
                        <h2>${lead.name}</h2>
                        <p><strong>Category:</strong> ${lead.category}</p>
                        <p><strong>Location:</strong> ${lead.address}</p>
                        <p><strong>Score:</strong> ${lead.ai_lead_score}/100</p>
                        
                        <h3>AI Insights</h3>
                        <ul>${insights.map(i => `<li>${i}</li>`).join('')}</ul>
                        
                        ${concerns.length > 0 ? `<h3>Concerns</h3><ul>${concerns.map(c => `<li>${c}</li>`).join('')}</ul>` : ''}
                        
                        ${lead.ai_outreach_message ? `
                            <h3>Generated Outreach Message</h3>
                            <div class="outreach-message" id="outreach-${lead.id}">${lead.ai_outreach_message}</div>
                            <button class="copy-btn" onclick="copyOutreach(${lead.id})">Copy Message</button>
                        ` : ''}
                        
                        <h3>Update Status</h3>
                        <select id="status-update-${lead.id}">
                            <option value="new">New</option>
                            <option value="qualified" ${lead.status === 'qualified' ? 'selected' : ''}>Qualified</option>
                            <option value="contacted" ${lead.status === 'contacted' ? 'selected' : ''}>Contacted</option>
                            <option value="converted" ${lead.status === 'converted' ? 'selected' : ''}>Converted</option>
                            <option value="rejected" ${lead.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                        </select>
                        <button class="action-btn" onclick="saveStatus(${lead.id})">Save Status</button>
                    `;
                    
                    modal.style.display = 'flex';
                });
        
        function closeModal() {
            document.getElementById('lead-modal').style.display = 'none';
        }
        
        function copyOutreach(leadId) {
            const text = document.getElementById(`outreach-${leadId}`).textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert('Outreach message copied to clipboard!');
            });
        }
        
        function updateStatus(leadId, status) {
            fetch(`/api/leads/${leadId}/status`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({status: status})
            }).then(() => {
                loadLeads();
                refreshStats();
            });
        }
        
        function saveStatus(leadId) {
            const status = document.getElementById(`status-update-${leadId}`).value;
            updateStatus(leadId, status);
            closeModal();
        }
        
        function exportLeads() {
            const status = document.getElementById('status-filter').value;
            window.location.href = `/api/export?status=${status}`;
        }
        
        function syncToHubSpot() {
            const status = document.getElementById('status-filter').value || 'qualified';
            const minScore = document.getElementById('min-score').value || 70;
            
            if (!confirm(`Sync ${status} leads (min score: ${minScore}) to HubSpot?`)) {
                return;
            }
            
            fetch('/api/v1/hubspot/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': prompt('Enter API Key (or leave blank if not set):') || ''
                },
                body: JSON.stringify({
                    status: status,
                    min_score: parseInt(minScore),
                    batch_size: 100
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Synced ${data.stats.created + data.stats.updated} leads to HubSpot!\n\nCreated: ${data.stats.created}\nUpdated: ${data.stats.updated}\nFailed: ${data.stats.failed}`);
                    refreshStats();
                } else {
                    alert('❌ Sync failed: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(e => {
                alert('❌ Error: ' + e.message);
            });
        }
        
        function toggleSearchPanel() {
            const panel = document.getElementById('search-panel');
            panel.classList.toggle('active');
        }
        
        // Handle custom industry field
        document.addEventListener('DOMContentLoaded', function() {
            const industrySelect = document.getElementById('search-industry');
            const customField = document.getElementById('custom-industry-field');
            
            if (industrySelect) {
                industrySelect.addEventListener('change', function() {
                    if (this.value === 'custom') {
                        customField.style.display = 'block';
                        document.getElementById('search-custom-industry').required = true;
                    } else {
                        customField.style.display = 'none';
                        document.getElementById('search-custom-industry').required = false;
                    }
                });
            }
        });
        
        function runLeadSearch(event) {
            event.preventDefault();
            
            const location = document.getElementById('search-location').value;
            const industry = document.getElementById('search-industry').value;
            const customIndustry = document.getElementById('search-custom-industry').value;
            const radius = document.getElementById('search-radius').value;
            const limit = parseInt(document.getElementById('search-limit').value);
            const minRating = parseFloat(document.getElementById('search-min-rating').value);
            const minReviews = parseInt(document.getElementById('search-min-reviews').value);
            const minScore = parseInt(document.getElementById('search-min-score').value);
            const autoQualify = document.getElementById('search-auto-qualify').checked;
            
            // Build search query
            const finalIndustry = industry === 'custom' ? customIndustry : industry;
            const searchQuery = `${finalIndustry} in ${location}`;
            
            // Show loading state
            const submitBtn = document.getElementById('search-submit-btn');
            const btnText = document.getElementById('search-btn-text');
            const btnLoading = document.getElementById('search-loading');
            
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            
            // Show status message
            showSearchStatus('⏳ Generating leads... This may take 1-2 minutes.', 'info');
            
            // Call API to generate leads
            fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    search_query: searchQuery,
                    location: location,
                    industry: finalIndustry,
                    radius: radius,
                    max_results: limit,
                    min_rating: minRating,
                    min_reviews: minReviews,
                    min_score: minScore,
                    auto_qualify: autoQualify
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showSearchStatus(
                        `✅ Generated ${data.stats.saved || data.stats.total || 0} leads! ${data.stats.qualified || 0} auto-qualified.`,
                        'success'
                    );
                    
                    // Refresh dashboard
                    setTimeout(() => {
                        refreshStats();
                        loadLeads();
                        toggleSearchPanel();
                    }, 1000);
                } else {
                    showSearchStatus('❌ Error: ' + (data.error || 'Failed to generate leads'), 'error');
                }
            })
            .catch(e => {
                showSearchStatus('❌ Error: ' + e.message, 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                btnText.style.display = 'inline';
                btnLoading.style.display = 'none';
            });
        }
        
        function showSearchStatus(message, type) {
            let statusDiv = document.getElementById('search-status');
            if (!statusDiv) {
                statusDiv = document.createElement('div');
                statusDiv.id = 'search-status';
                statusDiv.className = 'search-status';
                const header = document.querySelector('header');
                header.insertAdjacentElement('afterend', statusDiv);
            }
            
            statusDiv.textContent = message;
            statusDiv.className = `search-status active ${type}`;
            statusDiv.style.display = 'block';
            
            if (type === 'success' || type === 'error') {
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 5000);
            }
        }
    </script>
</body>
</html>
"""

# Import CSV viewer
try:
    from csv_viewer import create_csv_viewer_route, CSV_VIEWER_HTML
    create_csv_viewer_route(app)
    CSV_VIEWER_AVAILABLE = True
except Exception as e:
    logger.warning(f"CSV viewer not available: {e}")
    CSV_VIEWER_AVAILABLE = False

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    return jsonify(db.get_stats())

@app.route('/api/leads')
def get_leads():
    """Get leads with filtering"""
    status = request.args.get('status')
    min_score = request.args.get('min_score', type=int)
    city = request.args.get('city')
    
    leads = db.get_leads(
        status=status,
        min_score=min_score,
        city=city,
        limit=100
    )
    
    return jsonify(leads)

@app.route('/api/leads/<int:lead_id>')
def get_lead(lead_id):
    """Get single lead details"""
    leads = db.get_leads(limit=1)
    lead = next((l for l in leads if l['id'] == lead_id), None)
    
    if lead:
        return jsonify(lead)
    return jsonify({'error': 'Lead not found'}), 404

@app.route('/api/leads/<int:lead_id>/status', methods=['POST'])
def update_lead_status_api(lead_id):
    """Update lead status"""
    data = request.json
    status = data.get('status')
    notes = data.get('notes')
    
    db.update_lead_status(lead_id, status, notes)
    
    return jsonify({'success': True})

@app.route('/api/generate', methods=['POST'])
def generate_leads():
    """Generate new leads from dashboard search"""
    try:
        data = request.json or {}
        
        search_query = data.get('search_query', '')
        location = data.get('location', '')
        industry = data.get('industry', '')
        max_results = data.get('max_results', 50)
        min_rating = data.get('min_rating', 4.0)
        min_reviews = data.get('min_reviews', 10)
        min_score = data.get('min_score', 60)
        auto_qualify = data.get('auto_qualify', True)
        
        if not search_query:
            # Build search query from components
            if industry and location:
                search_query = f"{industry} in {location}"
            else:
                return jsonify({'success': False, 'error': 'Search query or location+industry required'}), 400
        
        logger.info(f"Dashboard lead generation request: {search_query}")
        
        # Import and run lead generator
        from lead_generator import LeadGenerator
        generator = LeadGenerator()
        
        # Generate leads
        stats = generator.process_leads(
            search_query=search_query,
            max_results=max_results,
            min_score=min_score
        )
        
        # Auto-qualify high-rated leads if enabled
        if auto_qualify:
            all_leads = db.get_leads(limit=10000)
            # Get most recently added leads (last batch)
            recent_leads = all_leads[:max_results] if len(all_leads) >= max_results else all_leads
            
            qualified_count = 0
            for lead in recent_leads:
                rating = lead.get('rating', 0) or 0
                review_count = lead.get('review_count', 0) or 0
                
                # Qualify if meets criteria
                if rating >= min_rating and review_count >= min_reviews:
                    if rating >= 4.5 and review_count >= 20:
                        db.update_lead_status(lead['id'], 'qualified', f'Auto-qualified: {rating}⭐ with {review_count} reviews')
                        qualified_count += 1
            
            stats['auto_qualified'] = qualified_count
        
        return jsonify({
            'success': True,
            'stats': stats,
            'search_query': search_query
        })
        
    except Exception as e:
        logger.error(f"Error generating leads: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export')
def export_leads():
    """Export leads to CSV"""
    status = request.args.get('status')
    leads = db.export_leads(status=status)
    
    # Create CSV
    output = io.StringIO()
    if leads:
        fieldnames = ['name', 'category', 'city', 'state', 'phone', 'email', 'website', 
                     'rating', 'review_count', 'ai_lead_score', 'status', 'ai_outreach_message']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(leads)
    
    # Convert to bytes
    output.seek(0)
    bytes_output = io.BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)
    
    filename = f"leads_{status or 'all'}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 ELEVEN VIEWS OPPORTUNITY ENGINE DASHBOARD")
    print("="*60)
    print("\n📊 Dashboard: http://localhost:5000")
    print("🔄 Refresh to see new leads")
    print("📤 Export curated targets to CSV")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
