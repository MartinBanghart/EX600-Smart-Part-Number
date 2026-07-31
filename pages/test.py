# general dependencies
import streamlit as st
from pydantic import StringConstraints, ValidationError

# model imports
from main_model import run_main_model

# Loading data
from utilities.config import YAML_DATA
# ---------------------------------------------------------------------------------------- 
# CSS to allow st.dialog to take up more space on the page
st.markdown(
    """
    <style>
        /* target the outer dialog container and force it to be wider */
        [data-testid="stDialog"] > div:first-child {
            width: 90vw !important;  /* 85% of viewport width */
            max-width: 90vw !important;
            height: 90vh !important; /* 85% of viewport height */
        }
    </style>
    """,
    unsafe_allow_html=True,
)
# ---------------------------------------------------------------------------------------- 
# --- Page Configuration ---
st.set_page_config(
    page_title="Configurator",
    layout="wide"
)
# ---------------------------------------------------------------------------------------- 
# initializing variables in to session state
if "valve_stations" not in st.session_state:
    st.session_state.valve_stations = [0]

# ---------------------------------------------------------------------------------------- 
# creates a list of all unique field options for a given category
def get_unique_field_values(data, category, field_name):
    return sorted({
        item[field_name]
        for item in data[category].values()
        if field_name in item
    })

# dives one level deeper by only grabbing field values for a specific type --> only used for valves_symbols field "type"
def get_unique_field_values_by_type(data, category, field_name, type_value):
    return sorted({
        item[field_name]
        for item in data[category].values()
        if item.get("type") == type_value
        and field_name in item
    })
    
# creates sorted list of all matching valve_symbols given the set field properties
def get_matching_symbols(data, category, **filters):
    matches = []

    for symbol, attrs in data[category].items():
        if all(attrs.get(field) == value for field, value in filters.items()):
            matches.append(symbol)

    return sorted(matches)

