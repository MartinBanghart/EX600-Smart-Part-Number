import streamlit as st

# ---------------------------------------------------------------------------------------- 
# controls size of the top navigation bar tabs
st.markdown("""
<style>
    /* Navigation links */
    [data-testid="stTopNavLinkContainer"] a {
        font-size: 1.3rem !important;
        padding: 0.3rem 3rem !important;
        min-height: 30px !important;
    }
    
    /* Reduce space between nav and page content */
    .block-container {padding-top: 3rem !important;
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
        st.Page("pages/home.py", title="Info"),
        st.Page("pages/test.py", title="Configure"),
]
pg = st.navigation(pages, position="top")
pg.run()
