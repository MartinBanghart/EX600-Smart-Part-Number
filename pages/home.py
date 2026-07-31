import streamlit as st 
from PIL import Image
from streamlit_image_zoom import image_zoom
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
from pathlib import Path

# ---------------------------------------------------------------------------------------- 
# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Part Number Project",
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

    with col2:
        
        st.markdown("## Context")
        
        st.markdown("""
            - ##### Recent meeting with EDM team members (Connor Davis, Mark Jackson) determined the previous VQC1000/2000 SPN project was very intensive (~1000+ hours) \n
            - ##### Their project utilized Tacton Design Automation Studio (SolidWorks add in) to generate a model and drawing based on the Tacton model for the SPN \n
            - ##### This process would only work for engineers with SolidWorks access and an RFS with an applicable special
            - ##### Currently, this projects HTO for the SY1 EX600 is largely complete. We are currently seeking direction to move forward with the implementation of it.
            """)
        
        st.divider()
        
        st.markdown("## General Questions")
        
        st.markdown("""
                    - ##### What is the scope we are targeting? (Consider MEG / Production limitations) \n
                    - ##### Is the goal to automate an RFS or to expedite processes within an RFS?
                    - ##### Can we begin to assign the Smart Part Number to applicable specials for current RFS? The process would not change but no serialized part number would be used.
                    - ##### Can the Quote process be refined to eliminate bottlenecks such as model/drawing creation? \n 
                        - ##### If not, could they be simplified and offloaded to a point after sales has received and confirmed the quoted price with the customer?
                    """)
        
        st.divider()
        
        st.markdown("## Flow Diagram for Modified Quote Process")
        
        with st.container(border=True):
            image = Image.open(r"notes_and_references\spn_RFS.png")
            image_zoom(image,size=1250,keep_resolution=True,zoom_factor=2.15)
            
        st.markdown("#### Near Complete MSS")
        st.write("""
                    - BOM could be automatically formatted into engineering bom sheets \n
                    - Assembly Testing / FRL sheet could be automatically determined and formatted \n
                    - Engineer would only need to fill in RFS related information from ARAS
                """)
        
        st.markdown("#### General Production Drawing")
        st.write("""
                    This drawing would only contain minimal dimensions (overall X, Y, Z) and pertinent BOM items (valves, SI units, etc that features a spec table)
                """)

# ---------------------------------------------------------------------------------------- 
with tab1:
    col1, col2, col3 = st.columns([0.5, 3, 0.5])

    with col2:
        with st.container(border=True):
            image1 = Image.open(r"notes_and_references\SY1_EX600_SPN_HTO.png")
            image_zoom(image1,size=1250,keep_resolution=True,zoom_factor=2.15)
    
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