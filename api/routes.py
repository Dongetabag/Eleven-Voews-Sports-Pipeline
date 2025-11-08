#!/usr/bin/env python3
"""
REST API routes for the Eleven Views Opportunity Engine
Production-ready API with authentication, rate limiting, and validation
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from database import Database
from lead_generator import LeadGenerator
from utils.logger import get_logger
from utils.security import SecurityValidator, validate_input, APIKeyAuth
from typing import Dict, Any

logger = get_logger('api')
validator = SecurityValidator()
auth = APIKeyAuth()

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
CORS(api_bp)  # Enable CORS for API

# Rate limiter (will be initialized in dashboard.py)
limiter = None

def init_limiter(app):
    """Initialize rate limiter with Flask app"""
    global limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour", "10 per minute"]
    )

# Initialize services
db = Database()
generator = LeadGenerator()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'eleven-views-opportunity-engine',
        'version': '1.0.0'
    })

@api_bp.route('/leads', methods=['GET'])
def get_leads():
    """Get leads with filtering"""
    try:
        status = request.args.get('status')
        min_score = request.args.get('min_score', type=int)
        city = request.args.get('city')
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Validate inputs
        if limit > 1000:
            return jsonify({'error': 'Limit cannot exceed 1000'}), 400
        if limit < 1:
            return jsonify({'error': 'Limit must be at least 1'}), 400
        
        leads = db.get_leads(
            status=status,
            min_score=min_score,
            city=city,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'leads': leads,
            'count': len(leads),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.error(f"Error getting leads: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id: int):
    """Get single lead by ID"""
    try:
        leads = db.get_leads(limit=10000)  # Get all to find by ID
        lead = next((l for l in leads if l['id'] == lead_id), None)
        
        if not lead:
            return jsonify({'error': 'Lead not found'}), 404
        
        return jsonify(lead)
    except Exception as e:
        logger.error(f"Error getting lead {lead_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/leads/generate', methods=['POST'])
@auth.require_auth
def generate_leads():
    """Generate new leads via API"""
    try:
        data = request.json
        
        # Validate input
        schema = {
            'search_query': {'required': True, 'type': str, 'max_length': 200},
            'max_results': {'required': False, 'type': int},
            'min_score': {'required': False, 'type': int},
            'auto_qualify': {'required': False, 'type': bool}
        }
        
        is_valid, error_msg = validate_input(data or {}, schema)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate search query
        search_query = validator.sanitize_input(data['search_query'])
        is_valid, error_msg = validator.validate_search_query(search_query)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Generate leads
        stats = generator.process_leads(
            search_query=search_query,
            max_results=data.get('max_results', 100),
            auto_qualify=data.get('auto_qualify', True),
            min_score=data.get('min_score', 60)
        )
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error generating leads: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/leads/<int:lead_id>/status', methods=['PATCH'])
def update_lead_status(lead_id: int):
    """Update lead status"""
    try:
        data = request.json or {}
        status = data.get('status')
        notes = data.get('notes')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['new', 'qualified', 'contacted', 'converted', 'rejected']
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        # Sanitize notes
        if notes:
            notes = validator.sanitize_input(notes, max_length=1000)
        
        db.update_lead_status(lead_id, status, notes)
        
        return jsonify({'success': True, 'lead_id': lead_id, 'status': status})
    except Exception as e:
        logger.error(f"Error updating lead status: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/search', methods=['GET'])
def search_leads():
    """Search leads by term"""
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        if len(search_term) < 2:
            return jsonify({'error': 'Search term must be at least 2 characters'}), 400
        
        # Sanitize search term
        search_term = validator.sanitize_input(search_term, max_length=100)
        
        limit = request.args.get('limit', default=50, type=int)
        if limit > 200:
            limit = 200
        
        leads = db.search_leads(search_term, limit=limit)
        
        return jsonify({
            'leads': leads,
            'count': len(leads),
            'search_term': search_term
        })
    except Exception as e:
        logger.error(f"Error searching leads: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

