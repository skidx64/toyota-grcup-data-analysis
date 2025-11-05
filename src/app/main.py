"""
GR Cup Performance Intelligence Platform
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import DATABASE_PATH
from src.app.database import (
    get_all_drivers,
    get_all_tracks,
    get_database_summary,
    get_driver_details,
    get_track_details
)


# Page configuration
st.set_page_config(
    page_title="GR Cup Performance Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Force sidebar to stay open and apply layout
st.markdown("""
    <script>
    const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.style.transform = 'none';
        sidebar.style.minWidth = '240px';
    }

    // Force main content styling
    const mainContainer = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
    if (mainContainer) {
        mainContainer.style.paddingLeft = '280px';
        mainContainer.style.paddingRight = '2rem';
        mainContainer.style.paddingTop = '7rem';
        mainContainer.style.paddingBottom = '2rem';
    }

    const blockContainer = window.parent.document.querySelector('.block-container');
    if (blockContainer) {
        blockContainer.style.backgroundColor = '#1A1A1A';
        blockContainer.style.borderRadius = '12px';
        blockContainer.style.boxShadow = '0 8px 24px rgba(0,0,0,0.5)';
        blockContainer.style.padding = '2rem';
    }

    // Remove collapse button
    const collapseIcons = window.parent.document.querySelectorAll('[data-testid="stIconMaterial"]');
    collapseIcons.forEach(icon => {
        if (icon.textContent.includes('keyboard_double_arrow_left')) {
            const button = icon.closest('button');
            if (button) button.remove();
            icon.remove();
        }
    });
    </script>
