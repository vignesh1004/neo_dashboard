#
import streamlit as st
from datetime import date
from database.db import run_query

def show():
    st.subheader("🔎 Filter Criteria")

    # Row 1
    col1, col2, col3 = st.columns(3)
    with col1:
        magnitude = st.slider("Absolute Magnitude (≤)", min_value=13.82, max_value=33.0, step=0.1, value=20.0)
    with col2:
        velocity = st.slider("Relative Velocity (km/h) (≤)", min_value=1418.22, max_value=200000.0,step=100.0, value=90000.0)
    with col3:
        start_date = st.date_input("Start Date", value=date(2024, 1, 1))

    # Row 2
    col4, col5, col6 = st.columns(3)
    with col4:
        min_diameter = st.slider("Min Estimated Diameter (km) (≤)", min_value=0.000799015, max_value=4.57673, step=0.01, value=2.0)
    with col5:
        au = st.slider("Astronomical Unit (≤)", min_value=0.0000516453,max_value=0.499952, step=0.01, value=0.30)
    with col6:
        end_date = st.date_input("End Date", value=date(2025, 12, 31))

    # Row 3
    col7, col8 = st.columns([1,1])
    with col7:
        max_diameter = st.slider("Max Estimated Diameter (km) (≤)", min_value=0.00178665, max_value=10.2339, step=0.01, value=5.0)
    with col8:
        hazard_option = st.selectbox("Potentially Hazardous", ["All", "Yes", "No"])


    # Filter button 
    if st.button("Apply Filters"):
        # SQL query based on filters
        query = """
            SELECT a.name, a.absolute_magnitude_h, a.estimated_diameter_min_km,
                   a.estimated_diameter_max_km, a.is_potentially_hazardous_asteroid,
                   c.relative_velocity_kmph, c.close_approach_date, c.astronomical
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.absolute_magnitude_h <= %s
            AND a.estimated_diameter_min_km <= %s
            AND a.estimated_diameter_max_km <= %s
            AND c.relative_velocity_kmph <= %s
            AND c.astronomical <= %s
            AND c.close_approach_date BETWEEN %s AND %s
        """

        params = [magnitude, min_diameter, max_diameter, velocity, au, start_date, end_date]

        if hazard_option == "Yes":
            query += " AND a.is_potentially_hazardous_asteroid = 1"
        elif hazard_option == "No":
            query += " AND a.is_potentially_hazardous_asteroid = 0"
        
        # st.write("🧪 SQL Query:", query)
        # st.write("🧾 Parameters:", params)

        df_filtered = run_query(query, params)

        
         # Count summary line
        st.markdown(f"### 📄 Filtered Asteroids - Total matching records :  **{len(df_filtered)}**")
       

        if not df_filtered.empty:
            st.dataframe(df_filtered)
        else:
            st.warning("⚠️ No data matched the selected filters. You're using a very strict combination. Try relaxing one or more filters.")


    else:
        st.markdown("### Click the 'Apply Filters' button to see results")
    

#filter page ends