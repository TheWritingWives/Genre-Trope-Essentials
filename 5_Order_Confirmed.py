import streamlit as st
import base64
from pathlib import Path

try:
    import stripe as stripe_lib
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

# ── Page config ───────────────────────────────────────────────────────────────


# ── Brand colours ─────────────────────────────────────────────────────────────
PRIMARY   = "#1A1A1A"
GOLD      = "#D4B36E"
GOLD_DARK = "#A8863A"
GOLD_LIGHT= "#FAF4E6"
GOLD_MID  = "#F5EDD6"
GREEN     = "#1A7A4A"
GREEN_BG  = "#D4EDDA"

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

def get_logo_b64():
    p = Path(__file__).parent / "logo.png"
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def verify_stripe_session(session_id):
    if not STRIPE_AVAILABLE:
        return False, None
    try:
        stripe_lib.api_key = get_secret("STRIPE_SECRET_KEY")
        session = stripe_lib.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            email = session.customer_details.email if session.customer_details else None
            return True, email
    except Exception:
        pass
    return False, None

def grant_access_for_tool(tool: str, email=None):
    """Set session_state access flags for the purchased tool."""
    if tool == "lifetime":
        st.session_state["lifetime_access"]       = True
        st.session_state["access_granted"]        = True
        st.session_state["access_reason"]         = "stripe"
        st.session_state["ad_access_granted"]     = True
        st.session_state["ad_access_reason"]      = "stripe"
        st.session_state["cover_access_granted"]  = True
        st.session_state["cover_access_reason"]   = "stripe"
        st.session_state["amazon_access_granted"] = True
        st.session_state["amazon_access_reason"]  = "stripe"
    elif tool == "blurb":
        st.session_state["access_granted"] = True
        st.session_state["access_reason"]  = "stripe"
    elif tool == "ad":
        st.session_state["ad_access_granted"] = True
        st.session_state["ad_access_reason"]  = "stripe"
    elif tool == "cover":
        st.session_state["cover_access_granted"] = True
        st.session_state["cover_access_reason"]  = "stripe"
    elif tool == "amazon":
        st.session_state["amazon_access_granted"] = True
        st.session_state["amazon_access_reason"]  = "stripe"
    if email:
        st.session_state["confirmed_email"] = email

