"""
Database queries for Streamlit app
"""

import duckdb
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.config import DATABASE_PATH


def get_connection():
    """Get database connection"""
    return duckdb.connect(str(DATABASE_PATH), read_only=True)


def get_all_drivers():
    """Get all drivers with their stats"""
    conn = get_connection()

    query = """
        SELECT
            d.driver_number,
            d.total_races,
            d.best_finish,
            d.total_laps,
            d.avg_position,
            ds.overall_rating,
            ds.braking_score,
            ds.cornering_score,
            ds.throttle_score,
            ds.consistency_score,
            ds.racecraft_score,
            ds.qualifying_score,
            ds.best_lap_time_seconds,
            ds.avg_lap_time_seconds,
            ds.total_podiums
        FROM drivers d
        LEFT JOIN driver_stats ds ON d.driver_number = ds.driver_number
        ORDER BY d.best_finish, d.avg_position
    """

    df = conn.execute(query).df()
    conn.close()
    return df


def get_driver_details(driver_number: int):
    """Get detailed stats for a specific driver"""
    conn = get_connection()

    # Basic info
    driver_info = conn.execute("""
        SELECT * FROM drivers WHERE driver_number = ?
    """, [driver_number]).df()

    # Stats
    driver_stats = conn.execute("""
        SELECT * FROM driver_stats WHERE driver_number = ?
    """, [driver_number]).df()

    # Race results
    race_results = conn.execute("""
        SELECT track_code, race_num, position, laps, fastest_lap_time
        FROM race_results
        WHERE driver_number = ?
        ORDER BY track_code, race_num
    """, [driver_number]).df()

    # Best laps per track
    best_laps = conn.execute("""
        SELECT
            track_code,
            MIN(lap_time_seconds) as best_lap_seconds
        FROM lap_times
        WHERE driver_number = ?
        GROUP BY track_code
        ORDER BY track_code
    """, [driver_number]).df()

    conn.close()

    return {
        'info': driver_info,
        'stats': driver_stats,
        'results': race_results,
        'best_laps': best_laps
    }


def get_all_tracks():
    """Get all tracks with their stats"""
    conn = get_connection()

    query = """
        SELECT
            t.track_code,
            t.track_name,
            t.location,
            t.length_miles,
            t.total_races,
            ts.lap_record_seconds,
            ts.lap_record_driver,
            ts.avg_speed_kph,
            ts.top_speed_kph,
            ts.total_laps,
            ts.avg_lap_time_seconds
        FROM tracks t
        LEFT JOIN track_stats ts ON t.track_code = ts.track_code
        ORDER BY t.track_name
    """

    df = conn.execute(query).df()
    conn.close()
    return df


def get_track_details(track_code: str):
    """Get detailed stats for a specific track"""
    conn = get_connection()

    # Basic info
    track_info = conn.execute("""
        SELECT * FROM tracks WHERE track_code = ?
    """, [track_code]).df()

    # Stats
    track_stats = conn.execute("""
        SELECT * FROM track_stats WHERE track_code = ?
    """, [track_code]).df()

    # Race results for this track
    race_results = conn.execute("""
        SELECT race_num, driver_number, position, fastest_lap_time
        FROM race_results
        WHERE track_code = ?
        ORDER BY race_num, position
        LIMIT 10
    """, [track_code]).df()

    # Fastest laps at this track
    fastest_laps = conn.execute("""
        SELECT
            driver_number,
            MIN(lap_time_seconds) as best_lap_seconds
        FROM lap_times
        WHERE track_code = ?
        GROUP BY driver_number
        ORDER BY best_lap_seconds
        LIMIT 10
    """, [track_code]).df()

    conn.close()

    return {
        'info': track_info,
        'stats': track_stats,
        'results': race_results,
        'fastest_laps': fastest_laps
    }


def get_database_summary():
    """Get summary statistics for the database"""
    conn = get_connection()

    summary = {
        'total_tracks': conn.execute('SELECT COUNT(*) FROM tracks').fetchone()[0],
        'total_drivers': conn.execute('SELECT COUNT(*) FROM drivers').fetchone()[0],
        'total_races': conn.execute('SELECT COUNT(DISTINCT track_code || race_num) FROM race_results').fetchone()[0],
        'total_laps': conn.execute('SELECT COUNT(*) FROM lap_times').fetchone()[0],
        'total_results': conn.execute('SELECT COUNT(*) FROM race_results').fetchone()[0],
    }

    conn.close()
    return summary
