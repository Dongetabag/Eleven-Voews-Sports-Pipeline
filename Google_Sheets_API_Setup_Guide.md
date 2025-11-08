# Google Sheets API Setup Guide for n8n

**Complete Step-by-Step Instructions**

---

## 🎯 What You Need

By the end of this guide, you'll have:
- ✅ Client ID
- ✅ Client Secret
- ✅ OAuth2 credentials for n8n

---

## 📋 Step-by-Step Setup

### Step 1: Go to Google Cloud Console

**Open this link**: https://console.cloud.google.com/

Or run:
```bash
open https://console.cloud.google.com/
```

---

### Step 2: Create a New Project (or Select Existing)

1. Click the **project dropdown** at the top of the page (next to "Google Cloud")
2. Click **"NEW PROJECT"** button (top right of the popup)
3. Enter project details:
   - **Project name**: `n8n-automation` (or any name you like)
   - **Organization**: Leave as-is or select if you have one
4. Click **"CREATE"**
5. Wait 10-20 seconds for the project to be created
6. Click the **notification bell** icon (top right) to see when it's ready
7. Click **"SELECT PROJECT"** in the notification

---

### Step 3: Enable Google Sheets API

**Method 1: Direct Link**
- Open: https://console.cloud.google.com/apis/library/sheets.googleapis.com
- Click the **"ENABLE"** button
- Wait for it to activate (5-10 seconds)

**Method 2: Manual Navigation**
1. From Google Cloud Console, click the **☰ menu** (top left)
2. Go to **"APIs & Services"** → **"Library"**
3. Search for **"Google Sheets API"**
4. Click on it
5. Click **"ENABLE"**

---

### Step 4: Enable Google Drive API

**Method 1: Direct Link**
- Open: https://console.cloud.google.com/apis/library/drive.googleapis.com
- Click the **"ENABLE"** button
- Wait for it to activate (5-10 seconds)

**Method 2: Manual Navigation**
1. In the API Library, search for **"Google Drive API"**
2. Click on it
3. Click **"ENABLE"**

---

### Step 5: Configure OAuth Consent Screen

**Direct Link**: https://console.cloud.google.com/apis/credentials/consent

**Or Navigate**: ☰ Menu → APIs & Services → OAuth consent screen

#### 5.1 Choose User Type
- Select **"External"** (unless you have Google Workspace)
- Click **"CREATE"**

#### 5.2 OAuth Consent Screen - App Information
Fill in the required fields:

- **App name**: `n8n Automation` (or your preferred name)
- **User support email**: Your email address (select from dropdown)
- **App logo**: (Optional - skip for now)
- **Application home page**: (Optional - skip)
- **Application privacy policy link**: (Optional - skip)
- **Application terms of service link**: (Optional - skip)
- **Authorized domains**: (Leave empty for now)
- **Developer contact information**: Your email address

Click **"SAVE AND CONTINUE"**

#### 5.3 Scopes
- Click **"ADD OR REMOVE SCOPES"**
- In the filter box, type: `sheets`
- Check these scopes:
  - `Google Sheets API` - `.../auth/spreadsheets` (See, edit, create, and delete all your Google Sheets spreadsheets)
  - `Google Sheets API` - `.../auth/drive` (See, edit, create, and delete all of your Google Drive files)
  
- In the filter box, type: `drive`
- Check:
  - `Google Drive API` - `.../auth/drive` (See, edit, create, and delete all of your Google Drive files)

Click **"UPDATE"** at the bottom
Click **"SAVE AND CONTINUE"**

#### 5.4 Test Users
- Click **"+ ADD USERS"**
- Enter your email address
- Click **"ADD"**
- Click **"SAVE AND CONTINUE"**

#### 5.5 Summary
- Review everything
- Click **"BACK TO DASHBOARD"**

---

### Step 6: Create OAuth 2.0 Client ID

**Direct Link**: https://console.cloud.google.com/apis/credentials

**Or Navigate**: ☰ Menu → APIs & Services → Credentials

#### 6.1 Create Credentials
1. Click **"+ CREATE CREDENTIALS"** at the top
2. Select **"OAuth client ID"** from the dropdown

#### 6.2 Configure OAuth Client
Fill in these details:

- **Application type**: Select **"Web application"**
- **Name**: `n8n Google Sheets Integration`

#### 6.3 Add Authorized Redirect URI
Under **"Authorized redirect URIs"**:

1. Click **"+ ADD URI"**
2. Paste this EXACT URL:
   ```
   http://localhost:5678/rest/oauth2-credential/callback
   ```
3. Press Enter

**⚠️ IMPORTANT**: The URL must be EXACTLY as shown above. No trailing slash!

#### 6.4 Create
- Click **"CREATE"** button at the bottom

---

