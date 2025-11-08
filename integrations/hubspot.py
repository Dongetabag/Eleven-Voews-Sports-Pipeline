#!/usr/bin/env python3
"""
HubSpot CRM Integration for the Eleven Views Opportunity Engine
Syncs luxury sports opportunities directly to HubSpot contacts and companies
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.logger import get_logger
from utils.rate_limiter import get_rate_limiter
from config import HUBSPOT_API_KEY, HUBSPOT_ENABLED

logger = get_logger('hubspot')

class HubSpotIntegration:
    """HubSpot CRM integration"""
    
    def __init__(self):
        """Initialize HubSpot integration"""
        self.api_key = HUBSPOT_API_KEY
        self.enabled = HUBSPOT_ENABLED and bool(self.api_key)
        
        if not self.enabled:
            logger.warning("HubSpot integration disabled - API key not configured")
            self.client = None
            return
        
        try:
            # Try to import HubSpot client
            try:
                from hubspot import HubSpot
                self.client = HubSpot(access_token=self.api_key)
                logger.info("HubSpot integration initialized")
            except ImportError as e:
                logger.warning(f"hubspot-api-client not installed. Install with: pip install hubspot-api-client. Error: {e}")
                self.client = None
                self.enabled = False
            except Exception as e:
                logger.warning(f"HubSpot client initialization error: {e}")
                self.client = None
                self.enabled = False
        except Exception as e:
            logger.error(f"HubSpot initialization error: {e}")
            self.client = None
            self.enabled = False
        
        # Rate limiter (HubSpot allows 100 requests per 10 seconds)
        self.rate_limiter = get_rate_limiter('hubspot', max_calls=90, period=10.0)
    
    def is_enabled(self) -> bool:
        """Check if HubSpot integration is enabled"""
        return self.enabled and self.client is not None
    
    def _map_lead_to_hubspot_contact(self, lead: Dict) -> Dict:
        """
        Map Eleven Views opportunity to HubSpot contact properties
        
        Args:
            lead: Lead dictionary
        
        Returns:
            HubSpot contact properties dictionary
        """
        # Parse insights if they're JSON strings
        insights = lead.get('ai_insights', '')
        if isinstance(insights, str):
            try:
                insights = json.loads(insights) if insights else []
            except:
                insights = []
        
        # Map to HubSpot properties
        properties = {
            'company': lead.get('name', ''),
            'firstname': self._extract_first_name(lead.get('name', '')),
            'lastname': self._extract_last_name(lead.get('name', '')),
            'phone': lead.get('phone', ''),
            'email': lead.get('email', ''),
            'website': lead.get('website', ''),
            'city': lead.get('city', ''),
            'state': lead.get('state', ''),
            'zip': lead.get('postal_code', ''),
            'country': lead.get('country', 'US'),
            'address': lead.get('address', ''),
            
            # Custom properties
            'hs_lead_status': self._map_status_to_hubspot(lead.get('status', 'new')),
            'lead_score': str(lead.get('ai_lead_score', 0)),
            'lead_source': 'Eleven Views Opportunity Engine',
            'industry': lead.get('category', ''),
            'google_rating': str(lead.get('rating', 0)),
            'review_count': str(lead.get('review_count', 0)),
            'ai_insights': ', '.join(insights) if isinstance(insights, list) else str(insights),
            'outreach_message': lead.get('ai_outreach_message', ''),
            'google_maps_url': lead.get('google_maps_url', ''),
        }
        
        # Remove empty values
        return {k: v for k, v in properties.items() if v}
    
    def _extract_first_name(self, name: str) -> str:
        """Extract first name from business name"""
        if not name:
            return ''
        parts = name.split()
        return parts[0] if parts else ''
    
    def _extract_last_name(self, name: str) -> str:
        """Extract last name from business name"""
        if not name:
            return ''
        parts = name.split()
        return parts[-1] if len(parts) > 1 else ''
    
    def _map_status_to_hubspot(self, status: str) -> str:
        """Map Eleven Views status to HubSpot lead status"""
        mapping = {
            'new': 'NEW',
            'qualified': 'QUALIFIED',
            'contacted': 'CONTACTED',
            'converted': 'CONVERTED',
            'rejected': 'REJECTED'
        }
        return mapping.get(status, 'NEW')
    
    def create_contact(self, lead: Dict) -> Optional[str]:
        """
        Create a contact in HubSpot
        
        Args:
            lead: Lead dictionary
        
        Returns:
            HubSpot contact ID or None
        """
        if not self.is_enabled():
            logger.warning("HubSpot integration not enabled")
            return None
        
        try:
            self.rate_limiter.wait_if_needed('hubspot')
            
            properties = self._map_lead_to_hubspot_contact(lead)
            
            # Create contact
            from hubspot.crm.contacts import SimplePublicObjectInputForCreate
            
            response = self.client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=SimplePublicObjectInputForCreate(properties=properties)
            )
            
            contact_id = response.id
            logger.info(f"Created HubSpot contact: {contact_id} for {lead.get('name')}")
            
            return contact_id
            
        except Exception as e:
            logger.error(f"Error creating HubSpot contact for {lead.get('name')}: {e}", exc_info=True)
            return None
    
    def update_contact(self, contact_id: str, lead: Dict) -> bool:
        """
        Update an existing HubSpot contact
        
        Args:
            contact_id: HubSpot contact ID
            lead: Lead dictionary with updated data
        
        Returns:
            True if successful
        """
        if not self.is_enabled():
            return False
        
        try:
            self.rate_limiter.wait_if_needed('hubspot')
            
            properties = self._map_lead_to_hubspot_contact(lead)
            
            from hubspot.crm.contacts import SimplePublicObjectInput
            
            self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input=SimplePublicObjectInput(properties=properties)
            )
            
            logger.info(f"Updated HubSpot contact: {contact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating HubSpot contact {contact_id}: {e}", exc_info=True)
            return False
    
    def find_contact_by_email(self, email: str) -> Optional[str]:
        """
        Find HubSpot contact by email
        
        Args:
            email: Email address
        
        Returns:
            Contact ID or None
        """
        if not self.is_enabled() or not email:
            return None
        
        try:
            self.rate_limiter.wait_if_needed('hubspot')
            
            # Search for contact by email
            from hubspot.crm.contacts import Filter, FilterGroup
            
            filter_group = FilterGroup(
                filters=[
                    Filter(
                        property_name='email',
                        operator='EQ',
                        value=email
                    )
                ]
            )
            
            response = self.client.crm.contacts.search_api.do_search(
                filter_groups=[filter_group],
                limit=1
            )
            
            if response.results and len(response.results) > 0:
                return response.results[0].id
            
            return None
            
        except Exception as e:
            # Contact not found is expected
            logger.debug(f"Contact not found by email {email}: {e}")
            return None
    
    def sync_lead(self, lead: Dict) -> Dict:
        """
        Sync a lead to HubSpot (create or update)
        
        Args:
            lead: Lead dictionary
        
        Returns:
            Dict with sync results
        """
        if not self.is_enabled():
            return {'success': False, 'reason': 'HubSpot not enabled'}
        
        result = {
            'success': False,
            'contact_id': None,
            'action': None
        }
        
        # Try to find existing contact by email
        email = lead.get('email')
        existing_id = None
        
        if email:
            existing_id = self.find_contact_by_email(email)
        
        if existing_id:
            # Update existing contact
            if self.update_contact(existing_id, lead):
                result['success'] = True
                result['contact_id'] = existing_id
                result['action'] = 'updated'
        else:
            # Create new contact
            contact_id = self.create_contact(lead)
            if contact_id:
                result['success'] = True
                result['contact_id'] = contact_id
                result['action'] = 'created'
        
        return result
    
    def sync_leads_batch(self, leads: List[Dict]) -> Dict:
        """
        Sync multiple leads to HubSpot
        
        Args:
            leads: List of lead dictionaries
        
        Returns:
            Summary statistics
        """
        if not self.is_enabled():
            return {'success': False, 'reason': 'HubSpot not enabled'}
        
        stats = {
            'total': len(leads),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        logger.info(f"Syncing {len(leads)} leads to HubSpot...")
        
        for lead in leads:
            try:
                result = self.sync_lead(lead)
                
                if result['success']:
                    if result['action'] == 'created':
                        stats['created'] += 1
                    elif result['action'] == 'updated':
                        stats['updated'] += 1
                else:
                    stats['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Error syncing lead {lead.get('name')}: {e}")
                stats['failed'] += 1
        
        logger.info(f"HubSpot sync complete: {stats['created']} created, {stats['updated']} updated, {stats['failed']} failed")
        
        return stats
    
    def test_connection(self) -> Dict:
        """
        Test HubSpot API connection
        
        Returns:
            Dict with test results
        """
        if not self.is_enabled():
            return {
                'success': False,
                'message': 'HubSpot integration not enabled. Add HUBSPOT_API_KEY to .env'
            }
        
        try:
            self.rate_limiter.wait_if_needed('hubspot')
            
            # Try to get contacts page (simple connection test)
            response = self.client.crm.contacts.basic_api.get_page(limit=1)
            
            return {
                'success': True,
                'message': 'HubSpot connection successful',
                'account_id': 'Connected'
            }
            
        except Exception as e:
            logger.error(f"HubSpot connection test failed: {e}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}'
            }

# Global instance
_hubspot = None

def get_hubspot() -> HubSpotIntegration:
    """Get HubSpot integration instance"""
    global _hubspot
    if _hubspot is None:
        _hubspot = HubSpotIntegration()
    return _hubspot

