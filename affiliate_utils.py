"""
Affiliate tracking utilities — The Writing Wives AI Author Tools
----------------------------------------------------------------
Handles referral capture, sale logging, and earnings lookup via Supabase.

Supabase tables required (run the SQL in SUPABASE_SETUP.md to create them):
  - affiliates       : one row per affiliate (code, name, email, rate)
  - affiliate_sales  : one row per tracked purchase
"""

import streamlit as st
from datetime import datetime, timezone

# ── Commission & pricing ───────────────────────────────────────────────────────
DEFAULT_COMMISSION_RATE = 0.20  # 20 %

PRODUCT_PRICES = {
    "blurb":    27.00,
    "ad":       25.00,
    "cover":    15.00,
    "amazon":   19.00,
    "lifetime": 97.00,
}

PRODUCT_NAMES = {
    "blurb":    "Blurb Auditor",
    "ad":       "FB & Instagram Ad Package",
    "cover":    "Cover Assessment",
    "amazon":   "Amazon Page Assessment",
    "lifetime": "Lifetime Access — All Tools",
}


# ── Supabase client ────────────────────────────────────────────────────────────
def _get_supabase():
    """Return a Supabase client, or None if not configured."""
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None


# ── Ref capture ────────────────────────────────────────────────────────────────
def capture_ref() -> str:
    """
    Call at the top of EVERY page.
    Reads ?ref= from the URL and stores it in session_state so it
    survives navigation. Returns the active ref (or "" if none).
    """
    ref = st.query_params.get("ref", "")
    if ref:
        st.session_state["affiliate_ref"] = ref.strip().upper()
    return st.session_state.get("affiliate_ref", "")


def affiliate_payment_link(base_link: str) -> str:
    """
    Append ?client_reference_id=REF to a Stripe Payment Link URL
    when an affiliate ref is active in session state.
    Stripe stores this on the CheckoutSession and we read it back
    in Order Confirmed to credit the sale.
    """
    ref = st.session_state.get("affiliate_ref", "")
    if base_link and ref:
        # Stripe Payment Links accept client_reference_id as a query param
        sep = "&" if "?" in base_link else "?"
        return f"{base_link}{sep}client_reference_id={ref}"
    return base_link


# ── Affiliate lookup ───────────────────────────────────────────────────────────
def get_affiliate(code: str) -> dict | None:
    """Return affiliate row dict, or None if code doesn't exist."""
    sb = _get_supabase()
    if not sb or not code:
        return None
    try:
        result = (
            sb.table("affiliates")
            .select("*")
            .eq("code", code.strip().upper())
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None


# ── Sale logging ───────────────────────────────────────────────────────────────
def log_sale(
    affiliate_code: str,
    stripe_session_id: str,
    product: str,
    customer_email: str = "",
) -> bool:
    """
    Record an affiliate sale. Idempotent — safe to call multiple times
    for the same stripe_session_id (duplicate check prevents double-logging).
    Returns True on success, False on failure.
    """
    sb = _get_supabase()
    if not sb or not affiliate_code or not stripe_session_id:
        return False

    try:
        # Idempotency: skip if already logged
        existing = (
            sb.table("affiliate_sales")
            .select("id")
            .eq("stripe_session_id", stripe_session_id)
            .execute()
        )
        if existing.data:
            return True  # already recorded

        # Look up the affiliate's individual commission rate (or use default)
        aff = get_affiliate(affiliate_code)
        rate = aff.get("commission_rate", DEFAULT_COMMISSION_RATE) if aff else DEFAULT_COMMISSION_RATE

        price      = PRODUCT_PRICES.get(product.lower(), 0.0)
        commission = round(price * rate, 2)

        sb.table("affiliate_sales").insert({
            "affiliate_code":   affiliate_code.strip().upper(),
            "stripe_session_id": stripe_session_id,
            "product":          product.lower(),
            "sale_amount":      price,
            "commission_amount": commission,
            "customer_email":   customer_email or "",
            "status":           "unpaid",
        }).execute()
        return True

    except Exception:
        return False


# ── Affiliate stats ────────────────────────────────────────────────────────────
def get_affiliate_sales(code: str) -> list:
    """Return all sales rows for one affiliate, newest first."""
    sb = _get_supabase()
    if not sb:
        return []
    try:
        result = (
            sb.table("affiliate_sales")
            .select("*")
            .eq("affiliate_code", code.strip().upper())
            .order("sale_date", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


# ── Admin helpers ──────────────────────────────────────────────────────────────
def get_all_affiliates() -> list:
    sb = _get_supabase()
    if not sb:
        return []
    try:
        result = sb.table("affiliates").select("*").order("created_at", desc=True).execute()
        return result.data or []
    except Exception:
        return []


def get_all_sales() -> list:
    sb = _get_supabase()
    if not sb:
        return []
    try:
        result = (
            sb.table("affiliate_sales")
            .select("*")
            .order("sale_date", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def mark_paid(sale_ids: list) -> bool:
    """Mark a list of sale IDs as paid."""
    sb = _get_supabase()
    if not sb or not sale_ids:
        return False
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        for sid in sale_ids:
            sb.table("affiliate_sales").update(
                {"status": "paid", "paid_at": now_iso}
            ).eq("id", sid).execute()
        return True
    except Exception:
        return False


def create_affiliate(
    code: str,
    name: str,
    email: str = "",
    notes: str = "",
    commission_rate: float = DEFAULT_COMMISSION_RATE,
) -> tuple[bool, str | None]:
    """
    Create a new affiliate. Returns (True, None) on success,
    or (False, error_message) on failure.
    """
    sb = _get_supabase()
    if not sb:
        return False, "Supabase is not configured."
    try:
        sb.table("affiliates").insert({
            "code":            code.strip().upper(),
            "name":            name.strip(),
            "email":           email.strip(),
            "notes":           notes.strip(),
            "commission_rate": commission_rate,
        }).execute()
        return True, None
    except Exception as e:
        return False, str(e)
