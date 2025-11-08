# 🚀 Eleven Views Sports Pipeline - Vercel Deployment Guide

## Overview
This Flask application is configured for seamless deployment on Vercel's serverless platform.

## Prerequisites
- Vercel account (free tier works)
- GitHub account with this repository
- API keys for Apify and Google AI

## Required Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

### Required
```bash
APIFY_API_TOKEN=your_apify_token_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Optional (but recommended)
```bash
FLASK_SECRET_KEY=your_flask_secret_key_here
HUBSPOT_API_KEY=your_hubspot_key_here
HUBSPOT_ENABLED=false
```

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Connect to Vercel**
   - Go to https://vercel.com/new
   - Select "Import Git Repository"
   - Connect your GitHub account
   - Select this repository

2. **Configure Project**
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

3. **Add Environment Variables**
   - Go to Settings → Environment Variables
   - Add all required variables from above
   - Select: Production, Preview, Development
   - Click Save

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build
   - Your app will be live at: `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

4. **Follow prompts**
   - Link to existing project or create new
   - Confirm settings
   - Wait for deployment

## Important Notes

### Database Considerations
- **Current Setup**: SQLite (stored in `/tmp` on Vercel)
- **Limitation**: Data is ephemeral on serverless (resets on each deploy)
- **For Production**: Consider migrating to PostgreSQL (Vercel Postgres, Supabase, or Neon)

### Serverless Limitations
- Each Lambda function has 50MB max deployment size
- 10-second execution timeout (can be extended on Pro plan)
- SQLite database resets on cold starts

### File Structure
```
.
├── app.py              # WSGI entrypoint (required for Vercel)
├── dashboard.py        # Main Flask application
├── database.py         # SQLite database manager
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel configuration
└── .vercelignore      # Files to exclude from deployment
```

## Testing Deployment

After deployment, test these endpoints:

1. **Dashboard Home**
   ```
   https://your-project.vercel.app/
   ```

2. **API Stats**
   ```
   https://your-project.vercel.app/api/stats
   ```

3. **CSV Viewer**
   ```
   https://your-project.vercel.app/csv-viewer
   ```

## Upgrading to Production Database

For production use with persistent data:

### Option 1: Vercel Postgres
```bash
vercel postgres create
```

### Option 2: Supabase
1. Create project at https://supabase.com
2. Get connection string
3. Add to environment variables
4. Update database.py to use PostgreSQL

### Option 3: Neon
1. Create project at https://neon.tech
2. Get connection string
3. Add to environment variables
4. Update database.py to use PostgreSQL

## Troubleshooting

### Issue: Build fails
- Check requirements.txt for unsupported packages
- Verify Python version compatibility (3.9+)
- Check build logs in Vercel dashboard

### Issue: 500 Internal Server Error
- Check Vercel function logs
- Verify environment variables are set
- Ensure API keys are valid

### Issue: Database resets
- Expected behavior with SQLite on serverless
- Migrate to PostgreSQL for persistent data

### Issue: Slow cold starts
- Normal for serverless (first request after idle)
- Upgrade to Vercel Pro for edge caching
- Consider edge functions for critical paths

## Performance Optimization

1. **Enable Edge Caching**
   - Add caching headers to static assets
   - Use Vercel Edge Network

2. **Database Optimization**
   - Use connection pooling with PostgreSQL
   - Implement Redis for session caching

3. **Code Optimization**
   - Minimize dependencies
   - Use lazy loading for heavy imports
   - Optimize database queries

## Monitoring

- **Vercel Analytics**: Automatic page views tracking
- **Function Logs**: Real-time logs in Vercel dashboard
- **Error Tracking**: Configure Sentry or similar

## Custom Domain

1. Go to Vercel Dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Wait for SSL certificate (automatic)

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Flask on Vercel**: https://vercel.com/docs/frameworks/flask
- **GitHub Issues**: [Your repo URL here]

---

**Last Updated**: November 2025
**Deployment Platform**: Vercel Serverless
**Framework**: Flask 3.0.0
**Python Version**: 3.9+
