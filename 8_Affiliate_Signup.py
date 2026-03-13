"""
Affiliate Signup — The Writing Wives AI Author Tools
-----------------------------------------------------
Public page where prospective affiliates apply.
Applications are reviewed by the admin (page 7) within 24–48 hours.
"""

import streamlit as st
from affiliate_utils import submit_application

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Become an Affiliate | The Writing Wives",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Brand colours ──────────────────────────────────────────────────────────────
PRIMARY    = "#1A1A1A"
GOLD       = "#D4B36E"
GOLD_DARK  = "#A8863A"
GOLD_LIGHT = "#FAF4E6"
GOLD_MID   = "#F5EDD6"
GREEN      = "#1A7A4A"
GREEN_BG   = "#D4EDDA"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', Arial, sans-serif; }}
  .block-container {{ max-width: 680px; padding-top: 1.5rem; }}
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

  .perk-row {{
    display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap;
  }}
  .perk-card {{
    flex:1; min-width:140px; background:{GOLD_LIGHT};
    border:1px solid #e8d9b0; border-top:3px solid {GOLD};
    border-radius:10px; padding:0.9rem 1rem; text-align:center;
  }}
  .perk-card .perk-icon {{ font-size:1.5rem; margin-bottom:0.3rem; }}
  .perk-card .perk-title {{ font-weight:700; font-size:0.85rem; color:{PRIMARY}; }}
  .perk-card .perk-desc {{ font-size:0.78rem; color:#666; margin-top:0.2rem; }}

  .form-card {{
    background:#fff; border:1px solid #e8d9b0;
    border-radius:12px; padding:1.8rem 2rem; margin-bottom:1.5rem;
  }}
  .form-card h2 {{ font-size:1.15rem; font-weight:900; color:{PRIMARY};
    border-bottom:2px solid {GOLD}; padding-bottom:0.5rem; margin:0 0 1.2rem; }}

  .success-card {{
    background:{GREEN_BG}; border:2px solid {GREEN};
    border-radius:12px; padding:2rem; text-align:center; margin-top:1rem;
  }}
  .success-card .check {{ font-size:3rem; margin-bottom:0.5rem; }}
  .success-card h2 {{ color:{GREEN}; font-size:1.5rem; font-weight:900; margin:0 0 0.5rem; }}
  .success-card p {{ color:#155724; margin:0; font-size:0.95rem; line-height:1.6; }}

  .stTextInput > label, .stTextArea > label {{
    font-weight:700 !important; color:{PRIMARY} !important; font-size:0.88rem !important;
  }}
  div[data-testid="stForm"] button[kind="primaryFormSubmit"] {{
    background:{PRIMARY} !important; color:{GOLD} !important;
    font-weight:700 !important; border-radius:8px !important;
    border:2px solid {GOLD} !important; font-size:1rem !important;
    padding:0.6rem 1rem !important;
  }}
  div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {{
    background:{GOLD} !important; color:{PRIMARY} !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-block">
  <p class="eyebrow">Partner Program</p>
  <h1>Become an Affiliate 🤝</h1>
  <p class="sub">Earn 20% commission on every sale you refer — paid straight to your PayPal.</p>
</div>
""", unsafe_allow_html=True)

# ── Perks ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="perk-row">
  <div class="perk-card">
    <div class="perk-icon">💰</div>
    <div class="perk-title">20% Commission</div>
    <div class="perk-desc">On every sale you refer</div>
  </div>
  <div class="perk-card">
    <div class="perk-icon">📊</div>
    <div class="perk-title">Live Dashboard</div>
    <div class="perk-desc">Track sales & earnings in real time</div>
  </div>
  <div class="perk-card">
    <div class="perk-icon">💸</div>
    <div class="perk-title">PayPal Payouts</div>
    <div class="perk-desc">Fast, reliable payments</div>
  </div>
  <div class="perk-card">
    <div class="perk-icon">📚</div>
    <div class="perk-title">5 Products</div>
    <div class="perk-desc">Blurb, ads, cover, Amazon &amp; more</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Show confirmation if already submitted this session ────────────────────────
if st.session_state.get("aff_app_submitted"):
    st.markdown(f"""
    <div class="success-card">
      <div class="check">🎉</div>
      <h2>Application Received!</h2>
      <p>
        Thank you! We'll review your application and — if approved —
        you'll receive your affiliate link, portal access, and login code
        by email within <strong>24–48 hours</strong>.
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Application form ───────────────────────────────────────────────────────────
st.markdown('<div class="form-card"><h2>Apply Now</h2>', unsafe_allow_html=True)

with st.form("affiliate_signup_form", clear_on_submit=False):
    name = st.text_input(
        "Your full name *",
        placeholder="Jane Smith",
    )

    requested_code = st.text_input(
        "Requested affiliate code *",
        placeholder="JANEREADS",
        help="This becomes your personal link (e.g. ?ref=JANEREADS). Letters and underscores only, no spaces.",
    )

    paypal_email = st.text_input(
        "PayPal email address *",
        placeholder="jane@example.com",
        help="This is where we'll send your commission payments.",
    )

    marketing_plan = st.text_area(
        "How do you plan to market this product? *",
        placeholder="e.g. I run a Facebook group for romance authors with 4,000 members, and I share writing tools weekly in my newsletter...",
        height=130,
        help="Tell us about your audience and how you'll share your link.",
    )

    submitted = st.form_submit_button("Submit Application →", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Handle submission ──────────────────────────────────────────────────────────
if submitted:
    errors = []
    if not name.strip():
        errors.append("Please enter your full name.")
    if not requested_code.strip():
        errors.append("Please enter a requested affiliate code.")
    elif not requested_code.strip().replace("_", "").isalnum():
        errors.append("Affiliate code can only contain letters, numbers, and underscores.")
    if not paypal_email.strip() or "@" not in paypal_email:
        errors.append("Please enter a valid PayPal email address.")
    if not marketing_plan.strip():
        errors.append("Please describe how you plan to market the product.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        ok, err = submit_application(
            name           = name.strip(),
            requested_code = requested_code.strip(),
            paypal_email   = paypal_email.strip(),
            marketing_plan = marketing_plan.strip(),
        )
        if ok:
            st.session_state["aff_app_submitted"] = True
            st.rerun()
        else:
            st.error(f"Something went wrong submitting your application: {err}")
            st.info("Please try again or email us directly at hello@thewritingwives.com")

# ── Footer note ────────────────────────────────────────────────────────────────
st.markdown(f"""
<p style="text-align:center;color:#999;font-size:0.8rem;margin-top:2rem;">
  Already approved? <a href="/Affiliate_Portal" style="color:{GOLD_DARK};">Log in to your portal →</a>
</p>
""", unsafe_allow_html=True)
