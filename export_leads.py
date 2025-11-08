#!/usr/bin/env python3
"""
Export utility for the Eleven Views Opportunity Engine
Export curated opportunities for CRM activation or hospitality outreach
"""

import csv
import json
import argparse
from datetime import datetime
from pathlib import Path
from database import Database
from config import EXPORT_DIRECTORY, EXPORT_FIELDS, HUBSPOT_ENABLED
from utils.logger import get_logger

logger = get_logger('export')

# Optional HubSpot import
try:
    from integrations.hubspot import get_hubspot
    HUBSPOT_AVAILABLE = True
except ImportError:
    HUBSPOT_AVAILABLE = False
    def get_hubspot():
        return None

class LeadExporter:
    """Export leads to various formats"""
    
    def __init__(self):
        self.db = Database()
        Path(EXPORT_DIRECTORY).mkdir(exist_ok=True)
    
    def export_to_csv(
        self,
        leads: list,
        filename: str = None,
        fields: list = None
    ) -> str:
        """
        Export leads to CSV
        
        Args:
            leads: List of lead dictionaries
            filename: Output filename
            fields: Fields to include (defaults to EXPORT_FIELDS)
        
        Returns:
            Path to created file
        """
        if not leads:
            print("⚠️  No leads to export")
            return None
        
        fields = fields or EXPORT_FIELDS
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"leads_export_{timestamp}.csv"
        
        filepath = Path(EXPORT_DIRECTORY) / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"✅ Exported {len(leads)} leads to: {filepath}")
        return str(filepath)
    
    def export_to_json(
        self,
        leads: list,
        filename: str = None
    ) -> str:
        """
        Export leads to JSON
        
        Args:
            leads: List of lead dictionaries
            filename: Output filename
        
        Returns:
            Path to created file
        """
        if not leads:
            print("⚠️  No leads to export")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"leads_export_{timestamp}.json"
        
        filepath = Path(EXPORT_DIRECTORY) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, default=str)
        
        print(f"✅ Exported {len(leads)} leads to: {filepath}")
        return str(filepath)
    
    def export_for_email_campaign(
        self,
        status: str = 'qualified',
        min_score: int = 70
    ) -> str:
        """
        Export leads formatted for email campaign
        Includes: name, email, outreach message, subject line
        
        Args:
            status: Lead status to export
            min_score: Minimum AI score
        
        Returns:
            Path to created file
        """
        leads = self.db.get_leads(
            status=status,
            min_score=min_score,
            limit=10000
        )
        
        # Filter to only leads with email and outreach message
        campaign_leads = [
            {
                'name': lead['name'],
                'email': lead['email'],
                'city': lead['city'],
                'score': lead['ai_lead_score'],
                'subject': f"{lead['city']} {lead['category']} x Eleven Views?",
                'message': lead['ai_outreach_message'],
                'website': lead['website'],
                'phone': lead['phone']
            }
            for lead in leads
            if lead.get('email') and lead.get('ai_outreach_message')
        ]
        
        if not campaign_leads:
            print("⚠️  No leads with email and outreach message found")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"email_campaign_{status}_{timestamp}.csv"
        
        return self.export_to_csv(
            campaign_leads,
            filename=filename,
            fields=['name', 'email', 'city', 'score', 'subject', 'message', 'website', 'phone']
        )
    
    def export_for_cold_calling(
        self,
        status: str = 'qualified',
        min_score: int = 70
    ) -> str:
        """
        Export leads formatted for cold calling
        Includes: name, phone, talking points
        
        Args:
            status: Lead status to export
            min_score: Minimum AI score
        
        Returns:
            Path to created file
        """
        leads = self.db.get_leads(
            status=status,
            min_score=min_score,
            limit=10000
        )
        
        # Filter to only leads with phone
        call_leads = [
            {
                'name': lead['name'],
                'phone': lead['phone'],
                'city': lead['city'],
                'category': lead['category'],
                'rating': lead['rating'],
                'score': lead['ai_lead_score'],
                'insights': lead['ai_insights'],
                'talking_points': lead['ai_outreach_message']
            }
            for lead in leads
            if lead.get('phone')
        ]
        
        if not call_leads:
            print("⚠️  No leads with phone numbers found")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cold_call_list_{status}_{timestamp}.csv"
        
        return self.export_to_csv(
            call_leads,
            filename=filename,
            fields=['name', 'phone', 'city', 'category', 'rating', 'score', 'insights', 'talking_points']
        )
    
    def export_crm_import(
        self,
        status: str = 'qualified',
        format: str = 'csv'
    ) -> str:
        """
        Export leads in CRM-ready format
        
        Args:
            status: Lead status to export
            format: Output format (csv or json)
        
        Returns:
            Path to created file
        """
        leads = self.db.get_leads(status=status, limit=10000)
        
        # Map to common CRM fields
        crm_leads = [
            {
                'Company': lead['name'],
                'Industry': lead['category'],
                'City': lead['city'],
                'State': lead['state'],
                'Country': lead['country'],
                'Phone': lead['phone'],
                'Email': lead['email'],
                'Website': lead['website'],
                'Lead Score': lead['ai_lead_score'],
                'Lead Status': lead['status'].title(),
                'Lead Source': 'Eleven Views Opportunity Engine',
                'Notes': lead['ai_insights'],
                'Created Date': lead['scraped_at']
            }
            for lead in leads
        ]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"crm_import_{status}_{timestamp}.{format}"
        
        if format == 'csv':
            return self.export_to_csv(
                crm_leads,
                filename=filename,
                fields=list(crm_leads[0].keys()) if crm_leads else []
            )
        else:
            return self.export_to_json(crm_leads, filename=filename)
    
    def sync_to_hubspot(
        self,
        status: str = 'qualified',
        min_score: int = 60,
        batch_size: int = 100
    ) -> Dict:
        """
        Sync leads directly to HubSpot CRM
        
        Args:
            status: Lead status to sync
            min_score: Minimum AI score
            batch_size: Number of leads to sync per batch
        
        Returns:
            Sync statistics
        """
        if not HUBSPOT_AVAILABLE:
            logger.warning("HubSpot integration not available")
            print("⚠️  HubSpot integration not available")
            print("   Install with: pip install hubspot-api-client")
            return {'success': False, 'reason': 'not_installed'}
        
        hubspot = get_hubspot()
        
        if not hubspot or not hubspot.is_enabled():
            logger.warning("HubSpot integration not enabled")
            print("⚠️  HubSpot integration not enabled")
            print("   Add HUBSPOT_API_KEY to .env file")
            print("   Get your key at: https://app.hubspot.com/private-apps")
            return {'success': False, 'reason': 'not_enabled'}
        
        # Get leads to sync
        leads = self.db.get_leads(
            status=status,
            min_score=min_score,
            limit=10000
        )
        
        if not leads:
            logger.warning("No leads found to sync")
            print("⚠️  No leads found matching criteria")
            return {'success': False, 'reason': 'no_leads'}
        
        logger.info(f"Syncing {len(leads)} leads to HubSpot...")
        print(f"\n📤 Syncing {len(leads)} leads to HubSpot...")
        
        # Sync in batches
        stats = {
            'total': len(leads),
            'created': 0,
            'updated': 0,
            'failed': 0
        }
        
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]
            batch_stats = hubspot.sync_leads_batch(batch)
            
            stats['created'] += batch_stats.get('created', 0)
            stats['updated'] += batch_stats.get('updated', 0)
            stats['failed'] += batch_stats.get('failed', 0)
            
            print(f"   Processed {min(i + batch_size, len(leads))}/{len(leads)} leads...")
        
        print(f"\n✅ HubSpot sync complete!")
        print(f"   Created: {stats['created']}")
        print(f"   Updated: {stats['updated']}")
        print(f"   Failed: {stats['failed']}")
        
        return stats


