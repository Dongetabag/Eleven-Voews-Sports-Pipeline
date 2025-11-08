# macOS App Build Instructions

## Prerequisites
- Node.js installed (download from nodejs.org)
- Your HTML app files
- Google AI API key

## Quick Start

1. **Make the build script executable:**
```bash
chmod +x build-macos-app.sh
```

2. **Run the build script:**
```bash
./build-macos-app.sh
```

3. **Configure your API key:**
```bash
cd macos-build
nano .env
```
Add your key:
```
GOOGLE_AI_API_KEY=your_actual_api_key_here
```

4. **Update your JavaScript** to use environment variables:

Replace:
```javascript
const API_KEY = "hardcoded_key";
```

With:
```javascript
const API_KEY = window.ENV?.GOOGLE_AI_API_KEY;
```

Or for async (more secure):
```javascript
async function getApiKey() {
  if (window.electron) {
    return await window.electron.getApiKey();
  }
  return window.ENV?.GOOGLE_AI_API_KEY;
}

const apiKey = await getApiKey();
```

5. **Build the app:**
```bash
cd macos-build
npm run build
```

## Commands

- `npm start` - Test in development
- `npm run build` - Build for your Mac architecture
- `npm run build-universal` - Build for Intel + Apple Silicon

## Output

Built app: `macos-build/dist/MyGoogleAIApp.dmg`

## Troubleshooting

**API key not working:**
- Check `.env` file has your key
- Verify no spaces around `=`
- Restart the build after editing `.env`

**Build fails:**
- Run `npm install` in macos-build directory
- Check Node.js version: `node --version` (need v16+)

**App won't open:**
- Right-click app → Open (first time only)
- Or: System Settings → Privacy & Security → Open Anyway
