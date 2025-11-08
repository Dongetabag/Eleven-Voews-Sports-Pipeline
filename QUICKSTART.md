# 🚀 Quick Start Guide - Recipe Labs Lead Generator

## Get Up and Running in 10 Minutes

---

## Step 1: Install Dependencies (2 minutes)

```bash
cd recipe-labs-leadgen
pip install -r requirements.txt
```

---

## Step 2: Get API Keys (3 minutes)

### Apify API Token
1. Go to https://console.apify.com/account/integrations
2. Sign up for free account (you get $5 free credits)
3. Click "Create new token"
4. Name it "Recipe Labs Lead Gen"
5. Copy the token

### Google AI API Key
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

---

## Step 3: Configure Environment (1 minute)

```bash
# Copy template
cp .env.template .env

# Edit .env file and add your keys
nano .env  # or use your favorite editor
```

Paste your keys:
```env
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxx
```

---

## Step 4: Generate Your First Leads (2 minutes)

```bash
# Generate 50 leads for plumbing companies in Boston
python lead_generator.py --search "plumbing companies in Boston" --limit 50
```

You should see:
```
🔍 Searching Google Maps: 'plumbing companies in Boston'
   Target: 50 results | Min Rating: 3.5
⚙️  Starting Apify scraper...
📥 Fetching results...
✅ Scraped 50 businesses
✅ 48 businesses match rating criteria
🧠 Enriching 48 leads with AI...
   Processing 1/48: AAA Plumbing... ✅ Saved & Qualified (Score: 82)
   ...
```

---

## Step 5: View Your Leads (1 minute)

```bash
python dashboard.py
```

Open browser to: **http://localhost:5000**

You'll see:
- 📊 Stats dashboard
- 🎯 Qualified leads list
- 💬 AI-generated outreach messages
- 📤 Export options

---

## Step 6: Export for Outreach (1 minute)

```bash
# Export qualified leads with outreach messages
python export_leads.py --status qualified --format email
```

Opens: `exports/email_campaign_qualified_YYYYMMDD_HHMMSS.csv`

Contains:
- Name
- Email
- Subject line
- Personalized message
- Contact info

**Ready to send!**

---

## 🎯 Common Use Cases

### Use Case 1: Daily Lead Generation
```bash
# Run once per day automatically at 9 AM
python automation.py --mode daily --time "09:00"
```

### Use Case 2: Rapid Database Building
```bash
# Generate 500 leads across multiple industries
python automation.py --mode once --runs 10
```

### Use Case 3: Export for Cold Calling
```bash
python export_leads.py --status qualified --format call --min-score 75
```

### Use Case 4: CRM Import
```bash
python export_leads.py --status qualified --format crm
```

---

## 🎨 Customize for Your Business

Edit `config.py` to customize:

```python
# Your target industries
TARGET_INDUSTRIES = [
    "plumbing companies",
    "HVAC contractors",
    "law firms",
    # Add your industries here
]

# Your service areas
TARGET_LOCATIONS = [
    "West Springfield, MA",
    "Boston, MA",
    # Add your cities here
]
```

---

## 📊 Understanding Lead Scores

**AI Lead Score (0-100):**
- **75-100**: Hot leads - High intent, strong fit
- **50-74**: Warm leads - Good potential
- **0-49**: Cold leads - Lower priority

**Scoring Factors:**
- ⭐ Google rating (up to +30 points)
- 💬 Review count (up to +20 points)
- 🌐 Has website (+10 points)
- 🆕 Unclaimed listing (+10 points, opportunity!)

---

## 💡 Pro Tips

### Tip 1: Target Unclaimed Businesses
```bash
# These businesses often need help the most!
# Look for "Not claimed" badge in dashboard
```

### Tip 2: Use Location Filters
```bash
python lead_generator.py --search "restaurants" --location "Boston, MA"
```

### Tip 3: Quality Over Quantity
```bash
# Higher rating = better leads
python lead_generator.py --search "law firms in Chicago" --min-rating 4.5
```

### Tip 4: Batch Different Cities
```bash
# Morning: Boston
python lead_generator.py --search "HVAC contractors in Boston" --limit 50

# Afternoon: Springfield  
python lead_generator.py --search "HVAC contractors in Springfield" --limit 50
```

---

## 🔧 Troubleshooting

### "APIFY_API_TOKEN not found"
- Make sure you created `.env` file (not `.env.template`)
- Check that your API keys are correctly pasted
- No quotes needed around the keys in .env

### "No leads found"
- Try a broader search query
- Lower your `--min-rating` threshold
- Check if Apify has credits (free tier = $5/month)

### Dashboard won't load
- Make sure you ran `python lead_generator.py` first
- Check that port 5000 isn't in use
- Try: `python dashboard.py` and open http://localhost:5000

### AI messages are generic
- The AI gets better with more context
- Try generating leads for specific industries
- Higher-rated businesses = better AI personalization

---

## 📈 Scaling to 1,000+ Leads

Once you've tested with 50-100 leads:

```bash
# 1. Generate leads across all industries
for industry in "plumbing" "HVAC" "roofing" "law firms"
do
  python lead_generator.py --search "$industry in Boston" --limit 100
done

# 2. Or use automation
python automation.py --mode continuous
# Press Ctrl+C after a few hours

# 3. Export all qualified leads
python export_leads.py --status qualified --format email

# 4. Import to your CRM or email system
```

---

## 🎓 Next Steps

### Week 1: Internal Use
- Generate 1,000 leads
- Test outreach messages
- Track conversion rates
- **Goal**: Get 5-10 client meetings

### Week 2: Optimize
- Refine your ICP in `config.py`
- A/B test outreach messages
- Add more target locations
- **Goal**: 15% response rate

### Week 3: Productize
- Build white-label dashboard
- Create client documentation
- Set up billing
- **Goal**: Sign first agency client

### Month 2: Scale
- Automate onboarding
- Add CRM integrations
- Build affiliate program
- **Goal**: $10K MRR

---

## 💰 Revenue Roadmap

| Metric | Month 1 | Month 2 | Month 3 |
|--------|---------|---------|---------|
| Leads Generated | 1,000 | 5,000 | 10,000 |
| Internal Use Revenue | $5K | $10K | $20K |
| White Label Clients | 0 | 2 | 5 |
| White Label Revenue | $0 | $4K | $10K |
| **Total MRR** | **$5K** | **$14K** | **$30K** |

---

## 🆘 Need Help?

Common issues:
- Check README.md for detailed documentation
- Review config.py for all settings
- Test with `--limit 10` first before large batches

---

## ✅ Success Checklist

- [ ] Installed dependencies
- [ ] Got API keys
- [ ] Generated first 50 leads
- [ ] Viewed dashboard
- [ ] Exported leads to CSV
- [ ] Sent first outreach email
- [ ] Got first response!
- [ ] Signed first client!

---

**You're ready to generate leads! 🎉**

Run this to get started:
```bash
python lead_generator.py --search "your industry in your city" --limit 50
```
