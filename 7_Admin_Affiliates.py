"""
Admin — Affiliate Management
The Writing Wives AI Author Tools
-----------------------------------
Password-protected admin view for:
  • Creating new affiliate codes
  • Viewing all sales by affiliate
  • Marking commissions as paid
  • Seeing total amounts owed

Access with ADMIN_PASSWORD from st.secrets.
"""

import streamlit as st
from datetime import datetime as _dt


from affiliate_utils import (
    get_all_affiliates,
    get_all_sales,
    create_affiliate,
    mark_paid,
    get_pending_applications,
    get_all_applications,
    approve_application,
    reject_application,
    PRODUCT_NAMES,
    DEFAULT_COMMISSION_RATE,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Admin — Affiliates | The Writing Wives",
    page_icon="🔐",
    layout="wide",
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
RED        = "#CC3333"
RED_BG     = "#FFF0F0"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', Arial, sans-serif; }}
  [data-testid="stSidebar"] {{ display: none; }}

  .admin-header {{
    background:{PRIMARY}; border-bottom:3px solid {GOLD};
    border-radius:10px; padding:1.5rem 2rem; margin-bottom:2rem;
  }}
  .admin-header h1 {{ color:#fff; font-size:1.7rem; font-weight:900; margin:0 0 0.2rem; }}
  .admin-header .sub {{ color:#aaa; font-size:0.9rem; margin:0; }}

  .section-title {{
    color:{PRIMARY}; font-size:1.1rem; font-weight:900;
    border-bottom:3px solid {GOLD}; padding-bottom:5px; margin:1.5rem 0 1rem;
  }}

  .stat-row {{ display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap; }}
  .stat-card {{
    flex:1; min-width:150px; background:#fff;
    border:1px solid #e8d9b0; border-top:4px solid {GOLD};
    border-radius:10px; padding:1rem; text-align:center;
  }}
  .stat-card .stat-label {{ font-size:0.72rem; font-weight:700; color:#888;
    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem; }}
  .stat-card .stat-value {{ font-size:1.8rem; font-weight:900; color:{PRIMARY}; }}
  .stat-card .stat-sub {{ font-size:0.75rem; color:#999; margin-top:0.2rem; }}

  .badge-paid {{
    background:{GREEN_BG}; color:{GREEN};
    font-size:0.75rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
  }}
  .badge-unpaid {{
    background:#FFF3CD; color:#856404;
    font-size:0.75rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
  }}

  .stButton > button {{
    background:{PRIMARY} !important; color:{GOLD} !important;
    font-weight:700 !important; border-radius:8px !important;
    border:2px solid {GOLD} !important; font-size:0.9rem !important;
  }}
  .stButton > button:hover {{ background:{GOLD} !important; color:{PRIMARY} !important; }}

  .badge-pending {{
    background:#FFF3CD; color:#856404;
    font-size:0.75rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
  }}
  .badge-approved {{
    background:#D4EDDA; color:#1A7A4A;
    font-size:0.75rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
  }}
  .badge-rejected {{
    background:#FFF0F0; color:#CC3333;
    font-size:0.75rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
  }}
  .app-card {{
    background:#fff; border:1px solid #e8d9b0;
    border-radius:10px; padding:1.2rem 1.4rem; margin-bottom:1rem;
    border-left:4px solid #D4B36E;
  }}
  .info-box {{
    background:#EEF4FF; border:1px solid #c5d8f8;
    border-left:4px solid #3B6FD4; border-radius:0 8px 8px 0;
    padding:0.8rem 1rem; font-size:0.87rem; color:#1a3a6b;
    margin-bottom:1rem;
  }}
  .success-box {{
    background:{GREEN_BG}; border:1px solid #b8ddc8;
    border-left:4px solid {GREEN}; border-radius:0 8px 8px 0;
    padding:0.8rem 1rem; font-size:0.87rem; color:#155724;
    margin-bottom:1rem;
  }}
</style>
""", unsafe_allow_html=True)

# ── Password gate ──────────────────────────────────────────────────────────────
def check_admin_pw(pw: str) -> bool:
    try:
        return pw == st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        return False

if not st.session_state.get("admin_auth"):
    st.markdown(f"""
    <div class="admin-header">
      <h1>🔐 Affiliate Admin</h1>
      <p class="sub">Enter your admin password to access this page.</p>
    </div>
    """, unsafe_allow_html=True)
    with st.form("admin_login"):
        pw   = st.text_input("Admin password", type="password")
        sub  = st.form_submit_button("Log In →", use_container_width=True)
    if sub:
        if check_admin_pw(pw):
            st.session_state["admin_auth"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# ── Authenticated ──────────────────────────────────────────────────────────────

# Load all data first so we can use counts in the header
all_affiliates   = get_all_affiliates()
all_sales        = get_all_sales()
pending_apps     = get_pending_applications()

st.markdown(f"""
<div class="admin-header">
  <h1>🔐 Affiliate Admin</h1>
  <p class="sub">The Writing Wives — manage affiliates, view sales, and record payouts.</p>
</div>
""", unsafe_allow_html=True)

if pending_apps:
    st.warning(f"⚠️ {len(pending_apps)} pending application(s) waiting for review — see the Applications tab.")

# ── Summary stats ──────────────────────────────────────────────────────────────
total_commission = sum(s.get("commission_amount", 0) for s in all_sales)
total_paid       = sum(s.get("commission_amount", 0) for s in all_sales if s.get("status") == "paid")
total_owed       = total_commission - total_paid
total_revenue    = sum(s.get("sale_amount", 0) for s in all_sales)

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card">
    <div class="stat-label">Active Affiliates</div>
    <div class="stat-value">{len(all_affiliates)}</div>
    <div class="stat-sub">all time</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total Sales</div>
    <div class="stat-value">{len(all_sales)}</div>
    <div class="stat-sub">via affiliates</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total Revenue</div>
    <div class="stat-value">${total_revenue:,.0f}</div>
    <div class="stat-sub">affiliate-driven</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total Commission</div>
    <div class="stat-value">${total_commission:,.2f}</div>
    <div class="stat-sub">earned by affiliates</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">⚠️ Total Owed</div>
    <div class="stat-value" style="color:#B8860B;">${total_owed:,.2f}</div>
    <div class="stat-sub">unpaid commissions</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab0, tab1, tab2, tab3 = st.tabs(["📬 Applications", "💰 Unpaid Commissions", "📋 All Sales", "➕ Manage Affiliates"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 0 — Affiliate Applications
# ─────────────────────────────────────────────────────────────────────────────
with tab0:
    all_apps = get_all_applications()
    pending  = [a for a in all_apps if a.get("status") == "pending"]
    reviewed = [a for a in all_apps if a.get("status") != "pending"]

    if not all_apps:
        st.info("No applications yet. Share the signup link: "
                f"`{st.secrets.get('APP_BASE_URL','https://YOUR-APP.streamlit.app')}/Affiliate_Signup`")
    else:
        # Pending applications
        if pending:
            st.markdown(f"### 📬 Pending Applications ({len(pending)})")
            st.markdown(
                '<div class="info-box">Review each application below. '
                'Approved applicants are automatically created as affiliates and emailed their link.</div>',
                unsafe_allow_html=True,
            )
            for app in pending:
                app_id    = app["id"]
                app_name  = app.get("name", "—")
                app_code  = app.get("requested_code", "")
                app_email = app.get("paypal_email", "")
                app_plan  = app.get("marketing_plan", "")
                raw_date  = app.get("applied_at", "")
                try:
                    display_date = _dt.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    ).strftime("%b %d, %Y at %I:%M %p")
                except Exception:
                    display_date = raw_date[:10] if raw_date else "—"

                st.markdown(f"""
                <div class="app-card">
                  <strong style="font-size:1.05rem;">{app_name}</strong>
                  &nbsp;<span class="badge-pending">Pending</span>
                  <div style="font-size:0.85rem;color:#666;margin-top:0.3rem;">
                    Applied: {display_date}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**PayPal email:** {app_email}")
                    st.markdown(f"**Requested code:** `{app_code}`")
                with col_b:
                    st.markdown(f"**Marketing plan:**")
                    st.markdown(f"> {app_plan[:300]}{'...' if len(app_plan) > 300 else ''}")

                with st.expander(f"✅ Approve {app_name}"):
                    with st.form(f"approve_form_{app_id}"):
                        st.markdown("Confirm the details before approving. The affiliate will be created and emailed automatically.")
                        conf_code = st.text_input(
                            "Affiliate code (confirm or change)",
                            value=app_code,
                            key=f"code_{app_id}",
                        )
                        conf_rate = st.number_input(
                            "Commission rate (%)",
                            min_value=1, max_value=50,
                            value=int(DEFAULT_COMMISSION_RATE * 100),
                            step=1, key=f"rate_{app_id}",
                        )
                        conf_notes = st.text_input(
                            "Internal notes (optional)",
                            placeholder="e.g. Big newsletter — 10k subscribers",
                            key=f"notes_{app_id}",
                        )
                        approve_btn = st.form_submit_button(
                            "✅ Approve & Send Email", use_container_width=True
                        )
                    if approve_btn:
                        ok, err = approve_application(
                            app_id=app_id,
                            code=conf_code.strip().upper(),
                            name=app_name,
                            email=app_email,
                            notes=conf_notes.strip(),
                            commission_rate=conf_rate / 100,
                        )
                        if ok:
                            st.success(f"✅ {app_name} approved and emailed their affiliate link!")
                            st.rerun()
                        else:
                            st.error(f"Error approving: {err}")

                col_rej, _ = st.columns([1, 3])
                with col_rej:
                    if st.button(f"❌ Reject", key=f"reject_{app_id}"):
                        reject_application(app_id)
                        st.warning(f"Application from {app_name} rejected.")
                        st.rerun()

                st.divider()

        else:
            st.success("🎉 No pending applications right now!")

        # Previously reviewed
        if reviewed:
            with st.expander(f"View {len(reviewed)} reviewed application(s)"):
                for app in reviewed:
                    status    = app.get("status", "")
                    badge_cls = "badge-approved" if status == "approved" else "badge-rejected"
                    st.markdown(
                        f"**{app.get('name','—')}** &nbsp;"
                        f"<span class='{badge_cls}'>{status.title()}</span> &nbsp; "
                        f"`{app.get('requested_code','')}` &nbsp; {app.get('paypal_email','')}",
                        unsafe_allow_html=True,
                    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Unpaid commissions (grouped by affiliate)
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    unpaid = [s for s in all_sales if s.get("status") == "unpaid"]

    if not unpaid:
        st.success("🎉 All commissions are paid! Nothing owed right now.")
    else:
        # Group by affiliate
        by_aff: dict[str, list] = {}
        for s in unpaid:
            c = s.get("affiliate_code", "UNKNOWN")
            by_aff.setdefault(c, []).append(s)

        # Build affiliate name lookup
        aff_names = {a["code"]: a.get("name", a["code"]) for a in all_affiliates}

        st.markdown(f"""
        <div class="info-box">
          ℹ️ Check the boxes next to the sales you've paid, then click <strong>Mark Selected as Paid</strong>.
        </div>
        """, unsafe_allow_html=True)

        paid_ids_to_mark = []

        for code, code_sales in by_aff.items():
            aff_total = sum(s.get("commission_amount", 0) for s in code_sales)
            aff_name  = aff_names.get(code, code)

            # Find email from affiliates list
            aff_email = next(
                (a.get("email", "") for a in all_affiliates if a["code"] == code), ""
            )

            st.markdown(f"""
            <div style="background:{GOLD_LIGHT};border:1px solid #e8d9b0;
              border-radius:8px;padding:0.8rem 1rem;margin:1rem 0 0.5rem;">
              <strong style="color:{PRIMARY};font-size:1rem;">{aff_name}</strong>
              &nbsp;<code style="font-size:0.82rem;">{code}</code>
              {f'&nbsp;·&nbsp;<span style="color:#666;font-size:0.85rem;">{aff_email}</span>' if aff_email else ''}
              &nbsp;·&nbsp;
              <strong style="color:{GOLD_DARK};">Owes: ${aff_total:,.2f}</strong>
            </div>
            """, unsafe_allow_html=True)

            for s in code_sales:
                product_name = PRODUCT_NAMES.get(s.get("product", ""), s.get("product", ""))
                raw_date     = s.get("sale_date", "")
                try:
                    display_date = _dt.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    ).strftime("%b %d, %Y")
                except Exception:
                    display_date = raw_date[:10] if raw_date else "—"

                col_cb, col_info, col_amt = st.columns([0.5, 5, 1.5])
                with col_cb:
                    checked = st.checkbox(
                        "Select",
                        key=f"pay_{s['id']}",
                        label_visibility="collapsed",
                    )
                    if checked:
                        paid_ids_to_mark.append(s["id"])
                with col_info:
                    st.markdown(
                        f"**{product_name}** &nbsp; <span style='color:#888;font-size:0.85rem;'>{display_date}</span>",
                        unsafe_allow_html=True,
                    )
                with col_amt:
                    st.markdown(
                        f"<div style='text-align:right;font-weight:700;color:{GOLD_DARK};'>${s.get('commission_amount',0):.2f}</div>",
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"✅ Mark {len(paid_ids_to_mark)} Selected Sale(s) as Paid", use_container_width=True):
            if paid_ids_to_mark:
                ok = mark_paid(paid_ids_to_mark)
                if ok:
                    st.markdown(f"""
                    <div class="success-box">
                      ✅ Marked {len(paid_ids_to_mark)} sale(s) as paid.
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error("Something went wrong updating the records. Check your Supabase connection.")
            else:
                st.warning("No sales selected — check the boxes next to the sales you've paid first.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — All sales
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    if not all_sales:
        st.info("No affiliate sales recorded yet.")
    else:
        aff_names = {a["code"]: a.get("name", a["code"]) for a in all_affiliates}

        # Filter controls
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_status = st.selectbox("Filter by status", ["All", "Unpaid", "Paid"])
        with col_f2:
            all_codes   = sorted(set(s.get("affiliate_code","") for s in all_sales))
            filter_code = st.selectbox("Filter by affiliate", ["All"] + all_codes)

        filtered = all_sales
        if filter_status == "Unpaid":
            filtered = [s for s in filtered if s.get("status") == "unpaid"]
        elif filter_status == "Paid":
            filtered = [s for s in filtered if s.get("status") == "paid"]
        if filter_code != "All":
            filtered = [s for s in filtered if s.get("affiliate_code") == filter_code]

        st.markdown(f"**{len(filtered)} sale(s) shown**")

        for s in filtered:
            code         = s.get("affiliate_code", "")
            aff_name     = aff_names.get(code, code)
            product_name = PRODUCT_NAMES.get(s.get("product", ""), s.get("product", ""))
            raw_date     = s.get("sale_date", "")
            try:
                display_date = _dt.fromisoformat(raw_date.replace("Z", "+00:00")).strftime("%b %d, %Y")
            except Exception:
                display_date = raw_date[:10] if raw_date else "—"
            status = s.get("status", "unpaid")

            c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1.5, 1])
            with c1:
                st.markdown(f"**{aff_name}** `{code}`")
            with c2:
                st.markdown(f"{product_name}")
            with c3:
                st.markdown(f"${s.get('sale_amount',0):.2f} sale")
            with c4:
                st.markdown(f"**${s.get('commission_amount',0):.2f}** commission")
            with c5:
                st.markdown(
                    f"<span class='{'badge-paid' if status=='paid' else 'badge-unpaid'}'>{'✓ Paid' if status=='paid' else 'Pending'}</span>",
                    unsafe_allow_html=True,
                )
            st.caption(f"📅 {display_date}  ·  Stripe: {s.get('stripe_session_id','')[:24]}...")
            st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Manage affiliates
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    # ── Existing affiliates table ──────────────────────────────────────────────
    st.markdown('<div class="section-title">Current Affiliates</div>', unsafe_allow_html=True)

    if not all_affiliates:
        st.info("No affiliates yet — create one below.")
    else:
        # Build summary per affiliate
        sales_by_code: dict[str, list] = {}
        for s in all_sales:
            c = s.get("affiliate_code", "")
            sales_by_code.setdefault(c, []).append(s)

        try:
            app_base_url = st.secrets.get("APP_BASE_URL", "https://YOUR-APP.streamlit.app")
        except Exception:
            app_base_url = "https://YOUR-APP.streamlit.app"

        for aff in all_affiliates:
            code      = aff["code"]
            aff_sales = sales_by_code.get(code, [])
            earned    = sum(s.get("commission_amount", 0) for s in aff_sales)
            paid_out  = sum(s.get("commission_amount", 0) for s in aff_sales if s.get("status") == "paid")
            owed      = earned - paid_out
            rate_pct  = int(aff.get("commission_rate", 0.20) * 100)
            ref_link  = f"{app_base_url}/?ref={code}"

            with st.expander(f"**{aff.get('name', code)}** — {code} — {len(aff_sales)} sales — Owed: ${owed:.2f}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Name:** {aff.get('name','—')}")
                    st.markdown(f"**Email:** {aff.get('email','—')}")
                    st.markdown(f"**Commission rate:** {rate_pct}%")
                with col_b:
                    st.markdown(f"**Total sales:** {len(aff_sales)}")
                    st.markdown(f"**Total earned:** ${earned:.2f}")
                    st.markdown(f"**Paid out:** ${paid_out:.2f} &nbsp;·&nbsp; **Owed:** ${owed:.2f}")
                if aff.get("notes"):
                    st.markdown(f"**Notes:** {aff['notes']}")
                st.markdown(f"**Referral link:** `{ref_link}`")

    # ── Create new affiliate ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">Create New Affiliate</div>', unsafe_allow_html=True)

    with st.form("new_affiliate_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name  = st.text_input("Full name *", placeholder="Jane Smith")
            new_code  = st.text_input(
                "Affiliate code *",
                placeholder="JANE_SMITH",
                help="Uppercase, no spaces. This is their login and appears in their referral link.",
            )
        with col2:
            new_email = st.text_input("Email address", placeholder="jane@example.com")
            new_rate  = st.number_input(
                "Commission rate (%)",
                min_value=1,
                max_value=50,
                value=int(DEFAULT_COMMISSION_RATE * 100),
                step=1,
                help="20 = 20% of each sale",
            )
        new_notes = st.text_area("Internal notes (optional)", placeholder="Referred by...", height=70)
        create_btn = st.form_submit_button("➕ Create Affiliate", use_container_width=True)

    if create_btn:
        if not new_name.strip() or not new_code.strip():
            st.error("Name and code are required.")
        else:
            ok, err = create_affiliate(
                code            = new_code.strip(),
                name            = new_name.strip(),
                email           = new_email.strip(),
                notes           = new_notes.strip(),
                commission_rate = new_rate / 100,
            )
            if ok:
                try:
                    app_base_url = st.secrets.get("APP_BASE_URL", "https://YOUR-APP.streamlit.app")
                except Exception:
                    app_base_url = "https://YOUR-APP.streamlit.app"
                ref_link = f"{app_base_url}/?ref={new_code.strip().upper()}"
                st.markdown(f"""
                <div class="success-box">
                  ✅ Affiliate <strong>{new_name.strip()}</strong> created with code
                  <code>{new_code.strip().upper()}</code>.<br>
                  Their referral link: <strong>{ref_link}</strong>
                </div>
                """, unsafe_allow_html=True)
                st.rerun()
            else:
                st.error(f"Couldn't create affiliate: {err}")

# ── Log out ────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🔓 Log out of admin"):
    st.session_state["admin_auth"] = False
    st.rerun()
