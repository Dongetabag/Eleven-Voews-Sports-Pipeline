# 🚀 DEPLOY TO VERCEL NOW - Step by Step

## ✅ Everything is Ready!

Your application is **100% configured** and ready to deploy. All API keys are set up.

---

## 🎯 OPTION 1: Deploy via Vercel Dashboard (5 Minutes)

### Step 1: Go to Vercel
**Open in browser:** https://vercel.com/new

### Step 2: Import Your Repository
1. Click **"Import Git Repository"**
2. If asked, authorize Vercel to access your GitHub
3. Search for: `Eleven-Voews-Sports-Pipeline`
4. Select the repository
5. Click **"Import"**

### Step 3: Configure Project Settings
**You'll see a configuration screen:**

- **Framework Preset:** Select **"Other"** (or leave as detected)
- **Root Directory:** Leave as `./`
- **Build Command:** Leave empty (auto-detected)
- **Output Directory:** Leave empty
- **Install Command:** Leave empty (uses requirements.txt)

Click **"Deploy"** at the bottom

⏸️ **WAIT!** Before the build completes, quickly go to the next step...

### Step 4: Add Environment Variables (CRITICAL!)

While the build is running (or if it fails):

1. Click **"Environment Variables"** tab in the configuration screen

   OR after deployment fails, go to:
   - **Settings** → **Environment Variables**

2. **Add these 5 variables one by one:**

   Click **"Add New"** for each:

   | Name | Value |
   |------|-------|
   | `APIFY_API_TOKEN` | `[See .env file or contact admin]` |
   | `GOOGLE_API_KEY` | `[See .env file or contact admin]` |
   | `FLASK_SECRET_KEY` | `[See .env file or contact admin]` |
   | `HUBSPOT_API_KEY` | `[See .env file or contact admin]` |
   | `HUBSPOT_ENABLED` | `true` |

3. **For EACH variable:**
   - ✅ Check **Production**
   - ✅ Check **Preview**
   - ✅ Check **Development**
   - Click **"Save"**

### Step 5: Redeploy (If needed)

