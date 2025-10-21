"""
Configuration file for GR Cup Performance Intelligence Platform
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT  # Track folders are in project root
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

# Track configurations
TRACKS = {
    "BMP": {
        "name": "Barber Motorsports Park",
        "location": "Alabama",
        "directory": "barber-motorsports-park/BMP",
        "length_miles": 2.38,
        "telemetry_prefix": "barber"
    },
    "COTA": {
        "name": "Circuit of the Americas",
        "location": "Texas",
        "directory": "circuit-of-the-americas/COTA",
        "length_miles": 3.41,
        "telemetry_prefix": "cota"
    },
    "RA": {
        "name": "Road America",
        "location": "Wisconsin",
        "directory": "road-america/Road America",
        "length_miles": 4.05,
        "telemetry_prefix": "road_america"
    },
    "SEB": {
        "name": "Sebring International Raceway",
        "location": "Florida",
        "directory": "sebring/Sebring",
        "length_miles": 3.74,
        "telemetry_prefix": "sebring"
    },
    "SON": {
        "name": "Sonoma Raceway",
        "location": "California",
        "directory": "sonoma/Sonoma",
        "length_miles": 2.52,
        "telemetry_prefix": "sonoma"
    },
    "VIR": {
        "name": "Virginia International Raceway",
        "location": "Virginia",
        "directory": "virginia-international-raceway/VIR",
        "length_miles": 3.27,
        "telemetry_prefix": "vir"
    }
}

# File naming patterns
FILE_PATTERNS = {
    "telemetry": [
        "R{race_num}_{track}_telemetry_data.csv",
        "{track}_telemetry_R{race_num}.csv"  # Sonoma variant
    ],
    "lap_analysis": "23_AnalysisEnduranceWithSections_Race {race_num}_Anonymized.CSV",
    "best_laps": "99_Best 10 Laps By Driver_Race {race_num}_Anonymized.CSV",
    "weather": "26_Weather_Race {race_num}_Anonymized.CSV",
    "results": "03_Provisional Results_Race {race_num}_Anonymized.CSV",
    "class_results": "05_*Results*Class_Race {race_num}_Anonymized.CSV",
    "lap_time": "{track}_lap_time_R{race_num}.csv",
    "lap_start": "{track}_lap_start_time_R{race_num}.csv",
    "lap_end": "{track}_lap_end_time_R{race_num}.csv"
}

# Database configuration
DATABASE_PATH = PROCESSED_DATA_DIR / "driver_stats.db"

# Data processing parameters
TELEMETRY_SAMPLE_RATE = 100  # Hz
LAP_AGGREGATION_METRICS = [
    "speed_max",
    "speed_avg",
    "speed_min",
    "throttle_avg",
    "brake_avg",
    "gforce_lat_max",
    "gforce_long_max"
]

# Known telemetry field names (from COTA sample)
TELEMETRY_FIELDS = {
    "accx_can": "Longitudinal acceleration (G-force)",
    "accy_can": "Lateral acceleration (G-force)",
    "vcar": "Vehicle speed",
    "gear": "Current gear",
    "aps": "Accelerator pedal position (throttle)",
    "pbrake_f": "Front brake pressure",
    "pbrake_r": "Rear brake pressure",
    "steer_ang": "Steering angle",
    "nmot": "Engine RPM",
    "VBOX_Long_Minutes": "GPS Longitude",
    "VBOX_Lat_Min": "GPS Latitude",
    "Laptrigger_lapdist_dls": "Lap distance"
}

# UI Configuration (for Week 2+)
DRIVER_CARD_RATINGS = [
    "braking",
    "cornering",
    "throttle_control",
    "consistency",
    "racecraft",
    "qualifying"
]

TRACK_CARD_STATS = [
    "lap_record",
    "avg_speed",
    "top_speed",
    "sector_count",
    "total_laps"
]
