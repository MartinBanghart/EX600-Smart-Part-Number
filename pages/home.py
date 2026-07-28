import streamlit as st 
from PIL import Image
from streamlit_image_zoom import image_zoom
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
from pathlib import Path

# ---------------------------------------------------------------------------------------- 
# --- Page Configuration ---
st.set_page_config(
    page_title="Part Number Research",
    layout="wide"
)
# ---------------------------------------------------------------------------------------- 
t1, tab1, tab2, tab3 = st.tabs([
    "Process",
    "How To Order",
    "Valve Options",
    "SMC Catalogs"
])

# ---------------------------------------------------------------------------------------- 
with t1:
    col1, col2, col3 = st.columns([0.5, 3, 0.5])

    st.subheader("")



# ---------------------------------------------------------------------------------------- 
with tab1:
    col1, col2, col3 = st.columns([0.5, 3, 0.5])

    with col2:
        with st.container(border=True):
            image = Image.open(r"notes_and_references\SY1_EX600_SPN_HTO.png")
            image_zoom(image,size=1250,keep_resolution=True,zoom_factor=2.15)
    
# ---------------------------------------------------------------------------------------- 
with tab2:
    col1, col2, col3 = st.columns([0.35, 3, 0.35])

    with col2:
        df = pd.read_excel(
            r"notes_and_references\Valve Options - SY-1 EX600 Smart Part Number.xlsx",
            engine="openpyxl"
        )

        st.dataframe(df, height=800)

# ---------------------------------------------------------------------------------------- 
with tab3:

    pdf_folder = Path("notes_and_references/Catalog HTO")
    pdf_files = sorted(pdf_folder.glob("*.pdf"))

    if not pdf_files:
        st.warning("No PDF files found.")
    else:

        col1, col2, col3 = st.columns([1.5, 3, 1.5])

        with col1:
            selected_pdf = st.radio(
                "Documents",
                pdf_files,
                format_func=lambda p: p.stem
            )

        with col2:
            with st.container(border=True):
                with open(selected_pdf, "rb") as f:
                    pdf_data = f.read()

                pdf_viewer(
                    pdf_data,
                    width="100%",
                    height=1000
            )