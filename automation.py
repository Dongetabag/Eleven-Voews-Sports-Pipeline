#!/usr/bin/env python3
"""
Automation scheduler for Recipe Labs Lead Generator
Run lead generation automatically on a schedule
"""

import schedule
import time
import argparse
from datetime import datetime
from lead_generator import LeadGenerator
from config import (
    TARGET_INDUSTRIES,
    TARGET_LOCATIONS,
    AUTO_SCRAPE_TIME,
    AUTO_SCRAPE_LIMIT,
    AUTO_SCRAPE_ROTATION
)

class LeadGenAutomation:
    """Automated lead generation scheduler"""
    
    def __init__(self):
        self.generator = LeadGenerator()
        self.current_industry_index = 0
        self.current_location_index = 0
    
    def generate_search_query(self) -> str:
        """
        Generate next search query using rotation
        
        Returns:
            Search query string
        """
        if AUTO_SCRAPE_ROTATION:
            # Rotate through industries and locations
            industry = TARGET_INDUSTRIES[self.current_industry_index % len(TARGET_INDUSTRIES)]
            location = TARGET_LOCATIONS[self.current_location_index % len(TARGET_LOCATIONS)]
            
            # Increment indices
            self.current_industry_index += 1
            if self.current_industry_index >= len(TARGET_INDUSTRIES):
                self.current_industry_index = 0
                self.current_location_index += 1
                if self.current_location_index >= len(TARGET_LOCATIONS):
                    self.current_location_index = 0
            
            return f"{industry} in {location}"
        else:
            # Use first industry and location
            return f"{TARGET_INDUSTRIES[0]} in {TARGET_LOCATIONS[0]}"
    
    def run_generation(self):
        """Run automated lead generation"""
        print("\n" + "="*60)
        print(f"🤖 AUTOMATED LEAD GENERATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        try:
            search_query = self.generate_search_query()
            
            print(f"🎯 Query: {search_query}")
            print(f"📊 Target: {AUTO_SCRAPE_LIMIT} leads\n")
            
            stats = self.generator.process_leads(
                search_query=search_query,
                max_results=AUTO_SCRAPE_LIMIT,
                auto_qualify=True
            )
            
            print(f"\n✅ Automation run complete!")
            print(f"   Generated: {stats.get('saved', 0)} new leads")
            print(f"   Qualified: {stats.get('qualified', 0)} leads")
            
        except Exception as e:
            print(f"\n❌ Automation run failed: {e}")
    
    def schedule_daily(self, time_str: str = AUTO_SCRAPE_TIME):
        """
        Schedule daily lead generation
        
        Args:
            time_str: Time to run (HH:MM format)
        """
        print("\n" + "="*60)
        print("⏰ LEAD GENERATION AUTOMATION SCHEDULER")
        print("="*60)
        print(f"\n📅 Scheduled: Daily at {time_str}")
        print(f"🎯 Rotating through {len(TARGET_INDUSTRIES)} industries")
        print(f"📍 Across {len(TARGET_LOCATIONS)} locations")
        print(f"📊 Generating {AUTO_SCRAPE_LIMIT} leads per run")
        print("\n" + "="*60 + "\n")
        
        # Schedule the job
        schedule.every().day.at(time_str).do(self.run_generation)
        
        print("✅ Scheduler started! Press Ctrl+C to stop.")
        print(f"⏳ Next run: {schedule.next_run()}\n")
        
        # Run the scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped")
    
    def schedule_hourly(self):
        """Schedule hourly lead generation (for aggressive campaigns)"""
        print("\n⚠️  HOURLY MODE - High volume lead generation")
        print("   This will generate leads every hour")
        print("   Recommended for initial database building only\n")
        
        schedule.every().hour.do(self.run_generation)
        
        print("✅ Hourly scheduler started! Press Ctrl+C to stop.\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped")
    
    def run_once(self, num_runs: int = 1):
        """
        Run lead generation once or multiple times immediately
        
        Args:
            num_runs: Number of times to run
        """
        print(f"\n🚀 Running {num_runs} lead generation batch(es)...\n")
        
        for i in range(num_runs):
            if num_runs > 1:
                print(f"\n--- BATCH {i+1}/{num_runs} ---\n")
            
            self.run_generation()
            
            if i < num_runs - 1:
                print("\n⏳ Waiting 30 seconds before next batch...\n")
                time.sleep(30)


def main():
    """CLI interface for automation"""
    parser = argparse.ArgumentParser(description='Recipe Labs Lead Generation Automation')
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['once', 'daily', 'hourly', 'continuous'],
        default='once',
        help='Automation mode'
    )
    
    parser.add_argument(
        '--time',
        type=str,
        default=AUTO_SCRAPE_TIME,
        help='Time for daily runs (HH:MM format)'
    )
    
    parser.add_argument(
        '--runs',
        type=int,
        default=1,
        help='Number of runs for once mode'
    )
    
    args = parser.parse_args()
    
    automation = LeadGenAutomation()
    
    if args.mode == 'once':
        automation.run_once(num_runs=args.runs)
    elif args.mode == 'daily':
        automation.schedule_daily(time_str=args.time)
    elif args.mode == 'hourly':
        automation.schedule_hourly()
    elif args.mode == 'continuous':
        print("\n🔄 CONTINUOUS MODE")
        print("   Generating leads in rapid succession")
        print("   Use Ctrl+C to stop\n")
        
        try:
            while True:
                automation.run_generation()
                print("\n⏳ Waiting 5 minutes before next run...\n")
                time.sleep(300)  # 5 minutes
        except KeyboardInterrupt:
            print("\n\n⏹️  Continuous mode stopped")


if __name__ == '__main__':
    main()
