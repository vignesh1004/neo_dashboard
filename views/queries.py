# handles queries page 

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express 
import plotly.graph_objects 
import matplotlib as mpl
import matplotlib.pyplot as plt

from database.db import run_query



def show():
    st.subheader("📊 Queries : Select questions")

    questions = [
        "1.Count how many times each asteroid has approached Earth",
        "2.Average velocity of each asteroid over multiple approaches",
        "3.List top 10 fastest asteroids",
        "4.Find potentially hazardous asteroids that have approached Earth more than 3 times",
        "5.Find the month with the most asteroid approaches",
        "6.Get the asteroid with the fastest ever approach speed",
        "7.Sort asteroids by maximum estimated diameter (descending)",
        "8.An asteroid whose closest approach is getting nearer over time",
        "9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth",
        "10.List names of asteroids that approached Earth with velocity > 50,000 km/h",
        "11.Count how many approaches happened per month",
        "12.Find asteroid with the highest brightness (lowest magnitude value)",
        "13.Get number of hazardous vs non-hazardous asteroids",
        "14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance",
        "15.Find asteroids that came within 0.05 AU (astronomical distance)"
    ]

    selected_question = st.selectbox("Choose a question", questions)

    # Placeholder for dynamic query logic
    st.write(f"Selected Question: **{selected_question}**")

    # 1st question
    if selected_question == "1.Count how many times each asteroid has approached Earth":

        # -----------------------------
        # Query 1: Detail per asteroid
        # -----------------------------
        query1 = """
        SELECT a.name AS asteroid_name, COUNT(*) AS approach_count
        FROM close_approach ca
        JOIN asteroids a ON ca.neo_reference_id = a.id
        WHERE ca.orbiting_body = 'Earth'
        GROUP BY ca.neo_reference_id, a.name 
        HAVING COUNT(*) >= 2
        ORDER BY approach_count DESC;
        """
        df_detail = run_query(query1)

        # -----------------------------
        # Query 2: Group by approach count
        # -----------------------------
        query2 = """
        SELECT 
            approach_count,
            COUNT(*) AS total_asteroids
        FROM (
            SELECT 
                neo_reference_id,
                COUNT(*) AS approach_count
            FROM close_approach
            WHERE orbiting_body = 'Earth'
            GROUP BY neo_reference_id
            HAVING COUNT(*) >= 2
        ) AS sub
        GROUP BY approach_count
        ORDER BY approach_count;
        """
        df_summary = run_query(query2)

        # -----------------------------
        # Layout: 2 Columns
        # -----------------------------
        col1, col2 = st.columns([2, 2])
        
        # -----------------------------
        # Left: Asteroid Detail Table
        # -----------------------------
        with col1:
            st.markdown("### 📋 Asteroids that Approached Earth (≥ 2 Times)")
            st.dataframe(df_detail, use_container_width=True, height=600)

        # -----------------------------
        # Right: Pie Chart Summary
        # -----------------------------
        with col2:
            # st.markdown("### 🥧 Asteroid Approach Frequency Summary")

            total_asteroids = df_summary["total_asteroids"].sum()
            st.markdown(
            f"""
            <div style='
                background-color: #f0f0f0;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            '>
                <h3 style='margin: 0;'>Totally: 
                    <span style='color: #FF5733; font-weight: bold; font-size: 38px;'>{total_asteroids}</span> approached more than 2 times
                </h3>
            </div>
            """,
            unsafe_allow_html=True
            )
            #  pie chart using Plotly Express
            import plotly.express as px
            fig =px.pie(
                df_summary,
                names="approach_count",
                values="total_asteroids",
                color_discrete_sequence=px.colors.qualitative.Safe,
                hole=0.4  # donut-style
            )

            # Remove percentage display
            fig.update_traces(textinfo="label+value", textfont_size=14)

            fig.update_layout(
                width=600,
                height=600,
                showlegend=False,
                margin=dict(t=30, b=30, l=0, r=0)
            )

            st.plotly_chart(fig, use_container_width=True)

    #  2nd question
    elif selected_question == "2.Average velocity of each asteroid over multiple approaches":
        
        # -----------------------------
        # SQL Query
        # -----------------------------
        query = """
        WITH filtered AS (
            SELECT 
                a.name AS Asteroid_Name,
                ROUND(AVG(ca.relative_velocity_kmph), 2) AS Average_Velocity_Kmph,
                COUNT(*) AS Total_Approaches
            FROM 
                asteroids a
            JOIN 
                close_approach ca ON a.id = ca.neo_reference_id
            WHERE 
                ca.orbiting_body = 'Earth'
            GROUP BY 
                a.id, a.name
            HAVING 
                COUNT(*) >= 2
        )
        SELECT * FROM filtered
        ORDER BY Average_Velocity_Kmph DESC
        LIMIT 30
        """
        df = run_query(query)  # Your function to run SQL

        # -----------------------------
        # Color mapping using matplotlib colormap
        # -----------------------------
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        norm = mpl.colors.Normalize(vmin=df["Average_Velocity_Kmph"].min(), vmax=df["Average_Velocity_Kmph"].max())
        cmap = mpl.cm.get_cmap("coolwarm")
        df["color"] = df["Average_Velocity_Kmph"].apply(lambda x: mpl.colors.to_hex(cmap(norm(x))))

        # -----------------------------
        # Detect dark colors and apply font color
        # -----------------------------
        def is_dark_color(hex_color):
            hex_color = hex_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness < 128

        def color_cell(val):
            row_color = df.loc[df["Average_Velocity_Kmph"] == val, "color"].values[0]
            font_color = "white" if is_dark_color(row_color) else "black"
            return f"background-color: {row_color}; color: {font_color}"

        # -----------------------------
        # Layout
        # -----------------------------
        col1, col2 = st.columns([1.2, 2])

        with col1:
            st.markdown("### List - Average Velocity of each Asteroids")
            styled_df = df[["Asteroid_Name", "Average_Velocity_Kmph", "Total_Approaches"]].style.applymap(
                color_cell, subset=["Average_Velocity_Kmph"]
            )
            st.dataframe(styled_df, use_container_width=True, height=550)

        with col2:
            st.markdown("<h4 style='text-align: center;'>Average Velocity - Bar Chart</h4>", unsafe_allow_html=True)
            import plotly.express as px
            fig = px.bar(
                df,
                x="Average_Velocity_Kmph",
                y="Asteroid_Name",
                color="Average_Velocity_Kmph",
                color_continuous_scale="thermal",
                orientation="h",
                labels={"Average_Velocity_Kmph": "Avg Velocity (km/h)", "Asteroid_Name": "Asteroid"},
                height=600
            )

            # Center the title above the chart
            fig.update_layout(
                yaxis=dict(categoryorder="total ascending"),
                coloraxis_showscale=False
            )

            st.plotly_chart(fig, use_container_width=True)

    # 3rd question
    elif selected_question == "3.List top 10 fastest asteroids":
        
        # --------------------------
        # SQL Query
        # --------------------------
        query = """
            SELECT 
                a.name AS asteroid_name,
                MAX(ca.relative_velocity_kmph) AS max_velocity
            FROM 
                asteroids a
            JOIN 
                close_approach ca
                ON a.id = ca.neo_reference_id
            WHERE 
                ca.orbiting_body = 'Earth'
            GROUP BY 
                a.name
            ORDER BY 
                max_velocity DESC
            LIMIT 10
        """
        df = run_query(query)

        # --------------------------
        # Assign colors automatically using matplotlib colormap
        # --------------------------
        import matplotlib.pyplot as plt
        import matplotlib

        norm = matplotlib.colors.Normalize(vmin=df["max_velocity"].min(), vmax=df["max_velocity"].max())
        cmap = plt.get_cmap("Reds")  # You can change to 'plasma', 'viridis', etc.
        df["color"] = df["max_velocity"].apply(lambda x: matplotlib.colors.to_hex(cmap(norm(x))))

        # --------------------------
        # Define color styling function
        # --------------------------
        def is_dark_color(hex_color):
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness < 128

        def style_velocity_column(val):
            color = df.loc[df["max_velocity"] == val, "color"].values[0]
            font_color = "white" if is_dark_color(color) else "black"
            return f"background-color: {color}; color: {font_color};"

        # --------------------------
        # Layout: DataFrame (Left) + Pie Chart (Right)
        # --------------------------
        col1, col2 = st.columns([2, 2])

        with col1:
            st.markdown("#### List - Fastest Asteroids")

            styled_df = df[["asteroid_name", "max_velocity"]].style.applymap(
                style_velocity_column, subset=["max_velocity"]
            )
            st.dataframe(styled_df, use_container_width=True, height=500)

        with col2:
            st.markdown("<h4 style='text-align: center;'>🥧 Velocity Share</h4>", unsafe_allow_html=True)


            import plotly.graph_objects as go

            labels = df['asteroid_name']
            values = df['max_velocity']
            colors = df['color']
            font_colors = ['white' if is_dark_color(c) else 'black' for c in colors]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                textinfo='label',
                insidetextfont=dict(color=font_colors),
                showlegend=False
            )])

            fig.update_layout(
                width=650,
                height=650,
                margin=dict(l=100, r=50, t=0, b=50)
            )

            st.plotly_chart(fig, use_container_width=False)

    # 4th question
    elif selected_question == "4.Find potentially hazardous asteroids that have approached Earth more than 3 times":

        # ----------------------------
        # Get hazardous asteroids with 3 or more approaches and their closest info
        # ----------------------------
        query_4x_all = """
        WITH ranked AS (
            SELECT 
                ca.neo_reference_id, 
                a.name AS asteroid_name,
                ca.close_approach_date, 
                ca.miss_distance_km, 
                ca.relative_velocity_kmph,
                COUNT(*) OVER (PARTITION BY ca.neo_reference_id) AS total_approaches,
                ROW_NUMBER() OVER (PARTITION BY ca.neo_reference_id ORDER BY ca.miss_distance_km ASC) AS rn
            FROM close_approach ca
            JOIN asteroids a ON ca.neo_reference_id = a.id
            WHERE ca.orbiting_body = 'Earth' 
            AND a.is_potentially_hazardous_asteroid = 1
        )
        SELECT 
            asteroid_name,
            neo_reference_id,
            total_approaches,
            miss_distance_km AS closest_distance_km,
            close_approach_date AS closest_date,
            relative_velocity_kmph AS velocity_at_closest
        FROM ranked
        WHERE rn = 1 AND total_approaches >= 4
        LIMIT 10;
        """
        df_top = run_query(query_4x_all)

        # ----------------------------
        # Get count of other hazardous asteroids
        # ----------------------------
        query_counts = """
        SELECT approach_count, COUNT(*) AS total
        FROM (
            SELECT ca.neo_reference_id, COUNT(*) AS approach_count
            FROM close_approach ca
            JOIN asteroids a ON ca.neo_reference_id = a.id
            WHERE ca.orbiting_body = 'Earth' AND a.is_potentially_hazardous_asteroid = 1
            GROUP BY ca.neo_reference_id
        ) AS sub
        GROUP BY approach_count;
        """
        df_counts = run_query(query_counts)

        # ----------------------------------
        # UI Rendering
        # ----------------------------------
        # st.markdown("""<h3 style='text-align: center;'>🚀 Hazardous Asteroids Approached more than 3 times </h3>""", unsafe_allow_html=True)

        if not df_top.empty:
            for idx, row in df_top.iterrows():
                st.markdown(f"""<h4 style='text-align: center; '>Hazardous Asteroids Approached more than 3 times is - <span style='color: brown; font-weight: bold;font-size:30px;'>{row['asteroid_name']}</span></h4>""", unsafe_allow_html=True)
                st.dataframe(
                    pd.DataFrame({
                        "Asteroid Name": [row["asteroid_name"]],
                        "Total Approaches": [row["total_approaches"]],
                        "Closest Date": [row["closest_date"]],
                        "Closest Distance (km)": [row["closest_distance_km"]],
                        "Velocity at Closest (km/h)": [row["velocity_at_closest"]]
                    }),
                    use_container_width=True,
                    height=80,
                )

        # ----------------------------
        # Row with 3 info boxes
        # ----------------------------
        st.markdown("""<hr><h4 style='text-align: center;'>Other Hazardous Asteroids by Approach Count</h4>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        value_map = dict(zip(df_counts['approach_count'], df_counts['total']))

        with col1:
            st.markdown(f"""
            <div style='border:2px solid #FF7F50; padding:20px; border-radius:10px; background-color:#FFF4E0; text-align:center;'>
                <h5 style='color:black;'>Hazardous Asteroids: <span style='color: crimson; font-weight: bold;font-size:30px;'>{value_map.get(3, 0)}</span></h5>
                <h5 style='color:#FF4500;'>Approached: 3 times</h5>
            </div>""", unsafe_allow_html=True)


        with col2:
            st.markdown(f"""
            <div style='border:2px solid #FFD700; padding:20px; border-radius:10px; background-color:#FFFFE0; text-align:center;'>
                <h5 style='color:black;'>Hazardous Asteroids: <span style='color: crimson; font-weight: bold;font-size:30px;'>{value_map.get(2, 0)}</span></h5>
                <h5 style='color:#DAA520;'>Approached: 2 times</h5>
            </div>""", unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style='border:2px solid #90EE90; padding:20px; border-radius:10px; background-color:#F0FFF0; text-align:center;'>
                <h5 style='color:black;'>Hazardous Asteroids: <span style='color: crimson; font-weight: bold;font-size:30px;'>{value_map.get(1, 0)}</span></h5>
                <h5 style='color:#228B22;'>Approached: 1 time</h5>
            </div>""", unsafe_allow_html=True)

    # 5th question
    elif selected_question == "5.Find the month with the most asteroid approaches":
        # ---- SQL Queries ----
        query_2024 = """
        SELECT 
            MONTHNAME(close_approach_date) AS month,
            COUNT(*) AS approach_count
        FROM close_approach
        WHERE YEAR(close_approach_date) = 2024
        GROUP BY MONTHNAME(close_approach_date)
        ORDER BY approach_count DESC
        LIMIT 6;
        """

        query_2025 = """
        SELECT 
            MONTHNAME(close_approach_date) AS month,
            COUNT(*) AS approach_count
        FROM close_approach
        WHERE YEAR(close_approach_date) = 2025
        GROUP BY MONTHNAME(close_approach_date)
        ORDER BY approach_count DESC
        LIMIT 6;
        """

        # ---- Fetch Data ----
        df_2024 = run_query(query_2024)
        df_2025 = run_query(query_2025)

        top_2024 = df_2024.iloc[0]
        top_2025 = df_2025.iloc[0]

        # ---- Layout Columns ----
        col1, col2 = st.columns(2)

        # ----------------- Column 1: 2024 -----------------
        with col1:
            st.markdown("## 📅 Year: 2024")
            
            st.markdown(f"""
            <div style='background-color:#003366;padding:16px;border-radius:10px;color:white;margin-bottom:20px'>
                <b>📊 Month with Highest Approaches:</b> {top_2024['month']}<br>
                <b>🪐 Total Approaches:</b> {top_2024['approach_count']}
            </div>
            """, unsafe_allow_html=True)

            # Dataframe
            styled_df_2024 = df_2024.style.background_gradient(
                subset='approach_count', cmap='Blues'
            )
            st.dataframe(styled_df_2024, use_container_width=True)

        # ----------------- Column 2: 2025 -----------------
        with col2:
            st.markdown("## 📅 Year: 2025")
            
            st.markdown(f"""
            <div style='background-color:#660000;padding:16px;border-radius:10px;color:white;margin-bottom:20px'>
                <b>📊 Month with Highest Approaches:</b> {top_2025['month']}<br>
                <b>🪐 Total Approaches:</b> {top_2025['approach_count']}
            </div>
            """, unsafe_allow_html=True)

            # Dataframe
            styled_df_2025 = df_2025.style.background_gradient(
                subset='approach_count', cmap='Reds'
            )
            st.dataframe(styled_df_2025, use_container_width=True)

    # 6th question
    elif selected_question == "6.Get the asteroid with the fastest ever approach speed":
        # st.markdown("<h2 style='text-align: center;'>Get the asteroid with the fastest ever approach speed</h2>", unsafe_allow_html=True)

        # Create two columns for layout
        col1, col2 = st.columns([2, 3])

        # Hazard filter dropdown
        with col1:
            hazard_filter = st.selectbox(
                "Filter by Hazardous Status:",
                options=["All", "Only Hazardous", "Only Non-Hazardous"]
            )

        # Build dynamic WHERE clause
        where_clause = ""
        if hazard_filter == "Only Hazardous":
            where_clause = "WHERE a.is_potentially_hazardous_asteroid = 1"
        elif hazard_filter == "Only Non-Hazardous":
            where_clause = "WHERE a.is_potentially_hazardous_asteroid = 0"

        # SQL Query Based on Filter
        query = f"""
            SELECT 
                a.name AS asteroid_name,
                c.relative_velocity_kmph,
                c.close_approach_date,
                a.is_potentially_hazardous_asteroid
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            {where_clause}
            ORDER BY c.relative_velocity_kmph DESC
            LIMIT 20;
        """

        df = run_query(query)

        # Display Fastest Asteroid Details and Table
        if not df.empty:
            fastest_asteroid = df.iloc[0]
            hazard_status = "Yes" if fastest_asteroid['is_potentially_hazardous_asteroid'] else "No"

            # Color theme based on hazard status
            if hazard_status == "Yes":
                hazard_color = "#D81F0B"  # Red
                cmap_name = "Reds"
            else:
                hazard_color = "#75B909"  # Green
                cmap_name = "Greens"

            with col1:
                st.markdown("### Fastest Asteroid ", unsafe_allow_html=True)

                st.markdown(
                    f"<b>Name:</b> <span style='color:{hazard_color}; font-size:20px; font-weight:bold'>{fastest_asteroid['asteroid_name']}</span>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<b>Speed:</b> <span style='color:{hazard_color}; font-size:20px;font-weight:bold'>{fastest_asteroid['relative_velocity_kmph']:,} km/h</span>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<b>Hazardous Status:</b> <span style='color:{hazard_color}; font-size:20px;font-weight:bold'>{hazard_status}</span>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<b>Close Approach Date:</b> <span style='color:{hazard_color}; font-size:20px;font-weight:bold'>{fastest_asteroid['close_approach_date']}</span>",
                    unsafe_allow_html=True
                )

                st.markdown("### 📄 List - Fastest Asteroids")

                styled_df = df.style.background_gradient(
                    subset=["relative_velocity_kmph"], cmap=cmap_name
                ).format({
                    "relative_velocity_kmph": "{:,.2f}",
                    "close_approach_date": lambda d: d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else d
                })

                st.dataframe(styled_df, use_container_width=True)

            # Bar Chart in col2
            with col2:
                import matplotlib.pyplot as plt
                st.markdown("### 📊 Asteroids with the fastest ever approach speed")
                chart_df = df.sort_values("relative_velocity_kmph", ascending=True)
                fig, ax = plt.subplots(figsize=(10, 8))

                colors = plt.get_cmap(cmap_name)(np.linspace(0.4, 0.9, len(chart_df)))
                ax.barh(
                    y=chart_df["asteroid_name"],
                    width=chart_df["relative_velocity_kmph"],
                    color=colors
                )
                ax.set_xlabel("Speed (km/h)")
                ax.set_ylabel("Asteroid")
                ax.set_title("Top 20 Fastest Asteroids")
                plt.tight_layout()

                st.pyplot(fig)

        else:
            st.warning("No data found for the selected filter.")

    #7th question
    elif selected_question == "7.Sort asteroids by maximum estimated diameter (descending)":
        
        # Layout with two columns
        col1, col2 = st.columns([2, 3])

        with col1:
            # Dropdown filter
            hazard_filter = st.selectbox(
                "Filter by Hazardous Status:",
                options=["All", "Only Hazardous", "Only Non-Hazardous"]
            )

            # Set WHERE clause and color/cmap based on filter
            where_clause = ""
            title_color = "#1f77b4"  # default blue
            cmap = "Blues"

            if hazard_filter == "Only Hazardous":
                where_clause = "WHERE is_potentially_hazardous_asteroid = 1"
                title_color = "#D81F0B"  # red
                cmap = "Reds"
            elif hazard_filter == "Only Non-Hazardous":
                where_clause = "WHERE is_potentially_hazardous_asteroid = 0"
                title_color = "#555555"  # grey
                cmap = "Greys"

            # SQL query for top 20 by diameter
            query = f"""
                SELECT 
                    name AS asteroid_name,
                    estimated_diameter_max_km,
                    estimated_diameter_min_km,
                    is_potentially_hazardous_asteroid
                FROM asteroids
                {where_clause}
                ORDER BY estimated_diameter_max_km DESC
                LIMIT 20;
            """

            df = run_query(query)

            # Show details of largest asteroid
            if not df.empty:
                largest = df.iloc[0]
                hazard_status = "Yes" if largest['is_potentially_hazardous_asteroid'] else "No"

                st.markdown("### Largest Diameter Asteroid")
                st.markdown(
                    f"<b>Name:</b> <span style='color:{title_color}; font-size:20px; font-weight:bold'>{largest['asteroid_name']}</span>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<b>Estimated Diameter Max:</b> <span style='color:{title_color}; font-size:20px; font-weight:bold'>{largest['estimated_diameter_max_km']:.3f} km</span>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<b>Estimated Diameter Min:</b> <span style='color:{title_color}; font-size:20px; font-weight:bold'>{largest['estimated_diameter_min_km']:.3f} km</span>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<b>Hazardous:</b> <span style='color:{title_color}; font-size:20px; font-weight:bold'>{hazard_status}</span>",
                    unsafe_allow_html=True
                )

                # Styled DataFrame
                st.markdown("### 📋 List - Largest Diameter Asteroids")
                styled_df = df.style.background_gradient(
                    subset=["estimated_diameter_max_km"], cmap=cmap
                ).format({
                    "estimated_diameter_max_km": "{:.3f}",
                    "estimated_diameter_min_km": "{:.3f}"
                })

                st.dataframe(styled_df, use_container_width=True)

            else:
                st.warning("No asteroids found for the selected filter.")

        # Bar chart in col2
        with col2:
            st.markdown("### 📊 Asteroids by Maximum Estimated Diameter")
            import matplotlib.pyplot as plt
            if not df.empty:
                sorted_df = df.sort_values("estimated_diameter_max_km", ascending=True)
                fig, ax = plt.subplots(figsize=(10, 8))

                colors = plt.get_cmap(cmap)(np.linspace(0.4, 0.9, len(sorted_df)))

                ax.barh(
                    y=sorted_df["asteroid_name"],
                    width=sorted_df["estimated_diameter_max_km"],
                    color=colors
                )
                ax.set_xlabel("Max Diameter (km)")
                ax.set_ylabel("Asteroid")
                ax.set_title("Top 20 Asteroids by Max Diameter")
                plt.tight_layout()
                st.pyplot(fig)
        
    #8th question -  need checks
    elif selected_question == "8.An asteroid whose closest approach is getting nearer over time":

        # Layout with two columns
        col1, col2 = st.columns([2, 3])

        with col1:
            hazard_filter = st.selectbox(
                "Filter by Hazardous Status:",
                options=["All", "Only Hazardous", "Only Non-Hazardous"]
            )

            if hazard_filter == "Only Hazardous":
                where_clause = "WHERE a.is_potentially_hazardous_asteroid = 1"
                title_color = "#D81F0B"
                cmap = "Reds_r"
            elif hazard_filter == "Only Non-Hazardous":
                where_clause = "WHERE a.is_potentially_hazardous_asteroid = 0"
                title_color = "#555555"
                cmap = "Greys_r"
            else:  # All
                where_clause = ""
                title_color = "#1f77b4"
                cmap = "Blues_r"

            query = f"""
                SELECT 
                    a.name,
                    a.is_potentially_hazardous_asteroid,
                    MIN(ca.close_approach_date) AS first_date,
                    MAX(ca.close_approach_date) AS last_date,
                    MIN(CASE WHEN ca.close_approach_date = (SELECT MIN(ca2.close_approach_date) FROM close_approach ca2 WHERE ca2.neo_reference_id = ca.neo_reference_id) THEN ca.miss_distance_km END) AS first_distance_km,
                    MAX(CASE WHEN ca.close_approach_date = (SELECT MAX(ca2.close_approach_date) FROM close_approach ca2 WHERE ca2.neo_reference_id = ca.neo_reference_id) THEN ca.miss_distance_km END) AS last_distance_km,
                    ROUND(
                        MIN(CASE WHEN ca.close_approach_date = (SELECT MIN(ca2.close_approach_date) FROM close_approach ca2 WHERE ca2.neo_reference_id = ca.neo_reference_id) THEN ca.miss_distance_km END)
                        -
                        MAX(CASE WHEN ca.close_approach_date = (SELECT MAX(ca2.close_approach_date) FROM close_approach ca2 WHERE ca2.neo_reference_id = ca.neo_reference_id) THEN ca.miss_distance_km END)
                    , 2) AS distance_diff_km
                    FROM asteroids a
                    JOIN close_approach ca ON a.id = ca.neo_reference_id
                    {where_clause}
                    GROUP BY a.name, a.is_potentially_hazardous_asteroid
                    HAVING COUNT(*) >= 2 AND distance_diff_km > 0
                    ORDER BY last_distance_km ASC
                
            """

            df = run_query(query)

            if not df.empty:
                top_row = df.iloc[0]
                hazard_status = "Yes" if top_row['is_potentially_hazardous_asteroid'] else "No"

                # --- Container for Asteroid Details ---
                st.markdown("### Closest Approaching Asteroid")

                # Define the HTML content for the box
                details_html = f"""
                <div style="border: 2px solid #666; border-radius: 10px; padding: 15px; font-size: 20px; line-height: 1.6;">
                    <b>Name:</b> <span style='color:{title_color}; font-weight:bold;'>{top_row['name']}</span><br>
                    <b>First Approach Date:</b> <span style='color:{title_color}; font-weight:bold;'>{top_row['first_date']}</span><br>
                    <b>Distance at First:</b> <span style='color:{title_color}; font-weight:bold;'>{top_row['first_distance_km']:.2f} km</span><br>
                    <b>Last Approach Date:</b> <span style='color:{title_color}; font-weight:bold;'>{top_row['last_date']}</span><br>
                    <b>Distance at Last:</b> <span style='color:{title_color}; font-weight:bold;'>{top_row['last_distance_km']:.2f} km</span><br>
                    <b>Distance Reduced By:</b> <span style='color:{title_color}; font-weight:bold;'>{top_row['distance_diff_km']:.2f} km</span><br>
                    <b>Hazardous:</b> <span style='color:{title_color}; font-weight:bold;'>{hazard_status}</span>
                </div>
                """

                # Render the HTML box in Streamlit
                st.markdown(details_html, unsafe_allow_html=True)

                st.markdown("### List - Getting Closer Asteroids")
                display_df = df[[
                    "name",
                    "first_date",
                    "first_distance_km",
                    "last_date",
                    "last_distance_km",
                    "distance_diff_km"
                ]]
                styled_df = display_df.head(30).style.background_gradient(
                    subset=["last_distance_km"], cmap=cmap,
                ).format({
                    "first_distance_km": "{:.2f}",
                    "last_distance_km": "{:.2f}",
                    "distance_diff_km": "{:.2f}"
                })

                st.dataframe(styled_df, use_container_width=True)
            else:
                st.warning("No asteroids found for the selected filter.")

        with col2:
            if not df.empty:
                chart_df = df.head(40)

                line_df = chart_df[["name", "first_distance_km", "last_distance_km"]].copy()
                melted_df = line_df.melt(
                    id_vars="name", 
                    value_vars=["first_distance_km", "last_distance_km"],
                    var_name="approach", 
                    value_name="distance_km"
                )

                import plotly.express as px
                fig2 = px.line(
                    melted_df,
                    x="name",
                    y="distance_km",
                    color="approach",
                    markers=True,
                    title="Approach Distance Change per Asteroid"
                )
                fig2.update_layout(
                    xaxis_title="Surface of Earth",
                    yaxis_title="Distance ( Km )",
                    title_x=0.35,
                    height=700,
                    legend_title="Approach"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
    #9th question
    elif selected_question == "9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth":
        st.subheader("Closest Approach per Asteroid")

        col1, col2 = st.columns([1, 2])

        with col1:
            hazard_filter = st.selectbox(
                "Filter by Hazardous Status:",
                options=["All", "Only Hazardous", "Only Non-Hazardous"]
            )

            where_clause = ""
            title_color = "#1f77b4"
            cmap = "Blues_r"

            if hazard_filter == "Only Hazardous":
                where_clause = "WHERE a.is_potentially_hazardous_asteroid = 1"
                title_color = "#D81F0B"
                cmap = "Reds_r"
            elif hazard_filter == "Only Non-Hazardous":
                where_clause = "WHERE a.is_potentially_hazardous_asteroid = 0"
                title_color = "#555555"
                cmap = "Greys_r"

            query = f"""
                SELECT 
                    a.name,
                    ca.close_approach_date,
                    ca.miss_distance_km
                FROM asteroids a
                JOIN close_approach ca ON a.id = ca.neo_reference_id
                {where_clause}
                AND ca.miss_distance_km IS NOT NULL
                ORDER BY ca.miss_distance_km ASC
                LIMIT 1000;
            """
            df = run_query(query)

            if not df.empty:
                df["miss_distance_km"] = df["miss_distance_km"].astype(float)
                df = df.sort_values("miss_distance_km").reset_index(drop=True)
                top_asteroid = df.iloc[0]

                st.markdown(f"""
                    <div style='background-color:{title_color};padding:10px;border-radius:10px'>
                        <h4 style='color:white'>Closest Asteroid: {top_asteroid["name"]}</h4>
                        <p style='color:white'>Miss Distance: {top_asteroid["miss_distance_km"]:.2f} km</p>
                        <p style='color:white'>Date: {top_asteroid["close_approach_date"]}</p>
                    </div>
                """, unsafe_allow_html=True)

        with col2:
            styled_df = df.head(20).style.background_gradient(
                cmap=cmap, subset=["miss_distance_km"]
            ).format({"miss_distance_km": "{:,.2f}"})

            st.dataframe(styled_df, use_container_width=True)
    
    #10th question
    elif selected_question == "10.List names of asteroids that approached Earth with velocity > 50,000 km/h":

        col1, col2 = st.columns([2, 3])

        with col1:
            hazard_filter = st.selectbox(
                "Filter by Hazardous Status:",
                options=["All", "Only Hazardous", "Only Non-Hazardous"]
            )

            where_clause = "WHERE ca.relative_velocity_kmph > 50000"
            title_color = "#1f77b4"   # Blue
            cmap = "Blues"

            if hazard_filter == "Only Hazardous":
                where_clause += " AND a.is_potentially_hazardous_asteroid = 1"
                title_color = "#D81F0B"  # Red
                cmap = "Reds"
            elif hazard_filter == "Only Non-Hazardous":
                where_clause += " AND a.is_potentially_hazardous_asteroid = 0"
                title_color = "#555555"  # Grey
                cmap = "Greys"

            query = f"""
                SELECT 
                    a.name,
                    ca.close_approach_date,
                    ca.relative_velocity_kmph
                FROM asteroids a
                JOIN close_approach ca ON a.id = ca.neo_reference_id
                {where_clause}
                ORDER BY ca.relative_velocity_kmph DESC
                LIMIT 1000;
            """
            df = run_query(query)

            if not df.empty:
                df["relative_velocity_kmph"] = df["relative_velocity_kmph"].astype(float)
                df = df.sort_values("relative_velocity_kmph", ascending=False).reset_index(drop=True)
                top_asteroid = df.iloc[0]

                st.markdown(f"""
                    <div style='background-color:{title_color};padding:10px;border-radius:10px'>
                        <h4 style='color:white'>Fastest Asteroid: {top_asteroid["name"]}</h4>
                        <p style='color:white'>Velocity: {top_asteroid["relative_velocity_kmph"]:.2f} km/h</p>
                        <p style='color:white'>Date: {top_asteroid["close_approach_date"]}</p>
                    </div>
                """, unsafe_allow_html=True)

                styled_df = df.head(20).style.background_gradient(
                    cmap=cmap, subset=["relative_velocity_kmph"]
                ).format({"relative_velocity_kmph": "{:,.2f}"})

                # divider line
                st.markdown("""<hr style="margin: 1rem 0; border: 1px solid #ccc;" />""", unsafe_allow_html=True)


                st.dataframe(styled_df, use_container_width=True)
            else:
                st.warning("No asteroids found with velocity greater than 50,000 km/h for this filter.")

        with col2:
            if not df.empty:
                import plotly.express as px
                chart_df = df.head(20)
                fig = px.bar(
                    chart_df,
                    x="name",
                    y="relative_velocity_kmph",
                    color="relative_velocity_kmph",
                    color_continuous_scale=cmap,
                    labels={"relative_velocity_kmph": "Velocity (km/h)", "name": "Asteroid"},
                    # title="Top 20 Fastest Asteroids"
                )
                fig.update_layout(
                    xaxis_tickangle=-45,
                    plot_bgcolor="white",
                    font_color="black"
                )

                # Adjust white text for dark bars
                fig.update_traces(
                    text=chart_df["relative_velocity_kmph"].round(1),
                    textposition="outside"
                )               
                st.plotly_chart(fig, use_container_width=True)

    #11th question
    elif selected_question == "11.Count how many approaches happened per month":
        col1, col2 = st.columns([1, 2])

        with col1:
            filter_option = st.selectbox(
                "Select Asteroid Type:",
                ("All", "Hazardous", "Non-Hazardous")
            )

            # Determine WHERE clause based on filter selection
            where_clause = ""
            if filter_option == "Hazardous":
                where_clause = "WHERE a.is_potentially_hazardous_asteroid = 1"
            elif filter_option == "Non-Hazardous":
                where_clause = "WHERE a.is_potentially_hazardous_asteroid = 0"

            # Final query with dynamic WHERE clause
            query = f"""
                SELECT 
                    YEAR(c.close_approach_date) AS approach_year,
                    MONTH(c.close_approach_date) AS approach_month,
                    COUNT(*) AS total_approaches
                FROM close_approach c
                JOIN asteroids a ON c.neo_reference_id = a.id
                {where_clause}
                GROUP BY approach_year, approach_month
                ORDER BY approach_year, approach_month;
            """

            df = run_query(query)

            # Month name mapping
            month_map = {
                1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
            }
            df["month_label"] = df["approach_month"].map(month_map)

            # Pivot for better display
            df_pivot = df.pivot(index="month_label", columns="approach_year", values="total_approaches").fillna(0)

            # Ensure correct month order
            df_pivot = df_pivot.reindex(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

            st.markdown("### Table - Monthly Approach Counts ")
            styled_table = df_pivot.style
            if 2024 in df_pivot.columns:
                styled_table = styled_table.background_gradient(cmap="Blues", subset=[2024])
            if 2025 in df_pivot.columns:
                styled_table = styled_table.background_gradient(cmap="Reds", subset=[2025])
            st.dataframe(styled_table)

        with col2:
            import plotly.express as px
            fig = px.line(
                df_pivot,
                x=df_pivot.index,
                y=[col for col in df_pivot.columns],
                markers=True,
                labels={"value": "Approach Count", "month_label": "Month"},
                title=f"Asteroid Approaches Per Month ( 2024 - 2025 )",
            )
            fig.update_traces(line=dict(width=3))
            if 2024 in df_pivot.columns:
                fig.update_traces(selector=dict(name=str(2024)), line=dict(color='blue'), name='2024')
            if 2025 in df_pivot.columns:
                fig.update_traces(selector=dict(name=str(2025)), line=dict(color='red'), name='2025')
            fig.update_layout(xaxis_title="Month", yaxis_title="Number of Approaches", height=400)
            st.plotly_chart(fig, use_container_width=True)

    #12th question
    elif selected_question == "12.Find asteroid with the highest brightness (lowest magnitude value)":

        # Single optimized query: top 10 brightest asteroids with all needed info
        query = """
            SELECT 
                a.id,
                a.name,
                a.absolute_magnitude_h AS brightness,
                a.is_potentially_hazardous_asteroid,
                COUNT(ca.close_approach_date) AS approach_count
            FROM asteroids a
            JOIN close_approach ca ON a.id = ca.neo_reference_id
            GROUP BY a.id, a.name, a.absolute_magnitude_h, a.is_potentially_hazardous_asteroid
            ORDER BY brightness ASC
            LIMIT 10;
        """
        result_df = run_query(query)

        # Layout
        col1, col2 = st.columns([1, 2])

        with col1:
            if not result_df.empty:
                row = result_df.iloc[0]  # Brightest asteroid
                st.markdown("### 🌟 Brightest Asteroid")
                st.markdown(f"""
                    <div style='border: 1px solid #ccc; padding: 10px; border-radius: 10px; background-color: #f9f9f9'>
                        <b>Name:</b> {row['name']}<br>
                        <b>ID:</b> {row['id']}<br>
                        <b>Brightness (Magnitude):</b> {row['brightness']}<br>
                        <b>Hazardous:</b> {"Yes" if row['is_potentially_hazardous_asteroid'] else "No"}<br>
                        <b>Total Approaches:</b> {row['approach_count']}
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("### List - Brightest Asteroids")
            display_df = result_df[["name", "brightness"]]  # only name and brightness in table
            styled_df = display_df.style.background_gradient(cmap='YlOrRd_r', subset=["brightness"])
            st.dataframe(styled_df, height=350)

        with col2:
            import plotly.express as px

            fig = px.bar(
                display_df,
                x='name',
                y='brightness',
                color='brightness',
                color_continuous_scale='YlOrRd_r',
                title="Brightness Bar Chart (Lower = Brighter)",
                labels={'brightness': 'Brightness (Magnitude)', 'name': 'Asteroid Name'},
            )
            fig.update_layout(
                xaxis_title="Asteroid Name",
                yaxis_title="Magnitude (Lower = Brighter)",
                coloraxis_showscale=False,
                height=450,
                title_x=0.35
            )
            st.plotly_chart(fig, use_container_width=True)

    #13th question
    elif selected_question == "13.Get number of hazardous vs non-hazardous asteroids":
        col1, col2 = st.columns(2)

        # ---------- Hazardous Asteroids ----------
        with col1:
            hazardous_query = """
                SELECT 
                    a.id,
                    a.name,
                    a.absolute_magnitude_h,
                    a.estimated_diameter_max_km,
                    a.is_potentially_hazardous_asteroid,
                    c.close_approach_date,
                    c.astronomical AS miss_distance_au
                FROM asteroids a
                JOIN close_approach c ON a.id = c.neo_reference_id
                WHERE 
                   is_potentially_hazardous_asteroid = 1 
                ORDER BY a.estimated_diameter_max_km DESC;
            """
            df_hazardous = run_query(hazardous_query)

            st.markdown(f"### Hazardous Asteroids : {len(df_hazardous)}")

            # Get top asteroid for detail box
            top_hazardous = df_hazardous.iloc[0]

            # Detail box
            st.markdown(f"""
            <div style="padding: 1em; border-radius: 10px; background: linear-gradient(135deg, #FFB347, #FF6347); color: black;">
                <h4>{top_hazardous['name']}</h4>
                <b>Hazardous:</b> {'Yes' if top_hazardous['is_potentially_hazardous_asteroid'] else 'No'}<br>
                <b>Miss Distance (AU):</b> {top_hazardous['miss_distance_au']}<br>
                <b>Magnitude:</b> {top_hazardous['absolute_magnitude_h']}<br>
                <b>Max Diameter (km):</b> {top_hazardous['estimated_diameter_max_km']}
            </div>
            """, unsafe_allow_html=True)

            # Color gradient styling (warm tones)
            styled_hazardous_df = df_hazardous.style.background_gradient(
                cmap="Oranges", subset=["estimated_diameter_max_km"]
            )

            st.markdown("#### List - Hazardous Asteroids")
            st.dataframe(styled_hazardous_df, use_container_width=True)

        # ---------- Non-Hazardous Asteroids ----------
        with col2:
            nonhaz_query = """
                SELECT 
                    a.id,
                    a.name,
                    a.absolute_magnitude_h,
                    a.estimated_diameter_max_km,
                    a.is_potentially_hazardous_asteroid,
                    c.close_approach_date,
                    c.astronomical AS miss_distance_au
                FROM asteroids a
                JOIN close_approach c ON a.id = c.neo_reference_id
                WHERE is_potentially_hazardous_asteroid = 0
                ORDER BY a.estimated_diameter_max_km DESC;
            """
            df_nonhazardous = run_query(nonhaz_query)
            st.markdown(f"### Non-Hazardous Asteroids : {len(df_nonhazardous)}")

            # Top non-hazardous
            top_nonhazardous = df_nonhazardous.iloc[0]

            # Detail box
            st.markdown(f"""
            <div style="padding: 1em; border-radius: 10px; background: linear-gradient(135deg, #b0b0b0, #eeeeee); color: black;">
                <h4>{top_nonhazardous['name']}</h4>
                <b>Hazardous:</b> {'Yes' if top_nonhazardous['is_potentially_hazardous_asteroid'] else 'No'}<br>
                <b>Miss Distance (AU):</b> {top_nonhazardous['miss_distance_au']}<br>
                <b>Magnitude:</b> {top_nonhazardous['absolute_magnitude_h']}<br>
                <b>Max Diameter (km):</b> {top_nonhazardous['estimated_diameter_max_km']}
            </div>
            """, unsafe_allow_html=True)

            # Grey tone for non-hazardous
            styled_nonhaz_df = df_nonhazardous.style.background_gradient(
                cmap="Greys", subset=["estimated_diameter_max_km"]
            )

            st.markdown("#### List - Non-Hazardous Asteroids")
            st.dataframe(styled_nonhaz_df, use_container_width=True)

    #14th question
    elif selected_question =="14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance":
        
        st.markdown("""
                    <div style='padding:12px 0 16px 0; font-size:16px; line-height:1.6;'>
                    One lunar distance (1 LD) is the average distance between the Earth and the Moon, <b>1 LD = 384,400 kilometers</b> (238,900 miles).<br>
                    It's a standard unit of measurement in astronomy, often used to express the distance to near-Earth objects, like asteroids.
                    </div>
                    """, unsafe_allow_html=True)

        # ---- SQL Query ----
        query = """
        SELECT 
            a.id,
            a.name,
            a.is_potentially_hazardous_asteroid,
            c.close_approach_date,
            c.miss_distance_lunar,
            c.miss_distance_km
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.miss_distance_lunar < 1
        ORDER BY c.miss_distance_lunar ASC
        LIMIT 100;
        """
        df = run_query(query)

        # ---- Top Asteroid ----
        # ---- Reorder and Rename Columns ----
        df = df.rename(columns={
            "name": "Asteroid Name",
            "miss_distance_lunar": "Lunar Distance (LD)",
            "miss_distance_km": "Distance km",
            "close_approach_date": "Close Approach Date",
            "is_potentially_hazardous_asteroid": "Hazardous"
        })

        df = df[["Asteroid Name", "Lunar Distance (LD)", "Distance km", "Close Approach Date", "Hazardous"]]

        top_asteroid = df.iloc[0]

        # ---- Layout Columns ----
        col1, col2 = st.columns([2, 3])

        # ---- Column 1 ----
        with col1:
            st.markdown("### Closest Asteroid")

            st.markdown(f"""
            <div style='background-color:grey;padding:16px;border-radius:10px;color:white;margin-bottom:20px'>
                <div style='font-size:20px;'><b> Name:</b> {top_asteroid['Asteroid Name']}</div>
                <div style='font-size:20px;'><b> Date:</b> {top_asteroid['Close Approach Date']}</div>
                <div style='font-size:20px;'><b> Distance - Lunar (LD):</b> {top_asteroid['Lunar Distance (LD)']}</div>
                <div style='font-size:20px;'><b> Distance - Kilometers:</b> {top_asteroid['Distance km']} Kilometers</div>
                <div style='font-size:20px;'><b> Hazardous:</b> {"Yes" if top_asteroid['Hazardous'] else "No"}</div>

            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### list - Asteroids < 1 LD")
            styled_df = df.style.background_gradient(
                subset=['Lunar Distance (LD)'],
                cmap='magma'  # Darker color for small values
            )
            st.dataframe(styled_df, use_container_width=True)

        # ---- Column 2 ----
        with col2:
            
            top20 = df.head(20)
            import plotly.express as px

            fig = px.bar(
                top20,
                x='Asteroid Name',
                y='Lunar Distance (LD)',
                color='Lunar Distance (LD)',
                color_continuous_scale='magma',  # Dark for low distance
                labels={'Lunar Distance (LD)': 'Lunar Distance (LD)', 'Asteroid Name': 'Asteroid Name'},
                title='Closest Approaches (< 1 LD)'
            )
            fig.update_layout(xaxis_tickangle=-90, title_x=0.35)
            st.plotly_chart(fig, use_container_width=True)

    #15 question
    elif selected_question =="15.Find asteroids that came within 0.05 AU (astronomical distance)":

        # AU Description
        st.markdown("""
            <div style='padding:12px 0 16px 0; font-size:16px; line-height:1.6;'>
            One astronomical unit (1 AU) is the average distance from the Earth to the Sun.<b>1 AU = 149.6 million kilometers</b> (or 93 million miles).<br>
            It's used to measure large distances within our solar system. Asteroids within <b>0.05 AU</b> are considered <i>close approaches</i>.
            </div>
            """, unsafe_allow_html=True)

        # ---- SQL Query ----
        query = """

        SELECT 
            a.id,
            a.name,
            a.is_potentially_hazardous_asteroid,
            c.close_approach_date,
            c.astronomical AS au_distance
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.astronomical < 0.05
        ORDER BY c.astronomical ASC
        LIMIT 100;
        """
        df = run_query(query)

        # ---- Rename Columns ----
        df = df.rename(columns={
            "name": "Asteroid Name",
            "au_distance": "Distance (AU)",
            "close_approach_date": "Close Approach Date",
            "is_potentially_hazardous_asteroid": "Hazardous"
        })

        df = df[["Asteroid Name", "Distance (AU)", "Close Approach Date", "Hazardous"]]
        top_asteroid = df.iloc[0]

        # ---- Layout Columns ----
        col1, col2 = st.columns([2, 3])

        # ---- Column 1 ----
        with col1:
            st.markdown("### Asteroid that approched very close to 🌍 ")

            # Detail Box
            st.markdown(f"""
            <div style='background-color:#0e1f2c;padding:18px;border-radius:10px;color:white;margin-bottom:20px'>
                <div style='font-size:18px'><b>🪐 Name:</b> {top_asteroid['Asteroid Name']}</div>
                <div style='font-size:18px'><b>📅 Date:</b> {top_asteroid['Close Approach Date']}</div>
                <div style='font-size:18px'><b>🌌 Distance (AU):</b> {top_asteroid['Distance (AU)']}</div>
                <div style='font-size:18px'><b>🚨 Hazardous:</b> {"Yes" if top_asteroid['Hazardous'] else "No"}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### List - All Asteroids < 0.05 AU")
            styled_df = df.style.background_gradient(
                subset=['Distance (AU)'],
                cmap='Purples_r'  # Darker for lower distance
            )
            st.dataframe(styled_df, use_container_width=True)

        # ---- Column 2 ----
        with col2:
            import plotly.express as px

            top20 = df.head(20)
            fig = px.bar(
                top20,
                x='Asteroid Name',
                y='Distance (AU)',
                color='Distance (AU)',
                color_continuous_scale='Purples_r',
                labels={'Distance (AU)': 'Distance (AU)', 'Asteroid Name': 'Asteroid Name'},
                title='Asteroids Within 0.05 AU'
            )
            fig.update_layout(xaxis_tickangle=-45, title_x=0.35)
            st.plotly_chart(fig, use_container_width=True)
