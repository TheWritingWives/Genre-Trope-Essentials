"""
Affiliate Portal — The Writing Wives AI Author Tools
-----------------------------------------------------
Affiliates enter their unique code to view their sales, earnings,
and payout history. No account needed — the code IS the password.
"""

import streamlit as st

# Pages live at the app root, so __file__.parent IS the app root

from affiliate_utils import (
    capture_ref,
    get_affiliate,
    get_affiliate_sales,
    PRODUCT_NAMES,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Affiliate Portal | The Writing Wives",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Capture ?ref= in case an affiliate lands here directly
capture_ref()

# ── Brand colours ──────────────────────────────────────────────────────────────
PRIMARY    = "#1A1A1A"
GOLD       = "#D4B36E"
GOLD_DARK  = "#A8863A"
GOLD_LIGHT = "#FAF4E6"
GOLD_MID   = "#F5EDD6"
GREEN      = "#1A7A4A"
GREEN_BG   = "#D4EDDA"
RED        = "#CC3333"
RED_BG     = "#FFF0F0"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', Arial, sans-serif; }}
  .block-container {{ max-width: 760px; padding-top: 1.5rem; }}
  [data-testid="stSidebar"] {{ display: none; }}

  .header-block {{
    background: {PRIMARY}; padding: 2rem 2.5rem 1.6rem;
    border-radius: 12px; margin-bottom: 2rem;
    border-bottom: 3px solid {GOLD}; text-align: center;
  }}
  .header-block .eyebrow {{ color:{GOLD}; font-size:0.72rem; font-weight:700;
    letter-spacing:0.18em; text-transform:uppercase; margin:0 0 0.4rem; }}
  .header-block h1 {{ color:#fff; font-size:2rem; font-weight:900; margin:0 0 0.4rem; }}
  .header-block .sub {{ color:#aaa; font-size:0.95rem; margin:0; }}

  /* Stats cards */
  .stat-row {{ display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap; }}
  .stat-card {{
    flex:1; min-width:140px; background:#fff;
    border:1px solid #e8d9b0; border-top:4px solid {GOLD};
    border-radius:10px; padding:1.1rem 1rem; text-align:center;
  }}
  .stat-card .stat-label {{ font-size:0.75rem; font-weight:700; color:#888;
    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem; }}
  .stat-card .stat-value {{ font-size:1.8rem; font-weight:900; color:{PRIMARY}; }}
  .stat-card .stat-sub {{ font-size:0.78rem; color:#999; margin-top:0.2rem; }}

  /* Owed highlight */
  .owed-card {{
    background: {PRIMARY}; border: 2px solid {GOLD};
    border-radius: 12px; padding: 1.4rem 1.5rem;
    text-align: center; margin-bottom: 1.5rem;
  }}
  .owed-card .oc-label {{ color:{GOLD}; font-size:0.72rem; font-weight:700;
    letter-spacing:0.18em; text-transform:uppercase; margin-bottom:0.3rem; }}
  .owed-card .oc-amount {{ color:#fff; font-size:2.8rem; font-weight:900; margin:0.2rem 0; }}
  .owed-card .oc-sub {{ color:#aaa; font-size:0.9rem; }}

  /* Sale row */
  .sale-row {{
    background:#fff; border:1px solid #e8d9b0;
    border-radius:8px; padding:0.85rem 1rem;
    margin-bottom:0.5rem; display:flex;
    align-items:center; justify-content:space-between; gap:0.5rem;
    flex-wrap:wrap;
  }}
  .sale-row .sr-product {{ font-weight:700; color:{PRIMARY}; font-size:0.92rem; }}
  .sale-row .sr-date {{ color:#888; font-size:0.82rem; }}
  .sale-row .sr-amount {{ font-size:1rem; font-weight:700; color:{GOLD_DARK}; }}
  .sale-row .badge-paid {{
    background:{GREEN_BG}; color:{GREEN}; font-size:0.75rem;
    font-weight:700; padding:2px 10px; border-radius:20px;
  }}
  .sale-row .badge-unpaid {{
    background:#FFF3CD; color:#856404; font-size:0.75rem;
    font-weight:700; padding:2px 10px; border-radius:20px;
  }}

  /* Empty state */
  .empty-state {{
    background:{GOLD_LIGHT}; border:1px solid #e8d9b0;
    border-radius:10px; padding:2rem; text-align:center;
    color:#888; font-size:0.92rem; margin-bottom:1.5rem;
  }}

  /* Info box */
  .info-box {{
    background:#EEF4FF; border:1px solid #c5d8f8;
    border-left:4px solid #3B6FD4; border-radius:0 8px 8px 0;
    padding:0.85rem 1rem; font-size:0.87rem; color:#1a3a6b;
    margin-bottom:1.2rem;
  }}

  /* Section title */
  .section-title {{ color:{PRIMARY}; font-size:1.1rem; font-weight:900;
    border-bottom:3px solid {GOLD}; padding-bottom:5px; margin:1.5rem 0 1rem; }}

  /* Buttons */
  .stButton > button {{
    background:{PRIMARY} !important; color:{GOLD} !important;
    font-weight:700 !important; padding:0.65rem 2rem !important;
    border-radius:8px !important; border:2px solid {GOLD} !important;
    font-size:1rem !important; width:100%;
  }}
  .stButton > button:hover {{ background:{GOLD} !important; color:{PRIMARY} !important; }}

  .footer-note {{ text-align:center; color:#aaa; font-size:0.78rem;
    margin-top:3rem; padding-top:1rem; border-top:1px solid #f0e6cc; }}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-block">
  <div class="eyebrow">The Writing Wives · Affiliate Program</div>
  <h1>🤝 Affiliate Portal</h1>
  <p class="sub">Enter your affiliate code to see your earnings and sale history.</p>
</div>
""", unsafe_allow_html=True)

# ── Session state helpers ──────────────────────────────────────────────────────
if "aff_logged_in" not in st.session_state:
    st.session_state["aff_logged_in"] = False
if "aff_code_active" not in st.session_state:
    st.session_state["aff_code_active"] = ""

# ── Login form ─────────────────────────────────────────────────────────────────
if not st.session_state["aff_logged_in"]:
    st.markdown("""
    <div class="info-box">
      🔑 Your affiliate code is the unique code you were given when you joined
      the program — for example <strong>JANES_CODE</strong>. It's not case-sensitive.
    </div>
    """, unsafe_allow_html=True)

    with st.form("aff_login_form"):
        entered_code = st.text_input(
            "Your affiliate code",
            placeholder="e.g. JANES_CODE",
            label_visibility="visible",
        )
        submitted = st.form_submit_button("View My Earnings →", use_container_width=True)

    if submitted:
        if not entered_code.strip():
            st.error("Please enter your affiliate code.")
        else:
            with st.spinner("Checking your code..."):
                aff = get_affiliate(entered_code.strip())
            if aff:
                st.session_state["aff_logged_in"]   = True
                st.session_state["aff_code_active"] = aff["code"]
                st.rerun()
            else:
                st.error("That code wasn't found. Double-check the spelling, or contact hello@thewritingwives.com if you think this is a mistake.")

    st.markdown("""
    <div class="footer-note">
      The Writing Wives ·
      <a href="https://thewritingwives.com" style="color:#aaa;">thewritingwives.com</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Logged in — load data ──────────────────────────────────────────────────────
code = st.session_state["aff_code_active"]
aff  = get_affiliate(code)

if not aff:
    st.session_state["aff_logged_in"]   = False
    st.session_state["aff_code_active"] = ""
    st.rerun()

sales = get_affiliate_sales(code)

# ── Compute summary stats ──────────────────────────────────────────────────────
total_sales       = len(sales)
total_revenue     = sum(s.get("sale_amount", 0) for s in sales)
total_commission  = sum(s.get("commission_amount", 0) for s in sales)
paid_commission   = sum(s.get("commission_amount", 0) for s in sales if s.get("status") == "paid")
owed_commission   = total_commission - paid_commission
commission_rate   = int((aff.get("commission_rate", 0.20)) * 100)

# ── Greeting ───────────────────────────────────────────────────────────────────
aff_name = aff.get("name", code)
st.markdown(f"""
<div style="margin-bottom:1rem;">
  <span style="font-size:1.05rem;color:#555;">Welcome back, <strong style="color:{PRIMARY};">{aff_name}</strong>
  &nbsp;·&nbsp; Your code: <code style="background:{GOLD_LIGHT};padding:2px 7px;border-radius:4px;font-weight:700;">{code}</code>
  &nbsp;·&nbsp; Commission rate: <strong style="color:{GOLD_DARK};">{commission_rate}%</strong></span>
</div>
""", unsafe_allow_html=True)

# ── Amount owed highlight ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="owed-card">
  <div class="oc-label">Unpaid Commission Owed to You</div>
  <div class="oc-amount">${owed_commission:,.2f}</div>
  <div class="oc-sub">
    {"You're all paid up — no outstanding balance." if owed_commission == 0
     else "This will be paid out on the next payout date. Questions? Email hello@thewritingwives.com"}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Summary stats ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stat-row">
  <div class="stat-card">
    <div class="stat-label">Total Sales</div>
    <div class="stat-value">{total_sales}</div>
    <div class="stat-sub">all time</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total Revenue</div>
    <div class="stat-value">${total_revenue:,.0f}</div>
    <div class="stat-sub">you drove</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total Earned</div>
    <div class="stat-value">${total_commission:,.2f}</div>
    <div class="stat-sub">commission ({commission_rate}%)</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Paid Out</div>
    <div class="stat-value">${paid_commission:,.2f}</div>
    <div class="stat-sub">to date</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Referral link ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Your Referral Link</div>', unsafe_allow_html=True)

try:
    app_base_url = st.secrets.get("APP_BASE_URL", "https://YOUR-APP.streamlit.app")
except Exception:
    app_base_url = "https://YOUR-APP.streamlit.app"

ref_link = f"{app_base_url}/?ref={code}"
st.markdown(f"""
<div class="info-box">
  🔗 Share this link to get credit for sales:<br>
  <strong><a href="{ref_link}" target="_blank" style="color:#1a3a6b;">{ref_link}</a></strong><br>
  <span style="font-size:0.82rem;margin-top:0.3rem;display:block;">
    Anyone who clicks your link and buys within the same browser session will be tracked to you.
  </span>
</div>
""", unsafe_allow_html=True)

# ── Sale history ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Sale History</div>', unsafe_allow_html=True)

if not sales:
    st.markdown("""
    <div class="empty-state">
      No sales yet — share your referral link to get started! 🚀
    </div>
    """, unsafe_allow_html=True)
else:
    for s in sales:
        product_name = PRODUCT_NAMES.get(s.get("product", ""), s.get("product", "Unknown"))
        raw_date     = s.get("sale_date", "")
        try:
            from datetime import datetime as _dt
            display_date = _dt.fromisoformat(raw_date.replace("Z", "+00:00")).strftime("%b %d, %Y")
        except Exception:
            display_date = raw_date[:10] if raw_date else "—"

        status       = s.get("status", "unpaid")
        badge_class  = "badge-paid" if status == "paid" else "badge-unpaid"
        badge_label  = "✓ Paid" if status == "paid" else "Pending"
        commission   = s.get("commission_amount", 0)

        st.markdown(f"""
        <div class="sale-row">
          <div>
            <div class="sr-product">{product_name}</div>
            <div class="sr-date">{display_date}</div>
          </div>
          <div style="display:flex;align-items:center;gap:0.75rem;">
            <div class="sr-amount">+${commission:.2f}</div>
            <span class="{badge_class}">{badge_label}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Log out ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔓 Log out"):
    st.session_state["aff_logged_in"]   = False
    st.session_state["aff_code_active"] = ""
    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-note">
  The Writing Wives · Affiliate Program ·
  Questions? <a href="mailto:hello@thewritingwives.com" style="color:#aaa;">hello@thewritingwives.com</a>
</div>
""", unsafe_allow_html=True)
