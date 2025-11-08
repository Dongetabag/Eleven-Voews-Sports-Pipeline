# 🚀 AISim Nursing Assistant - Installation Guide

Complete installation instructions for all platforms.

---

## ⚡ Quick Install (Recommended)

### Prerequisites
- Node.js 18+ ([Download here](https://nodejs.org/))
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### One-Command Install

```bash
chmod +x deploy.sh && ./deploy.sh
```

**That's it!** The script will:
1. ✅ Check your system
2. ✅ Install dependencies
3. ✅ Setup environment
4. ✅ Build application
5. ✅ Start server

---

## 📋 Step-by-Step Installation

If you prefer manual installation or the script fails:

### Step 1: Verify Prerequisites

**Check Node.js version:**
```bash
node -v
# Should show v18.0.0 or higher
```

**If Node.js is not installed:**
- Visit https://nodejs.org/
- Download LTS version
- Install and verify

### Step 2: Install Dependencies

```bash
npm install
```

**If you get errors:**
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Step 3: Configure Environment

```bash
# Copy template
cp .env.example .env.local

# Edit the file
nano .env.local
# or
code .env.local
```

**Add your API key:**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 4: Build the Application

```bash
npm run build
```

**This creates:**
- Optimized production build
- Static assets
- Server bundles

### Step 5: Start the Server

**Development mode:**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

### Step 6: Access the Application

Open your browser to:
```
http://localhost:3000
```

---

## 🐳 Docker Installation

### Quick Docker Setup

```bash
# Build image
docker build -t aisim-nursing-assistant .

# Run container
docker run -d \
  -p 3000:3000 \
  -e ANTHROPIC_API_KEY=your-key-here \
  --name aisim-nursing \
  aisim-nursing-assistant
```

### Using Docker Compose

1. **Create .env file:**
```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

---

## ☁️ Cloud Installation

### Vercel (Easiest)

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Login:**
```bash
vercel login
```

3. **Deploy:**
```bash
vercel
```

4. **Add API key:**
```bash
vercel env add ANTHROPIC_API_KEY
# Paste your key when prompted
```

5. **Deploy to production:**
```bash
vercel --prod
```

### Google Cloud Run

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Quick commands:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/aisim-nursing-assistant
gcloud run deploy aisim-nursing-assistant \
  --image gcr.io/PROJECT_ID/aisim-nursing-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your-key
```

---

## 🖥️ Platform-Specific Instructions

### Windows

**Using PowerShell:**
```powershell
# Install dependencies
npm install

# Create environment file
Copy-Item .env.example .env.local

# Edit .env.local in Notepad
notepad .env.local

# Run development server
npm run dev
```

### macOS / Linux

**Using Terminal:**
```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit with your preferred editor
nano .env.local
# or
vim .env.local

# Run development server
npm run dev
```

---

## 🔧 IDE-Specific Setup

### Cursor IDE

1. **Open project:**
```bash
cursor .
```

2. **Open terminal in Cursor** (Ctrl/Cmd + `)

3. **Run deploy script:**
```bash
./deploy.sh
```

See [CURSOR_GUIDE.md](CURSOR_GUIDE.md) for detailed Cursor instructions.

### VS Code

1. **Open project:**
```bash
code .
```

2. **Install recommended extensions:**
- ESLint
- Prettier
- Tailwind CSS IntelliSense

3. **Open terminal** (Ctrl/Cmd + `)

4. **Run commands:**
```bash
npm install
npm run dev
```

---

## 🔑 Getting Your API Key

### Anthropic API Key

1. **Visit:** https://console.anthropic.com/

2. **Sign up or log in**

3. **Navigate to:** API Keys section

4. **Create new key:**
   - Click "Create Key"
   - Give it a name (e.g., "AISim Nursing")
   - Copy the key (starts with `sk-ant-`)

5. **Add to .env.local:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

**⚠️ Important:**
- Keep your key secret
- Never commit to Git
- Rotate regularly
- Monitor usage

---

## ✅ Verify Installation

### Check List

Run these commands to verify:

```bash
# Check Node.js
node -v
# Expected: v18.0.0 or higher

# Check npm
npm -v
# Expected: 9.0.0 or higher

# Check dependencies
npm list --depth=0
# Should show all packages installed

# Check build
npm run build
# Should complete without errors

# Start server
npm run dev
# Should start on port 3000
```

### Test in Browser

1. Open http://localhost:3000
2. You should see the AISim Nursing Assistant interface
3. Try filling out a test chart
4. Verify chart generation works

---

## 🐛 Troubleshooting

### Common Issues

**"Cannot find module"**
```bash
# Solution
rm -rf node_modules package-lock.json
npm install
```

**"Port 3000 already in use"**
```bash
# Find and kill process
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port:
PORT=3001 npm run dev
```

**"API key not found"**
```bash
# Check .env.local exists
ls -la .env.local

# Verify content
cat .env.local

# Ensure proper format
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**Build errors**
```bash
# Clear cache
rm -rf .next
npm run build
```

**Permission denied (deploy.sh)**
```bash
# Make executable
chmod +x deploy.sh
```

---

## 📦 What Gets Installed

### Dependencies (~150 packages)

**Core:**
- next@14.1.0 - React framework
- react@18.2.0 - UI library
- @anthropic-ai/sdk - AI integration

**UI/Styling:**
- tailwindcss - Utility CSS
- framer-motion - Animations
- lucide-react - Icons

**Utilities:**
- jspdf - PDF generation
- date-fns - Date formatting
- typescript - Type safety

### Size
- **node_modules:** ~200MB
- **Build output:** ~15MB
- **Total:** ~215MB

---

## 🔄 Updates and Maintenance

### Update Dependencies

```bash
# Check for updates
npm outdated

# Update all dependencies
npm update

# Update specific package
npm update next

# Major version updates
npm install next@latest
```

### Update Application

```bash
# Pull latest code (if using Git)
git pull

# Reinstall dependencies
npm install

# Rebuild
npm run build

# Restart server
npm start
```

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] API key stored in environment variables
- [ ] .env.local added to .gitignore
- [ ] HTTPS enabled
- [ ] Environment variables secured
- [ ] Dependencies updated
- [ ] Security audit run (`npm audit`)
- [ ] Access logs enabled
- [ ] Backup strategy in place

---

## 📊 System Requirements

### Minimum
- **CPU:** 1 core
- **RAM:** 512MB
- **Storage:** 500MB
- **Node.js:** v18.0.0+
- **Network:** Internet connection

### Recommended
- **CPU:** 2+ cores
- **RAM:** 1GB+
- **Storage:** 2GB+
- **Node.js:** v20.0.0+
- **Network:** Stable broadband

### For Production
- **CPU:** 2+ cores
- **RAM:** 2GB+
- **Storage:** 5GB+
- **Redundancy:** Load balancer
- **Monitoring:** Enabled

---

## 🎯 Next Steps After Installation

1. **Test the System**
   - Generate a test chart
   - Try different chart formats
   - Test export features

2. **Customize (Optional)**
   - Update branding colors
   - Add facility logo
   - Customize chart templates

3. **Train Users**
   - Share USAGE.md with nurses
   - Conduct brief demo
   - Provide support contact

4. **Deploy to Production**
   - Choose deployment platform
   - Configure domain
   - Enable monitoring

5. **Monitor and Maintain**
   - Track API usage
   - Monitor errors
   - Gather feedback

---

## 📚 Additional Resources

- **Main Documentation:** [README.md](README.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **User Guide:** [USAGE.md](USAGE.md)
- **Cursor Guide:** [CURSOR_GUIDE.md](CURSOR_GUIDE.md)
- **Project Summary:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🆘 Getting Help

### Self-Help
1. Check error messages in terminal
2. Review relevant documentation
3. Try troubleshooting steps above

### Support Channels
- **Technical Issues:** IT Department
- **Usage Questions:** See USAGE.md
- **Bugs:** Contact development team

### Useful Commands
```bash
# View logs
npm run dev (watch terminal output)

# Test build
npm run build

# Check versions
npm list

# Clear everything and start fresh
rm -rf node_modules .next package-lock.json
npm install
npm run dev
```

---

## ✨ Success!

You're now ready to use AISim Nursing Assistant!

**Quick start:**
```bash
npm run dev
```

Open http://localhost:3000 and start generating charts!

---

Made with ❤️ by the AISim Team
