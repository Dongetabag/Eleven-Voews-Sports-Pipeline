# 🏷️ STRIPE PRODUCTS - EXACT NAMES & DESCRIPTIONS

Copy and paste these directly into your Stripe product creation forms.

---

## 🆓 PRODUCT 1: FREE TIER

**Note:** You don't need to create this in Stripe since it's free. Just handle it in your app logic.

---

## 📘 PRODUCT 2: STARTER PLAN

### Product Information:

**Name (required):**
```
AI Sim Starter
```

**Description:**
```
For students who want to accelerate their learning. Includes 50 tool uses per day, unlimited custom courses, standard AI model, and priority email support.
```

**Image:** (Optional - upload your logo or leave blank)

**Product Type:** 
- ✅ Recurring

---

### Pricing Information:

**Monthly Price:**
- Amount: `9.99`
- Currency: `USD`
- Billing period: `Monthly`

**Annual Price (if offering):**
- Amount: `97.00` (or whatever you want - typically 2 months free)
- Currency: `USD`
- Billing period: `Yearly`

**After saving, copy these IDs:**
- Monthly Price ID: `price_________` (save this!)
- Annual Price ID: `price_________` (save this!)

---

## 🌟 PRODUCT 3: PRO PLAN (MOST POPULAR)

### Product Information:

**Name (required):**
```
AI Sim Pro
```

**Description:**
```
Unlock the full power of AI for ultimate productivity. Includes unlimited tool uses, access to advanced AI models, exclusive tools (MindMeld & Career Compass), and AI-powered quiz feedback.
```

**Image:** (Optional - upload your logo or leave blank)

**Product Type:** 
- ✅ Recurring

---

### Pricing Information:

**Monthly Price:**
- Amount: `20.00`
- Currency: `USD`
- Billing period: `Monthly`

**Annual Price (35% savings = $156/year):**
- Amount: `156.00`
- Currency: `USD`
- Billing period: `Yearly`

**After saving, copy these IDs:**
- Monthly Price ID: `price_________` (save this!)
- Annual Price ID: `price_________` (save this!)

---

## 👑 PRODUCT 4: LEGEND PLAN

### Product Information:

**Name (required):**
```
AI Sim Legend
```

**Description:**
```
For the dedicated user who wants it all, and more. Includes all Pro features plus early access to new tools, personalized onboarding session (simulated), and an exclusive "Legend" profile badge.
```

**Image:** (Optional - upload your logo or leave blank)

**Product Type:** 
- ✅ Recurring

---

### Pricing Information:

**Monthly Price:**
- Amount: `50.00`
- Currency: `USD`
- Billing period: `Monthly`

**Annual Price (35% savings = $390/year):**
- Amount: `390.00`
- Currency: `USD`
- Billing period: `Yearly`

**After saving, copy these IDs:**
- Monthly Price ID: `price_________` (save this!)
- Annual Price ID: `price_________` (save this!)

---

## 📋 QUICK CREATION CHECKLIST

For each product:

1. **Create Product:**
   - [ ] Go to: https://dashboard.stripe.com/test/products
   - [ ] Click "+ Add product"
   - [ ] Copy/paste Name from above
   - [ ] Copy/paste Description from above
   - [ ] Click "Save product"

2. **Add Monthly Price:**
   - [ ] Click "Add another price"
   - [ ] Select "Recurring"
   - [ ] Enter monthly amount
   - [ ] Set billing period to "Monthly"
   - [ ] Click "Add price"
   - [ ] **Copy the Price ID** (starts with `price_`)

3. **Add Annual Price (Optional):**
   - [ ] Click "Add another price" again
   - [ ] Select "Recurring"
   - [ ] Enter annual amount (with 35% discount)
   - [ ] Set billing period to "Yearly"
   - [ ] Click "Add price"
   - [ ] **Copy the Price ID** (starts with `price_`)

4. **Save Price IDs:**
   - [ ] Create a note with all Price IDs
   - [ ] You'll need these in your code!

---

## 🎯 PRICE ID REFERENCE SHEET

After creating all products, fill this out:

