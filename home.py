import streamlit as st
import base64
from pathlib import Path

try:
    import stripe as stripe_lib
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

# ── Brand colours ─────────────────────────────────────────────────────────────
PRIMARY    = "#1A1A1A"
PRIMARY_MID= "#2E2E2E"
GOLD       = "#D4B36E"
GOLD_DARK  = "#A8863A"
GOLD_LIGHT = "#FAF4E6"
GOLD_MID   = "#F5EDD6"
GOLD_BG    = "#FFFBEC"
GREEN      = "#1A7A4A"
GREEN_BG   = "#D4EDDA"

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_logo_b64():
    p = Path(__file__).parent / "logo.png"
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', Arial, sans-serif; }}
  .block-container {{ max-width: 840px; padding-top: 1rem; }}
  [data-testid="stSidebar"] {{ display: none; }}

  /* Hero */
  .hero-block {{
    background: {PRIMARY}; padding: 2.5rem 2.5rem 2rem;
    border-radius: 12px; margin-bottom: 2rem;
    border-bottom: 3px solid {GOLD}; text-align: center;
  }}
  .hero-block .logo-wrap {{ margin-bottom: 1.2rem; }}
  .hero-block .logo-wrap img {{ height: 140px; max-width: 100%; object-fit: contain; }}
  .hero-block .eyebrow {{ color:{GOLD}; font-size:0.72rem; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; margin:0 0 0.4rem; }}
  .hero-block h1 {{ color:#fff; font-size:2rem; font-weight:900; margin:0 0 0.5rem; line-height:1.2; }}
  .hero-block .hero-sub {{ color:#ccc; font-size:1rem; margin:0 auto; max-width:520px; line-height:1.65; }}

  /* Tool cards */
  .tool-card {{
    background:#fff; border:1px solid #e8d9b0;
    border-top:4px solid {GOLD}; border-radius:12px;
    padding:1.5rem 1.5rem 1.2rem; margin-bottom:0.5rem;
  }}
  .tool-card .tc-icon {{ font-size:2rem; margin-bottom:0.4rem; }}
  .tool-card .tc-name {{ font-size:1.15rem; font-weight:900; color:{PRIMARY}; margin-bottom:0.2rem; }}
  .tool-card .tc-tagline {{ font-size:0.86rem; color:#666; margin-bottom:0.9rem; line-height:1.5; }}
  .tool-card ul {{ list-style:none; padding:0; margin:0 0 1rem; }}
  .tool-card ul li {{ font-size:0.86rem; color:#444; padding:2px 0; line-height:1.5; }}
  .tool-card ul li::before {{ content:"✓ "; color:{GOLD_DARK}; font-weight:700; }}
  .tool-card .tc-price {{ font-size:1.5rem; font-weight:900; color:{PRIMARY}; }}
  .tool-card .tc-price-sub {{ font-size:0.76rem; color:#999; margin-bottom:0.6rem; }}

  /* Lifetime card */
  .lifetime-card {{
    background:{PRIMARY}; border:2px solid {GOLD};
    border-radius:14px; padding:2rem 2.5rem;
    margin:1.5rem 0; text-align:center;
  }}
  .lifetime-card .lc-eyebrow {{ color:{GOLD}; font-size:0.72rem; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; margin-bottom:0.4rem; }}
  .lifetime-card h2 {{ color:#fff; font-size:1.6rem; font-weight:900; margin:0 0 0.4rem; }}
  .lifetime-card .lc-sub {{ color:#bbb; font-size:0.95rem; margin-bottom:1.2rem; line-height:1.6; }}
  .lifetime-card ul {{ list-style:none; padding:0; display:inline-block; text-align:left; margin:0 auto 1.5rem; }}
  .lifetime-card ul li {{ font-size:0.93rem; color:#ddd; padding:3px 0; }}
  .lifetime-card ul li::before {{ content:"✓ "; color:{GOLD}; font-weight:700; }}
  .lc-price {{ font-size:2.2rem; font-weight:900; color:{GOLD}; }}
  .lc-price-sub {{ font-size:0.85rem; color:#999; margin-bottom:1.5rem; }}

  /* How it works */
  .how-step {{
    background:{GOLD_LIGHT}; border:1px solid #e8d9b0;
    border-radius:10px; padding:1.3rem 1.2rem;
    text-align:center;
  }}
  .how-step .step-num {{ font-size:2rem; font-weight:900; color:{GOLD_DARK}; margin-bottom:0.3rem; }}
  .how-step .step-title {{ font-size:0.95rem; font-weight:700; color:{PRIMARY}; margin-bottom:0.3rem; }}
  .how-step .step-desc {{ font-size:0.84rem; color:#555; line-height:1.55; }}

  /* Section title */
  .section-title {{ color:{PRIMARY}; font-size:1.3rem; font-weight:900; border-bottom:3px solid {GOLD}; padding-bottom:6px; margin:2rem 0 1.2rem; }}

  /* Banners */
  .success-banner {{ background:{GREEN_BG}; border:1px solid #b8ddc8; border-left:4px solid {GREEN}; border-radius:0 8px 8px 0; padding:1rem 1.25rem; margin-bottom:1.5rem; font-size:0.92rem; color:#155724; }}
  .info-banner {{ background:#EEF4FF; border:1px solid #c5d8f8; border-left:4px solid #3B6FD4; border-radius:0 8px 8px 0; padding:0.85rem 1.1rem; margin-bottom:1.5rem; font-size:0.88rem; color:#1a3a6b; }}

  /* Buttons */
  .stButton > button {{
    background:{PRIMARY} !important; color:{GOLD} !important;
    font-weight:700 !important; padding:0.65rem 2rem !important;
    border-radius:8px !important; border:2px solid {GOLD} !important;
    font-size:1rem !important; width:100%;
  }}
  .stButton > button:hover {{ background:{GOLD} !important; color:{PRIMARY} !important; }}

  /* Community CTA */
  .community-card {{
    background: {PRIMARY}; border: 2px solid {GOLD};
    border-radius: 14px; padding: 2rem 2.5rem;
    margin: 0.5rem 0 1.5rem; text-align: center;
  }}
  .community-card .cc-eyebrow {{ color:{GOLD}; font-size:0.72rem; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; margin-bottom:0.4rem; }}
  .community-card h2 {{ color:#fff; font-size:1.5rem; font-weight:900; margin:0 0 0.5rem; }}
  .community-card .cc-sub {{ color:#bbb; font-size:0.95rem; line-height:1.65; margin:0 auto 1.4rem; max-width:500px; }}
  .cc-btn {{
    display:inline-block; background:{GOLD}; color:{PRIMARY};
    font-weight:700; padding:0.7rem 2rem; border-radius:8px;
    font-size:1rem; text-decoration:none; border:2px solid {GOLD};
  }}
  .cc-btn:hover {{ background:#fff; color:{PRIMARY}; border-color:#fff; }}

  .footer-note {{ text-align:center; color:#aaa; font-size:0.78rem; margin-top:3rem; padding-top:1rem; border-top:1px solid {GOLD_MID}; }}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
_logo_b64 = get_logo_b64()
_logo_html = f'<div class="logo-wrap"><img src="data:image/png;base64,{_logo_b64}" alt="The Writing Wives"></div>' if _logo_b64 else ""

st.markdown(f"""
<div class="hero-block">
  {_logo_html}
  <div class="eyebrow">Genre and Trope Essentials</div>
  <h1>Convert Browsers Into Buyers</h1>
  <p class="hero-sub">Every tool is built on real genre and trope principles — not generic writing advice.
  Pick the tool you need.</p>
</div>
""", unsafe_allow_html=True)

# ── Tool grid ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Choose Your Tool</div>', unsafe_allow_html=True)

TOOLS = [
    {
        "icon": "📖",
        "name": "Blurb Auditor",
        "tagline": "Know exactly why your blurb isn't converting — and get it rewritten for you.",
        "features": [
            "6-category scored audit",
            "2 complete rewritten blurbs",
            "Trope signal check",
            "GEO section for AI discovery",
            "Downloadable Word doc",
            "+ FB Ad Package available as add-on",
        ],
        "price": get_secret("PRICE_DISPLAY", "$27"),
        "price_sub": get_secret("PRICE_SUBTITLE", "per report · unlimited audits"),
        "page": "1_Blurb_Auditor.py",
        "cta": "Audit My Blurb →",
    },
    {
        "icon": "📱",
        "name": "FB & Instagram Ad Package",
        "tagline": "Ready-to-paste ad copy in every format — built from your blurb.",
        "features": [
            "5 headline variations (under 40 chars)",
            "3 primary text options (short/medium/long)",
            "2 description field options",
            "⭐ Best Pick for each element",
            "Audience targeting suggestion",
        ],
        "price": get_secret("AD_PRICE_DISPLAY", "$25"),
        "price_sub": get_secret("AD_PRICE_SUBTITLE", "per report · ad copy for your blurb"),
        "page": "2_FB_Ad_Package.py",
        "cta": "Get My Ad Copy →",
    },
    {
        "icon": "🎨",
        "name": "Cover Assessment",
        "tagline": "Does your cover signal the right genre and work at thumbnail size?",
        "features": [
            "Genre signal analysis",
            "Thumbnail & mobile performance",
            "Title & author name readability",
            "Professional quality score",
            "Specific redesign recommendations",
        ],
        "price": get_secret("COVER_PRICE_DISPLAY", "$15"),
        "price_sub": get_secret("COVER_PRICE_SUBTITLE", "per report · per cover"),
        "page": "3_Cover_Assessment.py",
        "cta": "Assess My Cover →",
    },
    {
        "icon": "🛒",
        "name": "Amazon Page Assessment",
        "tagline": "Your full Amazon product page scored: title, cover, blurb, and star rating.",
        "features": [
            "Title & subtitle optimization",
            "Cover effectiveness review",
            "Blurb conversion analysis",
            "Star rating health check (4.2+ target)",
            "Keyword & category suggestions",
        ],
        "price": get_secret("AMAZON_PRICE_DISPLAY", "$19"),
        "price_sub": get_secret("AMAZON_PRICE_SUBTITLE", "per report · full page review"),
        "page": "4_Amazon_Assessment.py",
        "cta": "Assess My Page →",
    },
]

col1, col2 = st.columns(2)
for i, tool in enumerate(TOOLS):
    with (col1 if i % 2 == 0 else col2):
        st.markdown(f"""
        <div class="tool-card">
          <div class="tc-icon">{tool['icon']}</div>
          <div class="tc-name">{tool['name']}</div>
          <div class="tc-tagline">{tool['tagline']}</div>
          <ul>{''.join(f"<li>{f}</li>" for f in tool['features'])}</ul>
          <div class="tc-price">{tool['price']}</div>
          <div class="tc-price-sub">{tool['price_sub']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(tool["cta"], use_container_width=True, key=f"tool_btn_{i}"):
            st.switch_page(tool["page"])

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
h1, h2, h3 = st.columns(3)
steps = [
    ("1", "Pick your tool", "Choose the report you need — blurb, ads, cover, or full Amazon page."),
    ("2", "Paste or upload", "Add your blurb, upload your cover image, or fill in your book details."),
    ("3", "Get your report", "Receive a scored, actionable report in seconds — with a Word doc to download."),
]
for col, (num, title, desc) in zip([h1, h2, h3], steps):
    with col:
        st.markdown(f"""
        <div class="how-step">
          <div class="step-num">{num}</div>
          <div class="step-title">{title}</div>
          <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Community CTA ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Want the Full Training?</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="community-card">
  <div class="cc-eyebrow">The Writing Wives Community</div>
  <h2>Join The Writing Wives on Skool</h2>
  <p class="cc-sub">Get full training on growing your Author Empire — plus discounts on the
  Genre and Trope Essential Package when you join the community.</p>
  <a class="cc-btn" href="http://www.skool.com/thewritingwives" target="_blank">
    Join The Writing Wives →
  </a>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-note">
  The Writing Wives · Genre and Trope Essentials ·
  <a href="https://thewritingwives.com" style="color:#999;">thewritingwives.com</a>
</div>
""", unsafe_allow_html=True)