# ---------------------------------------------------------------------------------------- 
# resuable code for generating and removing valve station configuration blocks
def render_valve_station(station_idx):
    with st.container(border=True):
        
        maincol_1, maincol_2 = st.columns([1,5])
        with maincol_1:
            st.write("") # used for vertically spacing the below markdown down, to center more with st.pills() in next column over
            st.markdown(f"### Station {station_idx + 1}")

        with maincol_2:
            # Type
            station_type_opts = get_unique_field_values(YAML_DATA, "valve_symbols", "type",)
            station_type = st.pills("Station Type", station_type_opts, default='valve', key=f"station_type_{station_idx}", label_visibility="collapsed")
        
        (vsub_col1, vsub_col2, vsub_col3, vsub_col4, vsub_col5, vsub_col6, vsub_col7, vdesc_col) = st.columns([0.3, 0.3, 0.5, 0.4, 0.4, 0.3, 0.4, 1])

        # Actuation
        with vsub_col1:
            actuation_opts = get_unique_field_values_by_type(YAML_DATA,"valve_symbols","actuation",station_type)
            st.selectbox("Actuation", actuation_opts if actuation_opts else [""], key=f"actuation_{station_idx}", disabled=not actuation_opts)

        # Seal Type
        with vsub_col2:
            seal_type_opts = get_unique_field_values_by_type(YAML_DATA, "valve_symbols", "seal_type", station_type)
            st.selectbox("Seal Type",seal_type_opts if seal_type_opts else [""], key=f"seal_type_{station_idx}", disabled=not seal_type_opts,)

        # Back Pressure Check
        with vsub_col3:
            back_pressure_opts = get_unique_field_values_by_type(YAML_DATA, "valve_symbols", "back_pressure_check", station_type)
            st.selectbox("Back Pressure Check", back_pressure_opts if back_pressure_opts else [""], key=f"back_pressure_check_{station_idx}", disabled=not back_pressure_opts)

        # Pilot Valve
        with vsub_col4:
            pilot_valve_opts = get_unique_field_values_by_type(YAML_DATA, "valve_symbols", "pilot_valve", station_type)
            st.selectbox("Pilot Valve", pilot_valve_opts if pilot_valve_opts else [""], key=f"pilot_valve_{station_idx}", disabled=not pilot_valve_opts)

        # Fitting Size
        with vsub_col5:
            fitting_size_opts = get_unique_field_values_by_type(YAML_DATA, "valve_symbols", "fitting_size", station_type )
            st.selectbox("Fitting Size", fitting_size_opts if fitting_size_opts else [""], key=f"fitting_size_{station_idx}", disabled=not fitting_size_opts)

        # Qty
        with vsub_col6:
            domain = [1] if station_type == "supply_blocking_disk" else list(range(1, 32))
            st.selectbox("Qty", domain, key=f"qty_{station_idx}",)

        # Valve Symbol
        with vsub_col7:
            matching_symbols = get_matching_symbols(
                YAML_DATA,
                "valve_symbols",
                type=station_type,
                actuation=st.session_state.get(f"actuation_{station_idx}", ""),
                seal_type=st.session_state.get(f"seal_type_{station_idx}", ""),
                back_pressure_check=st.session_state.get(
                    f"back_pressure_check_{station_idx}",
                    "",
                ),
                pilot_valve=st.session_state.get(
                    f"pilot_valve_{station_idx}",
                    "",
                ),
                fitting_size=st.session_state.get(
                    f"fitting_size_{station_idx}",
                    "",
                ),
            )
            
            
            selected_symbol = st.selectbox(
                "Valve Symbol",
                matching_symbols if matching_symbols else [""],
                key=f"valve_symbol_{station_idx}",
                disabled=not matching_symbols,
            )

        # Matching Description for Valve Symbol
        with vdesc_col:
            desc = YAML_DATA["valve_symbols"].get(
                selected_symbol, {}
            ).get("desc", "")

            if desc:
                st.text_input(
                    "Description",
                    value=desc,
                    disabled=True,
                    key=f"desc_display_{station_idx}_{selected_symbol}"
                )
            else:
                # in the event no matching symbols are found for the given values configured
                # --- return that valve configuration is invalid
                st.text_input(
                    "Description",
                    value="Invalid Options Configured",
                    disabled=True,
                    key=f"desc_display_{station_idx}_{selected_symbol}"
                )

        # Remove button
        if len(st.session_state.valve_stations) > 1:
            if st.button(
                "Remove Station",
                key=f"remove_{station_idx}",
            ):
                st.session_state.valve_stations.remove(station_idx)
                st.rerun()

# ----------------------------------------------------------------------------------------

col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    with st.container(border=True):
        st.subheader("Manifold Options")
        
        series = st.selectbox("Series", ("3", "5", "7"), key="series")
        
        si_unit_symbols = YAML_DATA['si_unit_symbols'].keys()
        si_unit = st.selectbox("SI Unit", si_unit_symbols, key="si_unit")
        
        endplate_type_symbols = YAML_DATA['endplate_type_symbols'].keys()
        endplate_type = st.selectbox("Endplate Type", endplate_type_symbols, key="endplate_type")
        
        io_unit_symbols = YAML_DATA['io_unit_symbols'].keys()
        io_unit_1 = st.selectbox("I/O Unit 1", [""] + list(io_unit_symbols), key="io_unit_1")
        io_unit_2 = st.selectbox("I/O Unit 2", [""] + list(io_unit_symbols), key="io_unit_2")
        io_unit_3 = st.selectbox("I/O Unit 3", [""] + list(io_unit_symbols), key="io_unit_3")
        io_unit_4 = st.selectbox("I/O Unit 4", [""] + list(io_unit_symbols), key="io_unit_4")

        lt_surge_volt_sup_and_coil_type_symbols = YAML_DATA['lt_surge_volt_sup_and_coil_type_symbols'].keys()
        lt_surge_volt_sup_and_coil_type = st.selectbox("Light/Surge Volt/Sup and Coil Type", lt_surge_volt_sup_and_coil_type_symbols, key = "lt_surge_volt_sup_and_coil_type")
        
        man_override_symbols = YAML_DATA['man_override_symbols'].keys()
        man_override = st.selectbox("Manual Override", man_override_symbols, key="man_override")
        
        sup_exh_porting_dir_and_cover_assy_symbols = YAML_DATA['sup_exh_porting_dir_and_cover_assy_symbols'].keys()
        sup_exh_porting_dir_and_cover_assy = st.selectbox("Sup/Exh Porting Direction and Cover Assy", 
                                                            sup_exh_porting_dir_and_cover_assy_symbols,
                                                            key="sup_exh_porting_dir_and_cover_assy")
        
        ab_port_size_symbols = YAML_DATA['ab_port_size_symbols'].keys()
        ab_port_size_assy = st.selectbox("A/B Port Size", ab_port_size_symbols, key="ab_port_size")
        
        mounting_and_nameplate_symbols = YAML_DATA['mounting_and_nameplate_symbols'].keys()
        mounting_and_nameplate = st.selectbox("Mounting and Nameplate", mounting_and_nameplate_symbols, key="mounting_and_nameplate")
        
