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
    initial_sidebar_state="expanded"
)


# Custom CSS for FIFA-style cards
def load_custom_css():
    st.markdown("""
    <style>
    /* FIFA-style card styling */
    .driver-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        margin: 10px;
        transition: transform 0.2s;
    }

    .driver-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
    }

    .track-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        margin: 10px;
        transition: transform 0.2s;
    }

    .track-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
    }

    .card-rating {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }

    .card-name {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }

    .card-stat {
        display: flex;
        justify-content: space-between;
        margin: 5px 0;
        font-size: 14px;
    }

    .stat-label {
        opacity: 0.9;
    }

    .stat-value {
        font-weight: bold;
    }

    /* Locked feature styling */
    .locked-feature {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Navigation styling */
    .nav-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
    }

    .nav-item:hover {
        background-color: rgba(255,255,255,0.1);
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


def render_driver_card(driver_row):
    """Render a single driver card in FIFA style"""
    driver_num = int(driver_row['driver_number'])
    rating = int(driver_row.get('overall_rating', 75)) if pd.notna(driver_row.get('overall_rating')) else 75
    best_finish = int(driver_row['best_finish'])
    total_races = int(driver_row['total_races'])
    total_podiums = int(driver_row.get('total_podiums', 0)) if pd.notna(driver_row.get('total_podiums')) else 0

    # Determine card color based on rating
    if rating >= 85:
        card_class = "driver-card"
        card_color = "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)"  # Gold
    elif rating >= 75:
        card_class = "driver-card"
        card_color = "linear-gradient(135deg, #C0C0C0 0%, #808080 100%)"  # Silver
    else:
        card_class = "driver-card"
        card_color = "linear-gradient(135deg, #CD7F32 0%, #8B4513 100%)"  # Bronze

    card_html = f"""
    <div class="{card_class}" style="background: {card_color};">
        <div class="card-rating">{rating}</div>
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
            <span class="stat-value">P{driver_row['avg_position']:.1f}</span>
        </div>
    </div>
    """

    return card_html


def render_track_card(track_row):
    """Render a single track card in FIFA style"""
    track_code = track_row['track_code']
    track_name = track_row['track_name']
    location = track_row['location']
    length = float(track_row['length_miles'])
    lap_record = track_row.get('lap_record_seconds', 0)

    card_html = f"""
    <div class="track-card">
        <div class="card-name">{track_code}</div>
        <div style="text-align: center; font-size: 18px; margin-bottom: 10px;">{track_name}</div>
        <div class="card-stat">
            <span class="stat-label">Location:</span>
            <span class="stat-value">{location}</span>
        </div>
        <div class="card-stat">
            <span class="stat-label">Length:</span>
            <span class="stat-value">{length:.2f} miles</span>
        </div>
        <div class="card-stat">
            <span class="stat-label">Lap Record:</span>
            <span class="stat-value">{format_lap_time(lap_record)}</span>
        </div>
        <div class="card-stat">
            <span class="stat-label">Total Laps:</span>
            <span class="stat-value">{int(track_row.get('total_laps', 0))}</span>
        </div>
    </div>
    """

    return card_html


def show_drivers_page():
    """Display driver cards grid"""
    st.title("📊 Driver Profiling")

    # Check if database exists
    if not DATABASE_PATH.exists():
        st.error(f"❌ Database not found at {DATABASE_PATH}")
        st.info("📦 Please run the data pipeline first:")
        st.code("python src/pipeline/ingest_data.py", language="bash")
        return

    # Load drivers
    drivers_df = get_all_drivers()

    if drivers_df.empty:
        st.warning("No driver data available")
        return

    st.write(f"**{len(drivers_df)} drivers** across the championship")

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        min_races = st.slider("Minimum races", 1, int(drivers_df['total_races'].max()), 1)
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
            # Add click handler (placeholder for Week 3)
            if st.button(f"View Details", key=f"driver_{driver['driver_number']}"):
                st.info("🚧 Driver detail view coming in Week 3!")


def show_tracks_page():
    """Display track cards grid"""
    st.title("🏁 Track Analysis")

    # Check if database exists
    if not DATABASE_PATH.exists():
        st.error(f"❌ Database not found")
        return

    # Load tracks
    tracks_df = get_all_tracks()

    if tracks_df.empty:
        st.warning("No track data available")
        return

    st.write(f"**{len(tracks_df)} championship tracks**")

    # Display cards in grid (3 columns for tracks)
    num_cols = 3
    cols = st.columns(num_cols)

    for idx, (_, track) in enumerate(tracks_df.iterrows()):
        col_idx = idx % num_cols
        with cols[col_idx]:
            st.markdown(render_track_card(track), unsafe_allow_html=True)
            # Add click handler (placeholder for Week 3)
            if st.button(f"View Details", key=f"track_{track['track_code']}"):
                st.info("🚧 Track detail view coming in Week 3!")


def show_search_page():
    """Simple search placeholder"""
    st.title("❓ Ask Questions")
    st.info("🚧 Week 4: Simple search feature coming soon...")
    st.write("Ask questions like:")
    st.write("- 'Who is the fastest driver?'")
    st.write("- 'Show Driver 13 stats'")
    st.write("- 'Track records at COTA'")


def main():
    """Main application entry point"""

    # Load custom CSS
    load_custom_css()

    # Sidebar navigation
    st.sidebar.title("🏎️ GR Cup Intelligence")

    # Get database summary for sidebar
    if DATABASE_PATH.exists():
        summary = get_database_summary()
        st.sidebar.metric("Tracks", summary['total_tracks'])
        st.sidebar.metric("Drivers", summary['total_drivers'])
        st.sidebar.metric("Total Laps", f"{summary['total_laps']:,}")

    st.sidebar.markdown("---")

    # Navigation
    nav_options = {
        "📊 Drivers": "drivers",
        "🏁 Tracks": "tracks",
        "❓ Ask Questions": "search",
        "🎯 Training": "training",
        "🔮 Predictions": "predictions",
        "📈 Analytics": "analytics",
        "✨ Extras": "extras"
    }

    # Phase 1: Only Drivers, Tracks, and Ask Questions are active
    active_pages = ["drivers", "tracks", "search"]

    # Create navigation with locked indicator
    nav_labels = []
    for label, page in nav_options.items():
        if page in active_pages:
            nav_labels.append(label)
        else:
            nav_labels.append(f"{label} 🔒")

    selected = st.sidebar.radio("Navigation", nav_labels)

    # Extract page from selection
    selected_label = selected.replace(" 🔒", "")
    page = nav_options[selected_label]

    # Route to appropriate page
    if page == "drivers":
        show_drivers_page()
    elif page == "tracks":
        show_tracks_page()
    elif page == "search":
        show_search_page()
    elif page in ["training", "predictions", "analytics", "extras"]:
        st.title(f"{selected_label}")
        st.warning("🔒 This feature will be unlocked in a future phase")

        phase_info = {
            "training": "Phase 2 (Weeks 5-6)",
            "predictions": "Phase 3 (Weeks 7-9)",
            "analytics": "Phase 4 (Weeks 10-12)",
            "extras": "Phase 6 (Week 15)"
        }
        st.write(f"**Coming in:** {phase_info.get(page, 'Future phase')}")

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("🏎️ GR Cup Performance Intelligence Platform")
    st.sidebar.caption("Phase 1: Driver & Track Profiling")


if __name__ == "__main__":
    main()
