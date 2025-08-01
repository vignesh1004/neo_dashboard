#
import streamlit as st
from database.db import run_query
import requests

def show():
    
    st.subheader("🌍 Welcome to the Asteroid Tracker Dashboard")
    st.markdown("Use the sidebar to filter or explore queries. Below is a quick snapshot of asteroid data from 2024–2025.")

    # ------------------------
    # Section 1: Summary Metrics
    # ------------------------
    total_count = run_query("SELECT COUNT(*) AS count FROM asteroids")["count"].iloc[0]
    hazardous_count = run_query("SELECT COUNT(*) AS count FROM asteroids WHERE is_potentially_hazardous_asteroid = 1")["count"].iloc[0]
    close_approach_count = run_query("SELECT COUNT(*) AS count FROM close_approach")["count"].iloc[0]

    # Fastest asteroid query
    fastest_info = run_query("""
        SELECT a.name, c.relative_velocity_kmph, c.neo_reference_id
        FROM close_approach c
        JOIN asteroids a ON a.id = c.neo_reference_id
        ORDER BY c.relative_velocity_kmph DESC
        LIMIT 1
    """)
    if not fastest_info.empty:
        fastest_speed = fastest_info['relative_velocity_kmph'].iloc[0]
        fastest_name = fastest_info['name'].iloc[0]
        fastest_id = fastest_info['neo_reference_id'].iloc[0]
    else:
        fastest_speed = 0
        fastest_name = "Unknown"
        fastest_id = None

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("☄️ Total Asteroids", f"{total_count:,}")
    col2.metric("⚠️ Hazardous", f"{hazardous_count:,}")
    col3.metric("🛰️ Close Approaches", f"{close_approach_count:,}")
    col4.metric("💨 Fastest Speed", f"{fastest_speed:,.0f} km/h")

    st.markdown("---")

    # ------------------------
    # Section: Fastest Asteroid + NASA Picture (Better Layout)
    # ------------------------
    
    # Fetch NASA image + explanation
    def get_nasa_fact():
        api_key = "xaci6V0IebvuL0bGLERVBv4WtU5aEsCXKdvWw2qb"  # Replace with your actual NASA API key
        try:
            response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={api_key}")
            if response.status_code == 200:
                data = response.json()
                return data.get("title"), data.get("explanation"), data.get("url")
        except:
            pass
        return None, "Could not retrieve today's NASA fact.", None

    title, explanation, image_url = get_nasa_fact()

    col1, col2 = st.columns([2, 2])
    with col1:
        st.markdown("### Fastest Asteroid details")

    with col2:
        st.markdown(f"""
                        <p style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                        font-size: 25px;'>
                        🌌 NASA Image of the Day: <strong style="color: #0B3D91; font-weight:bold">{title}</strong>
                        </p>
                        """, unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2 = st.columns([2, 2])
        
    with col1:
    # Top: Asteroid Details
        if fastest_id is not None:
            st.markdown(f"#### ☄️ Asteroid: **{fastest_name}**")
            st.write(f"**Speed:** {fastest_speed:,.0f} km/h")

            approach_dates_df = run_query("""
                SELECT close_approach_date
                FROM close_approach
                WHERE neo_reference_id = %s
                ORDER BY close_approach_date
            """, (int(fastest_id),))

            # Format date(s) into comma-separated string
            dates = ', '.join(approach_dates_df['close_approach_date'].astype(str).tolist())
            st.write(f"**Number of Approaches:** {len(approach_dates_df)}")
            st.write(f"**Approach Dates:** {dates}")

        st.markdown("---")
        
        # Bottom: NASA Explanation
        if explanation:
            st.markdown(f"""
                        <p style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                        font-size: 25px;'>
                        About -  <strong style="color: #0B3D91; font-weight:bold">{title}</strong>
                        </p>
                        """, unsafe_allow_html=True)
            st.write(explanation)

    with col2:
        # Only image, sized to match full height
        
        if image_url:
            st.image(image_url, caption=title, use_container_width=True)
   
# home page end