# 🔗 HubSpot Integration Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Get Your HubSpot API Key

1. Log in to HubSpot: https://app.hubspot.com
2. Go to **Settings** (gear icon in top right)
3. Navigate to **Integrations** → **Private Apps**
4. Click **Create a private app**
5. Name it: "Recipe Labs Lead Generator"
6. Grant these scopes:
   - **Contacts**: `crm.objects.contacts.read`, `crm.objects.contacts.write`
   - **Companies**: `crm.objects.companies.read` (optional)
7. Click **Create app**
8. Copy the **Access Token**

### Step 2: Add API Key to .env

Edit your `.env` file:

```env
HUBSPOT_API_KEY=your_hubspot_access_token_here
```

### Step 3: Install HubSpot Client

```bash
pip install hubspot-api-client
```

### Step 4: Enable HubSpot in Config

Edit `config.py`:

```python
HUBSPOT_ENABLED = True
```

Or set in `.env`:

```env
HUBSPOT_ENABLED=true
```

### Step 5: Test Connection

```bash
python3 -c "from integrations.hubspot import get_hubspot; print(get_hubspot().test_connection())"
```

---

## Usage

### Sync Leads to HubSpot

#### Via Command Line

```bash
# Sync all qualified leads
python3 export_leads.py --format hubspot --status qualified

# Sync with minimum score
python3 export_leads.py --format hubspot --status qualified --min-score 70
```

#### Via Python

```python
from export_leads import LeadExporter

exporter = LeadExporter()
stats = exporter.sync_to_hubspot(
    status='qualified',
    min_score=70
)

print(f"Created: {stats['created']}")
print(f"Updated: {stats['updated']}")
```

#### Via API

```bash
curl -X POST http://localhost:5002/api/v1/hubspot/sync \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "qualified",
    "min_score": 70
  }'
```

---

## Field Mapping

Recipe Labs fields are automatically mapped to HubSpot:

| Recipe Labs | HubSpot Property |
|------------|------------------|
| name | company |
| name (first part) | firstname |
| name (last part) | lastname |
| email | email |
| phone | phone |
| website | website |
| city | city |
| state | state |
| postal_code | zip |
| address | address |
| category | industry |
| status | hs_lead_status |
| ai_lead_score | lead_score |
| rating | google_rating |
| review_count | review_count |
| ai_insights | ai_insights |
| ai_outreach_message | outreach_message |
| google_maps_url | google_maps_url |

**Lead Source**: Automatically set to "Recipe Labs Lead Generator"

---

## Status Mapping

| Recipe Labs Status | HubSpot Status |
|-------------------|----------------|
| new | NEW |
| qualified | QUALIFIED |
| contacted | CONTACTED |
| converted | CONVERTED |
| rejected | REJECTED |

---

## Features

### ✅ Automatic Deduplication
- Checks for existing contacts by email
- Updates existing contacts instead of creating duplicates

### ✅ Batch Processing
- Syncs leads in batches of 100
- Respects HubSpot rate limits (90 requests per 10 seconds)

### ✅ Error Handling
- Continues syncing even if individual leads fail
- Logs all errors for debugging

### ✅ Rate Limiting
- Built-in rate limiter prevents API overages
- Automatic retry logic

---

## Testing

### Test Connection

```bash
# Via Python
python3 -c "from integrations.hubspot import get_hubspot; import json; print(json.dumps(get_hubspot().test_connection(), indent=2))"

# Via API
curl http://localhost:5002/api/v1/hubspot/test \
  -H "X-API-Key: your-api-key"
```

### Sync Test Lead

```python
from integrations.hubspot import get_hubspot

hubspot = get_hubspot()
test_lead = {
    'name': 'Test Company',
    'email': 'test@example.com',
    'phone': '555-1234',
    'city': 'Boston',
    'state': 'MA',
    'status': 'qualified',
    'ai_lead_score': 85
}

result = hubspot.sync_lead(test_lead)
print(result)
```

---

## Troubleshooting

### "HubSpot integration not enabled"

**Solution**: 
1. Add `HUBSPOT_API_KEY` to `.env`
2. Set `HUBSPOT_ENABLED = True` in `config.py` or `.env`

### "hubspot-api-client not installed"

**Solution**:
```bash
pip install hubspot-api-client
```

### "Invalid API key"

**Solution**:
1. Verify your API key in HubSpot
2. Check that you granted the correct scopes
3. Ensure the key hasn't expired

### "Rate limit exceeded"

**Solution**:
- The system automatically rate limits
- If you see this error, reduce batch size or wait a few seconds

---

## Advanced Configuration

### Custom Property Mapping

Edit `integrations/hubspot.py` to customize field mappings:

```python
def _map_lead_to_hubspot_contact(self, lead: Dict) -> Dict:
    properties = {
        # Add custom mappings here
        'custom_property': lead.get('your_field'),
    }
    return properties
```

### Batch Size

Adjust batch size in sync calls:

```python
exporter.sync_to_hubspot(batch_size=50)  # Smaller batches
```

---

## API Endpoints

### Test Connection
```
GET /api/v1/hubspot/test
Headers: X-API-Key: your-api-key
```

### Sync Leads
```
POST /api/v1/hubspot/sync
Headers: X-API-Key: your-api-key
Body: {
  "status": "qualified",
  "min_score": 70,
  "batch_size": 100
}
```

### Sync Single Lead
```
POST /api/v1/hubspot/sync/<lead_id>
Headers: X-API-Key: your-api-key
```

---

## Best Practices

1. **Sync Regularly**: Set up automation to sync qualified leads daily
2. **Filter Before Syncing**: Only sync high-quality leads (min_score: 70+)
3. **Monitor Rate Limits**: HubSpot allows 100 requests per 10 seconds
4. **Test First**: Always test with a few leads before bulk sync
5. **Backup**: Export to CSV before syncing as backup

---

## Automation Example

Add to `automation.py`:

```python
# After generating leads, sync qualified ones to HubSpot
if HUBSPOT_ENABLED:
    from export_leads import LeadExporter
    exporter = LeadExporter()
    exporter.sync_to_hubspot(status='qualified', min_score=70)
```

---

**Status**: ✅ Ready to Use  
**Last Updated**: 2024






