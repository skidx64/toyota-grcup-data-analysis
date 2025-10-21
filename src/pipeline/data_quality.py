"""
Data Quality Checks and Cleaning for GR Cup Data Pipeline
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class DataQualityReport:
    """Track data quality metrics during ingestion"""

    def __init__(self):
        self.total_records = 0
        self.null_counts = {}
        self.outliers_removed = {}
        self.invalid_records = {}
        self.warnings = []

    def add_nulls(self, table: str, column: str, count: int):
        """Record null values found"""
        key = f"{table}.{column}"
        self.null_counts[key] = count

    def add_outliers(self, table: str, description: str, count: int):
        """Record outliers removed"""
        key = f"{table}: {description}"
        self.outliers_removed[key] = count

    def add_invalid(self, table: str, description: str, count: int):
        """Record invalid records"""
        key = f"{table}: {description}"
        self.invalid_records[key] = count

    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)

    def print_report(self):
        """Print comprehensive data quality report"""
        print("\n" + "="*70)
        print("DATA QUALITY REPORT")
        print("="*70)

        if self.null_counts:
            print("\n[NULL VALUES FOUND]")
            for key, count in sorted(self.null_counts.items()):
                if count > 0:
                    print(f"  {key}: {count:,} nulls")
        else:
            print("\n[NULL VALUES] None found")

        if self.outliers_removed:
            print("\n[OUTLIERS REMOVED]")
            for key, count in sorted(self.outliers_removed.items()):
                print(f"  {key}: {count:,} records")
        else:
            print("\n[OUTLIERS] None removed")

        if self.invalid_records:
            print("\n[INVALID RECORDS SKIPPED]")
            for key, count in sorted(self.invalid_records.items()):
                print(f"  {key}: {count:,} records")
        else:
            print("\n[INVALID RECORDS] None skipped")

        if self.warnings:
            print("\n[WARNINGS]")
            for warning in self.warnings:
                print(f"  - {warning}")
        else:
            print("\n[WARNINGS] None")

        print("\n" + "="*70 + "\n")


# Global report instance
quality_report = DataQualityReport()


def validate_lap_time(lap_time_seconds: float, track_code: str) -> bool:
    """
    Check if lap time is reasonable for the track

    Args:
        lap_time_seconds: Lap time in seconds
        track_code: Track identifier

    Returns:
        True if valid, False otherwise
    """
    if pd.isna(lap_time_seconds):
        return False

    # Track-specific reasonable lap time ranges (based on track length and expected speeds)
    track_ranges = {
        'BMP': (140, 200),    # Barber: 2.38 miles, technical
        'COTA': (145, 210),   # COTA: 3.41 miles, fast
        'RA': (130, 200),     # Road America: 4.05 miles, very fast
        'SEB': (140, 220),    # Sebring: 3.74 miles, bumpy
        'SON': (90, 160),     # Sonoma: 2.52 miles, technical
        'VIR': (100, 180)     # VIR: 3.27 miles, flowing
    }

    min_time, max_time = track_ranges.get(track_code, (60, 300))
    return min_time <= lap_time_seconds <= max_time


def clean_lap_times(df: pd.DataFrame, track_code: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Clean lap times data and remove outliers

    Args:
        df: DataFrame with lap times
        track_code: Track identifier

    Returns:
        Tuple of (cleaned DataFrame, stats dict)
    """
    stats = {
        'total_laps': len(df),
        'null_laps': 0,
        'outliers_removed': 0,
        'negative_times': 0,
        'extremely_slow': 0,
        'extremely_fast': 0
    }

    # Check for nulls
    stats['null_laps'] = df['lap_time_seconds'].isna().sum()
    quality_report.add_nulls('lap_times', 'lap_time_seconds', stats['null_laps'])

    # Remove null lap times
    df_clean = df[df['lap_time_seconds'].notna()].copy()

    # Remove negative or zero times (data errors)
    negative_mask = df_clean['lap_time_seconds'] <= 0
    stats['negative_times'] = negative_mask.sum()
    df_clean = df_clean[~negative_mask]

    # Track-specific outlier detection
    valid_mask = df_clean['lap_time_seconds'].apply(
        lambda x: validate_lap_time(x, track_code)
    )

    stats['outliers_removed'] = (~valid_mask).sum()
    df_clean = df_clean[valid_mask]

    # Log outliers removed
    if stats['outliers_removed'] > 0:
        quality_report.add_outliers(
            'lap_times',
            f'{track_code} invalid lap times',
            stats['outliers_removed']
        )

    if stats['negative_times'] > 0:
        quality_report.add_invalid(
            'lap_times',
            f'{track_code} negative/zero times',
            stats['negative_times']
        )

    return df_clean, stats


