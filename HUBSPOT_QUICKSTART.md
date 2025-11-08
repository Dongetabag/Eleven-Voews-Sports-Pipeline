# 🚀 HubSpot Quick Start

## Setup in 3 Steps

### 1. Get HubSpot API Key
1. Go to: https://app.hubspot.com/private-apps
2. Create private app
3. Grant contacts read/write permissions
4. Copy access token

### 2. Add to .env
```env
HUBSPOT_API_KEY=your_token_here
HUBSPOT_ENABLED=true
```

### 3. Sync Leads
```bash
python3 export_leads.py --format hubspot --status qualified --min-score 70
```

## Done! ✅

Your leads are now in HubSpot. See HUBSPOT_SETUP.md for full documentation.
