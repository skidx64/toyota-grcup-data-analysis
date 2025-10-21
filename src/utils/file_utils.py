"""
Utility functions for finding and loading data files
"""

import os
import glob
from pathlib import Path
from typing import Optional, Dict, List
import pandas as pd

from src.config import DATA_DIR, TRACKS, FILE_PATTERNS


def get_track_race_path(track_code: str, race_num: int) -> Path:
    """
    Get the path to a specific track's race directory

    Args:
        track_code: Track code (e.g., 'COTA', 'BMP')
        race_num: Race number (1 or 2)

    Returns:
        Path to the race directory
    """
    if track_code not in TRACKS:
        raise ValueError(f"Unknown track code: {track_code}")

    track_dir = DATA_DIR / TRACKS[track_code]["directory"]
    race_dir = track_dir / f"Race {race_num}"

    if not race_dir.exists():
        raise FileNotFoundError(f"Race directory not found: {race_dir}")

    return race_dir


def find_file_by_pattern(directory: Path, pattern: str, **kwargs) -> Optional[Path]:
    """
    Find a file matching a pattern in a directory

    Args:
        directory: Directory to search
        pattern: File pattern with placeholders
        **kwargs: Values to format into the pattern

    Returns:
        Path to the file if found, None otherwise
    """
    formatted_pattern = pattern.format(**kwargs)

    # Handle glob patterns in the formatted string
    if '*' in formatted_pattern:
        matches = list(directory.glob(formatted_pattern))
        return matches[0] if matches else None

    file_path = directory / formatted_pattern
    return file_path if file_path.exists() else None


def load_lap_analysis(track_code: str, race_num: int) -> pd.DataFrame:
    """
    Load lap analysis data for a specific race

    Args:
        track_code: Track code (e.g., 'COTA', 'BMP')
        race_num: Race number (1 or 2)

    Returns:
        DataFrame with lap analysis data
    """
    race_dir = get_track_race_path(track_code, race_num)
    file_path = find_file_by_pattern(
        race_dir,
        FILE_PATTERNS["lap_analysis"],
        race_num=race_num
    )

    if file_path is None:
        raise FileNotFoundError(f"Lap analysis file not found for {track_code} Race {race_num}")

    df = pd.read_csv(file_path, sep=';')

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    df['track_code'] = track_code
    df['race_num'] = race_num

    return df


def load_race_results(track_code: str, race_num: int) -> pd.DataFrame:
    """
    Load race results for a specific race

    Args:
        track_code: Track code (e.g., 'COTA', 'BMP')
        race_num: Race number (1 or 2)

    Returns:
        DataFrame with race results
    """
    race_dir = get_track_race_path(track_code, race_num)
    file_path = find_file_by_pattern(
        race_dir,
        FILE_PATTERNS["results"],
        race_num=race_num
    )

    if file_path is None:
        raise FileNotFoundError(f"Results file not found for {track_code} Race {race_num}")

    df = pd.read_csv(file_path, sep=';')
    df['track_code'] = track_code
    df['race_num'] = race_num

    return df


def load_best_laps(track_code: str, race_num: int) -> pd.DataFrame:
    """
    Load best laps data for a specific race

    Args:
        track_code: Track code (e.g., 'COTA', 'BMP')
        race_num: Race number (1 or 2)

    Returns:
        DataFrame with best lap times
    """
    race_dir = get_track_race_path(track_code, race_num)
    file_path = find_file_by_pattern(
        race_dir,
        FILE_PATTERNS["best_laps"],
        race_num=race_num
    )

    if file_path is None:
        raise FileNotFoundError(f"Best laps file not found for {track_code} Race {race_num}")

    df = pd.read_csv(file_path, sep=';')
    df['track_code'] = track_code
    df['race_num'] = race_num

    return df


def load_weather(track_code: str, race_num: int) -> pd.DataFrame:
    """
    Load weather data for a specific race

    Args:
        track_code: Track code (e.g., 'COTA', 'BMP')
        race_num: Race number (1 or 2)

    Returns:
        DataFrame with weather data
    """
    race_dir = get_track_race_path(track_code, race_num)
    file_path = find_file_by_pattern(
        race_dir,
        FILE_PATTERNS["weather"],
        race_num=race_num
    )

    if file_path is None:
        print(f"Warning: Weather file not found for {track_code} Race {race_num}")
        return pd.DataFrame()

    df = pd.read_csv(file_path, sep=';')
    df['track_code'] = track_code
    df['race_num'] = race_num

    return df


def load_lap_boundaries(track_code: str, race_num: int) -> Dict[str, pd.DataFrame]:
    """
    Load lap boundary files (lap_time, lap_start, lap_end)

    Args:
        track_code: Track code (e.g., 'COTA', 'BMP')
        race_num: Race number (1 or 2)

    Returns:
        Dictionary with 'time', 'start', 'end' DataFrames
    """
    race_dir = get_track_race_path(track_code, race_num)
    track_prefix = TRACKS[track_code]["telemetry_prefix"]

    result = {}

    for key, pattern_key in [("time", "lap_time"), ("start", "lap_start"), ("end", "lap_end")]:
        file_path = find_file_by_pattern(
            race_dir,
            FILE_PATTERNS[pattern_key],
            track=track_prefix,
            race_num=race_num
        )

        if file_path and file_path.exists():
            result[key] = pd.read_csv(file_path)
            result[key]['track_code'] = track_code
            result[key]['race_num'] = race_num

    return result


def get_telemetry_file_path(track_code: str, race_num: int) -> Optional[Path]:
    """
    Find the telemetry file path for a specific race
    Handles multiple naming conventions

    Args:
        track_code: Track code (e.g., 'COTA', 'BMP')
        race_num: Race number (1 or 2)

    Returns:
        Path to telemetry file if found, None otherwise
    """
    race_dir = get_track_race_path(track_code, race_num)
    track_prefix = TRACKS[track_code]["telemetry_prefix"]

    # Try both naming patterns
    for pattern in FILE_PATTERNS["telemetry"]:
        file_path = find_file_by_pattern(
            race_dir,
            pattern,
            track=track_prefix,
            race_num=race_num
        )
        if file_path and file_path.exists():
            return file_path

    return None


def get_all_races() -> List[Dict[str, any]]:
    """
    Get a list of all available races

    Returns:
        List of dictionaries with track_code, race_num, and metadata
    """
    races = []

    for track_code, track_info in TRACKS.items():
        for race_num in [1, 2]:
            try:
                race_dir = get_track_race_path(track_code, race_num)
                telemetry_path = get_telemetry_file_path(track_code, race_num)

                races.append({
                    "track_code": track_code,
                    "track_name": track_info["name"],
                    "location": track_info["location"],
                    "race_num": race_num,
                    "race_dir": race_dir,
                    "has_telemetry": telemetry_path is not None,
                    "telemetry_path": telemetry_path
                })
            except FileNotFoundError:
                continue

    return races
