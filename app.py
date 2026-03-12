import streamlit as st

st.set_page_config(
    page_title="AI Author Tools | The Writing Wives",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

pg = st.navigation(
    [
        st.Page("home.py",               title="Home",                      icon="✍️",  default=True),
        st.Page("1_Blurb_Auditor.py",    title="Blurb Auditor",             icon="📖"),
        st.Page("2_FB_Ad_Package.py",    title="FB & Instagram Ad Package", icon="📱"),
        st.Page("3_Cover_Assessment.py", title="Cover Assessment",          icon="🎨"),
        st.Page("4_Amazon_Assessment.py",title="Amazon Assessment",         icon="🛒"),
        st.Page("5_Order_Confirmed.py",  title="Order Confirmed",           icon="✅",  url_path="Order_Confirmed"),
    ],
    position="hidden",
)

pg.run()
