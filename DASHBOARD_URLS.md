# 🌐 Dashboard URLs Reference

## Main Dashboard
**URL:** http://localhost:5002/

This is the main Recipe Labs Lead Generator dashboard with:
- Lead statistics
- Lead filtering and search
- Status management
- Export to CSV
- **Sync to HubSpot** button

---

## API Endpoints

### Health Check
```
GET http://localhost:5002/api/v1/health
```
Returns system health status

### Statistics
```
GET http://localhost:5002/api/stats
```
Returns lead statistics (total, by status, top categories, etc.)

### Get Leads
```
GET http://localhost:5002/api/leads
GET http://localhost:5002/api/v1/leads
```
Query parameters:
- `status` - Filter by status (new, qualified, contacted, etc.)
- `min_score` - Minimum AI lead score
- `city` - Filter by city
- `limit` - Number of leads to return

### Get Single Lead
```
GET http://localhost:5002/api/leads/<lead_id>
GET http://localhost:5002/api/v1/leads/<lead_id>
```

### Update Lead Status
```
POST http://localhost:5002/api/leads/<lead_id>/status
PATCH http://localhost:5002/api/v1/leads/<lead_id>/status
```
Body: `{"status": "qualified"}`

### Export Leads
```
GET http://localhost:5002/api/export?status=qualified
```
Downloads CSV file

### Generate Leads
```
POST http://localhost:5002/api/v1/leads/generate
```
Body:
```json
{
  "search": "plumbing companies in Boston",
  "limit": 50
}
```

---

## HubSpot Integration Endpoints

### Test Connection
```
GET http://localhost:5002/api/v1/hubspot/test
Headers: X-API-Key: your-api-key (if configured)
```

### Sync Leads
```
POST http://localhost:5002/api/v1/hubspot/sync
Headers: 
  Content-Type: application/json
  X-API-Key: your-api-key (if configured)
Body:
{
  "status": "qualified",
  "min_score": 70,
  "batch_size": 100
}
```

### Sync Single Lead
```
POST http://localhost:5002/api/v1/hubspot/sync/<lead_id>
Headers: X-API-Key: your-api-key (if configured)
```

---

## Troubleshooting 404 Errors

### If you see "404 Not Found":

1. **Check the Port**
   - Dashboard runs on **port 5002**
   - Use: `http://localhost:5002/`
   - NOT: `http://localhost:5001/` or `http://localhost:5000/`

2. **Check the URL Path**
   - Main dashboard: `/` (root)
   - API endpoints: `/api/...` or `/api/v1/...`
   - HubSpot endpoints: `/api/v1/hubspot/...`

3. **Restart Dashboard After Code Changes**
   If you just added new routes (like HubSpot), restart:
   ```bash
   # Stop current dashboard (Ctrl+C)
   # Then restart:
   python3 launch.py
   # Or:
   python3 dashboard.py
   ```

4. **Verify Route Exists**
   - Check `dashboard.py` for `@app.route()` decorators
   - Check `api/routes.py` for API routes
   - Check `api/hubspot_routes.py` for HubSpot routes

---

## Quick Access

**Main Dashboard:**
👉 http://localhost:5002/

**API Health:**
👉 http://localhost:5002/api/v1/health

**HubSpot Test:**
👉 http://localhost:5002/api/v1/hubspot/test

---

**Note:** If the dashboard isn't running, start it with:
```bash
python3 launch.py
```