def clean_race_results(df: pd.DataFrame, track_code: str, race_num: int) -> Tuple[pd.DataFrame, Dict]:
    """
    Clean race results and handle missing values

    Args:
        df: DataFrame with race results
        track_code: Track identifier
        race_num: Race number

    Returns:
        Tuple of (cleaned DataFrame, stats dict)
    """
    stats = {
        'total_drivers': len(df),
        'missing_driver_numbers': 0,
        'missing_positions': 0,
        'invalid_positions': 0
    }

    # Check for missing driver numbers
    stats['missing_driver_numbers'] = df['driver_number'].isna().sum() + (df['driver_number'] == 0).sum()

    # Check for missing or invalid positions
    stats['missing_positions'] = df['position'].isna().sum()
    stats['invalid_positions'] = ((df['position'] <= 0) | (df['position'] > 50)).sum()

    # Log issues
    if stats['missing_driver_numbers'] > 0:
        quality_report.add_warning(
            f"{track_code} Race {race_num}: {stats['missing_driver_numbers']} records with missing driver numbers"
        )

    if stats['invalid_positions'] > 0:
        quality_report.add_warning(
            f"{track_code} Race {race_num}: {stats['invalid_positions']} records with invalid positions"
        )

    # Remove records with missing critical fields
    df_clean = df[
        (df['driver_number'] > 0) &
        (df['position'] > 0) &
        (df['position'] <= 50)
    ].copy()

    return df_clean, stats


def check_missing_fields(df: pd.DataFrame, required_fields: List[str], table_name: str) -> Dict:
    """
    Check for missing required fields

    Args:
        df: DataFrame to check
        required_fields: List of required column names
        table_name: Name of the table for reporting

    Returns:
        Dictionary of missing field counts
    """
    missing = {}

    for field in required_fields:
        if field in df.columns:
            null_count = df[field].isna().sum()
            if null_count > 0:
                missing[field] = null_count
                quality_report.add_nulls(table_name, field, null_count)
        else:
            quality_report.add_warning(f"{table_name}: Required field '{field}' not found in data")

    return missing


def validate_driver_consistency(lap_times_df: pd.DataFrame, results_df: pd.DataFrame) -> Dict:
    """
    Check if drivers in lap times match drivers in results

    Args:
        lap_times_df: Lap times data
        results_df: Race results data

    Returns:
        Dictionary with consistency stats
    """
    lap_drivers = set(lap_times_df['driver_number'].unique())
    result_drivers = set(results_df['driver_number'].unique())

    only_in_laps = lap_drivers - result_drivers
    only_in_results = result_drivers - lap_drivers

    if only_in_laps:
        quality_report.add_warning(
            f"Drivers in lap times but not results: {sorted(only_in_laps)}"
        )

    if only_in_results:
        quality_report.add_warning(
            f"Drivers in results but not lap times: {sorted(only_in_results)}"
        )

    return {
        'total_unique_drivers': len(lap_drivers | result_drivers),
        'only_in_laps': len(only_in_laps),
        'only_in_results': len(only_in_results),
        'in_both': len(lap_drivers & result_drivers)
    }


def detect_speed_outliers(df: pd.DataFrame, column: str = 'top_speed') -> pd.Series:
    """
    Detect speed outliers using IQR method

    Args:
        df: DataFrame with speed data
        column: Column name with speed values

    Returns:
        Boolean series indicating outliers
    """
    if column not in df.columns or df[column].isna().all():
        return pd.Series([False] * len(df), index=df.index)

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    # Define outliers as values outside 1.5*IQR
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = (df[column] < lower_bound) | (df[column] > upper_bound)

    return outliers


def get_quality_summary() -> str:
    """
    Get a summary string of data quality metrics

    Returns:
        Formatted summary string
    """
    total_nulls = sum(quality_report.null_counts.values())
    total_outliers = sum(quality_report.outliers_removed.values())
    total_invalid = sum(quality_report.invalid_records.values())

    summary = f"""
Data Quality Summary:
  - Null values handled: {total_nulls:,}
  - Outliers removed: {total_outliers:,}
  - Invalid records skipped: {total_invalid:,}
  - Warnings: {len(quality_report.warnings)}
"""
    return summary
