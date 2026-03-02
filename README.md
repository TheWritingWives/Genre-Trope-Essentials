# AI Author Tools — The Writing Wives

A multi-tool Streamlit app for romance and genre fiction authors. Four paid tools with Stripe payment gating, coupon support for Skool members, and a lifetime access option.

**Live tools:**
- 📖 Blurb Auditor — $27
- 📱 FB & Instagram Ad Package — $25
- 🎨 Cover Assessment — $15
- 🛒 Amazon Page Assessment — $19
- 🏆 Lifetime Access — all four tools — $97

---

## Prerequisites

You need accounts at two services before deploying:

1. **OpenRouter** — provides the AI model (Claude). Sign up at [openrouter.ai](https://openrouter.ai) and create an API key.
2. **Stripe** — handles payments. Sign up at [stripe.com](https://stripe.com) and get your Secret Key.

---

## Deployment — Streamlit Cloud

### Step 1 — Push to GitHub

1. Create a new **private** GitHub repository.
2. Push this entire folder to it. Confirm `.gitignore` is present so `secrets.toml` is never committed.

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**.
3. Select your repository, set the main file to `app.py`.
4. Click **Advanced settings** — you'll add secrets in Step 4.
5. Click **Deploy**. Note your app URL — it looks like `https://your-app-name.streamlit.app`.

### Step 3 — Create Stripe Payment Links

In your [Stripe Dashboard](https://dashboard.stripe.com/payment-links) → **Payment Links** → **Create payment link**, create **5 links** — one per product.

For each link, go to **After payment** → **Redirect customers to your website** and enter the URL from the table below. Replace `YOUR-APP` with your actual Streamlit subdomain.

| Product | Price | Success URL (paste into Stripe) |
|---|---|---|
| Blurb Auditor | $27 | `https://YOUR-APP.streamlit.app/Order_Confirmed?tool=blurb&session_id={CHECKOUT_SESSION_ID}` |
| FB & Instagram Ad Package | $25 | `https://YOUR-APP.streamlit.app/Order_Confirmed?tool=ad&session_id={CHECKOUT_SESSION_ID}` |
| Cover Assessment | $15 | `https://YOUR-APP.streamlit.app/Order_Confirmed?tool=cover&session_id={CHECKOUT_SESSION_ID}` |
| Amazon Page Assessment | $19 | `https://YOUR-APP.streamlit.app/Order_Confirmed?tool=amazon&session_id={CHECKOUT_SESSION_ID}` |
| Lifetime Access | $97 | `https://YOUR-APP.streamlit.app/Order_Confirmed?tool=lifetime&session_id={CHECKOUT_SESSION_ID}` |

**Your Payment Links (replace YOUR-APP with your Streamlit URL):**

| Product | Payment Link |
|---|---|
| Blurb Auditor | https://buy.stripe.com/7sYeVcgXv9Gu6sa0vy48003 |
| FB & Instagram Ad Package | https://buy.stripe.com/4gMfZgdLjcSGbMu1zC48004 |
| Cover Assessment | https://buy.stripe.com/fZufZggXv05UcQy1zC48005 |
| Amazon Page Assessment | https://buy.stripe.com/fZudR836FaKy17Q4LO48006 |
| Lifetime Access | ⚠️ Not yet created — add when ready |

> ⚠️ **Important:** Paste `{CHECKOUT_SESSION_ID}` exactly as shown. It is a Stripe variable — Stripe replaces it with a real session ID at checkout automatically.

Once each link is created, copy the `https://buy.stripe.com/...` URL. You'll need all five in the next step.

### Step 4 — Add Secrets to Streamlit Cloud

In Streamlit Cloud → your app → **Settings** → **Secrets**, paste the following with your real values filled in:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
MODEL              = "anthropic/claude-sonnet-4-5"

STRIPE_SECRET_KEY = "sk_live_your-secret-key-here"

STRIPE_PAYMENT_LINK = "https://buy.stripe.com/7sYeVcgXv9Gu6sa0vy48003"
PRICE_DISPLAY       = "$27"
PRICE_SUBTITLE      = "per report · unlimited audits"

STRIPE_AD_LINK    = "https://buy.stripe.com/4gMfZgdLjcSGbMu1zC48004"
AD_PRICE_DISPLAY  = "$25"
AD_PRICE_SUBTITLE = "per report · ad copy for your blurb"

STRIPE_COVER_LINK    = "https://buy.stripe.com/fZufZggXv05UcQy1zC48005"
COVER_PRICE_DISPLAY  = "$15"
COVER_PRICE_SUBTITLE = "per report · per cover"

STRIPE_AMAZON_LINK    = "https://buy.stripe.com/fZudR836FaKy17Q4LO48006"
AMAZON_PRICE_DISPLAY  = "$19"
AMAZON_PRICE_SUBTITLE = "per report · full page review"

# STRIPE_LIFETIME_LINK  = "https://buy.stripe.com/ADD-WHEN-CREATED"
LIFETIME_PRICE_DISPLAY  = "$97"
LIFETIME_PRICE_SUBTITLE = "one-time · all four tools · forever"

COUPON_CODES = "WRITINGWIVES, SKOOLMEMBER"
```

A fully annotated version of this config is in `.streamlit/secrets.toml.example`.

### Step 5 — Test the payment flow

1. In Stripe, switch to **Test mode** and create a second set of 5 test Payment Links with the same success URLs.
2. Use Stripe's test card: `4242 4242 4242 4242` (any future expiry, any CVC).
3. Complete a test checkout — you should land on the Order Confirmed page and be forwarded to the tool.
4. Once confirmed working, switch your secrets to the live Stripe key and live Payment Links.

---

## File Structure

```
blurb-auditor-app/
├── app.py                          # Homepage — tool cards + lifetime access block
├── requirements.txt                # Python dependencies
├── logo.png                        # Writing Wives logo (used in every page)
├── .gitignore
│
├── pages/
│   ├── 1_Blurb_Auditor.py          # Blurb audit tool
│   ├── 2_FB_Ad_Package.py          # Facebook/Instagram ad copy generator
│   ├── 3_Cover_Assessment.py       # Cover image analysis (vision AI)
│   ├── 4_Amazon_Assessment.py      # Amazon product page scraper + assessment
│   └── 5_Order_Confirmed.py        # Post-payment confirmation + access grant
│
└── .streamlit/
    ├── secrets.toml.example        # Template — copy to secrets.toml for local dev
    └── secrets.toml                # Real secrets — NEVER commit this file
```

---

## How Access Works

| Method | How it works |
|---|---|
| **Pay** | User clicks Buy → Stripe Checkout → redirects to Order Confirmed page with session ID → payment verified → access granted in session → user sent to their tool |
| **Coupon** | User enters coupon code on the tool page → instant access |
| **Lifetime** | Same as Pay — grants access to all four tools at once |

Access is held in Streamlit `session_state` for the duration of the browser session. If a user closes the tab they will need to re-purchase or re-enter a coupon. This is intentional for per-report pricing.

---

## Coupon Codes

Set in Secrets. Case-insensitive, comma-separated.

```toml
# Master list — unlocks ALL tools
COUPON_CODES = "WRITINGWIVES, SKOOLMEMBER, LAUNCH2026"

# Optional: per-tool lists (fall back to COUPON_CODES if not set)
# AD_COUPON_CODES     = "ADPACKAGE"
# COVER_COUPON_CODES  = "COVERCHECK"
# AMAZON_COUPON_CODES = "AMAZONCHECK"
```

**Ideas for codes:**
- Shared Skool member code: `WRITINGWIVES`
- Launch promo: `LAUNCH2026`
- Individual gift access: `GIFT-JANE-APR26`
- Beta testers: `BETAACCESS`

To invalidate a code, remove it from Secrets and reboot the app.

---

## Changing Prices

Prices are controlled entirely by Secrets — no code changes needed.

1. Update the `PRICE_DISPLAY` value in Streamlit Cloud → Settings → Secrets.
2. Update the corresponding Stripe Payment Link to charge the new amount.
3. Reboot the app (Settings → Reboot app).

---

## Running Locally

```bash
# 1. Clone your repo
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml — use test Stripe keys (sk_test_...) for local work

# 5. Run
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Costs

| Item | Cost |
|---|---|
| Streamlit Cloud hosting | Free |
| Stripe processing | 2.9% + 30¢ per transaction |
| OpenRouter AI per report | ~$0.003–$0.008 (under a cent) |

On a $27 sale, Stripe takes ~$1.08, so you net ~$25.92. AI cost per report is negligible.

---

## Adding a New Tool

1. Create `pages/6_Tool_Name.py` — follow the access-check pattern from any existing page.
2. Add the tool to the `TOOLS` list in `app.py`.
3. Create a new Stripe Payment Link with success URL:
   `https://YOUR-APP.streamlit.app/Order_Confirmed?tool=newtool&session_id={CHECKOUT_SESSION_ID}`
4. Add a new entry to `TOOL_META` in `pages/5_Order_Confirmed.py`.
5. Add the access flag to `grant_access_for_tool()` in `Order_Confirmed` and to `grant_lifetime_access()` in `app.py`.

---

## Support

Questions or payment issues: **hello@thewritingwives.com**
