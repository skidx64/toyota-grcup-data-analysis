"""
DuckDB database schema for GR Cup Performance Intelligence Platform
"""

import duckdb
from pathlib import Path


def create_database(db_path: Path) -> duckdb.DuckDBPyConnection:
    """
    Create DuckDB database with all required tables

    Args:
        db_path: Path to the database file

    Returns:
        DuckDB connection
    """
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database (creates if doesn't exist)
    conn = duckdb.connect(str(db_path))

    # Create tables
    create_tables(conn)

    return conn


def create_tables(conn: duckdb.DuckDBPyConnection):
    """
    Create all database tables

    Args:
        conn: DuckDB connection
    """

    # Tracks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            track_code VARCHAR PRIMARY KEY,
            track_name VARCHAR NOT NULL,
            location VARCHAR,
            length_miles DOUBLE,
            total_races INTEGER
        )
    """)

    # Drivers table (aggregated from all races)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            driver_number INTEGER PRIMARY KEY,
            total_races INTEGER,
            best_finish INTEGER,
            total_laps INTEGER,
            avg_position DOUBLE,
            total_points DOUBLE
        )
    """)

    # Race results table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS race_results (
            id INTEGER PRIMARY KEY,
            track_code VARCHAR,
            race_num INTEGER,
            driver_number INTEGER,
            position INTEGER,
            status VARCHAR,
            laps INTEGER,
            total_time VARCHAR,
            gap_first VARCHAR,
            gap_previous VARCHAR,
            fastest_lap_num INTEGER,
            fastest_lap_time VARCHAR,
            fastest_lap_kph DOUBLE,
            class VARCHAR
        )
    """)

    # Lap times table (summary from lap analysis)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lap_times (
            id INTEGER PRIMARY KEY,
            track_code VARCHAR,
            race_num INTEGER,
            driver_number INTEGER,
            lap_number INTEGER,
            lap_time_seconds DOUBLE,
            lap_time_str VARCHAR,
            s1_time DOUBLE,
            s2_time DOUBLE,
            s3_time DOUBLE,
            top_speed DOUBLE,
            flag_at_fl VARCHAR,
            improvement_flag VARCHAR
        )
    """)

    # Telemetry aggregates (lap-level summaries)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_aggregates (
            id INTEGER PRIMARY KEY,
            track_code VARCHAR,
            race_num INTEGER,
            driver_number INTEGER,
            lap_number INTEGER,
            speed_max DOUBLE,
            speed_avg DOUBLE,
            speed_min DOUBLE,
            throttle_avg DOUBLE,
            throttle_max DOUBLE,
            brake_avg DOUBLE,
            brake_max DOUBLE,
            gforce_lat_max DOUBLE,
            gforce_lat_avg DOUBLE,
            gforce_long_max DOUBLE,
            gforce_long_avg DOUBLE,
            rpm_max INTEGER,
            rpm_avg INTEGER,
            gear_max INTEGER,
            telemetry_points INTEGER,
                    )
    """)

    # Weather conditions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY,
            track_code VARCHAR,
            race_num INTEGER,
            timestamp_utc INTEGER,
            air_temp DOUBLE,
            track_temp DOUBLE,
            humidity DOUBLE,
            pressure DOUBLE,
            wind_speed DOUBLE,
            wind_direction INTEGER,
            rain BOOLEAN,
                    )
    """)

    # Best laps per driver
    conn.execute("""
        CREATE TABLE IF NOT EXISTS best_laps (
            id INTEGER PRIMARY KEY,
            track_code VARCHAR,
            race_num INTEGER,
            driver_number INTEGER,
            best_lap_1 VARCHAR,
            best_lap_2 VARCHAR,
            best_lap_3 VARCHAR,
            best_lap_4 VARCHAR,
            best_lap_5 VARCHAR,
            best_lap_6 VARCHAR,
            best_lap_7 VARCHAR,
            best_lap_8 VARCHAR,
            best_lap_9 VARCHAR,
            best_lap_10 VARCHAR,
            average_best_laps VARCHAR,
                    )
    """)

    # Driver statistics (computed metrics for Phase 1)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS driver_stats (
            driver_number INTEGER PRIMARY KEY,
            overall_rating DOUBLE,
            braking_score DOUBLE,
            cornering_score DOUBLE,
            throttle_score DOUBLE,
            consistency_score DOUBLE,
            racecraft_score DOUBLE,
            qualifying_score DOUBLE,
            avg_lap_time_seconds DOUBLE,
            best_lap_time_seconds DOUBLE,
            total_podiums INTEGER,
                    )
    """)

    # Track statistics (computed metrics for Phase 1)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_stats (
            track_code VARCHAR PRIMARY KEY,
            lap_record_seconds DOUBLE,
            lap_record_driver INTEGER,
            avg_speed_kph DOUBLE,
            top_speed_kph DOUBLE,
            total_laps INTEGER,
            avg_lap_time_seconds DOUBLE,
            track_difficulty_score DOUBLE,
                    )
    """)

    print("[OK] Database schema created successfully")


def get_connection(db_path: Path) -> duckdb.DuckDBPyConnection:
    """
    Get a connection to an existing database

    Args:
        db_path: Path to the database file

    Returns:
        DuckDB connection
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    return duckdb.connect(str(db_path))