# ---------------------------------------------------------------------------------------- 
with col2:
    #with st.container(border=True):

        #st.subheader("Configure Valve Options")

        for station_idx in st.session_state.valve_stations:
            render_valve_station(station_idx)

        if st.button(
            "+ Add Valve Station",
            use_container_width=True,
        ):
            new_idx = max(st.session_state.valve_stations) + 1
            st.session_state.valve_stations.append(new_idx)
            st.rerun()
            

# generating the valve callout string
# -- created by taking all quantities and valve symbols for each valve station block and joining together
valve_station_callouts = []

for station_idx in st.session_state.valve_stations:

    qty = st.session_state.get(f"qty_{station_idx}", 1)
    symbol = st.session_state.get(f"valve_symbol_{station_idx}", "")

    if symbol:

        qty_str = "" if qty == 1 else str(qty)

        valve_station_callouts.append(
            f"{qty_str}{symbol}"
        )

valve_station_string = "".join(valve_station_callouts)
                
# ----------------------------------------------------------------------------------------
with col3:
    with st.container(border=True):
        st.subheader("Output")

        part_number = (
            f"SY{st.session_state.series}6-"
            f"{st.session_state.si_unit}"
            f"{st.session_state.endplate_type}"
            f"{st.session_state.io_unit_1}"
            f"{st.session_state.io_unit_2}"
            f"{st.session_state.io_unit_3}"
            f"{st.session_state.io_unit_4}-"
            f"{st.session_state.lt_surge_volt_sup_and_coil_type}"
            f"{st.session_state.man_override}-{valve_station_string}-"
            f"{st.session_state.sup_exh_porting_dir_and_cover_assy}"
            f"{st.session_state.ab_port_size}"
            f"{st.session_state.mounting_and_nameplate}"
        )

        st.write(f"{part_number}")
        
        
        @st.dialog("Configuration Results", width="large")
        def show_results(model):
            
            maincol1, maincol2, maincol3 = st.columns([1,1,5])
            
            with maincol1:
                bom_download_button = st.button("Download Config File", width="stretch")
                if bom_download_button:
                    model.bom_output_to_pdf()
            
            subcol1, subcol2 = st.columns([1.5,2])

            with subcol1:
                st.subheader("Configuration")
                st.dataframe(
                    model.get_tokens_df(full_report=False),
                    width='stretch'
                )

            with subcol2:
                st.subheader("Bill of Materials")
                st.dataframe(
                    model.bom(),
                    width='stretch'
                )

        create_button = st.button('configure', width="stretch")


        if create_button:

            model, success, e = run_main_model(part_number.strip())

            if success:
                show_results(model)

            else:

                if isinstance(e, ValidationError):

                    messages = [
                        err["msg"].removeprefix("Value error, ")
                        for err in e.errors()
                    ]

                    st.error(
                        "Validation failed:\n\n" +
                        "\n".join(f"• {msg}" for msg in messages)
                    )

                elif e is not None:
                    st.error(str(e))

