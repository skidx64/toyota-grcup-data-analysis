"""
Main data ingestion pipeline for GR Cup Performance Intelligence Platform

This script:
1. Loads CSV data from all 12 races
2. Processes and cleans the data
3. Aggregates telemetry to lap-level summaries
4. Populates DuckDB database
5. Calculates driver and track metrics
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import DATABASE_PATH, TRACKS
from src.database import create_database
from src.utils import (
    get_all_races,
    load_lap_analysis,
    load_race_results,
    load_best_laps,
    load_weather,
    get_telemetry_file_path
)


def time_to_seconds(time_str: str) -> float:
    """
    Convert lap time string to seconds

    Args:
        time_str: Time string (e.g., '2:28.630' or '3:46.084')

    Returns:
        Time in seconds
    """
    if pd.isna(time_str) or time_str == '':
        return np.nan

    try:
        # Handle format "M:SS.mmm"
        parts = str(time_str).split(':')
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    except:
        return np.nan


def clean_numeric(value: str) -> float:
    """Clean numeric values from CSV (remove +/- signs, etc.)"""
    if pd.isna(value):
        return np.nan

    try:
        return float(str(value).replace('+', '').replace(' ', ''))
    except:
        return np.nan


def ingest_tracks(conn):
    """
    Populate tracks table

    Args:
        conn: DuckDB connection
    """
    print("\\n[TRACKS] Ingesting track data...")

    tracks_data = []
    for track_code, track_info in TRACKS.items():
        tracks_data.append({
            'track_code': track_code,
            'track_name': track_info['name'],
            'location': track_info['location'],
            'length_miles': track_info['length_miles'],
            'total_races': 2  # All tracks have 2 races
        })

    df_tracks = pd.DataFrame(tracks_data)
    conn.execute("DELETE FROM tracks")
    conn.execute("INSERT INTO tracks SELECT * FROM df_tracks")

    print(f"[OK] Loaded {len(df_tracks)} tracks")


def ingest_race_results(conn):
    """
    Populate race_results table from all races

    Args:
        conn: DuckDB connection
    """
    print("\\n[RESULTS] Ingesting race results...")

    all_results = []
    races = get_all_races()

    for race_info in races:
        track_code = race_info['track_code']
        race_num = race_info['race_num']

        try:
            df = load_race_results(track_code, race_num)

            # Clean and rename columns
            df_clean = pd.DataFrame({
                'track_code': track_code,
                'race_num': race_num,
                'driver_number': pd.to_numeric(df['NUMBER'], errors='coerce').fillna(0).astype(int),
                'position': pd.to_numeric(df['POSITION'], errors='coerce').fillna(0).astype(int),
                'status': df['STATUS'].astype(str),
                'laps': pd.to_numeric(df['LAPS'], errors='coerce').fillna(0).astype(int),
                'total_time': df['TOTAL_TIME'].astype(str),
                'gap_first': df['GAP_FIRST'].astype(str),
                'gap_previous': df['GAP_PREVIOUS'].astype(str),
                'fastest_lap_num': pd.to_numeric(df['FL_LAPNUM'], errors='coerce').fillna(0).astype(int) if 'FL_LAPNUM' in df.columns else 0,
                'fastest_lap_time': df['FL_TIME'].astype(str) if 'FL_TIME' in df.columns else '',
                'fastest_lap_kph': pd.to_numeric(df['FL_KPH'], errors='coerce').fillna(0.0) if 'FL_KPH' in df.columns else 0.0,
                'class': df['CLASS'].astype(str)
            })

            all_results.append(df_clean)
            print(f"  + {track_code} Race {race_num}: {len(df_clean)} drivers")

        except Exception as e:
            print(f"  - {track_code} Race {race_num}: Error - {e}")

    if all_results:
        df_all = pd.concat(all_results, ignore_index=True)
        df_all['id'] = range(1, len(df_all) + 1)

        # Reorder columns to match table schema
        df_all = df_all[[
            'id', 'track_code', 'race_num', 'driver_number', 'position',
            'status', 'laps', 'total_time', 'gap_first', 'gap_previous',
            'fastest_lap_num', 'fastest_lap_time', 'fastest_lap_kph', 'class'
        ]]

        conn.execute("DELETE FROM race_results")
        conn.execute("INSERT INTO race_results SELECT * FROM df_all")

        print(f"\\n[OK] Loaded {len(df_all)} race results from {len(all_results)} races")
    else:
        print("\\n[WARN] No race results loaded")


def ingest_lap_times(conn):
    """
    Populate lap_times table from lap analysis files

    Args:
        conn: DuckDB connection
    """
    print("\\n[LAP TIMES] Ingesting lap times...")

    all_laps = []
    races = get_all_races()

    for race_info in races:
        track_code = race_info['track_code']
        race_num = race_info['race_num']

        try:
            df = load_lap_analysis(track_code, race_num)

            # Clean and rename columns
            df_clean = pd.DataFrame({
                'track_code': track_code,
                'race_num': race_num,
                'driver_number': pd.to_numeric(df['DRIVER_NUMBER'], errors='coerce').fillna(0).astype(int),
                'lap_number': pd.to_numeric(df['LAP_NUMBER'], errors='coerce').fillna(0).astype(int),
                'lap_time_str': df['LAP_TIME'].astype(str),
                'lap_time_seconds': df['LAP_TIME'].apply(time_to_seconds),
                's1_time': pd.to_numeric(df['S1_SECONDS'], errors='coerce') if 'S1_SECONDS' in df.columns else np.nan,
                's2_time': pd.to_numeric(df['S2_SECONDS'], errors='coerce') if 'S2_SECONDS' in df.columns else np.nan,
                's3_time': pd.to_numeric(df['S3_SECONDS'], errors='coerce') if 'S3_SECONDS' in df.columns else np.nan,
                'top_speed': pd.to_numeric(df['TOP_SPEED'], errors='coerce') if 'TOP_SPEED' in df.columns else np.nan,
                'flag_at_fl': df['FLAG_AT_FL'].astype(str) if 'FLAG_AT_FL' in df.columns else '',
                'improvement_flag': df['LAP_IMPROVEMENT'].astype(str) if 'LAP_IMPROVEMENT' in df.columns else ''
            })

            # Filter out invalid laps (extremely slow or outliers)
            df_clean = df_clean[df_clean['lap_time_seconds'] < 600]  # Less than 10 minutes

            all_laps.append(df_clean)
            print(f"  + {track_code} Race {race_num}: {len(df_clean)} laps")

        except Exception as e:
            print(f"  - {track_code} Race {race_num}: Error - {e}")

    if all_laps:
        df_all = pd.concat(all_laps, ignore_index=True)
        df_all['id'] = range(1, len(df_all) + 1)

        # Reorder columns to match table schema
        df_all = df_all[[
            'id', 'track_code', 'race_num', 'driver_number', 'lap_number',
            'lap_time_seconds', 'lap_time_str', 's1_time', 's2_time', 's3_time',
            'top_speed', 'flag_at_fl', 'improvement_flag'
        ]]

        conn.execute("DELETE FROM lap_times")
        conn.execute("INSERT INTO lap_times SELECT * FROM df_all")

        print(f"\\n[OK] Loaded {len(df_all)} lap times")
    else:
        print("\\n[WARN] No lap times loaded")


def ingest_best_laps(conn):
    """
    Populate best_laps table

    Args:
        conn: DuckDB connection
    """
    print("\\n[BEST LAPS] Ingesting best laps...")

    all_best_laps = []
    races = get_all_races()

    for race_info in races:
        track_code = race_info['track_code']
        race_num = race_info['race_num']

        try:
            df = load_best_laps(track_code, race_num)

            # The best laps file has columns like BESTLAP_1, BESTLAP_2, etc.
            df_clean = pd.DataFrame({
                'track_code': track_code,
                'race_num': race_num,
                'driver_number': pd.to_numeric(df['NUMBER'], errors='coerce').fillna(0).astype(int),
                'best_lap_1': df['BESTLAP_1'].astype(str) if 'BESTLAP_1' in df.columns else '',
                'best_lap_2': df['BESTLAP_2'].astype(str) if 'BESTLAP_2' in df.columns else '',
                'best_lap_3': df['BESTLAP_3'].astype(str) if 'BESTLAP_3' in df.columns else '',
                'best_lap_4': df['BESTLAP_4'].astype(str) if 'BESTLAP_4' in df.columns else '',
                'best_lap_5': df['BESTLAP_5'].astype(str) if 'BESTLAP_5' in df.columns else '',
                'best_lap_6': df['BESTLAP_6'].astype(str) if 'BESTLAP_6' in df.columns else '',
                'best_lap_7': df['BESTLAP_7'].astype(str) if 'BESTLAP_7' in df.columns else '',
                'best_lap_8': df['BESTLAP_8'].astype(str) if 'BESTLAP_8' in df.columns else '',
                'best_lap_9': df['BESTLAP_9'].astype(str) if 'BESTLAP_9' in df.columns else '',
                'best_lap_10': df['BESTLAP_10'].astype(str) if 'BESTLAP_10' in df.columns else '',
                'average_best_laps': df['AVERAGE'].astype(str) if 'AVERAGE' in df.columns else ''
            })

            all_best_laps.append(df_clean)
            print(f"  + {track_code} Race {race_num}: {len(df_clean)} drivers")

        except Exception as e:
            print(f"  - {track_code} Race {race_num}: Error - {e}")

    if all_best_laps:
        df_all = pd.concat(all_best_laps, ignore_index=True)
        df_all['id'] = range(1, len(df_all) + 1)

        # Reorder columns to match table schema
        df_all = df_all[[
            'id', 'track_code', 'race_num', 'driver_number',
            'best_lap_1', 'best_lap_2', 'best_lap_3', 'best_lap_4', 'best_lap_5',
            'best_lap_6', 'best_lap_7', 'best_lap_8', 'best_lap_9', 'best_lap_10',
            'average_best_laps'
        ]]

        conn.execute("DELETE FROM best_laps")
        conn.execute("INSERT INTO best_laps SELECT * FROM df_all")

        print(f"\\n[OK] Loaded {len(df_all)} best lap records")
    else:
        print("\\n[WARN] No best laps loaded")


def ingest_weather(conn):
    """
    Populate weather table

    Args:
        conn: DuckDB connection
    """
    print("\\n[WEATHER] Ingesting weather data...")

    all_weather = []
    races = get_all_races()

    for race_info in races:
        track_code = race_info['track_code']
        race_num = race_info['race_num']

        try:
            df = load_weather(track_code, race_num)

            if df.empty:
                continue

            df_clean = pd.DataFrame({
                'track_code': track_code,
                'race_num': race_num,
                'timestamp_utc': df['TIME_UTC_SECONDS'].astype(int),
                'air_temp': df['AIR_TEMP'].astype(float),
                'track_temp': df['TRACK_TEMP'].astype(float),
                'humidity': df['HUMIDITY'].astype(float),
                'pressure': df['PRESSURE'].astype(float),
                'wind_speed': df['WIND_SPEED'].astype(float),
                'wind_direction': df['WIND_DIRECTION'].astype(int),
                'rain': df['RAIN'].astype(int) > 0
            })

            all_weather.append(df_clean)
            print(f"  + {track_code} Race {race_num}: {len(df_clean)} weather records")

        except Exception as e:
            print(f"  - {track_code} Race {race_num}: Skipped - {e}")

    if all_weather:
        df_all = pd.concat(all_weather, ignore_index=True)
        df_all['id'] = range(1, len(df_all) + 1)

        # Reorder columns to match table schema
        df_all = df_all[[
            'id', 'track_code', 'race_num', 'timestamp_utc',
            'air_temp', 'track_temp', 'humidity', 'pressure',
            'wind_speed', 'wind_direction', 'rain'
        ]]

        conn.execute("DELETE FROM weather")
        conn.execute("INSERT INTO weather SELECT * FROM df_all")

        print(f"\\n[OK] Loaded {len(df_all)} weather records")
    else:
        print("\\n[WARN] No weather data loaded")


def compute_driver_aggregates(conn):
    """
    Compute driver-level aggregates from race results and lap times

    Args:
        conn: DuckDB connection
    """
    print("\\n[DRIVERS] Computing driver aggregates...")

    # Get unique drivers from race results
    df_drivers = conn.execute("""
        SELECT
            driver_number,
            COUNT(DISTINCT track_code || '_' || race_num) as total_races,
            MIN(position) as best_finish,
            SUM(laps) as total_laps,
            AVG(position) as avg_position
        FROM race_results
        GROUP BY driver_number
    """).df()

    # Add placeholder for points (can be calculated later)
    df_drivers['total_points'] = 0.0

    conn.execute("DELETE FROM drivers")
    conn.execute("INSERT INTO drivers SELECT * FROM df_drivers")

    print(f"[OK] Loaded {len(df_drivers)} drivers")


def compute_driver_stats(conn):
    """
    Compute driver statistics for Phase 1 (FIFA-style ratings)

    Args:
        conn: DuckDB connection
    """
    print("\\n[STATS] Computing driver statistics...")

    # Get lap time statistics per driver
    df_stats = conn.execute("""
        SELECT
            driver_number,
            AVG(lap_time_seconds) as avg_lap_time_seconds,
            MIN(lap_time_seconds) as best_lap_time_seconds,
            STDDEV(lap_time_seconds) as lap_time_stddev,
            COUNT(*) as total_laps
        FROM lap_times
        WHERE lap_time_seconds IS NOT NULL
          AND lap_time_seconds > 0
        GROUP BY driver_number
    """).df()

    # Normalize scores to 0-100 scale (will be refined in Phase 1)
    # For now, use placeholder calculations
    df_stats['consistency_score'] = 100 - (df_stats['lap_time_stddev'] * 10).clip(0, 100)
    df_stats['qualifying_score'] = 75.0  # Placeholder
    df_stats['braking_score'] = 75.0  # Placeholder (requires telemetry)
    df_stats['cornering_score'] = 75.0  # Placeholder (requires telemetry)
    df_stats['throttle_score'] = 75.0  # Placeholder (requires telemetry)
    df_stats['racecraft_score'] = 75.0  # Placeholder (requires results analysis)

    # Overall rating (average of sub-scores)
    df_stats['overall_rating'] = df_stats[[
        'braking_score', 'cornering_score', 'throttle_score',
        'consistency_score', 'racecraft_score', 'qualifying_score'
    ]].mean(axis=1)

    # Count podiums
    df_podiums = conn.execute("""
        SELECT driver_number, COUNT(*) as total_podiums
        FROM race_results
        WHERE position <= 3
        GROUP BY driver_number
    """).df()

    df_stats = df_stats.merge(df_podiums, on='driver_number', how='left')
    df_stats['total_podiums'] = df_stats['total_podiums'].fillna(0).astype(int)

    # Select only columns that exist in driver_stats table
    df_final = df_stats[[
        'driver_number', 'overall_rating', 'braking_score', 'cornering_score',
        'throttle_score', 'consistency_score', 'racecraft_score', 'qualifying_score',
        'avg_lap_time_seconds', 'best_lap_time_seconds', 'total_podiums'
    ]]

    conn.execute("DELETE FROM driver_stats")
    conn.execute("INSERT INTO driver_stats SELECT * FROM df_final")

    print(f"[OK] Computed stats for {len(df_stats)} drivers")


def compute_track_stats(conn):
    """
    Compute track-level statistics for Phase 1

    Args:
        conn: DuckDB connection
    """
    print("\\n[RESULTS] Computing track statistics...")

    df_stats = conn.execute("""
        SELECT
            lt.track_code,
            MIN(lt.lap_time_seconds) as lap_record_seconds,
            AVG(lt.lap_time_seconds) as avg_lap_time_seconds,
            MAX(lt.top_speed) as top_speed_kph,
            COUNT(*) as total_laps
        FROM lap_times lt
        WHERE lt.lap_time_seconds IS NOT NULL
          AND lt.lap_time_seconds > 0
        GROUP BY lt.track_code
    """).df()

    # Find lap record holder
    df_record_holders = conn.execute("""
        SELECT DISTINCT ON (lt.track_code)
            lt.track_code,
            lt.driver_number as lap_record_driver
        FROM lap_times lt
        WHERE lt.lap_time_seconds IS NOT NULL
        ORDER BY lt.track_code, lt.lap_time_seconds ASC
    """).df()

    df_stats = df_stats.merge(df_record_holders, on='track_code', how='left')

    # Calculate average speed (track_length / lap_time)
    df_tracks = conn.execute("SELECT track_code, length_miles FROM tracks").df()
    df_stats = df_stats.merge(df_tracks, on='track_code', how='left')

    df_stats['avg_speed_kph'] = (df_stats['length_miles'] * 1.60934) / (df_stats['avg_lap_time_seconds'] / 3600)

    # Difficulty score (placeholder - will refine in Phase 1)
    df_stats['track_difficulty_score'] = 75.0

    df_stats = df_stats.drop(columns=['length_miles'])

    conn.execute("DELETE FROM track_stats")
    conn.execute("INSERT INTO track_stats SELECT * FROM df_stats")

    print(f"[OK] Computed stats for {len(df_stats)} tracks")


def main():
    """Main data ingestion pipeline"""

    print("=" * 70)
    print("GR CUP PERFORMANCE INTELLIGENCE PLATFORM")
    print("=" * 70)
    print("\\nWeek 1: Data Pipeline Ingestion\\n")

    start_time = time.time()

    # Create database
    print("\\n[DATABASE] Creating database...")
    conn = create_database(DATABASE_PATH)
    print(f"[OK] Database created at: {DATABASE_PATH}")

    # Ingest data
    ingest_tracks(conn)
    ingest_race_results(conn)
    ingest_lap_times(conn)
    ingest_best_laps(conn)
    ingest_weather(conn)

    # Compute aggregates
    compute_driver_aggregates(conn)
    compute_driver_stats(conn)
    compute_track_stats(conn)

    # Close connection
    conn.close()

    elapsed = time.time() - start_time
    print("\\n" + "=" * 70)
    print(f"PIPELINE COMPLETE in {elapsed:.2f} seconds")
    print("=" * 70)
    print(f"\\nDatabase ready at: {DATABASE_PATH}")
    print("\\nNext steps:")
    print("   - Week 2: Build Streamlit app with driver/track cards")
    print("   - Week 3: Add detail views with 6 widgets")
    print("   - Week 4: Implement simple search feature\\n")


if __name__ == "__main__":
    main()