### Step 7: Copy Your Credentials

A popup will appear: **"OAuth client created"**

You'll see:
- **Your Client ID**: Something like `123456789-abc123.apps.googleusercontent.com`
- **Your Client Secret**: Something like `GOCSPX-abc123xyz789`

**📋 COPY BOTH OF THESE!**

You can also:
- Click **"DOWNLOAD JSON"** to save them
- Or click **"OK"** and find them later in the Credentials list

---

### Step 8: Enter Credentials in n8n

Go back to your n8n window (http://localhost:5678)

In the **Google Sheets OAuth2 API** form:

1. **OAuth Redirect URL**: Already filled (http://localhost:5678/rest/oauth2-credential/callback)
2. **Client ID**: Paste your Client ID here
3. **Client Secret**: Paste your Client Secret here
4. **Allowed HTTP Request Domains**: Leave as "All"
5. Click **"Save"** (red button, top right)

---

### Step 9: Authenticate

After saving, n8n will show an **"OAuth Sign In"** button:

1. Click **"Sign in with Google"** or **"Authenticate"**
2. A Google login page will open
3. Sign in with your Google account
4. You may see a warning: **"Google hasn't verified this app"**
   - Click **"Advanced"**
   - Click **"Go to n8n Automation (unsafe)"**
5. Review the permissions
6. Click **"Allow"**
7. You'll be redirected back to n8n
8. Connection should now show as **"Connected"** with a green checkmark ✅

---

## ✅ Verification

To verify it's working:

1. In n8n, create a new workflow
2. Add a **Google Sheets** node
3. Select your newly created credential
4. It should load your Google Sheets without errors

---

## 🔧 Quick Links Reference

| Step | Direct Link |
|------|-------------|
| Google Cloud Console | https://console.cloud.google.com/ |
| Enable Sheets API | https://console.cloud.google.com/apis/library/sheets.googleapis.com |
| Enable Drive API | https://console.cloud.google.com/apis/library/drive.googleapis.com |
| OAuth Consent Screen | https://console.cloud.google.com/apis/credentials/consent |
| Create Credentials | https://console.cloud.google.com/apis/credentials |

---

## 📝 Important Information to Copy

### OAuth Redirect URI for n8n:
```
http://localhost:5678/rest/oauth2-credential/callback
```

### Required APIs to Enable:
1. ✅ Google Sheets API
2. ✅ Google Drive API

### Required OAuth Scopes:
- `https://www.googleapis.com/auth/spreadsheets` (Google Sheets)
- `https://www.googleapis.com/auth/drive` (Google Drive)

---

## 🐛 Troubleshooting

### "Redirect URI mismatch" error
**Fix**: Make sure the OAuth Redirect URI in Google Cloud exactly matches:
```
http://localhost:5678/rest/oauth2-credential/callback
```
- No `https://`
- No trailing `/`
- Exact port number: `5678`

### "Access blocked: This app's request is invalid"
**Fix**: 
1. Make sure both APIs are enabled (Sheets + Drive)
2. Check that OAuth Consent Screen is configured
3. Add yourself as a Test User

### "This app isn't verified"
**Fix**: 
- Click "Advanced"
- Click "Go to [app name] (unsafe)"
- This is normal for personal projects

### Can't find credentials later
**Fix**:
- Go to: https://console.cloud.google.com/apis/credentials
- Find your OAuth 2.0 Client ID in the list
- Click the pencil icon to view details
- Client ID is visible, but you'll need to regenerate Client Secret if lost

---

## 🎯 Summary Checklist

Before entering credentials in n8n, verify:

- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled
- [ ] OAuth Consent Screen configured
- [ ] Test user added (your email)
- [ ] OAuth 2.0 Client ID created
- [ ] Redirect URI added: `http://localhost:5678/rest/oauth2-credential/callback`
- [ ] Client ID copied
- [ ] Client Secret copied

---

## 💡 Pro Tips

1. **Save Your Credentials**: Download the JSON file for backup
2. **Document Your Project**: Note the project name and ID
3. **Multiple Credentials**: You can create multiple OAuth clients if needed
4. **Production Setup**: For production, use HTTPS and update redirect URIs
5. **Quota Monitoring**: Google APIs have usage quotas - monitor in Google Cloud Console

---

## 🚀 Next Steps

Once connected, you can:
- Read data from Google Sheets
- Write data to Google Sheets
- Create new sheets
- Update existing sheets
- Automate spreadsheet workflows
- Integrate with other n8n nodes

---

**Need Help?**
- n8n Documentation: https://docs.n8n.io/integrations/builtin/credentials/google/
- Google Cloud Support: https://console.cloud.google.com/support

---

*Last Updated: October 28, 2025*  
*For: n8n v1.117.2*  
*Platform: macOS*








