# Data Quality Checks - GR Cup Performance Intelligence Platform

## Overview

This document outlines all data quality measures implemented in the data pipeline.

---

## 1. Null Value Handling

### Strategy
- **Detect**: Track all null values by table and column
- **Report**: Generate summary of null counts
- **Handle**: Different strategies based on field importance

### Implementation

| Field Type | Null Handling Strategy | Rationale |
|------------|----------------------|-----------|
| **Critical IDs** (driver_number, lap_number) | **Remove record** | Cannot process without identifier |
| **Lap times** | **Remove record** | Core metric, cannot be missing |
| **Position** | **Remove record** | Essential for race results |
| **Optional fields** (weather, sector times) | **Keep as NULL** | Analysis can work without these |
| **Numeric calculations** | **Skip in calculations** | Use `.notna()` filters in aggregations |

### Example
```python
# Before: Filling all nulls with 0 (WRONG)
df['driver_number'] = df['driver_number'].fillna(0)  # ❌ Creates fake driver "0"

# After: Remove records with null critical fields (RIGHT)
df_clean = df[df['driver_number'].notna()]  # ✅ Only valid drivers
```

---

## 2. Outlier Detection

### Lap Times - Track-Specific Ranges

We validate lap times based on realistic ranges for each track:

| Track | Min Lap Time | Max Lap Time | Reasoning |
|-------|--------------|--------------|-----------|
| **Barber (BMP)** | 140s (2:20) | 200s (3:20) | Technical, 2.38 miles |
| **COTA** | 145s (2:25) | 210s (3:30) | Long, 3.41 miles |
| **Road America** | 130s (2:10) | 200s (3:20) | Fastest track, 4.05 miles |
| **Sebring** | 140s (2:20) | 220s (3:40) | Bumpy, 3.74 miles |
| **Sonoma** | 90s (1:30) | 160s (2:40) | Shortest, 2.52 miles |
| **VIR** | 100s (1:40) | 180s (3:00) | Flowing, 3.27 miles |

**Outliers Removed:**
- Laps faster than minimum (data errors, incomplete laps)
- Laps slower than maximum (caution laps, pit laps, incidents)

### Speed Outliers - IQR Method

For top speeds, we use the Interquartile Range (IQR) method:

```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1

Lower bound = Q1 - 1.5 * IQR
Upper bound = Q3 + 1.5 * IQR

Outlier = speed < lower_bound OR speed > upper_bound
```

**Example:** If top speeds are normally 180-205 kph:
- Remove: 50 kph (data error)
- Remove: 350 kph (impossible for GR86)

### Position Validation

- **Valid range**: 1 to 50 (no more than 50 cars in a race)
- **Remove**: position = 0, negative, or > 50

---

## 3. Data Type Validation

### Numeric Fields

All numeric conversions use safe coercion:

```python
# Safe conversion
pd.to_numeric(df['field'], errors='coerce')
# - Valid numbers → converted
# - Invalid values → NaN
# - Then we decide: remove or keep as null
```

### Time Conversions

Lap time strings ("2:30.123") converted to seconds:

```python
def time_to_seconds(time_str):
    if pd.isna(time_str) or time_str == '':
        return np.nan  # Keep as null
    try:
        minutes, seconds = parse_time(time_str)
        return minutes * 60 + seconds
    except:
        return np.nan  # Invalid format → null
```

---

## 4. Consistency Checks

### Driver Consistency Across Files

Check if drivers appearing in lap times also appear in results:

- **Lap times but no results** → Warning (incomplete data)
- **Results but no lap times** → Warning (DNS/DNF?)
- **Report**: List of mismatched driver numbers

### File Completeness

Track which races have complete vs incomplete data:

| Track | Race 1 | Race 2 | Issues |
|-------|--------|--------|--------|
| BMP | ✅ Complete | ✅ Complete | None |
| COTA | ✅ Complete | ⚠️ Incomplete | Missing results file |
| Road America | ✅ Complete | ✅ Complete | None |
| Sebring | ⚠️ Incomplete | ✅ Complete | Missing telemetry |
| Sonoma | ⚠️ Incomplete | ⚠️ Incomplete | Missing results, weather |
| VIR | ✅ Complete | ✅ Complete | None |

---

## 5. Data Quality Report

After pipeline runs, generate comprehensive report:

```
======================================================================
DATA QUALITY REPORT
======================================================================

[NULL VALUES FOUND]
  lap_times.lap_time_seconds: 143 nulls
  race_results.fastest_lap_kph: 5 nulls

[OUTLIERS REMOVED]
  lap_times: COTA invalid lap times: 37 records
  lap_times: BMP invalid lap times: 12 records

[INVALID RECORDS SKIPPED]
  lap_times: VIR negative/zero times: 3 records
  race_results: Invalid positions: 2 records

[WARNINGS]
  - COTA Race 2: Results file not found
  - Sonoma Race 1: 2 records with missing driver numbers
  - Drivers in lap times but not results: [47, 83]

======================================================================
```

---

## 6. What We DON'T Fix

**We preserve original data anomalies that might be real:**

1. **Extremely consistent lap times** (might be a fast driver!)
2. **Large performance variations** (might be traffic, tire deg)
3. **Missing sector splits** (some tracks don't have all splits)
4. **Weather gaps** (only recorded every minute, not every lap)

**Philosophy**: Remove obvious errors, keep unusual but possibly valid data.

---

## 7. Usage in Pipeline

```python
from src.pipeline.data_quality import (
    clean_lap_times,
    clean_race_results,
    quality_report
)

# Clean lap times with track-specific validation
df_clean, stats = clean_lap_times(df, track_code='COTA')

# Clean race results
df_clean, stats = clean_race_results(df, track_code='BMP', race_num=1)

# At end of pipeline
quality_report.print_report()
```

---

## 8. Future Enhancements

**For Phase 2+ (when we analyze telemetry):**

- Detect sensor failures (GPS dropouts, speed = 0 for extended periods)
- Validate throttle/brake ranges (0-100%)
- Check for impossible G-force values
- Detect missing telemetry chunks

**For Phase 3+ (predictions):**

- Flag races with weather anomalies
- Detect practice vs qualifying vs race sessions
- Identify red flag periods

---

## Summary

✅ **We check for:**
- Null values in all fields
- Outlier lap times (track-specific)
- Invalid positions, driver numbers
- Speed outliers (statistical)
- Data consistency across files

✅ **We handle by:**
- Removing records with critical nulls
- Keeping optional nulls for analysis
- Removing statistical outliers
- Logging all issues in quality report

✅ **We report:**
- Comprehensive summary after pipeline runs
- Warnings for missing files
- Counts of nulls, outliers, invalid records
