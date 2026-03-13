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


# ── Email helper ────────────────────────────────────────────────────────────────
def send_affiliate_welcome_email(name: str, email: str, code: str) -> tuple[bool, str]:
    """
    Send a welcome email to a newly approved affiliate.
    Requires SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in st.secrets.
    Returns (True, "") on success or (False, error_message) on failure.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    try:
        host     = st.secrets.get("SMTP_HOST", "")
        port     = int(st.secrets.get("SMTP_PORT", 587))
        user     = st.secrets.get("SMTP_USER", "")
        password = st.secrets.get("SMTP_PASSWORD", "")
        from_str = st.secrets.get("SMTP_FROM", f"The Writing Wives <{user}>")

        if not all([host, user, password]):
            return False, "SMTP not configured in secrets."

        base_url     = st.secrets.get("APP_BASE_URL", "https://genre-trope-essentials.streamlit.app")
        aff_link     = f"{base_url}/?ref={code}"
        portal_url   = f"{base_url}/Affiliate_Portal"

        html = f"""
        <html><body style="font-family:Arial,sans-serif;color:#1A1A1A;max-width:600px;margin:0 auto;">
          <div style="background:#1A1A1A;padding:2rem;border-radius:10px 10px 0 0;text-align:center;">
            <h1 style="color:#D4B36E;margin:0;font-size:1.8rem;">You're Approved! 🎉</h1>
            <p style="color:#aaa;margin:0.5rem 0 0;">The Writing Wives AI Author Tools</p>
          </div>
          <div style="background:#fff;border:1px solid #e8d9b0;border-top:none;
                      border-radius:0 0 10px 10px;padding:2rem;">
            <p>Hi <strong>{name}</strong>,</p>
            <p>Great news — you've been approved as an affiliate for
               <strong>The Writing Wives AI Author Tools</strong>!</p>
            <p>Here's everything you need to get started:</p>

            <div style="background:#FAF4E6;border:1px solid #e8d9b0;border-left:4px solid #D4B36E;
                        border-radius:0 8px 8px 0;padding:1rem 1.2rem;margin:1rem 0;">
              <p style="margin:0 0 0.5rem;"><strong>Your referral link:</strong></p>
              <p style="margin:0;font-family:monospace;color:#A8863A;">{aff_link}</p>
            </div>

            <p>Share this link anywhere — when someone buys through it, you earn
               <strong>20% commission</strong> on every sale!</p>

            <div style="background:#F0F7FF;border:1px solid #c5d8f8;border-left:4px solid #3B6FD4;
                        border-radius:0 8px 8px 0;padding:1rem 1.2rem;margin:1rem 0;">
              <p style="margin:0 0 0.3rem;"><strong>Your affiliate portal:</strong>
                 <a href="{portal_url}" style="color:#3B6FD4;">{portal_url}</a></p>
              <p style="margin:0;"><strong>Your login code (password):</strong>
                 <code style="background:#e8f0fe;padding:2px 8px;border-radius:4px;">{code}</code></p>
            </div>

            <p>Log in to your portal anytime to track your sales, earnings, and unpaid balance.</p>
            <p>Happy promoting! 🚀</p>
            <p style="color:#888;font-size:0.85rem;margin-top:2rem;border-top:1px solid #eee;
                      padding-top:1rem;">
              — The Writing Wives Team<br>
              <a href="https://thewritingwives.com" style="color:#D4B36E;">thewritingwives.com</a>
            </p>
          </div>
        </body></html>
        """

        plain = (
            f"Hi {name},\n\n"
            f"You've been approved as a Writing Wives affiliate!\n\n"
            f"Your referral link: {aff_link}\n"
            f"Your portal: {portal_url}\n"
            f"Your login code: {code}\n\n"
            f"Happy promoting!\n— The Writing Wives Team"
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "You're approved as a Writing Wives affiliate! 🎉"
        msg["From"]    = from_str
        msg["To"]      = email
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls()
            server.login(user, password)
            server.sendmail(user, email, msg.as_string())

        return True, ""

    except Exception as e:
        return False, str(e)


# ── Affiliate application functions ────────────────────────────────────────────
def submit_application(
    name: str,
    requested_code: str,
    paypal_email: str,
    marketing_plan: str,
) -> tuple[bool, str]:
    """Submit a new affiliate application. Returns (True, "") or (False, error)."""
    sb = _get_supabase()
    if not sb:
        return False, "Database not configured."
    try:
        sb.table("affiliate_applications").insert({
            "name":           name.strip(),
            "requested_code": requested_code.strip().upper(),
            "paypal_email":   paypal_email.strip(),
            "marketing_plan": marketing_plan.strip(),
            "status":         "pending",
        }).execute()
        return True, ""
    except Exception as e:
        return False, str(e)


def get_pending_applications() -> list:
    """Return all pending affiliate applications, oldest first."""
    sb = _get_supabase()
    if not sb:
        return []
    try:
        result = (
            sb.table("affiliate_applications")
            .select("*")
            .eq("status", "pending")
            .order("applied_at", desc=False)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_all_applications() -> list:
    """Return all affiliate applications."""
    sb = _get_supabase()
    if not sb:
        return []
    try:
        result = (
            sb.table("affiliate_applications")
            .select("*")
            .order("applied_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def approve_application(app_id: str, code: str, name: str, email: str,
                        notes: str = "", commission_rate: float = DEFAULT_COMMISSION_RATE
                        ) -> tuple[bool, str]:
    """
    Approve an application: create the affiliate, mark app as approved,
    and send the welcome email. Returns (True, "") or (False, error).
    """
    sb = _get_supabase()
    if not sb:
        return False, "Database not configured."
    try:
        # Create the affiliate account
        ok, err = create_affiliate(code=code, name=name, email=email,
                                   notes=notes, commission_rate=commission_rate)
        if not ok:
            return False, err

        # Mark application as approved
        from datetime import datetime, timezone
        sb.table("affiliate_applications").update({
            "status":      "approved",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", app_id).execute()

        # Send welcome email
        if email:
            send_affiliate_welcome_email(name=name, email=email, code=code)

        return True, ""
    except Exception as e:
        return False, str(e)


def reject_application(app_id: str) -> bool:
    """Mark an application as rejected."""
    sb = _get_supabase()
    if not sb:
        return False
    try:
        from datetime import datetime, timezone
        sb.table("affiliate_applications").update({
            "status":      "rejected",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", app_id).execute()
        return True
    except Exception:
        return False
