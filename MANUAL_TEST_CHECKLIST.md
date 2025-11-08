# 🧪 Manual Testing Checklist

## ✅ Complete this checklist to verify everything works

---

## LOCAL TESTING (http://localhost:3000)

### Test 1: Landing Page
- [ ] Open http://localhost:3000 in browser
- [ ] Page loads with gradient background
- [ ] "Welcome to AiSim" text visible
- [ ] "Get Started for Free" button visible
- [ ] No console errors (press F12 → Console tab)

**Expected:** Beautiful landing page with no errors
**If fails:** Check console for errors

---

### Test 2: Navigation to Login
- [ ] Click "Get Started for Free" button
- [ ] Redirected to login/sign-in page
- [ ] See Clerk UI (sign-in form)
- [ ] "Continue with Google" button visible (white button)

**Expected:** Clerk sign-in page with Google option
**If fails:** Check VITE_CLERK_PUBLISHABLE_KEY in .env

---

### Test 3: Google Sign-In (Local)
- [ ] Click "Continue with Google"
- [ ] Google OAuth opens in popup/redirect
- [ ] Sign in with your Google account
- [ ] Redirected back to app
- [ ] Intake form appears (for new users) OR Dashboard (for returning users)

**Expected:** Successful sign-in and redirect
**If fails:** 
- Check Clerk redirect URLs include http://localhost:3000
- Check Google is enabled in Clerk dashboard

---

### Test 4: Intake Form (New Users Only)
- [ ] Form has pre-filled name (from Google)
- [ ] Can select university, major, academic year
- [ ] Can click "Submit" or "Get Started"
- [ ] Redirected to dashboard

**Expected:** Smooth form submission
**If fails:** Check console errors

---

### Test 5: Dashboard
- [ ] Dashboard loads with user name
- [ ] Navigation menu visible
- [ ] No errors in console

**Expected:** Dashboard with user data
**If fails:** Check Supabase connection

---

