#!/usr/bin/env python3
"""
Eleven Views Opportunity Engine
High-touch pipeline builder for premium production and sports management prospects
Powered by Apify + Google Gemini with enterprise-grade logging, caching, and enrichment
"""

import os
import json
import argparse
import time
from datetime import datetime
from typing import List, Dict, Optional
from apify_client import ApifyClient
import google.generativeai as genai
from dotenv import load_dotenv
from database import Database
from ai_personalizer import AIPersonalizer
from utils.logger import get_logger, log_lead_generation, log_api_call, log_ai_request
from utils.cache import get_cache, cached
from utils.rate_limiter import get_rate_limiter
from utils.email_finder import get_email_finder
from utils.security import SecurityValidator

# Load environment variables
load_dotenv()

logger = get_logger('eleven_views.lead_generator')
validator = SecurityValidator()

class LeadGenerator:
    """Main lead generation orchestrator"""
    
    # Apify Actor ID for Google Maps Scraper
    GOOGLE_MAPS_ACTOR = "nwua9Gu5YrADL7ZDj"
    
    def __init__(self):
        """Initialize the lead generator"""
        apify_token = os.getenv('APIFY_API_TOKEN')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if not apify_token:
            raise ValueError("APIFY_API_TOKEN not found in environment")
        if not google_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        self.apify = ApifyClient(apify_token)
        genai.configure(api_key=google_key)
        self.db = Database()
        self.personalizer = AIPersonalizer()
        self.cache = get_cache()
        self.email_finder = get_email_finder()
        
        # Rate limiters
        self.apify_limiter = get_rate_limiter('apify', max_calls=30, period=60.0)
        self.ai_limiter = get_rate_limiter('google_ai', max_calls=60, period=60.0)
        
        logger.info("LeadGenerator initialized")
    
    def scrape_google_maps(
        self,
        search_query: str,
        max_results: int = 100,
        location: Optional[str] = None,
        min_rating: float = 3.5
    ) -> List[Dict]:
        """
        Scrape businesses from Google Maps using Apify
        
        Args:
            search_query: What to search for (e.g., "marketing agencies in Boston")
            max_results: Maximum number of results to return
            location: Optional location override
            min_rating: Minimum rating filter (1.0-5.0)
        
        Returns:
            List of business dictionaries with enriched data
        """
        start_time = time.time()
        
        # Validate input
        is_valid, error_msg = validator.validate_search_query(search_query)
        if not is_valid:
            logger.error(f"Invalid search query: {error_msg}")
            return []
        
        logger.info(f"Searching Google Maps: '{search_query}' (target: {max_results}, min_rating: {min_rating})")
        
        # Check cache first
        cache_key = f"apify_search:{search_query}:{max_results}:{min_rating}"
        cached_results = self.cache.get(cache_key, ttl=3600)  # 1 hour cache
        if cached_results:
            logger.info(f"Cache hit for search query: {search_query}")
            return cached_results
        
        # Rate limiting
        self.apify_limiter.wait_if_needed('apify')
        
        # Configure Apify actor input
        run_input = {
            "searchStringsArray": [search_query],
            "maxCrawledPlacesPerSearch": max_results,
            "language": "en",
            "includeReviews": False,  # Speed optimization
            "includeImages": False,   # We don't need images
            "includeOpeningHours": True,
            "includePeopleAlsoSearch": False,
            "maxReviews": 0,
            "maxImages": 0,
        }
        
        if location:
            run_input["locationQuery"] = location
        
        try:
            # Run the actor
            logger.debug("Starting Apify scraper...")
            api_start = time.time()
            run = self.apify.actor(self.GOOGLE_MAPS_ACTOR).call(run_input=run_input)
            api_duration = (time.time() - api_start) * 1000
            
            log_api_call(
                service='apify',
                endpoint='google-maps-scraper',
                status_code=200,
                duration_ms=api_duration
            )
            
            # Fetch results from dataset
            logger.debug("Fetching results from Apify dataset...")
            dataset_id = run["defaultDatasetId"]
            items = self.apify.dataset(dataset_id).list_items().items
            
            logger.info(f"Scraped {len(items)} businesses from Apify")
            
            # Filter by rating
            filtered_items = [
                item for item in items 
                if item.get('totalScore', 0) >= min_rating
            ]
            
            logger.info(f"{len(filtered_items)} businesses match rating criteria (min: {min_rating})")
            
            # Cache results
            self.cache.set(cache_key, filtered_items, ttl=3600)
            
            duration = time.time() - start_time
            logger.info(f"Scraping completed in {duration:.2f}s")
            
            return filtered_items
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Error scraping Google Maps: {e}", exc_info=True)
            log_api_call(
                service='apify',
                endpoint='google-maps-scraper',
                status_code=500,
                duration_ms=duration,
                error=str(e)
            )
            return []
    
    def enrich_lead(self, raw_lead: Dict) -> Dict:
        """
        Enrich raw lead data with AI analysis and standardization
        
        Args:
            raw_lead: Raw data from Google Maps
        
        Returns:
            Enriched lead dictionary
        """
        try:
            # Standardize lead data
            enriched = {
                # Basic info
                'name': raw_lead.get('title', ''),
                'category': raw_lead.get('categoryName', ''),
                'address': raw_lead.get('address', ''),
                'city': raw_lead.get('city', ''),
                'state': raw_lead.get('state', ''),
                'postal_code': raw_lead.get('postalCode', ''),
                'country': raw_lead.get('countryCode', 'US'),
                
                # Contact info
                'phone': raw_lead.get('phone', ''),
                'website': raw_lead.get('website', ''),
                'email': self._extract_email(raw_lead),
                
                # Social & reputation
                'rating': raw_lead.get('totalScore', 0),
                'review_count': raw_lead.get('reviewsCount', 0),
                'google_maps_url': raw_lead.get('url', ''),
                'place_id': raw_lead.get('placeId', ''),
                
                # Business intelligence
                'is_claimed': raw_lead.get('claimThisBusiness', False),
                'is_open': raw_lead.get('temporarilyClosed', False) == False,
                'price_level': raw_lead.get('priceLevel', ''),
                
                # Metadata
                'scraped_at': datetime.now().isoformat(),
                'source': 'google_maps',
                'status': 'new',
                
                # AI-generated fields (to be filled)
                'ai_lead_score': None,
                'ai_insights': None,
                'ai_outreach_message': None,
            }
            
            # AI-powered lead scoring and insights
            enriched = self._add_ai_intelligence(enriched)
            
            return enriched
            
        except Exception as e:
            logger.error(f"Error enriching lead {raw_lead.get('title', 'Unknown')}: {e}", exc_info=True)
            return raw_lead
    
    def _extract_email(self, lead: Dict) -> Optional[str]:
        """
        Extract email from lead data using email finding services
        
        Tries multiple methods:
        1. Direct email in website field
        2. Email finder APIs (Hunter.io, Clearbit, Snov.io)
        3. Pattern generation as fallback
        """
        website = lead.get('website', '')
        if not website:
            return None
        
        # Check if email is directly in website field
        if '@' in website:
            email = website
            if validator.validate_email(email):
                return email
        
        # Extract domain
        domain = website.replace('http://', '').replace('https://', '').split('/')[0]
        domain = domain.split('?')[0]
        
        if not domain or '.' not in domain:
            return None
        
        # Try email finder services
        try:
            # Extract name if available for better email finding
            name = lead.get('name', '')
            first_name = None
            last_name = None
            
            if name:
                name_parts = name.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
            
            email = self.email_finder.find_email(domain, first_name, last_name)
            if email and validator.validate_email(email):
                logger.debug(f"Found email for {lead.get('name')}: {email}")
                return email
        except Exception as e:
            logger.warning(f"Email finder error for {lead.get('name')}: {e}")
        
        # Fallback: Generate common pattern
        return f"info@{domain}"
    
    def _add_ai_intelligence(self, lead: Dict) -> Dict:
        """
        Add AI-powered insights and lead scoring
        
        Args:
            lead: Lead dictionary
        
        Returns:
            Lead with AI insights added
        """
        start_time = time.time()
        
        try:
            # Rate limiting for AI calls
            self.ai_limiter.wait_if_needed('google_ai')
            
            # Check cache for similar leads
            cache_key = f"ai_analysis:{lead.get('category', '')}:{lead.get('city', '')}:{lead.get('rating', 0)}"
            cached_analysis = self.cache.get(cache_key, ttl=7200)  # 2 hour cache
            
            if cached_analysis:
                logger.debug(f"Using cached AI analysis for {lead.get('name')}")
                lead['ai_lead_score'] = cached_analysis.get('score', 50)
                lead['ai_insights'] = json.dumps(cached_analysis.get('insights', []))
                lead['ai_concerns'] = json.dumps(cached_analysis.get('concerns', []))
                lead['recommended_services'] = json.dumps(cached_analysis.get('recommended_services', []))
            else:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # Create context for AI
                context = f"""
                You are the strategic intelligence analyst for Eleven Views, a boutique production house expanding into elite sports management.
                
                Evaluate the following organization as a potential Eleven Views partner or client:
                
                Organization: {lead['name']}
                Segment: {lead['category']}
                Location: {lead['city']}, {lead['state']}
                Website: {lead['website']}
                Public Reputation: {lead['rating']}/5 ({lead['review_count']} reviews)
                Primary Contact: {lead['phone']}
                
                Your assessment must help Eleven Views prioritize deals that need:
                - Luxury content production and storytelling
                - Athlete representation and NIL strategy
                - Sponsorship packaging or hospitality experiences
                - Media operations, live capture, or event coverage
                
                Tasks:
                1. Score their partnership potential from 0-100 (focus on appetite for premium production + sports management support).
                2. Share 2-3 insight bullets highlighting high-leverage ways Eleven Views could create value.
                3. Flag any risks, readiness issues, or credibility concerns.
                4. Suggest 2-3 Eleven Views service lanes that best match their needs (e.g., "Signature docuseries", "Athlete brand suite", "Game-day hybrid production").
                
                Respond in JSON format:
                {{
                    "score": <0-100>,
                    "insights": ["insight 1", "insight 2", "insight 3"],
                    "concerns": ["concern 1"],
                    "recommended_services": ["service 1", "service 2"]
                }}
                """
                
                ai_start = time.time()
                response = model.generate_content(context)
                ai_duration = (time.time() - ai_start) * 1000
                
                # Estimate cost (Gemini 2.0 Flash pricing)
                tokens_estimated = len(context.split()) * 1.3  # Rough estimate
                cost = (tokens_estimated / 1000) * 0.000075  # $0.075 per 1M tokens
                
                log_ai_request(
                    model='gemini-2.0-flash-exp',
                    tokens_used=int(tokens_estimated),
                    duration_ms=ai_duration,
                    cost=cost
                )
                
                # Parse AI response
                try:
                    response_text = response.text.strip()
                    # Clean JSON response
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                    ai_data = json.loads(response_text)
                    
                    lead['ai_lead_score'] = ai_data.get('score', 50)
                    lead['ai_insights'] = json.dumps(ai_data.get('insights', []))
                    lead['ai_concerns'] = json.dumps(ai_data.get('concerns', []))
                    lead['recommended_services'] = json.dumps(ai_data.get('recommended_services', []))
                    
                    # Cache the analysis
                    self.cache.set(cache_key, ai_data, ttl=7200)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse AI JSON response: {e}")
                    # Fallback scoring based on simple heuristics
                    score = 55  # Elevated base score to reflect boutique targeting
                    score += min(lead['rating'] * 8, 32)  # Reputation boost
                    score += min(lead['review_count'] / 15, 18)  # Public proof boost
                    if lead['website']: score += 8  # Digital presence
                    if not lead.get('is_claimed', True): score += 7  # Operational gap Eleven Views can solve
                    
                    lead['ai_lead_score'] = min(score, 100)
                    lead['ai_insights'] = json.dumps([
                        f"Reputation: {lead['rating']}/5 with {lead['review_count']} social proofs",
                        "Active digital presence" if lead['website'] else "Opportunity: elevate digital storytelling",
                        "Ownership signals room for managed experience" if not lead.get('is_claimed', True) else "Claimed listing shows structured operations"
                    ])
            
            # Generate personalized outreach message (outside cache check)
            if lead.get('ai_lead_score', 0) >= 60:
                try:
                    lead['ai_outreach_message'] = self.personalizer.generate_outreach(lead)
                except Exception as e:
                    logger.warning(f"Failed to generate outreach message: {e}")
            
            duration = time.time() - start_time
            logger.debug(f"AI enrichment completed in {duration:.2f}s for {lead.get('name')}")
            
            return lead
            
        except Exception as e:
            logger.error(f"AI enrichment failed for {lead.get('name', 'Unknown')}: {e}", exc_info=True)
            # Return with basic scoring
            lead['ai_lead_score'] = 50
            lead['ai_insights'] = json.dumps(["Basic lead - manual review needed"])
            return lead
    
    def process_leads(
        self,
        search_query: str,
        max_results: int = 100,
        auto_qualify: bool = True,
        min_score: int = 60
    ) -> Dict:
        """
        Complete lead generation pipeline
        
        Args:
            search_query: What to search for
            max_results: How many leads to generate
            auto_qualify: Automatically qualify leads above min_score
            min_score: Minimum AI score for auto-qualification
        
        Returns:
            Summary statistics
        """
        start_time = time.time()
        
        logger.info("="*60)
        logger.info("🚀 ELEVEN VIEWS OPPORTUNITY ENGINE")
        logger.info("="*60)
        logger.info(f"Search: {search_query}")
        logger.info(f"Max Results: {max_results}")
        logger.info(f"Auto-Qualify: {auto_qualify} (min_score: {min_score})")
        logger.info("="*60)
        
        # Step 1: Scrape
        raw_leads = self.scrape_google_maps(search_query, max_results)
        
        if not raw_leads:
            logger.warning("No leads found. Check your search query.")
            return {'success': False, 'leads_generated': 0}
        
        # Step 2: Enrich and save
        logger.info(f"Enriching {len(raw_leads)} leads with AI...")
        
        stats = {
            'total_scraped': len(raw_leads),
            'saved': 0,
            'qualified': 0,
            'duplicates': 0,
            'errors': 0,
            'success': True
        }
        
        for idx, raw_lead in enumerate(raw_leads, 1):
            try:
                lead_name = raw_lead.get('title', 'Unknown')
                logger.debug(f"Processing {idx}/{len(raw_leads)}: {lead_name}")
                
                # Enrich with AI
                enriched_lead = self.enrich_lead(raw_lead)
                
                # Save to database
                lead_id = self.db.save_lead(enriched_lead)
                
                if lead_id:
                    stats['saved'] += 1
                    
                    # Auto-qualify if score is high enough
                    if auto_qualify and enriched_lead.get('ai_lead_score', 0) >= min_score:
                        self.db.update_lead_status(lead_id, 'qualified')
                        stats['qualified'] += 1
                        logger.info(f"✅ {lead_name}: Saved & Qualified (Score: {enriched_lead.get('ai_lead_score', 0)})")
                    else:
                        logger.info(f"✅ {lead_name}: Saved (Score: {enriched_lead.get('ai_lead_score', 0)})")
                else:
                    stats['duplicates'] += 1
                    logger.debug(f"⚠️  {lead_name}: Duplicate (skipped)")
                    
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"❌ Error processing lead {raw_lead.get('title', 'Unknown')}: {e}", exc_info=True)
        
        # Log summary
        duration = time.time() - start_time
        logger.info("="*60)
        logger.info("📊 ELEVEN VIEWS PIPELINE SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Scraped:     {stats['total_scraped']}")
        logger.info(f"Saved:             {stats['saved']}")
        logger.info(f"Auto-Qualified:    {stats['qualified']}")
        logger.info(f"Duplicates:        {stats['duplicates']}")
        logger.info(f"Errors:            {stats['errors']}")
        logger.info(f"Duration:           {duration:.2f}s")
        logger.info("="*60)
        
        # Structured logging for analytics
        log_lead_generation(
            search_query=search_query,
            leads_found=stats['total_scraped'],
            leads_saved=stats['saved'],
            leads_qualified=stats['qualified'],
            duration_seconds=duration,
            errors=stats['errors']
        )
        
        return stats


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description='Eleven Views Opportunity Engine')
    parser.add_argument('--search', type=str, required=True, help='Search query')
    parser.add_argument('--limit', type=int, default=100, help='Max results')
    parser.add_argument('--min-score', type=int, default=60, help='Min AI score for qualification')
    parser.add_argument('--min-rating', type=float, default=3.5, help='Min Google rating')
    
    args = parser.parse_args()
    
    # Run lead generation
    generator = LeadGenerator()
    stats = generator.process_leads(
        search_query=args.search,
        max_results=args.limit,
        min_score=args.min_score
    )
    
    if stats['qualified'] > 0:
        print(f"🎯 View qualified leads: python dashboard.py")
        print(f"📧 Export for outreach: python export_leads.py --status qualified")


if __name__ == '__main__':
    main()
