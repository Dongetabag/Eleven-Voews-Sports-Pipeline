#!/usr/bin/env python3
"""
HubSpot API routes for the Eleven Views Opportunity Engine
"""

from flask import Blueprint, request, jsonify
from database import Database
from integrations.hubspot import get_hubspot
from utils.logger import get_logger
from utils.security import APIKeyAuth

logger = get_logger('hubspot_api')
auth = APIKeyAuth()

# Create HubSpot API blueprint
hubspot_bp = Blueprint('hubspot', __name__, url_prefix='/api/v1/hubspot')

# Initialize services
db = Database()

@hubspot_bp.route('/test', methods=['GET'])
@auth.require_auth
def test_connection():
    """Test HubSpot connection"""
    try:
        hubspot = get_hubspot()
        result = hubspot.test_connection()
        return jsonify(result)
    except Exception as e:
        logger.error(f"HubSpot test error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@hubspot_bp.route('/sync', methods=['POST'])
@auth.require_auth
def sync_leads():
    """Sync leads to HubSpot"""
    try:
        data = request.json or {}
        status = data.get('status', 'qualified')
        min_score = data.get('min_score', 60)
        batch_size = data.get('batch_size', 100)
        
        hubspot = get_hubspot()
        
        if not hubspot.is_enabled():
            return jsonify({
                'success': False,
                'error': 'HubSpot not enabled. Add HUBSPOT_API_KEY to .env'
            }), 400
        
        # Get leads
        leads = db.get_leads(status=status, min_score=min_score, limit=10000)
        
        if not leads:
            return jsonify({
                'success': False,
                'error': 'No leads found matching criteria'
            }), 404
        
        # Sync
        stats = hubspot.sync_leads_batch(leads)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'leads_synced': len(leads)
        })
        
    except Exception as e:
        logger.error(f"HubSpot sync error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@hubspot_bp.route('/sync/<int:lead_id>', methods=['POST'])
@auth.require_auth
def sync_single_lead(lead_id: int):
    """Sync a single lead to HubSpot"""
    try:
        # Get lead from database
        leads = db.get_leads(limit=10000)
        lead = next((l for l in leads if l['id'] == lead_id), None)
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        hubspot = get_hubspot()
        
        if not hubspot.is_enabled():
            return jsonify({
                'success': False,
                'error': 'HubSpot not enabled'
            }), 400
        
        # Sync lead
        result = hubspot.sync_lead(lead)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"HubSpot sync error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500



