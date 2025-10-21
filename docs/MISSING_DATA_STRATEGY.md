# Missing Data Handling Strategy

## Overview

Our dataset has some incomplete races. This document explains how we handle them.

---

## Missing Data Summary

| Track | Race | Missing Files | Impact | Status |
|-------|------|--------------|--------|--------|
| **COTA** | Race 2 | Results, Lap Analysis | Cannot analyze this race | ❌ **Exclude** |
| **Sebring** | Race 1 | Telemetry only | Can still analyze laps, results, weather | ✅ **Include** |
| **Sonoma** | Race 2 | Weather only | Can still analyze laps, results, telemetry | ✅ **Include** |
| **Sonoma** | Race 1 & 2 | Official Results | Have best laps and lap times | ⚠️ **Partial** |

---

## Strategy: Keep What We Have

### Philosophy
**"Partial data is better than no data"**

We keep races with missing files because:
1. **Most analyses don't need ALL files** - If we're analyzing lap times, we don't need weather
2. **Week 1 doesn't use telemetry** - We're building driver cards from lap times/results only
3. **Graceful degradation** - Features that need missing data simply show "N/A"

---

## How We Handle It

### 1. In the Database
**Action**: Load what exists, leave gaps as NULL

```sql
-- Sebring Race 1: Has lap times, NO telemetry
SELECT * FROM lap_times WHERE track_code = 'SEB' AND race_num = 1;
-- ✅ Returns 401 laps

SELECT * FROM telemetry_aggregates WHERE track_code = 'SEB' AND race_num = 1;
-- ⚠️ Returns 0 rows (no telemetry loaded)
```

### 2. In the UI (Week 2+)
**Action**: Show what we have, hide missing features

**Example - Driver Card:**
```python
# Week 2: FIFA-style cards use lap times + results
# ✅ Works for Sebring R1 (has both)

if telemetry_available:
    show_gforce_analysis()  # ✅ Show for most races
else:
    display_message("Telemetry not available")  # ⚠️ Sebring R1
```

**Example - Track Weather Analysis:**
```python
# Weather analysis feature
if weather_data.empty:
    st.warning("Weather data not available for this race")
    # Still show other analyses (lap times, results)
else:
    plot_temperature_vs_laptime(weather_data)
```

### 3. Data Completeness Indicator

Add a visual indicator on each race/track:

```
Race Card:
┌─────────────────────────┐
│ Sebring Race 1          │
│ ✅ Lap Times            │
│ ✅ Results              │
│ ✅ Weather              │
│ ❌ Telemetry            │  ← User knows what's available
└─────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Database (Week 1) ✅ DONE
- [x] Load all available data
- [x] Don't error on missing files
- [x] Log warnings for missing files

### Phase 2: UI (Week 2)
- [ ] Add `data_completeness` table to database
- [ ] Show data availability badges on cards
- [ ] Gracefully hide features when data missing

### Phase 3: Advanced (Week 3+)
- [ ] Cross-race comparisons only use complete datasets
- [ ] Predictions flag uncertainty when data incomplete
- [ ] Export functionality includes completeness metadata

---

## SQL to Check Data Completeness

```sql
-- Which races have complete data?
SELECT
    track_code,
    race_num,
    COUNT(DISTINCT CASE WHEN source = 'lap_times' THEN 1 END) as has_laps,
    COUNT(DISTINCT CASE WHEN source = 'weather' THEN 1 END) as has_weather,
    COUNT(DISTINCT CASE WHEN source = 'results' THEN 1 END) as has_results
FROM (
    SELECT track_code, race_num, 'lap_times' as source FROM lap_times
    UNION ALL
    SELECT track_code, race_num, 'weather' FROM weather
    UNION ALL
    SELECT track_code, race_num, 'results' FROM race_results
)
GROUP BY track_code, race_num
ORDER BY track_code, race_num;
```

---

## What We DON'T Do

❌ **Interpolate/Impute missing data** - Don't fake it
❌ **Exclude entire races** - Sebring R1 has 401 valid laps!
❌ **Hide missing data from users** - Be transparent
❌ **Assume files will appear later** - Work with what we have

---

## Benefits of This Approach

✅ **9 races analyzed** instead of 6 (if we excluded incomplete ones)
✅ **5,418 lap times** instead of ~4,600 (if we excluded Sebring R1)
✅ **Transparent** - Users see exactly what data exists
✅ **Flexible** - Easy to add data later if files appear
✅ **Realistic** - Real-world data is always incomplete

---

## User Messaging Examples

### Good Messages ✅
- "Weather data unavailable for this race"
- "Telemetry analysis requires high-frequency data (not available for Sebring R1)"
- "Showing 9 of 12 races (3 races missing critical files)"

### Bad Messages ❌
- "Error: No data" (too vague)
- "Data corrupted" (false - data just missing)
- Silently exclude races (confusing)

---

## Summary

**Keep all races that have lap times or results**
**Show data availability clearly**
**Degrade gracefully when features need missing data**

This gives us maximum analytical power while being honest about limitations.