If the first deployment failed (expected if env vars weren't set):

1. Go to **"Deployments"** tab
2. Click the **⋯** (three dots) on the latest deployment
3. Click **"Redeploy"**
4. Check ✅ **"Use existing build cache"** (or clear it if you want)
5. Click **"Redeploy"**

### Step 6: Wait for Build (~2-3 minutes)

You'll see:
```
Building...
├─ Installing Python dependencies
├─ Detecting Python version from requirements.txt
├─ Installing packages from requirements.txt
└─ Build completed
```

### Step 7: 🎉 SUCCESS!

You'll see:
- ✅ **Deployment Status: Ready**
- Your production URL: `https://eleven-voews-sports-pipeline.vercel.app`
  (or similar)

Click **"Visit"** to see your live app!

---

## 🎯 OPTION 2: Deploy via Vercel CLI (For Developers)

### Prerequisites
```bash
# Already installed! ✅
vercel --version
# Output: 48.9.0
```

### Steps

1. **Login to Vercel**
   ```bash
   vercel login
   ```
   - Opens browser
   - Confirm login
   - Return to terminal

2. **Deploy**
   ```bash
   cd /home/user/Eleven-Voews-Sports-Pipeline
   vercel --prod
   ```

3. **Follow Prompts**
   ```
   ? Set up and deploy? [Y/n] y
   ? Which scope? <Your Account>
   ? Link to existing project? [y/N] n
   ? What's your project's name? eleven-views-sports-pipeline
   ? In which directory is your code located? ./
   ```

4. **Add Environment Variables via CLI**
   ```bash
   # Add each variable (values are in .env file)
   vercel env add APIFY_API_TOKEN
   # Paste value from .env file
   # Select: Production, Preview, Development

   vercel env add GOOGLE_API_KEY
   # Paste value from .env file

   vercel env add FLASK_SECRET_KEY
   # Paste value from .env file

   vercel env add HUBSPOT_API_KEY
   # Paste value from .env file

   vercel env add HUBSPOT_ENABLED
   # Type: true
   ```

5. **Redeploy with Environment Variables**
   ```bash
   vercel --prod
   ```

---

## 🧪 Test Your Deployment

Once deployed, test these endpoints:

### 1. **Dashboard Home**
```
https://your-app.vercel.app/
```
Expected: Beautiful dark-themed dashboard with "ELEVEN VIEWS" branding

### 2. **API Stats**
```
https://your-app.vercel.app/api/stats
```
Expected: JSON response:
```json
{
  "total_leads": 0,
  "by_status": {},
  "avg_score": 0.0,
  "top_cities": {},
  "top_categories": {}
}
```

### 3. **CSV Viewer**
```
https://your-app.vercel.app/csv-viewer
```
Expected: CSV file viewer interface

### 4. **API Leads**
```
https://your-app.vercel.app/api/leads
```
Expected: JSON array (empty initially):
```json
[]
```

---

## 🎨 Your Live Dashboard Features

Once deployed, you'll have access to:

✅ **Lead Generation Dashboard**
- 🔍 Market scanning for sports industry
- 🎯 AI-powered lead scoring
- 💼 HubSpot integration
- 📊 Analytics and reporting
- 📤 CSV export
- 🎨 Luxury dark theme with gold accents

✅ **API Endpoints**
- `/api/stats` - Database statistics
- `/api/leads` - Get filtered leads
- `/api/generate` - Generate new leads
- `/api/export` - Export to CSV
- `/api/v1/hubspot/sync` - Sync to HubSpot

---

## ⚠️ Important Notes

### Database (Current Setup)
- **Type:** SQLite (ephemeral on Vercel)
- **Storage:** `/tmp` directory
- **Persistence:** ❌ Data resets on each deployment
- **For Production:** Upgrade to PostgreSQL (see below)

### Upgrade to PostgreSQL (Recommended)

When you're ready for production with persistent data:

**Option A: Vercel Postgres**
```bash
vercel postgres create
vercel link
vercel env pull .env.local
```

**Option B: Supabase** (Free tier available)
1. Go to https://supabase.com
2. Create new project
3. Get connection string
4. Add to Vercel env vars:
   ```
   DATABASE_URL=postgresql://...
   ```

**Option C: Neon** (Serverless Postgres)
1. Go to https://neon.tech
2. Create project
3. Get connection string
4. Add to Vercel env vars

---

## 🐛 Troubleshooting

### Issue: "Error: No existing credentials found"
**Solution:** You need to run `vercel login` first (Option 2)

### Issue: Build fails with "Module not found"
**Solution:**
- Check `requirements.txt` is present
- Verify all dependencies are listed
- Check Vercel build logs for specific error

### Issue: 500 Internal Server Error
**Solution:**
1. Check Vercel Function Logs (Dashboard → Logs)
2. Verify environment variables are set
3. Check API keys are valid

### Issue: "Invalid API key" errors
**Solution:**
1. Verify API keys in Vercel dashboard
2. Make sure no extra spaces in the values
3. Redeploy after fixing

### Issue: Database is empty after each deploy
**Expected behavior with SQLite on serverless!**
- Upgrade to PostgreSQL for persistence
- See "Upgrade to PostgreSQL" section above

---

## 📊 Monitoring Your Deployment

### Vercel Dashboard
**URL:** https://vercel.com/dashboard

Monitor:
- 📈 Analytics (page views, users)
- 🔧 Function logs (errors, requests)
- ⚡ Performance metrics
- 🌍 Geographic distribution

### HubSpot Integration
Once leads are synced:
- View in HubSpot CRM
- Track lead status
- Monitor conversion pipeline

---

## 🎉 What's Next?

After successful deployment:

1. **Test Lead Generation**
   - Click "🔍 New Market Scan"
   - Enter: "professional sports teams in Miami, FL"
   - Wait for AI-powered lead generation

2. **Explore Dashboard**
   - View analytics
   - Filter leads by score
   - Export to CSV
   - Sync to HubSpot

3. **Customize Branding**
   - Edit colors in `dashboard.py`
   - Update company info in `config.py`
   - Add your logo

4. **Upgrade Database**
   - Follow PostgreSQL migration guide
   - Set up automated backups

---

## 📞 Support Resources

- **Vercel Docs:** https://vercel.com/docs
- **Flask on Vercel:** https://vercel.com/docs/frameworks/flask
- **Deployment Guide:** See `VERCEL_DEPLOY_GUIDE.md` in repo
- **API Keys Help:** See `.env.example` in repo

---

## ✅ Pre-Deployment Checklist

- [x] API keys configured
- [x] Environment variables ready
- [x] Vercel.json configured
- [x] .vercelignore optimized
- [x] Requirements.txt updated
- [x] Flask secret key generated
- [x] HubSpot integration enabled
- [x] Code pushed to GitHub
- [ ] **→ NOW DEPLOY TO VERCEL! ←**

---

## 🚀 YOU'RE READY TO DEPLOY!

**Choose your deployment method above and launch in 5 minutes!**

Your app URL will be: `https://eleven-voews-sports-pipeline.vercel.app`
(or your custom domain)

**Good luck! 🎉**