""", unsafe_allow_html=True)


# Custom CSS for dark-themed dashboard
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', 'Roboto', 'Arial', sans-serif;
    }

    /* Hide Streamlit UI elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hide hamburger menu and sidebar collapse button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    button[kind="header"] {
        display: none !important;
    }

    /* Hide only the collapse control button in stSidebarNav */
    [data-testid="stSidebarNav"] > button[kind="header"] {
        display: none !important;
    }

    .css-1cypcdb, .css-163ttbj, [data-testid="baseButton-header"] {
        display: none !important;
    }

    /* Force sidebar to always be visible and prevent any collapse */
    [data-testid="stSidebar"][data-collapsed="true"] {
        display: block !important;
        margin-left: 0 !important;
    }

    .st-emotion-cache-1cypcdb,
    .st-emotion-cache-163ttbj,
    button[data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
    }

    /* Hide the keyboard_double_arrow_left icon */
    [data-testid="stIconMaterial"]:has-text("keyboard_double_arrow_left"),
    span[data-testid="stIconMaterial"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Hide any button containing the collapse icon */
    button:has(span[data-testid="stIconMaterial"]) {
        display: none !important;
    }

    /* Alternative selector for the collapse button */
    [data-testid="stSidebar"] button[aria-label*="collapse"],
    [data-testid="stSidebar"] button[aria-label*="Collapse"] {
        display: none !important;
    }

    /* Main App Background - Glittery Black */
    .stApp {
        background:
            radial-gradient(circle at 20% 50%, rgba(255,255,255,0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255,255,255,0.02) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(255,255,255,0.02) 0%, transparent 50%),
            #0a0a0a !important;
        color: #FFFFFF;
        background-attachment: fixed;
        padding: 0 !important;
    }

    /* Ensure app container takes full space */
    .stApp > header {
        background-color: transparent !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px),
            radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 50px 50px, 80px 80px;
        background-position: 0 0, 40px 40px;
        pointer-events: none;
        z-index: 0;
    }

    /* Sidebar Styling - Fixed position and locked with gap - Clean "Coo" UI style */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: none;
        border-radius: 0 12px 12px 0;
        padding: 1.5rem 1rem !important;
        pointer-events: auto !important;
        transform: none !important;
        transition: none !important;
        position: fixed !important;
        left: 1rem !important;
        top: 6rem !important;
        bottom: 1rem !important;
        width: 240px !important;
        height: auto !important;
        max-height: calc(100vh - 7rem) !important;
        overflow: hidden !important;
        overflow-y: hidden !important;
        z-index: 998 !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        display: flex !important;
        flex-direction: column !important;
    }

    /* Remove extra space at top of sidebar content - Clean compact layout */
    [data-testid="stSidebarContent"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
    }

    [data-testid="stSidebarUserContent"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        overflow: hidden !important;
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* Prevent any scrollable containers in sidebar */
    [data-testid="stSidebar"] * {
        overflow-y: visible !important;
    }

    [data-testid="stSidebar"] .css-1544g2n,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        overflow: visible !important;
        overflow-y: visible !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(0) !important;
        margin-left: 0 !important;
    }

    [data-testid="stSidebar"] .css-1d391kg {
        background-color: #1A1A1A;
    }

    /* Lock sidebar width */
    section[data-testid="stSidebar"] {
        min-width: 240px !important;
        max-width: 240px !important;
        transform: none !important;
    }

    /* Main content area with proper gaps */
    [data-testid="stAppViewContainer"] {
        padding-left: 280px !important;
        padding-right: 2rem !important;
        padding-top: 7rem !important;
        padding-bottom: 2rem !important;
    }

    [data-testid="stAppViewContainer"] > section {
        background-color: transparent !important;
    }

    /* Main content container box */
    [data-testid="stAppViewContainer"] .main .block-container {
        background-color: #1A1A1A !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
        padding: 2rem !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    /* Ensure proper spacing */
    .appview-container {
        padding-left: 280px !important;
        padding-right: 2rem !important;
        padding-top: 7rem !important;
        padding-bottom: 2rem !important;
    }

    /* Target all main sections */
    section[data-testid="stAppViewContainer"] .main,
    section.main,
    .main > .block-container,
    [data-testid="block-container"] {
        background-color: #1A1A1A !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }

    /* Specific element container */
    .element-container {
        background-color: transparent !important;
    }

    /* Force the card grid background */
    [data-testid="column"] {
        background-color: transparent !important;
    }

    /* Ensure navigation buttons are clickable */
    [data-testid="stSidebar"] .stButton {
        pointer-events: auto !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        pointer-events: auto !important;
    }

    /* Sidebar Title */
    .sidebar-title {
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin: 0 0 1rem 0 !important;
        padding: 0 1rem !important;
        letter-spacing: 0.5px !important;
        line-height: 1.4 !important;
    }

    /* Sidebar Navigation Buttons - Clean "Coo" UI style with compact spacing */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.4rem;
        padding: 0;
    }

    /* Remove extra spacing from button containers */
    [data-testid="stSidebar"] .stElementContainer {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Remove gap from vertical block */
    [data-testid="stSidebar"] .stVerticalBlock {
        gap: 0.4rem !important;
        overflow: visible !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, rgba(30, 30, 30, 0.6) 0%, rgba(20, 20, 20, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #A0A0A0;
        padding: 0.85rem 1.15rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 10px;
        transition: all 0.25s ease;
        box-shadow:
            0 4px 8px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.05) !important;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        height: auto;
        min-height: 42px;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, rgba(139, 0, 0, 0.3) 0%, rgba(75, 0, 0, 0.4) 100%);
        border-color: rgba(255, 200, 0, 0.4);
        color: #FFFFFF;
        transform: translateX(4px);
        box-shadow:
            0 6px 12px rgba(0,0,0,0.4),
            inset 0 1px 0 rgba(255,255,255,0.1),
            inset 4px 0 0 rgba(255, 200, 0, 0.6) !important;
    }

    /* Primary button (active page) - "Coo" UI style with yellow accent */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8B0000 0%, #4B0000 100%);
        color: #FFFFFF;
        font-weight: 700;
        border: 2px solid rgba(139, 0, 0, 0.8);
        box-shadow:
            0 6px 16px rgba(139, 0, 0, 0.6),
            inset 0 1px 0 rgba(255,255,255,0.15),
            inset 4px 0 0 rgba(255, 200, 0, 0.8) !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        transform: translateX(4px);
        border-color: rgba(255, 0, 0, 0.9);
        box-shadow:
            0 8px 20px rgba(139, 0, 0, 0.8),
            inset 0 1px 0 rgba(255,255,255,0.2),
            inset 4px 0 0 rgba(255, 200, 0, 1) !important;
    }

    /* Secondary button (inactive pages) - Box Style */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, rgba(30, 30, 30, 0.6) 0%, rgba(20, 20, 20, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Disabled button (locked features) - Box Style */
    [data-testid="stSidebar"] .stButton > button:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        background: linear-gradient(135deg, rgba(20, 20, 20, 0.4) 0%, rgba(15, 15, 15, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #505050;
    }

    [data-testid="stSidebar"] .stButton > button:disabled:hover {
        transform: none;
        border-color: rgba(255, 255, 255, 0.05);
        box-shadow:
            0 4px 8px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.05) !important;
    }

    /* Ensure sidebar container doesn't scroll */
    [data-testid="stSidebar"] > div:first-child {
        overflow: hidden !important;
        overflow-y: hidden !important;
    }

    /* Header Section - Full width with gap */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(180deg, #1A1A1A 0%, #0f0f0f 100%);
        padding: 1.25rem 2rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        position: fixed;
        top: 1rem;
        left: 1rem;
        right: 1rem;
        z-index: 999;
        margin: 0;
    }

    .header-left {
        display: flex;
        align-items: center;
    }

    .header-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .header-stats {
        display: flex;
        gap: 3rem;
        align-items: center;
    }

    .header-stat {
        text-align: center;
    }

    .header-stat-label {
        font-size: 0.875rem;
        color: #A0A0A0;
        margin-bottom: 0.25rem;
    }

    .header-stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* Track Cards - FIFA Style - LARGER SIZE */
    .track-card {
        /* All styling set by inline styles - don't override */
    }

    .track-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 16px 40px rgba(139, 0, 0, 0.8),
            inset 0 1px 0 rgba(255,255,255,0.2),
            inset 0 -1px 0 rgba(0,0,0,0.5) !important;
        border-color: rgba(255, 0, 0, 0.9) !important;
    }

    /* Driver Cards - FIFA Style with tier colors - LARGER SIZE */
    .driver-card {
        /* Size set by inline styles - don't override */
    }

    .driver-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 16px 40px rgba(0,0,0,0.9),
            inset 0 1px 0 rgba(255,255,255,0.25),
            inset 0 -1px 0 rgba(0,0,0,0.5) !important;
        filter: brightness(1.1);
    }

    .card-name {
        font-size: 1.25rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.75rem;
        color: white;
    }

    .card-stat {
        display: flex;
        justify-content: space-between;
        margin: 0.35rem 0;
        font-size: 0.8rem;
        padding: 0.2rem 0;
        width: 100%;
    }

    .driver-card .stat-label {
        color: rgba(255,255,255,0.85);
    }

    .driver-card .stat-value {
        font-weight: 700;
        color: white;
    }

    /* Button Styling */
    .stButton > button {
        background: transparent;
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 0.75rem;
    }

    .stButton > button:hover {
        background: rgba(255,255,255,0.1);
        border-color: rgba(255,255,255,0.6);
        transform: scale(1.02);
    }

    /* Page Title */
    h1 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
    }

    /* Hide header link icon */
    h1 a, h1 svg, h2 a, h2 svg, h3 a, h3 svg {
        display: none !important;
        visibility: hidden !important;
    }

    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {
        display: none !important;
    }

    /* Text Elements */
    .stMarkdown, p {
        color: #E0E0E0;
    }

    /* Ensure text doesn't overflow */
    .main .block-container {
        overflow-x: hidden !important;
    }

    /* Fix text rendering */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Metrics in Sidebar */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #A0A0A0 !important;
    }

    /* Radio Buttons (Main content area) */
    .stRadio > label {
        color: #E0E0E0 !important;
    }

    /* Sidebar caption styling */
    [data-testid="stSidebar"] .caption {
        color: #606060;
        font-size: 0.75rem;
    }

    /* Slider */
    .stSlider > label {
        color: #E0E0E0 !important;
    }

    /* Selectbox */
    .stSelectbox > label {
        color: #E0E0E0 !important;
    }

    /* Divider */
    hr {
        border-color: #2A2A2A !important;
    }

    /* Locked feature styling */
    .locked-feature {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Responsive spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def format_lap_time(seconds):
    """Convert seconds to M:SS.mmm format"""
    if pd.isna(seconds) or seconds == 0:
        return "N/A"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


def render_header(summary):
    """Render header section with title and stats"""
    header_html = f"""
    <div class="header-container">
        <div class="header-left">
            <h2 class="header-title">GR Cup Performance Intelligence</h2>
        </div>
        <div class="header-stats">
            <div class="header-stat">
                <div class="header-stat-label">Tracks</div>
                <div class="header-stat-value">{summary['total_tracks']}</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-label">Drivers</div>
                <div class="header-stat-value">{summary['total_drivers']}</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-label">Total Laps</div>
                <div class="header-stat-value">{summary['total_laps']:,}</div>
            </div>
        </div>
    </div>
    """
    return header_html


def render_driver_card(driver_row):
    """Render a single driver card with FIFA-style stats and tier color-coding"""
    driver_num = int(driver_row['driver_number'])

    # Get stats with defaults for missing values
    overall_rating = int(driver_row['overall_rating']) if pd.notna(driver_row.get('overall_rating')) else 50
    pace = int(driver_row.get('braking_score', 50)) if pd.notna(driver_row.get('braking_score')) else 50
    consistency = int(driver_row.get('consistency_score', 50)) if pd.notna(driver_row.get('consistency_score')) else 50
    qualifying = int(driver_row.get('qualifying_score', 50)) if pd.notna(driver_row.get('qualifying_score')) else 50
    racecraft = int(driver_row.get('racecraft_score', 50)) if pd.notna(driver_row.get('racecraft_score')) else 50

    # Determine tier based on overall rating with more explicit styling
    if overall_rating >= 80:
        tier = "gold"
        tier_gradient = "linear-gradient(180deg, #FFD700 0%, #B8860B 100%)"
        tier_border = "rgba(255, 215, 0, 0.9)"
        tier_shadow = "0 16px 40px rgba(255, 215, 0, 0.8)"
    elif overall_rating >= 65:
        tier = "silver"
        tier_gradient = "linear-gradient(180deg, #C0C0C0 0%, #808080 100%)"
        tier_border = "rgba(192, 192, 192, 0.9)"
        tier_shadow = "0 16px 40px rgba(192, 192, 192, 0.8)"
    else:
        tier = "bronze"
        tier_gradient = "linear-gradient(180deg, #CD7F32 0%, #8B5A2B 100%)"
        tier_border = "rgba(205, 127, 50, 0.9)"
        tier_shadow = "0 16px 40px rgba(205, 127, 50, 0.8)"

    card_html = f"""
    <div class="driver-card" style="
        background: {tier_gradient} !important;
        border: 2px solid {tier_border} !important;
        min-height: 400px !important;
        max-height: 440px !important;
        border-radius: 12px;
        padding: 2rem;
        color: white;
        box-shadow: 0 6px 16px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.15), inset 0 -1px 0 rgba(0,0,0,0.5);
        margin: 0.65rem;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        cursor: pointer;
        overflow: hidden;
        word-wrap: break-word;
    ">
        <div class="driver-rating" style="font-size: 3.5rem; font-weight: 900; margin: 1rem 0; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
            {overall_rating}
        </div>
        <div class="card-name" style="font-size: 1.4rem; font-weight: 700; text-align: center; margin-bottom: 1rem; color: white;">Driver #{driver_num}</div>
        <div style="width: 100%; margin: 1rem 0;">
            <div class="card-stat" style="display: flex; justify-content: space-between; margin: 0.5rem 0; font-size: 0.95rem; padding: 0.3rem 0;">
                <span class="stat-label" style="color: rgba(255,255,255,0.85);">PACE</span>
                <span class="stat-value" style="font-weight: 700; color: white;">{pace}</span>
            </div>
            <div class="card-stat" style="display: flex; justify-content: space-between; margin: 0.5rem 0; font-size: 0.95rem; padding: 0.3rem 0;">
                <span class="stat-label" style="color: rgba(255,255,255,0.85);">CONSISTENCY</span>
                <span class="stat-value" style="font-weight: 700; color: white;">{consistency}</span>
            </div>
            <div class="card-stat" style="display: flex; justify-content: space-between; margin: 0.5rem 0; font-size: 0.95rem; padding: 0.3rem 0;">
                <span class="stat-label" style="color: rgba(255,255,255,0.85);">QUALIFYING</span>
                <span class="stat-value" style="font-weight: 700; color: white;">{qualifying}</span>
            </div>
            <div class="card-stat" style="display: flex; justify-content: space-between; margin: 0.5rem 0; font-size: 0.95rem; padding: 0.3rem 0;">
                <span class="stat-label" style="color: rgba(255,255,255,0.85);">RACECRAFT</span>
                <span class="stat-value" style="font-weight: 700; color: white;">{racecraft}</span>
            </div>
        </div>
    </div>
    """

    return card_html


def render_track_card(track_row):
    """Render a single track card with enhanced styling and badges"""
    track_code = track_row['track_code']
    track_name = track_row['track_name']
    location = track_row['location']
    length = float(track_row['length_miles'])
    lap_record = track_row.get('lap_record_seconds', 0)
    top_speed = track_row.get('top_speed_kph', 0)
    difficulty = track_row.get('track_difficulty_score', 70)

    # Determine track type based on length and characteristics
    if length < 2.5:
        track_type = "Technical"
        type_color = "#FF6B6B"
    elif length > 3.5:
        track_type = "High-Speed"
        type_color = "#4ECDC4"
    else:
        track_type = "Mixed"
        type_color = "#FFE66D"

    # Weather icon (placeholder)
    weather_icon = "🌤️"

    card_html = f"""
    <div class="track-card" style="
        background: linear-gradient(180deg, #8B0000 0%, #4B0000 100%) !important;
        border-radius: 12px;
        padding: 2.5rem;
        color: white;
        box-shadow: 0 6px 16px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1), inset 0 -1px 0 rgba(0,0,0,0.5);
        margin: 0.78rem;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 480px !important;
        max-height: 520px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 2px solid rgba(139, 0, 0, 0.8);
        position: relative;
        cursor: pointer;
        overflow: hidden;
        word-wrap: break-word;
    ">
        <div class="track-header" style="text-align: center; margin-bottom: 1.25rem;">
            <div class="track-code" style="font-size: 2.5rem; font-weight: 800; color: white; margin-bottom: 0.5rem; letter-spacing: 1.5px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{track_code}</div>
            <div class="track-name" style="font-size: 1.15rem; font-weight: 600; color: rgba(255,255,255,0.95); margin-bottom: 0.25rem;">{track_name}</div>
        </div>
        <div class="track-location" style="text-align: center; font-size: 0.9rem; color: rgba(255,255,255,0.85); margin-bottom: 1rem; font-weight: 500;">{location} {weather_icon}</div>
        <div style="display: flex; justify-content: center; margin: 0.75rem 0;">
            <span style="
                background: {type_color};
                color: #000;
                padding: 0.35rem 1rem;
                border-radius: 14px;
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            ">{track_type}</span>
        </div>
        <div class="track-divider" style="height: 2px; background: rgba(255,255,255,0.3); margin: 1.25rem 0; border-radius: 1px;"></div>
        <div class="track-stats-grid" style="display: grid; grid-template-columns: 1fr; gap: 1rem;">
            <div class="track-stat-item" style="background: rgba(255,255,255,0.15); padding: 0.75rem; border-radius: 8px; text-align: center; backdrop-filter: blur(10px);">
                <div class="track-stat-label" style="font-size: 0.75rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; font-weight: 600;">Length</div>
                <div class="track-stat-value" style="font-size: 1.15rem; font-weight: 700; color: white;">{length:.2f} mi</div>
            </div>
            <div class="track-stat-item" style="background: rgba(255,255,255,0.15); padding: 0.75rem; border-radius: 8px; text-align: center; backdrop-filter: blur(10px);">
                <div class="track-stat-label" style="font-size: 0.75rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; font-weight: 600;">Difficulty</div>
                <div class="track-stat-value" style="font-size: 1.15rem; font-weight: 700; color: white;">{int(difficulty)}/100</div>
            </div>
            <div class="track-stat-item" style="background: rgba(255,255,255,0.15); padding: 0.75rem; border-radius: 8px; text-align: center; backdrop-filter: blur(10px);">
                <div class="track-stat-label" style="font-size: 0.75rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; font-weight: 600;">Best Lap</div>
                <div class="track-stat-value" style="font-size: 1.15rem; font-weight: 700; color: white;">{format_lap_time(lap_record)}</div>
            </div>
            <div class="track-stat-item" style="background: rgba(255,255,255,0.15); padding: 0.75rem; border-radius: 8px; text-align: center; backdrop-filter: blur(10px);">
                <div class="track-stat-label" style="font-size: 0.75rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; font-weight: 600;">Top Speed</div>
                <div class="track-stat-value" style="font-size: 1.15rem; font-weight: 700; color: white;">{int(top_speed)} kph</div>
            </div>
        </div>
    </div>
    """

    return card_html


def show_driver_detail(driver_number):
    """Display detailed driver profile with 6 widgets"""
    import plotly.graph_objects as go
    import plotly.express as px

    # Get driver details
    driver_data = get_driver_details(driver_number)

    if driver_data['info'].empty:
        st.error(f"Driver #{driver_number} not found")
        return

    driver_info = driver_data['info'].iloc[0]
    driver_stats = driver_data['stats'].iloc[0] if not driver_data['stats'].empty else None

    # Back button
    if st.button("← Back to Drivers", type="secondary"):
        st.session_state.selected_driver = None
        st.rerun()

    st.title(f"Driver #{driver_number} Profile")

    # Hero Section - Large driver card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if driver_stats is not None:
            overall_rating = int(driver_stats['overall_rating']) if pd.notna(driver_stats.get('overall_rating')) else 50
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(180deg, #8B0000 0%, #4B0000 100%); border-radius: 12px; margin: 1rem 0;">
                <div style="font-size: 4rem; font-weight: 900; color: white;">{overall_rating}</div>
                <div style="font-size: 1.5rem; color: rgba(255,255,255,0.9);">Overall Rating</div>
            </div>
            """, unsafe_allow_html=True)

    # Widget Grid Layout (2 columns, 3 rows = 6 widgets)
    st.markdown("### Performance Analysis")

    # Row 1: Performance Radar + Track Suitability
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Widget 1: Performance Radar")
        try:
            if driver_stats is not None:
                categories = ['Braking', 'Cornering', 'Throttle', 'Consistency', 'Racecraft', 'Qualifying']
                values = [
                    float(driver_stats.get('braking_score', 50) or 50),
                    float(driver_stats.get('cornering_score', 50) or 50),
                    float(driver_stats.get('throttle_score', 50) or 50),
                    float(driver_stats.get('consistency_score', 50) or 50),
                    float(driver_stats.get('racecraft_score', 50) or 50),
                    float(driver_stats.get('qualifying_score', 50) or 50)
                ]

                fig = go.Figure(data=go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    line=dict(color='#8B0000', width=2),
                    fillcolor='rgba(139, 0, 0, 0.3)'
                ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100]),
                        bgcolor='rgba(0,0,0,0.1)'
                    ),
                    showlegend=False,
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E0E0')
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Driver stats not available")
        except Exception as e:
            st.error(f"Error loading radar chart: {str(e)}")
            st.write("Debug - driver_stats:", driver_stats)

    with col2:
        st.markdown("#### Widget 2: Track Suitability Matrix")

        try:
            # Get best lap per track for this driver
            track_performance = driver_data['best_laps']

            if not track_performance.empty:
                # Create heatmap-style display
                st.markdown("""
                <div style="background: rgba(30,30,30,0.8); padding: 1rem; border-radius: 8px;">
                """, unsafe_allow_html=True)

                for _, row in track_performance.iterrows():
                    track_code = row['track_code']
                    best_lap = format_lap_time(row['best_lap_seconds'])

                    # Simple color coding (green/yellow/red based on relative performance)
                    color = "#4CAF50"  # Green by default

                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 0.5rem; margin: 0.25rem 0; background: {color}22; border-left: 3px solid {color}; border-radius: 4px;">
                        <span style="font-weight: 600; color: #E0E0E0;">{track_code}</span>
                        <span style="color: #E0E0E0;">{best_lap}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No track performance data available")
                st.write(f"Debug - Track data rows: {len(track_performance)}")
        except Exception as e:
            st.error(f"Error loading track matrix: {str(e)}")
            st.write("Debug - best_laps data:", driver_data.get('best_laps', 'N/A'))

    # Row 2: Season Progression + Head-to-Head
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Widget 3: Season Progression")

        race_results = driver_data['results']

        if not race_results.empty:
            fig = px.line(
                race_results,
                x=race_results.index,
                y='position',
                title='',
                markers=True
            )

            fig.update_layout(
                xaxis_title="Race Number",
                yaxis_title="Position",
                yaxis=dict(autorange='reversed'),
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,0.5)',
                font=dict(color='#E0E0E0')
            )

            fig.update_traces(line=dict(color='#8B0000', width=3), marker=dict(size=8, color='#FFD700'))

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No race data available")

    with col2:
        st.markdown("#### Widget 4: Head-to-Head Comparison")

        try:
            # Get all drivers for comparison
            all_drivers_df = get_all_drivers()
            other_drivers = all_drivers_df[all_drivers_df['driver_number'] != driver_number]['driver_number'].tolist()

            if other_drivers:
                compare_driver = st.selectbox("Select driver to compare", other_drivers, key=f"compare_{driver_number}")

                if compare_driver:
                    compare_data = get_driver_details(compare_driver)
                    compare_stats = compare_data['stats'].iloc[0] if not compare_data['stats'].empty else None

                    if compare_stats is not None and driver_stats is not None:
                        st.markdown(f"""
                        <div style="background: rgba(30,30,30,0.8); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                                <span>Overall Rating</span>
                                <span><strong>{int(driver_stats.get('overall_rating', 50) or 50)}</strong> vs <strong>{int(compare_stats.get('overall_rating', 50) or 50)}</strong></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                                <span>Best Lap Time</span>
                                <span>{format_lap_time(driver_stats.get('best_lap_time_seconds', 0))} vs {format_lap_time(compare_stats.get('best_lap_time_seconds', 0))}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                                <span>Consistency</span>
                                <span><strong>{int(driver_stats.get('consistency_score', 50) or 50)}</strong> vs <strong>{int(compare_stats.get('consistency_score', 50) or 50)}</strong></span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Stats not available for comparison")
                        st.write("Debug - driver_stats exists:", driver_stats is not None)
                        st.write("Debug - compare_stats exists:", compare_stats is not None)
            else:
                st.info("No other drivers available for comparison")
        except Exception as e:
            st.error(f"Error loading comparison: {str(e)}")

    # Row 3: Strengths & Weaknesses + Championship Stats
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Widget 5: Strengths & Weaknesses")

        try:
            if driver_stats is not None:
                # Calculate top 3 strengths and weaknesses
                scores = {
                    'Braking': float(driver_stats.get('braking_score', 50) or 50),
                    'Cornering': float(driver_stats.get('cornering_score', 50) or 50),
                    'Throttle': float(driver_stats.get('throttle_score', 50) or 50),
                    'Consistency': float(driver_stats.get('consistency_score', 50) or 50),
                    'Racecraft': float(driver_stats.get('racecraft_score', 50) or 50),
                    'Qualifying': float(driver_stats.get('qualifying_score', 50) or 50)
                }

                sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

                st.markdown("<div style='background: rgba(30,30,30,0.8); padding: 1rem; border-radius: 8px;'>", unsafe_allow_html=True)
                st.markdown("<strong style='color: #4CAF50;'>💪 Top Strengths:</strong>", unsafe_allow_html=True)
                for i, (skill, score) in enumerate(sorted_scores[:3]):
                    st.markdown(f"<div style='padding: 0.25rem 0; color: #E0E0E0;'>{i+1}. {skill}: <strong>{int(score)}/100</strong></div>", unsafe_allow_html=True)

                st.markdown("<br><strong style='color: #FF6B6B;'>⚠️ Areas for Improvement:</strong>", unsafe_allow_html=True)
                for i, (skill, score) in enumerate(list(reversed(sorted_scores))[:3]):
                    st.markdown(f"<div style='padding: 0.25rem 0; color: #E0E0E0;'>{i+1}. {skill}: <strong>{int(score)}/100</strong></div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Stats not available")
                st.write("Debug - driver_stats:", driver_stats)
        except Exception as e:
            st.error(f"Error loading strengths/weaknesses: {str(e)}")
            st.write("Debug - driver_stats:", driver_stats)

    with col2:
        st.markdown("#### Widget 6: Championship Stats")

        st.markdown(f"""
        <div style="background: rgba(30,30,30,0.8); padding: 1.5rem; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: #A0A0A0;">Total Races</span>
                <span style="color: #FFFFFF; font-weight: 700; font-size: 1.25rem;">{int(driver_info['total_races'])}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: #A0A0A0;">Podium Finishes</span>
                <span style="color: #FFD700; font-weight: 700; font-size: 1.25rem;">{int(driver_stats['total_podiums']) if driver_stats is not None else 0}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: #A0A0A0;">Best Finish</span>
                <span style="color: #4CAF50; font-weight: 700; font-size: 1.25rem;">P{int(driver_info['best_finish'])}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0;">
                <span style="color: #A0A0A0;">Avg Position</span>
                <span style="color: #FFFFFF; font-weight: 700; font-size: 1.25rem;">P{int(driver_info['avg_position']) if pd.notna(driver_info['avg_position']) else 'N/A'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def show_drivers_page():
    """Display driver cards grid or driver detail view"""
    # Check if database exists
    if not DATABASE_PATH.exists():
        st.error(f"❌ Database not found at {DATABASE_PATH}")
        st.info("📦 Please run the data pipeline first:")
        st.code("python src/pipeline/ingest_data.py", language="bash")
        return

    # Check if a driver is selected for detail view
    if st.session_state.selected_driver is not None:
        show_driver_detail(st.session_state.selected_driver)
        return

    st.title("Driver Profiling")

    # Load drivers
    drivers_df = get_all_drivers()

    if drivers_df.empty:
        st.warning("No driver data available")
        return

    # Filter options with elegant styling
    st.markdown("""
    <style>
    /* Elegant filter styling */
    .stNumberInput > label {
        color: #A0A0A0 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        margin-top: 0 !important;
        margin-bottom: 0.75rem !important;
        text-transform: capitalize !important;
        letter-spacing: 0.5px !important;
    }

    .stSelectbox > label {
        color: #A0A0A0 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        margin-top: 0 !important;
        margin-bottom: 0.75rem !important;
        text-transform: capitalize !important;
        letter-spacing: 0.5px !important;
    }

    /* Number Input styling */
    .stNumberInput input {
        background-color: #1A1A1A !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        padding: 0.5rem !important;
    }

    .stNumberInput input:hover {
        border-color: rgba(139, 0, 0, 0.6) !important;
        box-shadow: 0 0 0 1px rgba(139, 0, 0, 0.4) !important;
    }

    .stNumberInput input:focus {
        border-color: rgba(139, 0, 0, 0.8) !important;
        box-shadow: 0 0 0 2px rgba(139, 0, 0, 0.3) !important;
    }

    /* Number input steppers */
    .stNumberInput button {
        background-color: rgba(30, 30, 30, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #A0A0A0 !important;
    }

    .stNumberInput button:hover {
        background-color: rgba(139, 0, 0, 0.4) !important;
        border-color: rgba(139, 0, 0, 0.6) !important;
        color: #FFFFFF !important;
    }

    /* Selectbox button - dark background like image */
    .stSelectbox [data-baseweb="select"] {
        background-color: #1A1A1A !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }

    .stSelectbox [data-baseweb="select"]:hover {
        border-color: rgba(139, 0, 0, 0.6) !important;
        box-shadow: 0 0 0 1px rgba(139, 0, 0, 0.4) !important;
    }

    .stSelectbox div[role="button"] {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        padding: 0.5rem !important;
    }

    /* Dropdown menu styling - matching image */
    [data-baseweb="popover"] {
        background-color: #1A1A1A !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }

    /* Dropdown list */
    [role="listbox"] {
        background-color: #1A1A1A !important;
        border-radius: 8px !important;
    }

    /* Dropdown options */
    [role="option"] {
        background-color: transparent !important;
        color: #A0A0A0 !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    [role="option"]:hover {
        background-color: rgba(139, 0, 0, 0.3) !important;
        color: #FFFFFF !important;
    }

    /* Selected option - RED background like image */
    [role="option"][aria-selected="true"] {
        background-color: #8B0000 !important;
        background: linear-gradient(135deg, #8B0000 0%, #6B0000 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    [role="option"][aria-selected="true"]:hover {
        background: linear-gradient(135deg, #A00000 0%, #800000 100%) !important;
    }

    /* Filter container spacing */
    .element-container:has(.stNumberInput), .element-container:has(.stSelectbox) {
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
        padding-top: 0 !important;
    }

    /* Remove extra spacing before filters */
    div[data-testid="column"] > div {
        padding-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        min_races = st.number_input("Minimum races", min_value=1, max_value=int(drivers_df['total_races'].max()), value=1, step=1)
    with col2:
        sort_by = st.selectbox("Sort by", ["Best Finish", "Overall Rating", "Total Races", "Podiums"])

    # Filter and sort
    filtered_df = drivers_df[drivers_df['total_races'] >= min_races]

    if sort_by == "Best Finish":
        filtered_df = filtered_df.sort_values('best_finish')
    elif sort_by == "Overall Rating":
        filtered_df = filtered_df.sort_values('overall_rating', ascending=False, na_position='last')
    elif sort_by == "Total Races":
        filtered_df = filtered_df.sort_values('total_races', ascending=False)
    else:  # Podiums
        filtered_df = filtered_df.sort_values('total_podiums', ascending=False, na_position='last')

    # Display cards in grid (4 columns)
    num_cols = 4
    cols = st.columns(num_cols)

    for idx, (_, driver) in enumerate(filtered_df.iterrows()):
        col_idx = idx % num_cols
        with cols[col_idx]:
            st.markdown(render_driver_card(driver), unsafe_allow_html=True)
            # Add button to view details
            if st.button("View Details", key=f"driver_{int(driver['driver_number'])}", use_container_width=True):
                st.session_state.selected_driver = int(driver['driver_number'])
                st.rerun()


def show_tracks_page():
    """Display track cards grid"""
    # Check if database exists
    if not DATABASE_PATH.exists():
        st.error(f"❌ Database not found")
        return

    st.title("Track Analysis")

    # Load tracks
    tracks_df = get_all_tracks()

    if tracks_df.empty:
        st.warning("No track data available")
        return

    # Display cards in grid (3 columns for tracks)
    num_cols = 3
    cols = st.columns(num_cols)

    for idx, (_, track) in enumerate(tracks_df.iterrows()):
        col_idx = idx % num_cols
        with cols[col_idx]:
            st.markdown(render_track_card(track), unsafe_allow_html=True)


def show_search_page():
    """Simple search placeholder"""
    st.title("Questions")

    # Coming soon message with matching color scheme
    st.markdown("""
    <div style="
        background: linear-gradient(180deg, #8B0000 0%, #4B0000 100%);
        border-radius: 12px;
        padding: 2rem;
        color: white;
        box-shadow:
            0 6px 16px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(255,255,255,0.1),
            inset 0 -1px 0 rgba(0,0,0,0.5);
        border: 2px solid rgba(139, 0, 0, 0.8);
        margin: 2rem 0;
        text-align: center;
    ">
        <h3 style="color: white; margin-bottom: 1.5rem; font-size: 1.5rem;">🚧 Coming Soon</h3>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-bottom: 1rem;">
            Week 4: Simple search feature
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 30, 30, 0.8) 0%, rgba(20, 20, 20, 0.9) 100%);
        border-radius: 12px;
        padding: 2rem;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
    ">
        <h4 style="color: #FFFFFF; margin-bottom: 1rem; font-size: 1.2rem;">Example Questions:</h4>
        <ul style="color: rgba(255,255,255,0.85); font-size: 1rem; line-height: 1.8;">
            <li>"Who is the fastest driver?"</li>
            <li>"Show Driver 13 stats"</li>
            <li>"Track records at COTA"</li>
            <li>"Compare drivers at Barber"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point"""

    # Load custom CSS
    load_custom_css()

    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'drivers'
    if 'selected_driver' not in st.session_state:
        st.session_state.selected_driver = None
    if 'selected_track' not in st.session_state:
        st.session_state.selected_track = None

    # Render fixed header at top of entire app
    if DATABASE_PATH.exists():
        summary = get_database_summary()
        st.markdown(render_header(summary), unsafe_allow_html=True)

    # Navigation
    nav_options = {
        "Drivers": "drivers",
        "Tracks": "tracks",
        "Questions": "search",
        "Training": "training",
        "Predictions": "predictions",
        "Analytics": "analytics",
        "Extras": "extras"
    }

    # Phase 1: Only Drivers, Tracks, and Ask Questions are active
    active_pages = ["drivers", "tracks", "search"]

    # Create navigation buttons in sidebar
    for label, page in nav_options.items():
        is_active = st.session_state.current_page == page
        is_locked = page not in active_pages

        button_label = f"{label} 🔒" if is_locked else label

        if st.sidebar.button(button_label, key=f"nav_{page}", use_container_width=True,
                            type="primary" if is_active else "secondary",
                            disabled=is_locked):
            st.session_state.current_page = page
            st.rerun()

    page = st.session_state.current_page

    # Route to appropriate page
    if page == "drivers":
        show_drivers_page()
    elif page == "tracks":
        show_tracks_page()
    elif page == "search":
        show_search_page()
    elif page in ["training", "predictions", "analytics", "extras"]:
        # Get the label for the current page
        page_label = [label for label, p in nav_options.items() if p == page][0]
        st.title(f"{page_label}")
        st.warning("🔒 This feature will be unlocked in a future phase")

        phase_info = {
            "training": "Phase 2 (Weeks 5-6)",
            "predictions": "Phase 3 (Weeks 7-9)",
            "analytics": "Phase 4 (Weeks 10-12)",
            "extras": "Phase 6 (Week 15)"
        }
        st.write(f"**Coming in:** {phase_info.get(page, 'Future phase')}")



if __name__ == "__main__":
    main()
