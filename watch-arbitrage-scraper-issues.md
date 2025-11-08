# Watch Arbitrage System - Scraper Issues Documentation

**Date:** November 6, 2025  
**System:** Watch Arbitrage MVP - Multi-Source Scraper System  
**Status:** Partial Functionality - Only Reddit Working

---

## Executive Summary

The Watch Arbitrage system has a multi-source scraping architecture designed to collect watch listings from 7 different sources:
1. ✅ **Reddit** - Working (14 listings collected)
2. ❌ **eBay** - Not collecting listings (found items but parsing fails)
3. ❌ **Craigslist** - Not collecting listings
4. ❌ **Amazon** - Not collecting listings (requires browser automation)
5. ❌ **Apify-eBay** - Not collecting listings (token/config issues)
6. ❌ **Apify-Amazon** - Not collecting listings (token/config issues)
7. ❌ **Chrono24** - Not implemented

**Current State:** Only Reddit scraper is successfully collecting and saving listings to the database. All other scrapers are either failing silently, returning 0 listings, or encountering errors during execution.

---

## System Architecture

### File Structure
```
src/scrapers/
├── orchestrator.ts      # Main scraper coordinator
├── reddit.ts           # ✅ Working
├── ebay.ts             # ❌ Issues with parsing
├── craigslist.ts       # ❌ Not collecting listings
├── amazon.ts           # ❌ Requires browser automation
├── apify.ts            # ❌ Token/config issues
└── chrono24.ts         # ❌ Not implemented

src/app/api/
├── scrape/route.ts      # API endpoint for triggering scrapes
└── listings/route.ts   # API endpoint for retrieving listings
```

### Database Schema
- **Table:** `Listing` (PostgreSQL via Prisma)
- **Fields:** id, title, description, price, url, imageUrl, source, postedAt, scrapedAt, dealScore, isAuthentic, isProcessed, metadata

### API Endpoints
- `POST /api/scrape` - Triggers scraping from specified sources
- `GET /api/listings` - Retrieves listings from database
- `GET /api/analytics` - System statistics

---

## Detailed Issue Analysis

### 1. eBay Scraper (`src/scrapers/ebay.ts`)

**Status:** ❌ Finding items but not parsing correctly

**Symptoms:**
- Logs show: `[eBay] Found 69 items with alternative selector`
- But: `[eBay] Collected 0 listings so far`
- Final result: 0 listings saved

**Root Cause:**
The scraper finds items using alternative selectors but fails to extract data from them. The parsing logic in the `items.each()` loop is not correctly extracting:
- Title
- Price
- URL
- Image URL
- Condition

**Code Location:**
- File: `src/scrapers/ebay.ts`
- Lines: ~82-153
- Issue: Selector mismatch or HTML structure changes

**Error Pattern:**
```typescript
// Current code finds items:
const items = $('.s-item')
console.log(`[eBay] Found ${items.length} items`) // Shows 69 items

// But parsing fails:
items.each((index, element) => {
  // Title/price extraction not working
  const title = $item.find('.s-item__title, h3').text().trim()
  const priceText = $item.find('.s-item__price, .s-item__detail--primary').text().trim()
  // These return empty or invalid values
})
```

**Expected Behavior:**
- Should extract title, price, URL, image from each item
- Should filter items with price range $50-$50,000
- Should save to database via orchestrator

**Recent Changes Made:**
- Changed from sold listings to active listings (less blocking)
- Added multiple fallback selectors
- Reduced queries from 5 to 3
- Added better error handling

**What Needs Fixing:**
1. Debug why selectors find items but can't extract data
2. Verify eBay HTML structure matches selectors
3. Add more robust parsing with multiple selector attempts
4. Add logging to see what HTML is actually being parsed

---

### 2. Craigslist Scraper (`src/scrapers/craigslist.ts`)

**Status:** ❌ Not collecting any listings

**Symptoms:**
- No listings found
- May be blocked or selectors incorrect
- No error messages in logs

**Root Cause:**
Unknown - scraper runs but finds 0 items. Possible issues:
- Blocked by Craigslist (captcha/rate limiting)
- Selectors don't match current HTML structure
- Search queries not returning results
- Location/timeout issues

**Code Location:**
- File: `src/scrapers/craigslist.ts`
- Lines: ~36-116
- Issue: Selectors or blocking

**Error Pattern:**
```typescript
// Scraper runs:
console.log(`[Craigslist] Scraping ${loc} for "${searchTerm}"`)

// But finds nothing:
const items = $('.result-row, .cl-search-result')
console.log(`[Craigslist] Found ${items.length} items`) // Always 0
```

