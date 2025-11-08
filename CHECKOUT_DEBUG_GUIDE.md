# 🔍 STRIPE CHECKOUT NOT WORKING - DEBUG GUIDE

Your checkout session was created successfully (I can see the `cs_test_` ID), but the checkout page isn't loading. Let's fix this step by step.

---

## 🚨 IMMEDIATE CHECKS

### 1. Check Stripe Dashboard

Go to: https://dashboard.stripe.com/test/payments

**Questions:**
- Do you see any recent payment attempts?
- Are there any errors listed?
- What's the status of the checkout session?

---

### 2. Common Issues & Fixes

## Issue #1: No Products/Prices Created in Stripe

**This is the #1 reason checkouts fail!**

### How to Fix:

1. **Go to Stripe Dashboard:**
   https://dashboard.stripe.com/test/products

2. **Create a Product:**
   - Click **"+ Add product"**
   - Name: "AI Sim Premium Monthly"
   - Description: "Monthly subscription to AI Sim Premium"
   - Click **"Add product"**

3. **Add a Price:**
   - Under "Pricing", click **"Add another price"**
   - Choose **"Recurring"**
   - Price: $9.99
   - Billing period: Monthly
   - Click **"Add price"**

4. **Get the Price ID:**
   - Click on the price you just created
   - Copy the **Price ID** (starts with `price_`)
   - Example: `price_1AbCdEfGhIjKlMnO`

5. **Update Your Code:**

You have two options:

#### Option A: Use Price ID (Recommended)

Update your `stripe-routes.js` to use the price ID instead of creating prices on the fly:

```javascript
// In stripe-routes.js - UPDATE the create-checkout-session route

router.post('/create-checkout-session', async (req, res) => {
  try {
    const { priceId, userEmail, userId } = req.body;

    if (!priceId || !userEmail) {
      return res.status(400).json({ 
        error: 'Missing required fields: priceId and userEmail' 
      });
    }

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: 'subscription',
      line_items: [
        {
          price: priceId, // Use the Price ID from Stripe Dashboard
          quantity: 1,
        },
      ],
      success_url: `${process.env.CLIENT_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.CLIENT_URL}/pricing?canceled=true`,
      customer_email: userEmail,
      client_reference_id: userId || userEmail,
      allow_promotion_codes: true,
    });

    res.json({ 
      sessionId: session.id, 
      url: session.url 
    });

  } catch (error) {
    console.error('❌ Error:', error);
    res.status(500).json({ error: error.message });
  }
});
```

#### Option B: Keep Dynamic Pricing (Current Method)

If you want to keep using dynamic pricing (creating prices on the fly), you need to ensure you have a product created first.

**Create a default product:**

```javascript
// Run this once to create a product in your Stripe account
const product = await stripe.products.create({
  name: 'AI Sim Premium',
  description: 'Premium subscription for AI Sim',
});

console.log('Product ID:', product.id);
// Save this product ID and use it in your code
```

Then update your route to use this product ID:

```javascript
price_data: {
  currency: 'usd',
  product: 'prod_YOUR_PRODUCT_ID_HERE', // Add this line
  // ... rest of your price_data
}
```

---

## Issue #2: Checkout Session Expired

Checkout sessions expire after **24 hours**.

### How to Fix:

**Create a new checkout session** - the old URL won't work anymore.

1. Click the "Upgrade" or "Subscribe" button again
2. You'll get a fresh checkout URL
3. Try the new URL immediately

---

## Issue #3: Test Mode vs Live Mode

Make sure you're in **Test Mode** in Stripe Dashboard.

### How to Check:

1. Look at top of Stripe Dashboard
2. There's a toggle: **"Test mode"** / **"Live mode"**
3. Make sure it says **"Viewing test data"**
4. Your keys should start with `pk_test_` and `sk_test_`

---

## Issue #4: CORS / Domain Issues

If the checkout page loads but shows errors, check CORS.

### How to Fix:

In your `server.js`, make sure CORS is configured correctly:

```javascript
app.use(cors({
  origin: [
    'http://localhost:5173',
    'http://localhost:3000',
    process.env.CLIENT_URL,
    'https://checkout.stripe.com' // Add this!
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
}));
```

---

## Issue #5: API Keys Not Set

Check your `.env` file has the correct keys:

```env
STRIPE_SECRET_KEY=sk_test_XXXXXXXXXXXXX
VITE_STRIPE_PUBLIC_KEY=pk_test_XXXXXXXXXXXXX
```

### Verify Keys Work:

```bash
# Test your secret key
curl https://api.stripe.com/v1/customers \
  -u sk_test_YOUR_KEY:

# If valid, you'll get a JSON response
# If invalid, you'll get an authentication error
```

---

## 🔧 RECOMMENDED IMPLEMENTATION

