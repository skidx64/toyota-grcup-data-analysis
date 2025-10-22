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

    /* Track Cards - FIFA Style with darker red - 56% Larger (30% + 20% more) */
    .track-card {
        background: linear-gradient(180deg, #8B0000 0%, #4B0000 100%);
        border-radius: 12px;
        padding: 1.95rem;
        color: white;
        box-shadow:
            0 6px 16px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(255,255,255,0.1),
            inset 0 -1px 0 rgba(0,0,0,0.5);
        margin: 0.78rem;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 343px;
        max-height: 374px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 2px solid rgba(139, 0, 0, 0.8);
        position: relative;
        cursor: pointer;
        overflow: hidden;
        word-wrap: break-word;
    }

    .track-card * {
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .track-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(0,0,0,0.2) 100%);
        pointer-events: none;
    }

    .track-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 16px 40px rgba(139, 0, 0, 0.8),
            inset 0 1px 0 rgba(255,255,255,0.2),
            inset 0 -1px 0 rgba(0,0,0,0.5);
        border-color: rgba(255, 0, 0, 0.9);
    }

    .track-header {
        text-align: center;
        margin-bottom: 1rem;
    }

    .track-code {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.35rem;
        letter-spacing: 1.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .track-name {
        font-size: 1rem;
        font-weight: 600;
        color: rgba(255,255,255,0.95);
        margin-bottom: 0.2rem;
    }

    .track-location {
        text-align: center;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.85);
        margin-bottom: 0.75rem;
        font-weight: 500;
    }

    .track-divider {
        height: 2px;
        background: rgba(255,255,255,0.3);
        margin: 1rem 0;
        border-radius: 1px;
    }

    .track-stats-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.75rem;
    }

    .track-stat-item {
        background: rgba(255,255,255,0.15);
        padding: 0.5rem;
        border-radius: 6px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .track-stat-label {
        font-size: 0.65rem;
        color: rgba(255,255,255,0.8);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.2rem;
        font-weight: 600;
    }

    .track-stat-value {
        font-size: 1rem;
        font-weight: 700;
        color: white;
    }

    /* Driver Cards - FIFA Style with darker red - 30% Larger */
    .driver-card {
        background: linear-gradient(180deg, #8B0000 0%, #4B0000 100%);
        border-radius: 12px;
        padding: 1.625rem;
        color: white;
        box-shadow:
            0 6px 16px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(255,255,255,0.1),
            inset 0 -1px 0 rgba(0,0,0,0.5);
        margin: 0.65rem;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 286px;
        max-height: 312px;
        display: flex;
        flex-direction: column;
        align-items: center;
        border: 2px solid rgba(139, 0, 0, 0.8);
        position: relative;
        cursor: pointer;
        overflow: hidden;
        word-wrap: break-word;
    }

    .driver-card * {
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .driver-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(0,0,0,0.2) 100%);
        pointer-events: none;
    }

    .driver-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 16px 40px rgba(139, 0, 0, 0.8),
            inset 0 1px 0 rgba(255,255,255,0.2),
            inset 0 -1px 0 rgba(0,0,0,0.5);
        border-color: rgba(255, 0, 0, 0.9);
    }

    .driver-avatar {
        font-size: 3rem;
        margin: 0.5rem 0;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
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
    """Render a single driver card with red gradient and face placeholder"""
    driver_num = int(driver_row['driver_number'])
    best_finish = int(driver_row['best_finish'])
    total_races = int(driver_row['total_races'])
    total_podiums = int(driver_row.get('total_podiums', 0)) if pd.notna(driver_row.get('total_podiums')) else 0

    card_html = f"""
    <div class="driver-card">
        <div class="driver-avatar">👤</div>
        <div class="card-name">Driver #{driver_num}</div>
        <div class="card-stat">
            <span class="stat-label">Best Finish:</span>
            <span class="stat-value">P{best_finish}</span>
        </div>
        <div class="card-stat">
            <span class="stat-label">Races:</span>
            <span class="stat-value">{total_races}</span>
        </div>
        <div class="card-stat">
            <span class="stat-label">Podiums:</span>
            <span class="stat-value">{total_podiums}</span>
        </div>
        <div class="card-stat">
            <span class="stat-label">Avg Position:</span>
            <span class="stat-value">P{int(driver_row['avg_position']) if pd.notna(driver_row['avg_position']) else 'N/A'}</span>
        </div>
    </div>
    """

    return card_html


def render_track_card(track_row):
    """Render a single track card with enhanced styling"""
    track_code = track_row['track_code']
    track_name = track_row['track_name']
    location = track_row['location']
    length = float(track_row['length_miles'])
    lap_record = track_row.get('lap_record_seconds', 0)

    card_html = f"""
    <div class="track-card">
        <div class="track-header">
            <div class="track-code">{track_code}</div>
            <div class="track-name">{track_name}</div>
        </div>
        <div class="track-location">{location}</div>
        <div class="track-divider"></div>
        <div class="track-stats-grid">
            <div class="track-stat-item">
                <div class="track-stat-label">Length</div>
                <div class="track-stat-value">{length:.2f} mi</div>
            </div>
            <div class="track-stat-item">
                <div class="track-stat-label">Lap Record</div>
                <div class="track-stat-value">{format_lap_time(lap_record)}</div>
            </div>
        </div>
    </div>
    """

    return card_html


def show_drivers_page():
    """Display driver cards grid"""
    # Check if database exists
    if not DATABASE_PATH.exists():
        st.error(f"❌ Database not found at {DATABASE_PATH}")
        st.info("📦 Please run the data pipeline first:")
        st.code("python src/pipeline/ingest_data.py", language="bash")
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
