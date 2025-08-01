# 


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib
from database.db import run_query



# ✅ Page setup
st.set_page_config(page_title="Asteroid Dashboard", layout="wide")

# ✅ Session state for navigation
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"
# NASA logo URL
NASA_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/NASA_logo.svg/100px-NASA_logo.svg.png"


# ✅ Header (NASA Logo + Title)
st.markdown("""
    <style>
        .top-header {
            margin-top: -3rem;
            padding: 0.5rem 0rem;
            # border-radius: 0rem;
            # border: 1px solid pink;
            display: flex;
            align-items: center;
            justify-content: flex-start;
        }
        
    </style>

    <div class="top-header">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/NASA_logo.svg/100px-NASA_logo.svg.png"
             style="width: 80px; margin-right: 1rem;" />
        <h1 style='font-size: 30px;color: red;'>NASA <strong style="color: black;">Near-Earth Object Explorer</strong></h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Disable typing into the selectbox input */
    div[data-baseweb="select"] input {
        caret-color: transparent !important;  /* hide blinking cursor */
        color: transparent !important;        /* hide text being typed */
        pointer-events: none !important;      /* block input interactions */
    }

    div[data-baseweb="select"] div[role="combobox"] {
        pointer-events: auto !important; /* allow dropdown to still work */
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <hr style="border: 1px solid #ccc; margin-top: 0.2rem; margin-bottom: 1rem;" />
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar with button Navigation
# -------------------------------
def wide_button(label, key):
    return st.button(label, key=key, use_container_width=True)

with st.sidebar:
    st.markdown("### 🧭 Navigation")
    if wide_button("🏠 Home", key="home_btn"):
        st.session_state.active_page = "Home"
    if wide_button("🔍 Filter Criteria", key="filter_btn"):
        st.session_state.active_page = "Filter Criteria"
    if wide_button("📊 Queries", key="queries_btn"):
        st.session_state.active_page = "Queries"

# ✅ Page Routing
if st.session_state.active_page == "Home":
    import views.home
    views.home.show()

elif st.session_state.active_page == "Filter Criteria":
    import views.filter_criteria
    views.filter_criteria.show()

elif st.session_state.active_page == "Queries":
    import views.queries
    views.queries.show()

