#!/usr/bin/env python3
"""
Database module for Recipe Labs Lead Generation
SQLite-based storage with easy PostgreSQL migration path
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class Database:
    """SQLite database manager for leads"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        # Use /tmp for Vercel serverless (ephemeral but writable)
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', '/tmp/leads.db')

        self.db_path = db_path

        # Create data directory if it doesn't exist (and if not in /tmp)
        if not self.db_path.startswith('/tmp'):
            Path(os.path.dirname(self.db_path) or 'data').mkdir(exist_ok=True)

        # Initialize database schema
        self._init_schema()
    
    def _init_schema(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Basic info
                name TEXT NOT NULL,
                category TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                postal_code TEXT,
                country TEXT DEFAULT 'US',
                
                -- Contact info
                phone TEXT,
                website TEXT,
                email TEXT,
                
                -- Social & reputation
                rating REAL,
                review_count INTEGER,
                google_maps_url TEXT,
                place_id TEXT UNIQUE,
                
                -- Business intelligence
                is_claimed BOOLEAN,
                is_open BOOLEAN,
                price_level TEXT,
                
                -- AI-generated fields
                ai_lead_score INTEGER,
                ai_insights TEXT,
                ai_concerns TEXT,
                recommended_services TEXT,
                ai_outreach_message TEXT,
                
                -- Metadata
                status TEXT DEFAULT 'new',
                source TEXT DEFAULT 'google_maps',
                scraped_at TEXT,
                last_updated TEXT,
                
                -- CRM integration
                assigned_to TEXT,
                last_contacted TEXT,
                notes TEXT,
                
                -- Timestamps
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                -- Full-text search
                search_text TEXT
            )
        ''')
        
        # Interactions/activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                interaction_type TEXT NOT NULL,
                interaction_date TEXT NOT NULL,
                notes TEXT,
                outcome TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                search_query TEXT,
                total_leads INTEGER DEFAULT 0,
                qualified_leads INTEGER DEFAULT 0,
                contacted_leads INTEGER DEFAULT 0,
                converted_leads INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON leads(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_score ON leads(ai_lead_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_city ON leads(city)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON leads(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_place_id ON leads(place_id)')
        
        conn.commit()
        conn.close()
    
    def save_lead(self, lead: Dict) -> Optional[int]:
        """
        Save a lead to the database
        
        Args:
            lead: Lead dictionary
        
        Returns:
            Lead ID if successful, None if duplicate
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for duplicate by place_id
            if lead.get('place_id'):
                cursor.execute('SELECT id FROM leads WHERE place_id = ?', (lead['place_id'],))
                if cursor.fetchone():
                    conn.close()
                    return None  # Duplicate
            
            # Create search text for full-text search
            search_text = f"{lead.get('name', '')} {lead.get('category', '')} {lead.get('city', '')} {lead.get('state', '')}"
            
            # Insert lead
            cursor.execute('''
                INSERT INTO leads (
                    name, category, address, city, state, postal_code, country,
                    phone, website, email,
                    rating, review_count, google_maps_url, place_id,
                    is_claimed, is_open, price_level,
                    ai_lead_score, ai_insights, ai_concerns, recommended_services, ai_outreach_message,
                    status, source, scraped_at, last_updated, search_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead.get('name'),
                lead.get('category'),
                lead.get('address'),
                lead.get('city'),
                lead.get('state'),
                lead.get('postal_code'),
                lead.get('country', 'US'),
                lead.get('phone'),
                lead.get('website'),
                lead.get('email'),
                lead.get('rating'),
                lead.get('review_count'),
                lead.get('google_maps_url'),
                lead.get('place_id'),
                lead.get('is_claimed'),
                lead.get('is_open'),
                lead.get('price_level'),
                lead.get('ai_lead_score'),
                lead.get('ai_insights'),
                lead.get('ai_concerns'),
                lead.get('recommended_services'),
                lead.get('ai_outreach_message'),
                lead.get('status', 'new'),
                lead.get('source', 'google_maps'),
                lead.get('scraped_at'),
                datetime.now().isoformat(),
                search_text
            ))
            
            lead_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return lead_id
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
    
    def get_leads(
        self,
        status: Optional[str] = None,
        min_score: Optional[int] = None,
        city: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = 'ai_lead_score DESC'
    ) -> List[Dict]:
        """
        Get leads from database with filtering
        
        Args:
            status: Filter by status (new, qualified, contacted, converted, rejected)
            min_score: Minimum AI lead score
            city: Filter by city
            limit: Maximum results
            offset: Pagination offset
            order_by: Sort order
        
        Returns:
            List of lead dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query
        query = 'SELECT * FROM leads WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if min_score:
            query += ' AND ai_lead_score >= ?'
            params.append(min_score)
        
        if city:
            query += ' AND city LIKE ?'
            params.append(f'%{city}%')
        
        query += f' ORDER BY {order_by} LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        leads = [dict(row) for row in rows]
        
        conn.close()
        return leads
    
    def update_lead_status(self, lead_id: int, status: str, notes: Optional[str] = None):
        """
        Update lead status
        
        Args:
            lead_id: Lead ID
            status: New status (new, qualified, contacted, converted, rejected)
            notes: Optional notes about status change
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE leads 
            SET status = ?, last_updated = ?, notes = COALESCE(notes || ' | ' || ?, notes, ?)
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), notes, notes, lead_id))
        
        # Log interaction
        if notes:
            cursor.execute('''
                INSERT INTO interactions (lead_id, interaction_type, interaction_date, notes)
                VALUES (?, ?, ?, ?)
            ''', (lead_id, 'status_change', datetime.now().isoformat(), f"Changed to {status}: {notes}"))
        
        conn.commit()
        conn.close()
    
    def add_interaction(self, lead_id: int, interaction_type: str, notes: str, outcome: Optional[str] = None):
        """
        Log an interaction with a lead
        
        Args:
            lead_id: Lead ID
            interaction_type: Type (email, call, meeting, etc.)
            notes: Interaction notes
            outcome: Outcome (interested, not_interested, callback, etc.)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions (lead_id, interaction_type, interaction_date, notes, outcome)
            VALUES (?, ?, ?, ?, ?)
        ''', (lead_id, interaction_type, datetime.now().isoformat(), notes, outcome))
        
        # Update last_contacted
        cursor.execute('''
            UPDATE leads SET last_contacted = ? WHERE id = ?
        ''', (datetime.now().isoformat(), lead_id))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total leads
        cursor.execute('SELECT COUNT(*) FROM leads')
        stats['total_leads'] = cursor.fetchone()[0]
        
        # By status
        cursor.execute('SELECT status, COUNT(*) FROM leads GROUP BY status')
        stats['by_status'] = dict(cursor.fetchall())
        
        # Average score
        cursor.execute('SELECT AVG(ai_lead_score) FROM leads WHERE ai_lead_score IS NOT NULL')
        stats['avg_score'] = round(cursor.fetchone()[0] or 0, 1)
        
        # Top cities
        cursor.execute('SELECT city, COUNT(*) FROM leads WHERE city IS NOT NULL GROUP BY city ORDER BY COUNT(*) DESC LIMIT 5')
        stats['top_cities'] = dict(cursor.fetchall())
        
        # Top categories
        cursor.execute('SELECT category, COUNT(*) FROM leads WHERE category IS NOT NULL GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5')
        stats['top_categories'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def search_leads(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Search leads by name, category, or location
        
        Args:
            search_term: Search term
            limit: Maximum results
        
        Returns:
            List of matching leads
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM leads 
            WHERE search_text LIKE ?
            ORDER BY ai_lead_score DESC
            LIMIT ?
        ''', (f'%{search_term}%', limit))
        
        leads = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return leads
    
    def export_leads(self, status: Optional[str] = None) -> List[Dict]:
        """
        Export all leads for a given status
        
        Args:
            status: Filter by status (or None for all)
        
        Returns:
            List of all matching leads
        """
        return self.get_leads(status=status, limit=100000)


if __name__ == '__main__':
    # Test database
    db = Database()
    print("✅ Database initialized")
    print(f"📊 Stats: {db.get_stats()}")