# ── Tool metadata ─────────────────────────────────────────────────────────────
TOOL_META = {
    "blurb": {
        "name":    "Blurb Auditor",
        "icon":    "📖",
        "tagline": "Your scored audit is ready. Paste your blurb and get your report.",
        "page":    "1_Blurb_Auditor.py",
        "cta":     "Go to Blurb Auditor →",
        "price":   get_secret("PRICE_DISPLAY", "$27"),
    },
    "ad": {
        "name":    "FB & Instagram Ad Package",
        "icon":    "📱",
        "tagline": "Your ad copy is one click away. Fill in your book details and generate.",
        "page":    "2_FB_Ad_Package.py",
        "cta":     "Go to Ad Package →",
        "price":   get_secret("AD_PRICE_DISPLAY", "$25"),
    },
    "cover": {
        "name":    "Cover Assessment",
        "icon":    "🎨",
        "tagline": "Upload your cover and get your full genre signal report.",
        "page":    "3_Cover_Assessment.py",
        "cta":     "Go to Cover Assessment →",
        "price":   get_secret("COVER_PRICE_DISPLAY", "$15"),
    },
    "amazon": {
        "name":    "Amazon Page Assessment",
        "icon":    "🛒",
        "tagline": "Paste your Amazon link and get your full page score.",
        "page":    "4_Amazon_Assessment.py",
        "cta":     "Go to Amazon Assessment →",
        "price":   get_secret("AMAZON_PRICE_DISPLAY", "$19"),
    },
    "lifetime": {
        "name":    "Lifetime Access — All Four Tools",
        "icon":    "🏆",
        "tagline": "Every tool is now unlocked for as long as the classroom exists.",
        "page":    "app.py",
        "cta":     "Go to the Classroom →",
        "price":   get_secret("LIFETIME_PRICE_DISPLAY", "$97"),
    },
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', Arial, sans-serif; }}
  .block-container {{ max-width: 680px; padding-top: 2rem; }}
  [data-testid="stSidebar"] {{ display: none; }}

  .confirm-card {{
    background: {PRIMARY};
    border: 2px solid {GOLD};
    border-radius: 16px;
    padding: 2.5rem 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
  }}
  .confirm-card .logo-wrap {{ margin-bottom: 1.4rem; }}
  .confirm-card .logo-wrap img {{ height: 100px; max-width: 100%; object-fit: contain; }}
  .check-icon {{ font-size: 3.5rem; margin-bottom: 0.6rem; }}
  .confirm-card .eyebrow {{ color:{GOLD}; font-size:0.72rem; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; margin-bottom:0.4rem; }}
  .confirm-card h1 {{ color:#fff; font-size:2rem; font-weight:900; margin:0 0 0.5rem; line-height:1.2; }}
  .confirm-card .confirm-sub {{ color:#ccc; font-size:1rem; line-height:1.65; margin:0 auto; max-width:480px; }}

  .tool-purchased {{
    background: #fff;
    border: 1px solid #e8d9b0;
    border-top: 4px solid {GOLD};
    border-radius: 12px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }}
  .tp-icon {{ font-size: 2.4rem; flex-shrink: 0; }}
  .tp-body {{ flex: 1; }}
  .tp-name {{ font-size: 1.1rem; font-weight: 900; color:{PRIMARY}; margin-bottom: 0.2rem; }}
  .tp-tagline {{ font-size: 0.88rem; color: #555; line-height: 1.5; }}
  .tp-price {{ font-size: 1rem; font-weight: 700; color: {GOLD_DARK}; margin-top: 0.3rem; }}

  .next-steps {{
    background: {GOLD_LIGHT};
    border: 1px solid #e8d9b0;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .next-steps h3 {{ color:{PRIMARY}; font-size:1rem; font-weight:900; margin:0 0 0.75rem; }}
  .next-steps ol {{ margin:0; padding-left:1.3rem; color:#444; font-size:0.9rem; line-height:1.7; }}

  .lifetime-unlocked {{
    background: {PRIMARY};
    border: 2px solid {GOLD};
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .lifetime-unlocked h3 {{ color:{GOLD}; font-size:1rem; font-weight:900; margin:0 0 0.6rem; }}
  .lifetime-unlocked ul {{ margin:0; padding-left:1.3rem; color:#ccc; font-size:0.9rem; line-height:1.75; }}

  .email-note {{
    background:#EEF4FF; border:1px solid #c5d8f8; border-left:4px solid #3B6FD4;
    border-radius:0 8px 8px 0; padding:0.8rem 1rem; font-size:0.87rem; color:#1a3a6b;
    margin-bottom:1.2rem;
  }}

  .error-card {{
    background:#FFF5F5; border:1px solid #fcc; border-left:4px solid #CC0000;
    border-radius:0 8px 8px 0; padding:1rem 1.2rem; margin-bottom:1.5rem;
    font-size:0.92rem; color:#7b0000;
  }}

  .stButton > button {{
    background:{PRIMARY} !important; color:{GOLD} !important;
    font-weight:700 !important; padding:0.7rem 2rem !important;
    border-radius:8px !important; border:2px solid {GOLD} !important;
    font-size:1rem !important; width:100%;
  }}
  .stButton > button:hover {{ background:{GOLD} !important; color:{PRIMARY} !important; }}
  .stLinkButton > a {{
    background:{PRIMARY} !important; color:{GOLD} !important;
    font-weight:700 !important; border-radius:8px !important;
    font-size:1rem !important; border:2px solid {GOLD} !important;
    text-decoration:none !important; display:block !important;
    padding:0.7rem 1.2rem !important; text-align:center !important;
  }}
  .footer-note {{ text-align:center; color:#aaa; font-size:0.78rem; margin-top:3rem; padding-top:1rem; border-top:1px solid #f0e6cc; }}
</style>
""", unsafe_allow_html=True)

# ── Read query params ─────────────────────────────────────────────────────────
tool       = st.query_params.get("tool", "").lower().strip()
session_id = st.query_params.get("session_id", "").strip()

# ── Logo ──────────────────────────────────────────────────────────────────────
_logo_b64 = get_logo_b64()
_logo_html = (
    f'<div class="logo-wrap"><img src="data:image/png;base64,{_logo_b64}" alt="The Writing Wives"></div>'
    if _logo_b64 else ""
)

# ── Missing params guard ──────────────────────────────────────────────────────
if not tool or not session_id:
    st.markdown(f"""
    <div class="confirm-card">
      {_logo_html}
      <div class="eyebrow">AI Author Tools</div>
      <h1>Nothing to confirm here</h1>
      <p class="confirm-sub">This page is for order confirmation after checkout.
      If you've already paid, head back to your tool using the link below.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Back to the Classroom", key="back_no_session", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

# ── Verify with Stripe (once per session) ────────────────────────────────────
check_key = f"confirmed_{tool}_{session_id[:12]}"

if not st.session_state.get(check_key):
    st.session_state[check_key] = True
    with st.spinner("Verifying your payment — just a moment..."):
        ok, email = verify_stripe_session(session_id)
    if ok:
        grant_access_for_tool(tool, email=email)
        st.session_state["payment_verified"] = True
        st.session_state["payment_email"]    = email or ""
    else:
        st.session_state["payment_verified"] = False
        st.session_state["payment_email"]    = ""

verified = st.session_state.get("payment_verified", False)
email    = st.session_state.get("payment_email", "")
meta     = TOOL_META.get(tool)

# ── Not verified ─────────────────────────────────────────────────────────────
if not verified:
    st.markdown(f"""
    <div class="confirm-card">
      {_logo_html}
      <div class="eyebrow">Payment Check</div>
      <h1>Couldn't verify yet</h1>
      <p class="confirm-sub">Your payment may still be processing.
      Wait a few seconds and refresh this page.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="error-card">
      ⏳ <strong>Still not showing?</strong> Stripe payments occasionally take 10–15 seconds to process.
      Refresh once or twice more. If it still doesn't work after a minute,
      email <strong>hello@thewritingwives.com</strong> with your Stripe receipt and we'll sort it out.
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 Refresh to try again"):
        st.rerun()
    st.stop()

# ── Unknown tool ──────────────────────────────────────────────────────────────
if not meta:
    st.markdown(f"""
    <div class="confirm-card">
      {_logo_html}
      <div class="check-icon">✅</div>
      <div class="eyebrow">Payment Confirmed</div>
      <h1>You're all set!</h1>
      <p class="confirm-sub">Your payment went through. Head back to the classroom to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to the Classroom →", key="back_unknown_tool", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

# ── SUCCESS ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="confirm-card">
  {_logo_html}
  <div class="check-icon">✅</div>
  <div class="eyebrow">Payment Confirmed</div>
  <h1>You're all set{f', {email.split("@")[0].title()}' if email else ''}!</h1>
  <p class="confirm-sub">Your payment went through and your access is ready.
  {'Every tool in the classroom is now unlocked.' if tool == 'lifetime' else 'Head to your tool below to get started.'}</p>
</div>
""", unsafe_allow_html=True)

# Email note
if email:
    st.markdown(f"""
    <div class="email-note">
      📧 Receipt sent to <strong>{email}</strong> — Stripe will email your confirmation shortly.
      Bookmark the tool page to return any time (access is session-based — if you close the tab, re-purchase or use your coupon code).
    </div>
    """, unsafe_allow_html=True)

# Tool purchased card
st.markdown(f"""
<div class="tool-purchased">
  <div class="tp-icon">{meta['icon']}</div>
  <div class="tp-body">
    <div class="tp-name">{meta['name']}</div>
    <div class="tp-tagline">{meta['tagline']}</div>
    <div class="tp-price">{meta['price']} · paid ✓</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Lifetime: show all unlocked tools
if tool == "lifetime":
    st.markdown(f"""
    <div class="lifetime-unlocked">
      <h3>🏆 All tools unlocked for this session:</h3>
      <ul>
        <li>📖 Blurb Auditor — unlimited audits</li>
        <li>📱 FB &amp; Instagram Ad Package — unlimited</li>
        <li>🎨 Cover Assessment — unlimited</li>
        <li>🛒 Amazon Page Assessment — unlimited</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

# Next steps
if tool == "blurb":
    steps = [
        "Paste your blurb into the form on the next page.",
        "Hit <strong>Run Audit</strong> — your scored report generates in about 20 seconds.",
        "Download your Word doc from the results.",
        "Check the <em>FB &amp; Instagram Ad Package</em> if you also want ready-to-paste ad copy.",
    ]
elif tool == "ad":
    steps = [
        "Fill in your book title, genre, tropes, and excerpt on the next page.",
        "Hit <strong>Generate My Ad Copy</strong> — your package generates in about 20 seconds.",
        "Copy-paste headlines, primary text, and descriptions straight into Ads Manager.",
        "Download the Word doc as a reference while you build your ad.",
    ]
elif tool == "cover":
    steps = [
        "Upload your cover image on the next page (JPG or PNG, any size).",
        "Hit <strong>Assess My Cover</strong> — analysis takes about 15 seconds.",
        "Review each of the 6 scored categories.",
        "Share the downloaded Word doc with your cover designer if changes are needed.",
    ]
elif tool == "amazon":
    steps = [
        "Paste your Amazon product page URL (e.g. amazon.com/dp/B01234567) on the next page.",
        "Hit <strong>Assess My Page</strong> — your report generates in about 20 seconds.",
        "Review each scored section for specific action items.",
        "Use the keyword and category suggestions in your KDP dashboard.",
    ]
else:  # lifetime
    steps = [
        "Use the buttons below to jump straight to any tool.",
        "Each tool is now unlocked for this browser session.",
        "Bookmark the homepage and return any time you have a new book to assess.",
        "All future tools added to the classroom are included.",
    ]

steps_html = "".join(f"<li>{s}</li>" for s in steps)
st.markdown(f"""
<div class="next-steps">
  <h3>What to do next:</h3>
  <ol>{steps_html}</ol>
</div>
""", unsafe_allow_html=True)

# CTA button(s)
if tool == "lifetime":
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📖 Blurb Auditor →", key="lt_blurb", use_container_width=True):
            st.switch_page("1_Blurb_Auditor.py")
    with c2:
        if st.button("📱 Ad Package →", key="lt_ad", use_container_width=True):
            st.switch_page("2_FB_Ad_Package.py")
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🎨 Cover Assessment →", key="lt_cover", use_container_width=True):
            st.switch_page("3_Cover_Assessment.py")
    with c4:
        if st.button("🛒 Amazon Assessment →", key="lt_amazon", use_container_width=True):
            st.switch_page("4_Amazon_Assessment.py")
else:
    if st.button(meta["cta"], key="go_to_tool", use_container_width=True):
        st.switch_page(meta["page"])

# Footer
st.markdown("""
<div class="footer-note">
  The Writing Wives · Genre &amp; Trope AI Classroom ·
  <a href="https://thewritingwives.com" style="color:#aaa;">thewritingwives.com</a>
</div>
""", unsafe_allow_html=True)
