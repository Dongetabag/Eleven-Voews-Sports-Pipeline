#!/usr/bin/env python3
"""
Eleven Views Opportunity Engine Configuration
Tailor these settings to align with boutique production and sports management targets
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# ELEVEN VIEWS CONFIGURATION
# ==============================================================================

# Your company information
COMPANY_NAME = "Eleven Views"
COMPANY_WEBSITE = "https://elevenviews.com"  # Update with your actual URL
COMPANY_PHONE = "(310) 555-0011"  # Update with your phone
COMPANY_EMAIL = "hello@elevenviews.com"  # Update with your email

# ==============================================================================
# API CREDENTIALS
# ==============================================================================

# Apify API token (get from: https://console.apify.com/account/integrations)
APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')

# Google AI API key (get from: https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# ==============================================================================
# LEAD GENERATION SETTINGS
# ==============================================================================

# Default search parameters
DEFAULT_MAX_RESULTS = 100
DEFAULT_MIN_RATING = 4.2  # Minimum Google rating (1.0 - 5.0)
DEFAULT_MIN_SCORE = 68    # Minimum AI score for auto-qualification

# Lead scoring weights (adjust to fit your ICP)
SCORING_WEIGHTS = {
    'has_website': 8,
    'not_claimed': 7,
    'high_rating': 35,    # Weighted toward reputation and guest experience
    'review_count': 20,   # Public proof of fan/athlete engagement
    'base_score': 55      # Starting score tuned for boutique targeting
}

# ==============================================================================
# AI PERSONALIZATION SETTINGS
# ==============================================================================

# Default outreach style: 'professional', 'friendly', or 'direct'
DEFAULT_OUTREACH_STYLE = 'professional'

# AI Model selection
AI_MODEL = 'gemini-2.0-flash-exp'  # Fast and cost-effective

# Maximum tokens for AI responses
MAX_AI_TOKENS = 500

# ==============================================================================
# TARGET INDUSTRIES (Your Ideal Customer Profile)
# ==============================================================================

# High-priority industries for Eleven Views
TARGET_INDUSTRIES = [
    # Flagship sports properties
    "professional sports teams",
    "minor league clubs",
    "college athletic departments",
    "elite training facilities",
    "sports academies",
    "youth development programs",

    # Athlete performance & representation
    "athlete management firms",
    "sports agencies",
    "NIL collectives",
    "sports therapy and recovery centers",
    "high-performance gyms",

    # Media, production, and venues
    "sports content studios",
    "luxury event venues",
    "premium hospitality suites",
    "in-venue experience teams",
    "sports tech startups",
    "brand sponsorship teams"
]

# Target locations (your service areas)
TARGET_LOCATIONS = [
    "Los Angeles, CA",
    "New York, NY",
    "Miami, FL",
    "Dallas, TX",
    "Las Vegas, NV",
    "Atlanta, GA",
    "Chicago, IL",
    "Charlotte, NC",
    "Phoenix, AZ",
    "Seattle, WA",
]

# ==============================================================================
# SEARCH QUERY TEMPLATES
# ==============================================================================

# Templates for generating search queries
SEARCH_TEMPLATES = [
    "{industry} in {location}",
    "{industry} near {location}",
    "best {industry} in {location}",
    "top rated {industry} in {location}",
    "elite {industry} in {location}",
    "flagship {industry} in {location}",
]

# ==============================================================================
# DATABASE SETTINGS
# ==============================================================================

DATABASE_PATH = "data/leads.db"

# Automatic backup settings
AUTO_BACKUP = True
BACKUP_INTERVAL_DAYS = 7

# ==============================================================================
# AUTOMATION SETTINGS
# ==============================================================================

# Daily automation schedule
AUTO_SCRAPE_ENABLED = False  # Set to True to enable
AUTO_SCRAPE_TIME = "09:00"   # Time to run (24-hour format)

# How many leads to generate per automation run
AUTO_SCRAPE_LIMIT = 50

# Which industries to rotate through
AUTO_SCRAPE_ROTATION = True

# ==============================================================================
# EXPORT SETTINGS
# ==============================================================================

EXPORT_DIRECTORY = "exports"
EXPORT_FORMATS = ['csv', 'json', 'xlsx']  # Available formats

# Fields to include in exports
EXPORT_FIELDS = [
    'name',
    'category', 
    'city',
    'state',
    'phone',
    'email',
    'website',
    'rating',
    'review_count',
    'ai_lead_score',
    'status',
    'ai_outreach_message',
    'scraped_at'
]

# ==============================================================================
# CRM INTEGRATION (Optional)
# ==============================================================================

# HubSpot
HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY')
HUBSPOT_ENABLED = os.getenv('HUBSPOT_ENABLED', 'false').lower() == 'true'

# Salesforce
SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME')
SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD')
SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN')
SALESFORCE_ENABLED = False

# ==============================================================================
# EMAIL SETTINGS (Optional)
# ==============================================================================

# SendGrid
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', COMPANY_EMAIL)
SENDGRID_ENABLED = False

# SMTP (alternative to SendGrid)
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT', 587)
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_ENABLED = False

# ==============================================================================
# COMPLIANCE & ETHICS
# ==============================================================================

# Rate limiting (requests per minute)
RATE_LIMIT_RPM = 10

# Respect robots.txt
RESPECT_ROBOTS = True

# User agent string
USER_AGENT = f"{COMPANY_NAME} Lead Generator Bot"

# ==============================================================================
# FEATURE FLAGS
# ==============================================================================

FEATURES = {
    'ai_enrichment': True,
    'email_finding': False,  # Set to True when you integrate email finder
    'phone_verification': False,
    'social_media_scraping': False,
    'competitor_analysis': False,
}

# ==============================================================================
# VALIDATION
# ==============================================================================

def validate_config():
    """Validate required configuration"""
    errors = []
    
    if not APIFY_API_TOKEN:
        errors.append("APIFY_API_TOKEN not set in environment")
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY not set in environment")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))
    
    return True


if __name__ == '__main__':
    try:
        validate_config()
        print("✅ Configuration is valid")
        print(f"📍 Target locations: {len(TARGET_LOCATIONS)}")
        print(f"🎯 Target industries: {len(TARGET_INDUSTRIES)}")
        print(f"🤖 AI Model: {AI_MODEL}")
    except ValueError as e:
        print(f"❌ {e}")
