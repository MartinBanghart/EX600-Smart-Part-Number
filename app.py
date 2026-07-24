import streamlit as st

# ---------------------------------------------------------------------------------------- 
# controls size of the top navigation bar tabs
st.markdown("""
<style>
    /* Navigation links */
    [data-testid="stTopNavLinkContainer"] a {
        font-size: 1.2rem !important;
        padding: 0.3rem 4rem !important;
        min-height: 50px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------- 
# --- Page Configuration ---
st.set_page_config(
    page_title="Part Number Research",
    layout="wide"
)
# ---------------------------------------------------------------------------------------- 
pages = [
        st.Page("pages/home.py", title="Home"),
        st.Page("pages/test.py", title="Test"),
]
pg = st.navigation(pages, position="top")
pg.run()
