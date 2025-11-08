#!/usr/bin/env python3
"""
AI Personalizer - Generate customized outreach messages using Google Gemini
"""

import os
import json
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIPersonalizer:
    """AI-powered personalized outreach message generator"""
    
    def __init__(self):
        """Initialize AI personalizer"""
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Eleven Views brand voice templates
        self.templates = {
            'professional': {
                'tone': 'elevated, consultative, vision-led',
                'length': 'concise (3-4 sentences)',
                'style': 'luxury sports production & management'
            },
            'friendly': {
                'tone': 'inviting, relationship-first, boutique',
                'length': 'brief (2-3 sentences)',
                'style': 'white-glove introduction'
            },
            'direct': {
                'tone': 'precise, outcome-driven, confident',
                'length': 'very brief (2 sentences)',
                'style': 'premium value highlight'
            }
        }
    
    def generate_outreach(
        self,
        lead: Dict,
        template_style: str = 'professional',
        custom_context: Optional[str] = None
    ) -> str:
        """
        Generate personalized outreach message for a lead
        
        Args:
            lead: Lead dictionary with business info
            template_style: Style template (professional, friendly, direct)
            custom_context: Optional custom context to include
        
        Returns:
            Personalized outreach message
        """
        try:
            template = self.templates.get(template_style, self.templates['professional'])
            
            # Build comprehensive context
            context = f"""
You are writing on behalf of Eleven Views, a boutique production company launching a high-end sports management practice.

LEAD INFORMATION:
- Business Name: {lead.get('name', 'N/A')}
- Category: {lead.get('category', 'N/A')}
- Location: {lead.get('city', 'N/A')}, {lead.get('state', 'N/A')}
- Website: {lead.get('website', 'No website found')}
- Rating: {lead.get('rating', 'N/A')}/5 with {lead.get('review_count', 0)} reviews
- AI Insights: {lead.get('ai_insights', 'N/A')}

ELEVEN VIEWS SIGNATURE OFFERINGS:
- Cinematic documentary and episodic storytelling for teams & athletes
- Live event capture, highlight architecture, and behind-the-scenes coverage
- Athlete brand architecture, NIL strategy, and sponsorship packaging
- Hospitality design, premium partner experiences, and in-game media lounges
- Cross-platform content studios (broadcast, OTT, social, experiential)
- Strategic dealmaking with leagues, rights-holders, and brand partners

WRITING STYLE:
- Tone: {template['tone']}
- Length: {template['length']}
- Style: {template['style']}

INSTRUCTIONS:
1. Address them by business name (no "Hi" or "Hey"—open with name and insight).
2. Reference something specific about their presence (market, segment, reputation, facility quality, etc.).
3. Mention ONE signature Eleven Views capability that unlocks value for them.
4. Include a soft call-to-action
5. Keep it bespoke and cinematic—NOT transactional or salesy.
6. Do NOT use generic phrases like "I came across" or "I noticed".
7. Do NOT ask obvious questions they can answer themselves.
8. Emphasize how Eleven Views elevates their story, partners, or athletes.

{f'ADDITIONAL CONTEXT: {custom_context}' if custom_context else ''}

Write ONLY the message body. No subject line, no signature, no greeting beyond business name.
"""
            
            response = self.model.generate_content(context)
            message = response.text.strip()
            
            # Clean up any unwanted formatting
            message = message.replace('**', '').replace('*', '')
            
            return message
            
        except Exception as e:
            print(f"⚠️ AI personalization failed: {e}")
            return self._fallback_message(lead)
    
    def _fallback_message(self, lead: Dict) -> str:
        """
        Generate a basic fallback message if AI fails
        
        Args:
            lead: Lead dictionary
        
        Returns:
            Basic outreach message
        """
        name = lead.get('name', 'there')
        city = lead.get('city', '')
        category = lead.get('category', 'business')
        
        return f"""{name},

Eleven Views partners with {category.lower()} leaders in {city} who want cinematic storytelling, elevated hospitality, and athlete-first management under one roof.

Open to a brief conversation on where a boutique production and sports management team could plug into your 2025 initiatives?"""
    
    def generate_email_subject(self, lead: Dict) -> str:
        """
        Generate personalized email subject line
        
        Args:
            lead: Lead dictionary
        
        Returns:
            Subject line
        """
        try:
            context = f"""
Generate a short, attention-grabbing email subject line for this business:
- Business: {lead.get('name')}
- Category: {lead.get('category')}
- Location: {lead.get('city')}, {lead.get('state')}

Requirements:
- 5-8 words maximum
- Personalized (use city or business type)
- Benefit-focused, not salesy
- No spam trigger words
- No all caps or excessive punctuation

Examples of good subject lines:
- "Building {category} stories in {city}"
- "{city} {category}: elevate the experience"
- "{name} x Eleven Views concept?"

Write ONLY the subject line, nothing else.
"""
            
            response = self.model.generate_content(
                context.format(
                    name=lead.get('name', 'your business'),
                    category=lead.get('category', 'businesses'),
                    city=lead.get('city', 'your area')
                )
            )
            
            subject = response.text.strip().replace('"', '').replace("'", '')
            return subject[:80]  # Limit length
            
        except:
            # Fallback subject
            city = lead.get('city', '')
            return f"Quick question for {city} businesses"
    
    def generate_followup(self, lead: Dict, previous_interaction: str) -> str:
        """
        Generate a follow-up message based on previous interaction
        
        Args:
            lead: Lead dictionary
            previous_interaction: Summary of previous interaction
        
        Returns:
            Follow-up message
        """
        try:
            context = f"""
You're writing a follow-up message for Eleven Views' opportunity team.

LEAD: {lead.get('name')}
PREVIOUS INTERACTION: {previous_interaction}

Write a brief, natural follow-up that:
1. References the previous interaction
2. Adds value or new information
3. Includes a gentle call-to-action
4. Stays conversational and helpful

Keep it short (2-3 sentences).
"""
            
            response = self.model.generate_content(context)
            return response.text.strip()
            
        except:
            return f"""Just following up on my previous note—our Eleven Views team would love to explore where we can elevate {lead.get('name')}. Let me know if you’re open to a quick conversation."""
    
    def batch_generate(self, leads: list[Dict], template_style: str = 'professional') -> Dict[int, str]:
        """
        Generate messages for multiple leads efficiently
        
        Args:
            leads: List of lead dictionaries
            template_style: Message template style
        
        Returns:
            Dictionary mapping lead IDs to generated messages
        """
        messages = {}
        
        for lead in leads:
            lead_id = lead.get('id')
            if lead_id:
                messages[lead_id] = self.generate_outreach(lead, template_style)
        
        return messages


def test_personalizer():
    """Test the personalizer with sample data"""
    personalizer = AIPersonalizer()
    
    # Sample lead
    test_lead = {
        'name': 'Smith & Associates Law Firm',
        'category': 'Law Firm',
        'city': 'Boston',
        'state': 'MA',
        'website': 'https://smithlaw.com',
        'rating': 4.7,
        'review_count': 142,
        'ai_insights': json.dumps([
            "Well-established firm with strong reputation",
            "No active social media presence",
            "Website needs modernization"
        ])
    }
    
    print("="*60)
    print("🧪 TESTING AI PERSONALIZER")
    print("="*60 + "\n")
    
    # Test different styles
    for style in ['professional', 'friendly', 'direct']:
        print(f"\n{style.upper()} STYLE:")
        print("-" * 60)
        subject = personalizer.generate_email_subject(test_lead)
        message = personalizer.generate_outreach(test_lead, template_style=style)
        print(f"Subject: {subject}")
        print(f"\n{message}")
        print("-" * 60)


if __name__ == '__main__':
    test_personalizer()