def main():
    """CLI interface for exporting leads"""
    parser = argparse.ArgumentParser(description='Export opportunities from the Eleven Views Opportunity Engine')
    
    parser.add_argument(
        '--status',
        type=str,
        choices=['new', 'qualified', 'contacted', 'converted', 'rejected', 'all'],
        default='qualified',
        help='Status of leads to export'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'json', 'email', 'call', 'crm', 'hubspot'],
        default='csv',
        help='Export format (hubspot = direct sync to HubSpot)'
    )
    
    parser.add_argument(
        '--min-score',
        type=int,
        default=60,
        help='Minimum AI lead score'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output filename'
    )
    
    args = parser.parse_args()
    
    exporter = LeadExporter()
    
    print("\n" + "="*60)
    print("📤 RECIPE LABS LEAD EXPORTER")
    print("="*60 + "\n")
    
    status = None if args.status == 'all' else args.status
    
    # Route to appropriate export method
    if args.format == 'hubspot':
        stats = exporter.sync_to_hubspot(status=status, min_score=args.min_score)
        if stats.get('success') is not False:
            print(f"\n🎉 Successfully synced {stats.get('created', 0) + stats.get('updated', 0)} leads to HubSpot!")
        filepath = None
    elif args.format == 'email':
        filepath = exporter.export_for_email_campaign(status=status, min_score=args.min_score)
    elif args.format == 'call':
        filepath = exporter.export_for_cold_calling(status=status, min_score=args.min_score)
    elif args.format == 'crm':
        filepath = exporter.export_crm_import(status=status, format='csv')
    elif args.format == 'json':
        leads = exporter.db.get_leads(status=status, min_score=args.min_score, limit=10000)
        filepath = exporter.export_to_json(leads, filename=args.output)
    else:  # csv
        leads = exporter.db.get_leads(status=status, min_score=args.min_score, limit=10000)
        filepath = exporter.export_to_csv(leads, filename=args.output)
    
    if filepath:
        print(f"\n✅ Export complete!")
        print(f"📁 File: {filepath}")
        print(f"\n💡 Next steps:")
        print("   1. Review the exported leads")
        print("   2. Import to your CRM or email system")
        print("   3. Start your outreach campaign")
    else:
        print("\n❌ Export failed - no leads found")


if __name__ == '__main__':
    main()