```javascript
// Copy this to use in your code

const STRIPE_PRICES = {
  starter: {
    monthly: 'price_________________', // Starter Monthly
    annual: 'price_________________',  // Starter Annual (optional)
  },
  pro: {
    monthly: 'price_________________', // Pro Monthly
    annual: 'price_________________',  // Pro Annual
  },
  legend: {
    monthly: 'price_________________', // Legend Monthly
    annual: 'price_________________',  // Legend Annual
  },
};
```

---

## 💡 PRO TIPS

### Tip 1: Use Metadata
When creating products, click "More options" and add metadata:

**For Starter:**
```
tier: starter
tool_limit: 50
features: unlimited_courses,priority_support
```

**For Pro:**
```
tier: pro
tool_limit: unlimited
features: advanced_ai,exclusive_tools,quiz_feedback
```

**For Legend:**
```
tier: legend
tool_limit: unlimited
features: all_pro,early_access,onboarding,legend_badge
```

### Tip 2: Product Images
Use the same logo for all plans, or create distinct badges for each tier:
- Starter: Blue badge
- Pro: Purple/Pink badge (to match "Most Popular")
- Legend: Gold badge

### Tip 3: Annual Pricing
The standard discount for annual plans is 15-20%. You're showing "Save 35%" which is very generous!

**Calculations for 35% off:**
- Starter Annual: $9.99 × 12 × 0.65 = **$77.94** (round to $78 or $77)
- Pro Annual: $20 × 12 × 0.65 = **$156**
- Legend Annual: $50 × 12 × 0.65 = **$390**

---

## 🔄 AFTER CREATING PRODUCTS

### Update Your Frontend Code

```typescript
// src/components/Pricing.tsx (or wherever you handle pricing)

const plans = [
  {
    name: 'Starter',
    price: 9.99,
    priceId: 'price_STARTER_MONTHLY_ID', // Replace with actual ID
    annualPriceId: 'price_STARTER_ANNUAL_ID', // Replace with actual ID
    features: [
      '50 tool uses per day',
      'Unlimited custom courses',
      'Standard AI model',
      'Priority email support',
    ],
  },
  {
    name: 'Pro',
    price: 20.00,
    priceId: 'price_PRO_MONTHLY_ID', // Replace with actual ID
    annualPriceId: 'price_PRO_ANNUAL_ID', // Replace with actual ID
    popular: true,
    features: [
      'Unlimited tool uses',
      'Access to advanced AI models',
      'Exclusive tools: MindMeld & Career Compass',
      'AI-powered quiz feedback',
    ],
  },
  {
    name: 'Legend',
    price: 50.00,
    priceId: 'price_LEGEND_MONTHLY_ID', // Replace with actual ID
    annualPriceId: 'price_LEGEND_ANNUAL_ID', // Replace with actual ID
    features: [
      'All Pro features',
      'Early access to new tools',
      'Personalized onboarding session',
      'Exclusive "Legend" profile badge',
    ],
  },
];

// In your click handler:
const handleChoosePlan = async (plan) => {
  const isAnnual = billingToggle === 'annual'; // Your toggle state
  const priceId = isAnnual ? plan.annualPriceId : plan.priceId;
  
  await createCheckoutSession(
    priceId,
    user.email,
    user.id
  );
};
```

---

## ✅ VERIFICATION

After creating all products, verify:

1. Go to: https://dashboard.stripe.com/test/products
2. You should see 3 products:
   - ✅ AI Sim Starter
   - ✅ AI Sim Pro
   - ✅ AI Sim Legend
3. Each should have at least 1 price (monthly)
4. Optionally 2 prices each (monthly + annual)

---

## 🚀 READY TO TEST

Once you have your Price IDs:

1. Update your code with the actual Price IDs
2. Restart your server
3. Go to your pricing page
4. Click any "Choose" button
5. Should redirect to Stripe checkout ✅
6. Use test card: `4242 4242 4242 4242`

---

## 📸 EXAMPLE STRIPE PRODUCT VIEW

Your Stripe products page should look like this:

```
Products (3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ AI Sim Starter          │ $9.99/mo  │
│ For students who want   │           │
│ to accelerate their...  │           │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ AI Sim Pro             │ $20.00/mo │
│ Unlock the full power  │           │
│ of AI for ultimate...  │           │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ AI Sim Legend          │ $50.00/mo │
│ For the dedicated user │           │
│ who wants it all...    │           │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

**Now go create those products in Stripe! 🎉**