**Expected Behavior:**
- Should scrape 3 locations × 2 search terms = 6 searches
- Should find 10-30 listings per location
- Should save to database

**Recent Changes Made:**
- Reduced from 5 locations to 3
- Reduced from 3 terms to 2 per location
- Added block detection
- Added multiple selector fallbacks

**What Needs Fixing:**
1. Verify Craigslist HTML structure matches selectors
2. Test if requests are being blocked
3. Add better error logging to see what HTML is returned
4. Consider using browser automation for Craigslist
5. Test with different locations/search terms

---

### 3. Amazon Scraper (`src/scrapers/amazon.ts`)

**Status:** ❌ Requires browser automation, not configured

**Symptoms:**
- Skips scraping if `USE_BROWSER_AUTOMATION !== 'true'`
- Even with browser automation, may be blocked
- No listings collected

**Root Cause:**
Amazon has strong anti-bot measures. The scraper requires browser automation but:
1. Browser automation may not be properly configured
2. Amazon may still block automated browsers
3. Selectors may not match Amazon's dynamic HTML

**Code Location:**
- File: `src/scrapers/amazon.ts`
- Lines: ~36-135
- Issue: Browser automation + Amazon blocking

**Error Pattern:**
```typescript
if (process.env.USE_BROWSER_AUTOMATION === 'true') {
  // Tries browser automation
} else {
  console.warn(`[Amazon] Browser automation not enabled`)
  continue // Skips Amazon
}
```

**Expected Behavior:**
- Should use browser automation to scrape Amazon
- Should find 10-40 listings per query
- Should extract product details (title, price, rating, reviews)

**Recent Changes Made:**
- Added browser automation requirement check
- Reduced queries from 5 to 2
- Added block detection
- Skips gracefully if not configured

**What Needs Fixing:**
1. Verify browser automation is working (`src/lib/browser-automation.ts`)
2. Test Amazon scraping with browser automation enabled
3. Add better error handling for browser automation failures
4. Consider using Apify actors for Amazon instead
5. Add retry logic for blocked requests

---

### 4. Apify Scrapers (`src/scrapers/apify.ts`)

**Status:** ❌ Token/config issues

**Symptoms:**
- Requires `APIFY_TOKEN` environment variable
- May fail if token invalid or actors unavailable
- No listings collected

**Root Cause:**
- Apify integration requires valid API token
- Actor IDs may be incorrect or actors may not exist
- Error handling may be swallowing errors

**Code Location:**
- File: `src/scrapers/apify.ts`
- Lines: ~31-122
- Issue: Token validation and actor execution

**Error Pattern:**
```typescript
if (!process.env.APIFY_TOKEN) {
  console.warn(`[Apify] APIFY_TOKEN not set - skipping`)
  return []
}

// Actor execution may fail silently
const run = await client.actor(actorId).start(input, {
  waitForFinish: 120,
})
```

**Expected Behavior:**
- Should validate token before attempting
- Should run Apify actors for eBay and Amazon
- Should extract listings from actor results
- Should handle actor failures gracefully

**Recent Changes Made:**
- Added token validation
- Better error messages
- Improved timeout handling

**What Needs Fixing:**
1. Verify `APIFY_TOKEN` is set in environment
2. Verify actor IDs are correct:
   - eBay actor: Check if correct
   - Amazon actor: Check if correct
3. Add better error logging for actor failures
4. Test actor execution independently
5. Handle actor result format correctly

---

### 5. Chrono24 Scraper

**Status:** ❌ Not implemented

**Symptoms:**
- Throws error: "Chrono24 scraper not yet implemented"
- No code exists for Chrono24 scraping

**Code Location:**
- File: `src/scrapers/orchestrator.ts`
- Lines: ~142-144

**What Needs Fixing:**
1. Implement Chrono24 scraper
2. Or remove Chrono24 from active sources list
3. Or add placeholder that returns empty array

---

## Orchestrator Issues (`src/scrapers/orchestrator.ts`)

**Status:** ⚠️ Partially Working

**Issues:**
1. Error handling prevents one scraper failure from stopping others ✅ (Fixed)
2. Logging shows which scrapers are running ✅ (Fixed)
3. But scrapers are still failing silently or returning 0 results ❌

