# 🔑 HubSpot API Key Setup

## Current Status

✅ **Configuration Complete**
- API key saved to `.env`
- HubSpot integration enabled
- Module loaded successfully

⚠️ **Authentication Issue**
- HubSpot returned: `401 Unauthorized`
- The API key format appears incorrect

## The Problem

The key you provided (`na2-d4c6-18e2-414b-b2fa-22c09b65dbba`) doesn't match HubSpot's private app access token format.

HubSpot private app access tokens:
- Start with `pat-` (private app token)
- Format: `pat-na1-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Are 40+ characters long

## How to Get the Correct API Key

### Step 1: Go to HubSpot Private Apps
1. Log in to HubSpot: https://app.hubspot.com
2. Click **Settings** (gear icon, top right)
3. Navigate to **Integrations** → **Private Apps**
4. Click **Create a private app**

### Step 2: Configure the App
1. **Name**: "Recipe Labs Lead Generator"
2. **Description**: "Sync leads from Recipe Labs Lead Generator"

### Step 3: Set Permissions (Scopes)
Go to the **Scopes** tab and grant:

**Contacts:**
- ✅ `crm.objects.contacts.read`
- ✅ `crm.objects.contacts.write`

**Optional (for companies):**
- `crm.objects.companies.read`
- `crm.objects.companies.write`

### Step 4: Create and Copy Token
1. Click **Create app** at the bottom
2. You'll see the **Access Token**
3. **Copy the entire token** (it starts with `pat-`)
4. It looks like: `pat-na1-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Step 5: Update .env
```bash
# Edit .env file
HUBSPOT_API_KEY=pat-na1-your-actual-token-here
HUBSPOT_ENABLED=true
```

## Test the Connection

After updating the API key:

```bash
python3 -c "
from integrations.hubspot import get_hubspot
hubspot = get_hubspot()
result = hubspot.test_connection()
print('✅ Success!' if result.get('success') else f'❌ Error: {result.get(\"message\")}')
"
```

## Alternative: Check Your Current Key

If you believe your key is correct, verify:

1. **Is it a Private App token?**
   - Must be from Private Apps (not OAuth token)
   - Must start with `pat-`

2. **Are permissions correct?**
   - Must have contacts read/write

3. **Is the app active?**
   - Check that the private app is not deleted/disabled

## Quick Fix

If you have the correct token, update `.env`:

```bash
# Replace with your actual token
HUBSPOT_API_KEY=pat-na1-your-actual-token-here
HUBSPOT_ENABLED=true
```

Then test:
```bash
python3 export_leads.py --format hubspot --status qualified --min-score 70
```

---

**Need Help?** See `HUBSPOT_SETUP.md` for complete documentation.






