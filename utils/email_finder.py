#!/usr/bin/env python3
"""
Email finding and verification service integration
Supports multiple providers: Hunter.io, Clearbit, Snov.io
"""

import os
import re
import time
import requests
from typing import Optional, Dict, List
from urllib.parse import urlparse
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()

logger = get_logger('email_finder')

class EmailFinder:
    """Email finding service with multiple provider support"""
    
    def __init__(self):
        self.hunter_api_key = os.getenv('HUNTER_API_KEY')
        self.clearbit_api_key = os.getenv('CLEARBIT_API_KEY')
        self.snov_api_key = os.getenv('SNOV_API_KEY')
        self.snov_client_id = os.getenv('SNOV_CLIENT_ID')
        self.snov_client_secret = os.getenv('SNOV_CLIENT_SECRET')
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 0.5  # 500ms between requests
        
        # Provider priority (try in order)
        self.providers = []
        if self.hunter_api_key:
            self.providers.append('hunter')
        if self.clearbit_api_key:
            self.providers.append('clearbit')
        if self.snov_api_key:
            self.providers.append('snov')
        
        if not self.providers:
            logger.warning("No email finder API keys configured. Email finding will be limited.")
    
    def _rate_limit(self, provider: str):
        """Enforce rate limiting"""
        if provider in self.last_request_time:
            elapsed = time.time() - self.last_request_time[provider]
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time[provider] = time.time()
    
    def find_email_hunter(self, domain: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[Dict]:
        """Find email using Hunter.io"""
        if not self.hunter_api_key:
            return None
        
        try:
            self._rate_limit('hunter')
            
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.hunter_api_key,
                'limit': 10
            }
            
            if first_name and last_name:
                params['first_name'] = first_name
                params['last_name'] = last_name
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('emails'):
                emails = data['data']['emails']
                # Return the most likely email (usually first one)
                best_email = emails[0]
                return {
                    'email': best_email.get('value'),
                    'confidence': best_email.get('confidence_score', 0),
                    'sources': best_email.get('sources', []),
                    'provider': 'hunter'
                }
        except Exception as e:
            logger.error(f"Hunter.io email finder error: {e}")
        
        return None
    
    def find_email_clearbit(self, domain: str) -> Optional[Dict]:
        """Find email using Clearbit"""
        if not self.clearbit_api_key:
            return None
        
        try:
            self._rate_limit('clearbit')
            
            # Clearbit Enrichment API
            url = f"https://company.clearbit.com/v2/companies/find"
            headers = {'Authorization': f'Bearer {self.clearbit_api_key}'}
            params = {'domain': domain}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Clearbit doesn't directly provide emails, but we can construct common patterns
                if data.get('domain'):
                    return {
                        'email': f"info@{data['domain']}",
                        'confidence': 50,
                        'provider': 'clearbit',
                        'pattern': 'generic'
                    }
        except Exception as e:
            logger.debug(f"Clearbit email finder error: {e}")
        
        return None
    
    def find_email_snov(self, domain: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[Dict]:
        """Find email using Snov.io"""
        if not self.snov_api_key:
            return None
        
        try:
            self._rate_limit('snov')
            
            # Snov.io requires OAuth token first
            if not hasattr(self, '_snov_token'):
                token_url = "https://api.snov.io/v1/oauth/access_token"
                token_params = {
                    'grant_type': 'client_credentials',
                    'client_id': self.snov_client_id,
                    'client_secret': self.snov_client_secret
                }
                token_response = requests.post(token_url, data=token_params, timeout=10)
                if token_response.status_code == 200:
                    self._snov_token = token_response.json().get('access_token')
                else:
                    return None
            
            # Find emails
            url = "https://api.snov.io/v1/get-domain-emails-with-info"
            params = {
                'access_token': self._snov_token,
                'domain': domain,
                'limit': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') and data['result'].get('emails'):
                emails = data['result']['emails']
                best_email = emails[0]
                return {
                    'email': best_email.get('email'),
                    'confidence': best_email.get('verification', {}).get('status') == 'valid' and 90 or 50,
                    'provider': 'snov'
                }
        except Exception as e:
            logger.debug(f"Snov.io email finder error: {e}")
        
        return None
    
    def find_email(self, domain: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[str]:
        """
        Find email address for a domain using available providers
        
        Args:
            domain: Company domain (e.g., 'example.com')
            first_name: Optional first name
            last_name: Optional last name
        
        Returns:
            Email address or None
        """
        if not domain:
            return None
        
        # Clean domain
        domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
        domain = domain.split('?')[0]
        
        # Try each provider in order
        for provider in self.providers:
            try:
                if provider == 'hunter':
                    result = self.find_email_hunter(domain, first_name, last_name)
                elif provider == 'clearbit':
                    result = self.find_email_clearbit(domain)
                elif provider == 'snov':
                    result = self.find_email_snov(domain, first_name, last_name)
                else:
                    continue
                
                if result and result.get('email'):
                    logger.info(f"Found email via {result['provider']}: {result['email']} (confidence: {result.get('confidence', 0)})")
                    return result['email']
            except Exception as e:
                logger.warning(f"Email finder {provider} failed: {e}")
                continue
        
        # Fallback: Generate common email patterns
        logger.debug(f"No email found via APIs, generating pattern for {domain}")
        return self._generate_email_pattern(domain)
    
    def _generate_email_pattern(self, domain: str) -> str:
        """Generate common email patterns as fallback"""
        patterns = [
            f"info@{domain}",
            f"hello@{domain}",
            f"contact@{domain}",
            f"sales@{domain}",
            f"support@{domain}"
        ]
        return patterns[0]  # Return most common pattern
    
    def verify_email(self, email: str) -> Dict:
        """
        Verify email address validity
        
        Args:
            email: Email address to verify
        
        Returns:
            Dict with verification results
        """
        if not email or '@' not in email:
            return {'valid': False, 'reason': 'invalid_format'}
        
        # Basic format validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return {'valid': False, 'reason': 'invalid_format'}
        
        # If Hunter.io is available, use their verification
        if self.hunter_api_key:
            try:
                self._rate_limit('hunter')
                url = "https://api.hunter.io/v2/email-verifier"
                params = {
                    'email': email,
                    'api_key': self.hunter_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                result = data.get('data', {})
                return {
                    'valid': result.get('result') == 'deliverable',
                    'reason': result.get('result'),
                    'score': result.get('score', 0),
                    'provider': 'hunter'
                }
            except Exception as e:
                logger.debug(f"Email verification error: {e}")
        
        # Fallback: Basic validation only
        return {
            'valid': True,
            'reason': 'format_valid',
            'score': 50,
            'provider': 'basic'
        }

# Global instance
_email_finder = None

def get_email_finder() -> EmailFinder:
    """Get email finder instance"""
    global _email_finder
    if _email_finder is None:
        _email_finder = EmailFinder()
    return _email_finder