**Code Flow:**
```typescript
export async function scrapeAllSources(options) {
  // Determines active sources
  // Loops through each source
  // Calls scrapeSource() for each
  // Returns results
}

async function scrapeSource(source, options) {
  // Switch statement for each source
  // Calls individual scraper function
  // Processes and saves listings
  // Returns result with counts
}
```

**What Needs Fixing:**
1. Add better error propagation from individual scrapers
2. Add validation that scrapers actually return data
3. Add retry logic for failed scrapers
4. Add metrics/timing for each scraper

---

## API Integration Issues (`src/app/api/scrape/route.ts`)

**Status:** ✅ Working but slow

**Issues:**
1. Scraping takes 30+ seconds, causing timeouts
2. Background scraping not properly implemented
3. No progress updates during scraping

**Code Location:**
- File: `src/app/api/scrape/route.ts`
- Lines: ~36-64

**What Needs Fixing:**
1. Implement proper background job processing
2. Return job ID immediately, check status separately
3. Add WebSocket or polling for progress updates
4. Increase timeout or make truly async

---

## Environment Configuration

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://watch_user:watch_password@localhost:5432/watch_db

# Scrapers
ENABLE_REDDIT_SCRAPER=true
ENABLE_EBAY_SCRAPER=true
ENABLE_CRAIGSLIST_SCRAPER=true
ENABLE_AMAZON_SCRAPER=true
ENABLE_APIFY_SCRAPER=true
USE_BROWSER_AUTOMATION=true  # For Amazon

# Apify
APIFY_TOKEN=your_token_here

