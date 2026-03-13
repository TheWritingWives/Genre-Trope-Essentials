# Supabase Setup — Affiliate System

Run this SQL in your Supabase project to create the two required tables.

Go to: **Supabase Dashboard → your project → SQL Editor → New query**
Paste everything below and click **Run**.

---

```sql
-- ─────────────────────────────────────────────────────────────────────────────
-- TABLE 1: affiliates
-- One row per affiliate. The "code" is their login and referral token.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS affiliates (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code            TEXT UNIQUE NOT NULL,        -- e.g. "JANE_SMITH"
  name            TEXT NOT NULL,               -- e.g. "Jane Smith"
  email           TEXT DEFAULT '',             -- for your records
  commission_rate NUMERIC DEFAULT 0.20,        -- 0.20 = 20%
  notes           TEXT DEFAULT '',
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- TABLE 2: affiliate_sales
-- One row per tracked purchase. Logged automatically when a buyer
-- arrives via an affiliate referral link and completes checkout.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS affiliate_sales (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  affiliate_code     TEXT NOT NULL,            -- matches affiliates.code
  stripe_session_id  TEXT NOT NULL UNIQUE,     -- prevents duplicate logging
  product            TEXT NOT NULL,            -- 'blurb' | 'ad' | 'cover' | 'amazon' | 'lifetime'
  sale_amount        NUMERIC NOT NULL,         -- full price paid (e.g. 27.00)
  commission_amount  NUMERIC NOT NULL,         -- your payout to affiliate (e.g. 5.40)
  customer_email     TEXT DEFAULT '',
  status             TEXT DEFAULT 'unpaid',    -- 'unpaid' | 'paid'
  sale_date          TIMESTAMPTZ DEFAULT now(),
  paid_at            TIMESTAMPTZ
);
```

---

## After running the SQL

1. Go to **Project Settings → API** in Supabase
2. Copy your **service_role** secret key (under "Project API keys")
3. Paste it into `.streamlit/secrets.toml` as `SUPABASE_SERVICE_KEY`
4. Also add `ADMIN_PASSWORD` and `APP_BASE_URL` to your secrets

That's it — the affiliate system is ready to use.

---

## Table 3 — affiliate_applications

Run this SQL in your Supabase SQL Editor to add the affiliate signup form table:

```sql
CREATE TABLE IF NOT EXISTS affiliate_applications (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name           TEXT NOT NULL,
  requested_code TEXT NOT NULL,
  paypal_email   TEXT NOT NULL,
  marketing_plan TEXT NOT NULL,
  status         TEXT DEFAULT 'pending',  -- pending | approved | rejected
  applied_at     TIMESTAMPTZ DEFAULT now(),
  reviewed_at    TIMESTAMPTZ
);
```
