# 🚀 Production Deployment Guide

## Enterprise-Grade Lead Generation System

This guide covers deploying the Recipe Labs Lead Generator to production.

---

## 📋 Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] API keys configured in `.env`:
  - [ ] `APIFY_API_TOKEN`
  - [ ] `GOOGLE_API_KEY`
  - [ ] `API_MASTER_KEY` (for API authentication)
  - [ ] `FLASK_SECRET_KEY` (for session security)

### 2. Optional Services (Recommended)
- [ ] Hunter.io API key (for email finding)
- [ ] Clearbit API key (for company enrichment)
- [ ] Snov.io credentials (alternative email finder)

### 3. System Requirements
- [ ] Minimum 2GB RAM
- [ ] 10GB+ free disk space
- [ ] Network access for API calls

---

## 🐳 Docker Deployment (Recommended)

### Quick Start

```bash
# 1. Build and start
docker-compose up -d

# 2. Check logs
docker-compose logs -f

# 3. Access dashboard
# Open: http://localhost:5000
```

### Manual Docker Build

```bash
# Build image
docker build -t recipe-labs-leadgen .

# Run container
docker run -d \
  --name leadgen \
  -p 5000:5000 \
  -e APIFY_API_TOKEN=your_token \
  -e GOOGLE_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  recipe-labs-leadgen
```

---

## 🖥️ Native Python Deployment

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit .env with your API keys
nano .env
```

### 3. Run Pre-Flight Checks

```bash
python launch.py
```

### 4. Start Production Server

#### Option A: Using Gunicorn (Recommended)

```bash
gunicorn --bind 0.0.0.0:5000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  dashboard:app
```

#### Option B: Using launch.py

```bash
python launch.py
```

#### Option C: Direct Flask (Development Only)

```bash
python dashboard.py
```

---

## 🔒 Security Configuration

### 1. API Authentication

Set `API_MASTER_KEY` in `.env`:

```env
API_MASTER_KEY=your-secure-random-key-here
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Flask Secret Key

Set `FLASK_SECRET_KEY` in `.env`:

```env
FLASK_SECRET_KEY=your-secret-key-here
```

### 3. Rate Limiting

Rate limits are configured in `api/routes.py`. Adjust as needed:
- Default: 100 requests/hour, 10/minute
- Generate endpoint: 10/hour (requires auth)

### 4. HTTPS (Production)

Use a reverse proxy (nginx/Apache) with SSL:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoint

```bash
curl http://localhost:5000/api/v1/health
```

### System Monitoring

```python
from utils.monitoring import get_monitor

monitor = get_monitor()
health = monitor.check_health()
print(health)
```

### Log Files

- `logs/recipe_labs.log` - Main application log
- `logs/recipe_labs.json.log` - Structured JSON log
- `logs/errors.log` - Error-only log

---

## 💾 Database Management

### Automatic Backups

Backups are created automatically before major operations.

### Manual Backup

```python
from utils.backup import DatabaseBackup

backup = DatabaseBackup()
backup_path = backup.create_backup()
print(f"Backup created: {backup_path}")
```

### Restore Backup

```python
from utils.backup import DatabaseBackup
from pathlib import Path

backup = DatabaseBackup()
backup.restore_backup(Path("backups/leads_backup_20240101_120000.db"))
```

---

## 🔄 Automation Setup

### Daily Lead Generation

```bash
# Using cron
0 9 * * * cd /path/to/recipe-labs-leadgen && python automation.py --mode once >> logs/cron.log 2>&1
```

### Systemd Service (Linux)

Create `/etc/systemd/system/leadgen.service`:

```ini
[Unit]
Description=Recipe Labs Lead Generator
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/recipe-labs-leadgen
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 dashboard:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable leadgen
sudo systemctl start leadgen
```

---

## 📈 Performance Optimization

### 1. Caching

Caching is enabled by default:
- API responses: 1 hour
- AI analysis: 2 hours
- Cache directory: `cache/`

### 2. Database Optimization

- Indexes are automatically created
- Regular VACUUM recommended for SQLite:
```sql
VACUUM;
```

### 3. Rate Limiting

Rate limiters prevent API abuse:
- Apify: 30 calls/minute
- Google AI: 60 calls/minute

---

## 🚨 Troubleshooting

### Issue: "APIFY_API_TOKEN not found"

**Solution:** Ensure `.env` file exists and contains valid token.

### Issue: "Port 5000 already in use"

**Solution:** Change port or stop conflicting service:
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Issue: "Database locked"

**Solution:** Check for concurrent access. SQLite handles one writer at a time.

### Issue: High memory usage

**Solution:** 
- Reduce worker count in Gunicorn
- Clear cache: `rm -rf cache/*`
- Archive old logs

---

## 📞 API Usage Examples

### Generate Leads

```bash
curl -X POST http://localhost:5000/api/v1/leads/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "plumbing companies in Boston",
    "max_results": 50,
    "auto_qualify": true,
    "min_score": 60
  }'
```

### Get Leads

```bash
curl "http://localhost:5000/api/v1/leads?status=qualified&limit=10"
```

### Update Lead Status

```bash
curl -X PATCH http://localhost:5000/api/v1/leads/123/status \
  -H "Content-Type: application/json" \
  -d '{"status": "contacted", "notes": "Called and left voicemail"}'
```

---

## ✅ Post-Deployment Verification

1. **Health Check**
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

2. **Generate Test Leads**
   ```bash
   python lead_generator.py --search "test query" --limit 5
   ```

3. **Check Dashboard**
   - Open http://localhost:5000
   - Verify leads appear
   - Test filtering and export

4. **Monitor Logs**
   ```bash
   tail -f logs/recipe_labs.log
   ```

---

## 🎯 Production Best Practices

1. **Regular Backups**: Set up automated daily backups
2. **Monitor Logs**: Check error logs daily
3. **Update Dependencies**: Keep packages updated
4. **Rate Limiting**: Adjust limits based on usage
5. **Database Maintenance**: Run VACUUM weekly
6. **Security**: Rotate API keys quarterly
7. **Performance**: Monitor system resources

---

## 🚀 Scaling Considerations

### Horizontal Scaling

For high traffic, use a load balancer with multiple instances:

```nginx
upstream leadgen {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}
```

### Database Scaling

For production, consider migrating to PostgreSQL:
- Better concurrency
- Better performance at scale
- Easier replication

---

## 📚 Additional Resources

- [Apify Documentation](https://docs.apify.com)
- [Google AI Documentation](https://ai.google.dev)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Gunicorn Documentation](https://gunicorn.org)

---

**System Status:** ✅ Production Ready  
**Last Updated:** 2024  
**Version:** 1.0.0