# Chrono24
ENABLE_CHRONO24_SCRAPER=false  # Not implemented
```

**Current Configuration:**
- ✅ Database: Connected and working
- ✅ Reddit: Enabled and working
- ⚠️ eBay: Enabled but not working
- ⚠️ Craigslist: Enabled but not working
- ⚠️ Amazon: Enabled but requires browser automation
- ⚠️ Apify: Enabled but requires token
- ❌ Chrono24: Not implemented

---

## Error Logs and Evidence

### Recent Scraper Execution Logs

**eBay:**
```
[Orchestrator] Processing source: ebay
[eBay] Starting scrape with 10 queries
[eBay] Scraping: vintage watch
[eBay] Browser automation failed, trying axios: Error: Protocol error
[eBay] Found 0 items for "vintage watch"
[eBay] No items found - may be blocked or page structure changed
[eBay] Found 69 items with alternative selector
[eBay] Collected 0 listings so far from "vintage watch"
```

**Craigslist:**
```
[Orchestrator] Processing source: craigslist
[Craigslist] Starting scrape for 3 locations
[Craigslist] Scraping boston for "watch"
[Craigslist] Found 0 items in boston for "watch"
```

**Amazon:**
```
[Orchestrator] Processing source: amazon
[Amazon] Starting scrape with 2 queries
[Amazon] Browser automation not enabled - Amazon may block requests
[Amazon] Set USE_BROWSER_AUTOMATION=true for better results
```

**Apify:**
```
[Orchestrator] Processing source: apify-ebay
[Apify] APIFY_TOKEN not set - skipping apify-client/ACTOR_ID
```

**Chrono24:**
```
[Orchestrator] Processing source: chrono24
[Orchestrator] Source chrono24 failed completely: Chrono24 scraper not yet implemented
```

---

## Testing and Validation

### How to Test Each Scraper

**1. Reddit (Working):**
```bash
curl -X POST http://localhost:3000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"sources": ["reddit"]}'
```
✅ Expected: Returns listings

**2. eBay:**
```bash
curl -X POST http://localhost:3000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"sources": ["ebay"]}'
```
❌ Expected: Returns 0 listings (currently failing)

**3. Craigslist:**
```bash
curl -X POST http://localhost:3000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"sources": ["craigslist"]}'
```
❌ Expected: Returns 0 listings (currently failing)

**4. Amazon:**
```bash
# Requires browser automation
USE_BROWSER_AUTOMATION=true curl -X POST http://localhost:3000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"sources": ["amazon"]}'
```
❌ Expected: Returns listings (currently failing)

**5. Apify:**
```bash
# Requires APIFY_TOKEN
APIFY_TOKEN=xxx curl -X POST http://localhost:3000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"sources": ["apify-ebay"]}'
```
❌ Expected: Returns listings (currently failing)

---

## Recommended Fixes

### Priority 1: eBay Scraper
1. **Debug HTML Structure**
   - Log actual HTML received from eBay
   - Verify selectors match current eBay structure
   - Test with different search queries

2. **Fix Parsing Logic**
   - Add multiple selector attempts per field
   - Add validation for extracted data
   - Handle edge cases (missing fields, different formats)

3. **Add Better Error Handling**
   - Log what selectors are being tried
   - Log what data is extracted (even if invalid)
   - Add fallback extraction methods

### Priority 2: Craigslist Scraper
1. **Verify Blocking**
   - Check if requests are being blocked
   - Test with different user agents
   - Consider browser automation

2. **Fix Selectors**
   - Verify Craigslist HTML structure
   - Test selectors manually in browser console
   - Add more fallback selectors

### Priority 3: Amazon Scraper
1. **Fix Browser Automation**
   - Verify `src/lib/browser-automation.ts` is working
   - Test browser automation independently
   - Add better error handling

2. **Alternative Approach**
   - Consider using Apify actors for Amazon
   - Or use Amazon Product Advertising API (if available)

### Priority 4: Apify Integration
1. **Verify Configuration**
   - Check APIFY_TOKEN is valid
   - Verify actor IDs are correct
   - Test actor execution manually

2. **Fix Error Handling**
   - Add better error messages
   - Log actor execution details
   - Handle actor result format correctly

### Priority 5: Chrono24
1. **Implement Scraper**
   - Create `src/scrapers/chrono24.ts`
   - Add to orchestrator switch statement
   - Or remove from active sources

---

## Code References

### Key Files to Fix

1. **`src/scrapers/ebay.ts`**
   - Lines 82-153: Item parsing logic
   - Issue: Selectors find items but can't extract data

2. **`src/scrapers/craigslist.ts`**
   - Lines 64-101: Item parsing logic
   - Issue: Finding 0 items

3. **`src/scrapers/amazon.ts`**
   - Lines 51-67: Browser automation check
   - Issue: Browser automation not working or not configured

4. **`src/scrapers/apify.ts`**
   - Lines 31-122: Actor execution
   - Issue: Token/config problems

5. **`src/scrapers/orchestrator.ts`**
   - Lines 90-346: Source handling
   - Issue: Error handling could be better

6. **`src/lib/browser-automation.ts`**
   - Browser automation implementation
   - Issue: May not be working correctly

---

## Success Criteria

### All Scrapers Working When:
1. ✅ Reddit: Collecting 10+ listings per run
2. ❌ eBay: Collecting 20-50 listings per run
3. ❌ Craigslist: Collecting 10-30 listings per run
4. ❌ Amazon: Collecting 10-40 listings per run (with browser automation)
5. ❌ Apify-eBay: Collecting listings (with valid token)
6. ❌ Apify-Amazon: Collecting listings (with valid token)
7. ❌ Chrono24: Implemented or removed

### System Health Indicators:
- Total listings in database: Should be 100+ after full scrape
- Multiple sources: Should see listings from 3+ sources
- No errors: Scrapers should complete without errors
- Performance: Full scrape should complete in <5 minutes

---

## Additional Context

### System Dependencies
- **Next.js 14**: Framework for API routes
- **Prisma**: Database ORM
- **PostgreSQL**: Database
- **Cheerio**: HTML parsing
- **Axios**: HTTP requests
- **Puppeteer/Browser Automation**: For Amazon
- **Apify Client**: For Apify actors

### Current Database State
- **Total Listings:** 14 (all from Reddit)
- **Sources:** Only "reddit"
- **Last Scrape:** Recent (within last hour)
- **Deal Scores:** None (models not trained yet)

### Next Steps After Fixes
1. Train ML models to generate deal scores
2. Process listings through inference API
3. Set up alert system for high-score deals
4. Implement backtesting framework

---

## Conclusion

The Watch Arbitrage system has a solid foundation with Reddit scraping working correctly. However, 6 out of 7 scrapers are not functioning properly. The main issues are:

1. **eBay**: Parsing logic not extracting data correctly
2. **Craigslist**: Not finding items (blocking or selector issues)
3. **Amazon**: Browser automation not configured/working
4. **Apify**: Token/config issues
5. **Chrono24**: Not implemented

**Recommended Approach:**
1. Fix eBay scraper first (highest priority, most likely to work)
2. Fix Craigslist scraper (simpler than Amazon)
3. Fix Amazon scraper (requires browser automation)
4. Fix Apify integration (requires valid token)
5. Implement or remove Chrono24

**Estimated Time to Fix:** 4-8 hours for all scrapers

---

**Document Generated:** November 6, 2025  
**System Version:** Watch Arbitrage MVP v1.0.0  
**Status:** Ready for AI-assisted debugging and fixes