Here's the **simplest, most reliable way** to implement checkout:

### Step 1: Create Products in Stripe Dashboard

**Monthly Plan:**
1. Go to: https://dashboard.stripe.com/test/products
2. Create product: "AI Sim Premium Monthly"
3. Add price: $9.99/month
4. Copy Price ID: `price_1ABC...`

**Annual Plan:**
1. Create product: "AI Sim Premium Annual"  
2. Add price: $99.99/year
3. Copy Price ID: `price_2DEF...`

### Step 2: Update Backend Code

```javascript
// server/stripe-routes.js

router.post('/create-checkout-session', async (req, res) => {
  try {
    const { priceId, userEmail, userId } = req.body;

    console.log('Creating checkout for:', { priceId, userEmail });

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: 'subscription',
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.CLIENT_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.CLIENT_URL}/pricing?canceled=true`,
      customer_email: userEmail,
      client_reference_id: userId,
      metadata: { userId, userEmail },
    });

    console.log('✅ Session created:', session.id);
    res.json({ url: session.url });

  } catch (error) {
    console.error('❌ Checkout error:', error.message);
    res.status(500).json({ error: error.message });
  }
});
```

### Step 3: Update Frontend Code

```typescript
// src/utils/api.ts

export async function createCheckoutSession(
  priceId: string,
  userEmail: string,
  userId?: string
) {
  try {
    const response = await fetch(`${API_URL}/api/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priceId, userEmail, userId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Checkout failed');
    }

    const { url } = await response.json();
    window.location.href = url; // Redirect to Stripe

  } catch (error) {
    console.error('Checkout error:', error);
    throw error;
  }
}
```

### Step 4: Update Your Pricing Component

```typescript
// In your pricing component

const plans = [
  {
    name: 'Monthly',
    priceId: 'price_1ABC...', // Your actual Price ID from Stripe
    price: 9.99,
  },
  {
    name: 'Annual',
    priceId: 'price_2DEF...', // Your actual Price ID from Stripe
    price: 99.99,
  },
];

const handleSubscribe = async (plan) => {
  try {
    await createCheckoutSession(
      plan.priceId,
      user.email,
      user.id
    );
  } catch (error) {
    alert('Checkout failed: ' + error.message);
  }
};
```

---

## 🧪 TESTING STEPS

### 1. Test Backend is Running

```bash
# In terminal
curl http://localhost:3001/health

# Should return:
# {"status":"ok",...}
```

### 2. Test Checkout Creation

```bash
# Test creating a checkout session
curl -X POST http://localhost:3001/api/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{
    "priceId": "price_YOUR_PRICE_ID",
    "userEmail": "test@example.com",
    "userId": "test-user-123"
  }'

# Should return:
# {"url":"https://checkout.stripe.com/c/pay/cs_test_..."}
```

### 3. Test the URL

- Copy the URL from the response
- Paste in browser
- Should see Stripe checkout page

---

## 🎯 QUICK FIX CHECKLIST

Try these in order:

- [ ] Verify you're in Stripe Test Mode
- [ ] Create products/prices in Stripe Dashboard
- [ ] Update code to use Price IDs
- [ ] Restart backend server
- [ ] Clear browser cache
- [ ] Try checkout again
- [ ] Check server logs for errors
- [ ] Verify API keys in `.env`
- [ ] Test with the curl command above

---

## 🆘 STILL NOT WORKING?

### Check Server Logs

When you click checkout, watch your terminal where the server is running. You should see:

```
Creating checkout for: { priceId: 'price_...', userEmail: '...' }
✅ Session created: cs_test_...
```

If you see errors, they'll tell you exactly what's wrong.

### Check Browser Console

Open browser DevTools (F12) and check the Console tab for errors.

Common errors:
- `Failed to fetch` - Backend isn't running
- `404 Not Found` - Wrong API URL
- `CORS error` - CORS misconfigured
- `400 Bad Request` - Missing priceId or invalid data

---

## 📞 WHAT TO SEND ME FOR HELP

If still stuck, send me:

1. **Server logs** (from terminal where server is running)
2. **Browser console errors** (F12 → Console tab)
3. **Your checkout code** (how you're calling the API)
4. **Screenshot of Stripe products page**

---

## ✅ EXPECTED FLOW

When working correctly:

1. User clicks "Subscribe" button
2. Frontend calls backend API
3. Backend creates checkout session
4. Backend returns checkout URL
5. Frontend redirects to Stripe
6. User sees Stripe checkout page ✅
7. User enters card info
8. Payment completes
9. User redirects back to your app

You're at step 6 - the checkout page should load. If it doesn't, it's usually because no product/price exists in Stripe.

---

**Most likely fix:** Create products and prices in Stripe Dashboard, then use those Price IDs in your code!
