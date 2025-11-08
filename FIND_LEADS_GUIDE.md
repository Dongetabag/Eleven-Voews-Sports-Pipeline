# 🔍 Find Leads Guide

## Current Status
**Database:** Empty (0 leads)

You need to generate leads first, then you can search/filter them.

---

## 🚀 Generate New Leads

### Quick Start
```bash
python3 lead_generator.py --search "plumbing companies in Boston" --limit 50
```

### Command Options
```bash
python3 lead_generator.py \
  --search "YOUR_SEARCH_QUERY" \
  --limit NUMBER \
  --no-ai              # Skip AI enrichment (faster, cheaper)
  --no-email            # Skip email finding
```

### Search Query Examples

**By Industry & Location:**
```bash
# Plumbing
python3 lead_generator.py --search "plumbing companies in Boston" --limit 50
python3 lead_generator.py --search "plumbers in Springfield MA" --limit 100

# Restaurants
python3 lead_generator.py --search "restaurants in West Springfield MA" --limit 75
python3 lead_generator.py --search "Italian restaurants in New York" --limit 50

# Healthcare
python3 lead_generator.py --search "dentists in Boston" --limit 50
python3 lead_generator.py --search "chiropractors in Los Angeles" --limit 100

# Professional Services
python3 lead_generator.py --search "lawyers in Chicago" --limit 50
python3 lead_generator.py --search "accountants in Miami" --limit 75

# Home Services
python3 lead_generator.py --search "roofing companies in Denver" --limit 50
python3 lead_generator.py --search "HVAC contractors in Phoenix" --limit 100
```

**By Business Type:**
```bash
# Specific business types
python3 lead_generator.py --search "auto repair shops in Boston" --limit 50
python3 lead_generator.py --search "gyms in Los Angeles" --limit 75
python3 lead_generator.py --search "salons in Miami" --limit 50
```

---

## 📋 Search Existing Leads

Once you have leads in the database, you can search/filter them:

### Via Dashboard (Web UI)
1. Open: http://localhost:5002/
2. Use the filters:
   - **Status**: new, qualified, contacted, converted, rejected
   - **Min Score**: 0-100 (AI lead score)
   - **City**: Filter by city name
3. Click "Filter" to see results

### Via API

**Get All Leads:**
```bash
curl http://localhost:5002/api/leads
```

**Filter by Status:**
```bash
curl "http://localhost:5002/api/leads?status=qualified"
```

**Filter by Score:**
```bash
curl "http://localhost:5002/api/leads?min_score=70"
```

**Filter by City:**
```bash
curl "http://localhost:5002/api/leads?city=Boston"
```

**Combined Filters:**
```bash
curl "http://localhost:5002/api/leads?status=qualified&min_score=70&city=Boston&limit=50"
```

### Via Command Line

**Export Qualified Leads:**
```bash
python3 export_leads.py --status qualified --min-score 70
```

**Export by City:**
```bash
python3 export_leads.py --status qualified --format csv
# Then filter the CSV file
```

**Export for Email Campaign:**
```bash
python3 export_leads.py --format email --status qualified --min-score 70
```

**Export for Cold Calling:**
```bash
python3 export_leads.py --format call --status qualified --min-score 70
```

---

## 🔍 Advanced Search Options

### Python Script
```python
from database import Database

db = Database()

# Search by multiple criteria
leads = db.get_leads(
    status='qualified',
    min_score=70,
    city='Boston',
    limit=100,
    order_by='ai_lead_score DESC'
)

for lead in leads:
    print(f"{lead['name']} - Score: {lead['ai_lead_score']}")
```

### Database Query
```python
from database import Database

db = Database()

# Get stats
stats = db.get_stats()
print(f"Total: {stats['total_leads']}")
print(f"By Status: {stats['by_status']}")
print(f"Top Categories: {stats['top_categories']}")
```

---

## 📊 Search Results Format

Each lead includes:
- **name**: Business name
- **category**: Industry/category
- **city**, **state**: Location
- **phone**, **email**, **website**: Contact info
- **rating**, **review_count**: Google reviews
- **ai_lead_score**: AI-generated score (0-100)
- **ai_insights**: AI-generated insights
- **ai_outreach_message**: Personalized outreach message
- **status**: new, qualified, contacted, converted, rejected

---

## 💡 Tips

1. **Start Small**: Generate 50 leads first to test
2. **Use Specific Searches**: More specific = better results
3. **Filter by Score**: Focus on leads with score 70+
4. **Export Regularly**: Export qualified leads for outreach
5. **Update Status**: Mark leads as contacted/converted in dashboard

---

## 🚨 Troubleshooting

**No leads found?**
- Generate leads first: `python3 lead_generator.py --search "..." --limit 50`

**API keys missing?**
- Add to `.env`: `APIFY_API_TOKEN` and `GOOGLE_API_KEY`

**Search not working?**
- Check dashboard is running: http://localhost:5002/
- Verify database has leads: Check stats in dashboard

---

**Ready to generate leads?** Run:
```bash
python3 lead_generator.py --search "plumbing companies in Boston" --limit 50
```