### Test 6: Pricing Page
- [ ] Navigate to pricing (if there's a menu/button)
- [ ] See pricing cards (Free, Basic, Pro, Premium)
- [ ] Prices displayed correctly
- [ ] Subscribe buttons visible

**Expected:** All plans displayed
**If fails:** Check PricingPage component

---

### Test 7: Stripe Checkout
- [ ] Click subscribe on any plan
- [ ] Redirected to Stripe checkout page
- [ ] Use test card: `4242 4242 4242 4242`
- [ ] Expiry: Any future date (e.g., 12/25)
- [ ] CVC: Any 3 digits (e.g., 123)
- [ ] Submit payment
- [ ] Redirected back to app

**Expected:** Successful test payment
**If fails:**
- Check VITE_STRIPE_PUBLISHABLE_KEY in .env
- Check Stripe is in test mode

---

## PRODUCTION TESTING (Vercel URL)

### Test 8: Production Deployment
- [ ] Go to Vercel dashboard
- [ ] Find latest deployment
- [ ] Status shows "Ready" ✅
- [ ] Copy production URL

**Your Production URL:** ________________________

---

### Test 9: Production Landing Page
- [ ] Open production URL in browser
- [ ] Landing page loads
- [ ] No 404 errors
- [ ] "Get Started for Free" button works

**Expected:** Same as local
**If fails:** Check Vercel deployment logs

---

### Test 10: Production Google Sign-In
- [ ] Click "Get Started for Free"
- [ ] See Clerk sign-in UI
- [ ] Click "Continue with Google"
- [ ] Sign in with Google
- [ ] Redirected back to production site
- [ ] Intake form or dashboard appears

**Expected:** Google sign-in works
**If fails:**
- Check Clerk domain is added (your production URL)
- Check Clerk redirect URLs include production URL
- Check Google OAuth is enabled in Clerk

---

### Test 11: Production Stripe
- [ ] Navigate to pricing page
- [ ] Click subscribe
- [ ] Stripe checkout loads
- [ ] Test payment works
- [ ] Redirected back

**Expected:** Same as local
**If fails:** Check environment variables in Vercel

---

### Test 12: Supabase Data Sync
- [ ] Sign in with Google (production)
- [ ] Go to Supabase dashboard: https://supabase.com
- [ ] Navigate to Table Editor
- [ ] Check `users` table
- [ ] Your email should appear
- [ ] Check `user_profiles` table
- [ ] Your profile data should be there

**Expected:** User data in Supabase
**If fails:** 
- Check VITE_SUPABASE_URL in Vercel env vars
- Check VITE_SUPABASE_ANON_KEY in Vercel env vars

---

### Test 13: Vercel Analytics
- [ ] Visit your production site a few times
- [ ] Navigate between pages
- [ ] Wait 5 minutes
- [ ] Go to Vercel → Analytics tab
- [ ] Check for visitor data

**Expected:** Analytics showing page views
**If fails:** Analytics may take time to appear

---

## CLERK CONFIGURATION CHECK

### Verify Clerk Settings
- [ ] Go to https://dashboard.clerk.com
- [ ] Select AiSim application
- [ ] Check Configure → Domains
  - [ ] Production domain added (e.g., ai-sim.vercel.app)
- [ ] Check Configure → Redirect URLs
  - [ ] Production URL added with wildcard (*)
  - [ ] Local URLs added (localhost:3000/*)
- [ ] Check Configure → SSO Connections
  - [ ] Google is enabled ✅
- [ ] Check Configure → API Keys
  - [ ] Using production keys (pk_live_...)

---

## VERCEL ENVIRONMENT VARIABLES CHECK

### Verify Vercel Settings
- [ ] Go to Vercel → Settings → Environment Variables
- [ ] Check these are present (Production environment):
  - [ ] `VITE_CLERK_PUBLISHABLE_KEY` = pk_live_...
  - [ ] `VITE_SUPABASE_URL` = https://...
  - [ ] `VITE_SUPABASE_ANON_KEY` = eyJ...
  - [ ] `VITE_STRIPE_PUBLISHABLE_KEY` = pk_test_...
  - [ ] `VITE_API_URL` = (your backend URL or localhost)

---

## 🐛 TROUBLESHOOTING

### Issue: "Invalid publishable key"
**Fix:**
1. Check Clerk key in Vercel env vars
2. Make sure it starts with `pk_live_`
3. Redeploy after adding/updating

### Issue: Google sign-in doesn't redirect back
**Fix:**
1. Check Clerk redirect URLs
2. Must include your EXACT Vercel URL
3. Must have wildcard: `https://your-url.vercel.app/*`

### Issue: Stripe checkout fails
**Fix:**
1. Check Stripe key in Vercel env vars
2. Make sure using test key: `pk_test_...`
3. Check browser console for errors

### Issue: User data not saving to Supabase
**Fix:**
1. Check Supabase URL and key in Vercel
2. Check Supabase logs for errors
3. Verify user_profiles table exists

### Issue: 404 on production
**Fix:**
1. Check Vercel deployment logs
2. Make sure build succeeded
3. Check vercel.json configuration

---

## ✅ SUCCESS CRITERIA

All these should work:
- ✅ Landing page loads locally
- ✅ Landing page loads in production
- ✅ Google sign-in works locally
- ✅ Google sign-in works in production
- ✅ User data saves to Supabase
- ✅ Stripe checkout works (test mode)
- ✅ Analytics tracking (in production)
- ✅ No console errors
- ✅ All pages load without 404s

---

## 📊 SCORING

Count your ✅ checkmarks:

- **30+ checks:** Perfect! Everything works! 🎉
- **25-29 checks:** Great! Minor issues only
- **20-24 checks:** Good! Some features need attention
- **<20 checks:** Needs more configuration

---

**Start testing and check off each item as you go!** 🧪

