# GR Cup Performance Intelligence Platform
## Development Roadmap & Data Summary

---

## Product Vision

**One unified web application** with side navigation that progressively unlocks features through phased development. This platform provides comprehensive insights for the Toyota GR Cup Championship using data from 12 races across 6 championship venues.

**Development Approach**: Built iteratively using a phased rollout strategy, where each phase adds new functionality to the existing application.

---

## Complete Dataset Inventory

### Championship Overview: 6 Tracks × 2 Races = 12 Race Events

| Track Name | Location | Race 1 | Race 2 | Telemetry Records | Track Characteristics |
|------------|----------|--------|--------|-------------------|----------------------|
| **Barber Motorsports Park (BMP)** | Alabama | ✓ | ✓ | ~11.5M (R1), ~11.7M (R2) | Technical, elevation changes, 2.38 miles |
| **Circuit of the Americas (COTA)** | Texas | ✓ | ✓ | ~17.8M (R1), ~TBD (R2) | Grade 1, high-speed, 3.41 miles |
| **Road America** | Wisconsin | ✓ | ✓ | ~9M (R1), ~TBD (R2) | Fast, flowing, 4.05 miles (longest) |
| **Sebring International Raceway** | Florida | ✓ | ✓ | ~TBD | Bumpy, historic, 3.74 miles |
| **Sonoma Raceway** | California | ✓ | ✓ | ~TBD | Hilly, technical, 2.52 miles |
| **Virginia International Raceway (VIR)** | Virginia | ✓ | ✓ | ~TBD | Fast, elevation, 3.27 miles |

**Total Dataset**: 12 race events, ~22 drivers per race, estimated 70M+ telemetry records across full season

---

### Standard Data Structure Per Race Event

Each of the 12 race events contains the following file types:

| File Type | Naming Convention | Records | Key Fields | Purpose |
|-----------|-------------------|---------|------------|---------|
| **High-Frequency Telemetry** | `R{1/2}_{track}_telemetry_data.csv` | 8M-18M rows | `telemetry_name`, `telemetry_value`, `timestamp`, `lap`, `vehicle_id` | Vehicle dynamics: speed, gear, throttle (aps), brake pressure (pbrake_f/r), G-forces (accx/accy), steering angle, RPM (nmot), GPS coordinates |
| **Lap/Section Analysis** | `23_AnalysisEnduranceWithSections_Race {1/2}_Anonymized.CSV` | ~600-800 laps | `LAP_TIME`, `S1/S2/S3`, `IM1a/IM1/IM2a/IM2/IM3a/FL`, `TOP_SPEED`, `FLAG_AT_FL`, improvement flags | Structured timing with 3 sectors + 6 intermediate splits |
| **Best Laps Ranking** | `99_Best 10 Laps By Driver_Race {1/2}_Anonymized.CSV` | ~220 records | `BESTLAP_1` through `BESTLAP_10`, lap numbers, `AVERAGE` | Performance benchmarking per driver |
| **Weather Data** | `26_Weather_Race {1/2}_Anonymized.CSV` | Time series (~45 min) | `AIR_TEMP`, `TRACK_TEMP`, `HUMIDITY`, `PRESSURE`, `WIND_SPEED`, `WIND_DIRECTION`, `RAIN` | Environmental conditions |
| **Lap Boundaries** | `{track}_lap_time/start/end_R{1/2}.csv` | ~600-800 events | `lap`, `timestamp`, `vehicle_id`, `vehicle_number` | Session structure markers |
| **Official Results** | `03_Provisional Results_Race {1/2}_Anonymized.CSV` | ~22 drivers | Final positions, points, classification | Race outcomes |
| **Class Results** | `05_Results by Class_Race {1/2}_Anonymized.CSV` | ~22 drivers | Class-specific standings | Am class rankings |

### Data Granularity & Scale
- **Temporal**: High-frequency telemetry (~100 Hz), lap-level timing, session-level weather
- **Spatial**: GPS coordinates (VBOX_Long_Minutes, VBOX_Lat_Min), lap distance tracking (Laptrigger_lapdist_dls)
- **Participants**: ~22 drivers per race (anonymized), Toyota GR86 spec series (Am class)
- **Track Layouts**: Varies by venue (3 sectors standard, 6 intermediate timing points per lap)
- **Season Span**: Full championship season across diverse track types
- **Estimated Total Records**: 70M+ telemetry points, 7,000+ laps, 264 race results

---

## Application Architecture

### Core Application Structure (Built Once, Evolves Throughout)

```
┌─────────────────────────────────────────────────┐
│  🏎️ GR Cup Performance Intelligence Platform    │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Side Navigation]        [Main Content Area]  │
│                                                 │
│  📊 Drivers               [Dynamic Content]     │
│  🏁 Tracks                Based on Nav          │
│  🎯 Training              Selection             │
│  🔮 Predictions                                 │
│  📈 Analytics                                   │
│  ✨ Extras                                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Side Navigation Progressive Unlock

| Navigation Item | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 |
|-----------------|---------|---------|---------|---------|---------|---------|
| 📊 Drivers      | ✅ Active | ✅ Active | ✅ Active | ✅ Active | ✅ Active | ✅ Active |
| 🏁 Tracks       | ✅ Active | ✅ Active | ✅ Active | ✅ Active | ✅ Active | ✅ Active |
| 🎯 Training     | 🔒 Locked | ✅ Active | ✅ Active | ✅ Active | ✅ Active | ✅ Active |
| 🔮 Predictions  | 🔒 Locked | 🔒 Locked | ✅ Active | ✅ Active | ✅ Active | ✅ Active |
| 📈 Analytics    | 🔒 Locked | 🔒 Locked | 🔒 Locked | ✅ Active | ✅ Active | ✅ Active |
| ✨ Extras       | 🔒 Locked | 🔒 Locked | 🔒 Locked | 🔒 Locked | 🔒 Locked | ✅ Active |

**UI for Locked Items**: Grayed out with "Coming Soon" tooltip

---

## Complete Development Timeline

| Week       | Focus                    | Deliverable                      | Search Capabilities | Status          |
|------------|--------------------------|----------------------------------|---------------------|-----------------|
| **Week 1**     | Data Pipeline            | `driver_stats.db` created          | N/A | 🔄 **Starting Now** |
| **Week 2**     | Driver/Track Cards       | Grid views working               | N/A | ⏳ Pending       |
| **Week 3**     | Detail Views             | 6 widgets per page               | N/A | ⏳ Pending       |
| **Week 4**     | Simple Search (Phase 1)  | "Ask Questions" in side nav      | Basic facts (drivers, tracks, records) | ⏳ Pending       |
| **Week 5**     | Training Module          | Racing line, deltas, scorecards  | + Training insights | ⏳ Pending       |
| **Week 6**     | Deploy + Finish Training | AWS EC2 live + Training complete | (refinements) | ⏳ Pending       |
| **Week 7-9**   | Phase 3: Predictions     | Forecast models                  | + Predictions | ⏳ Pending       |
| **Week 10-12** | Phase 4: Analytics       | Race storytelling                | + Race analytics | ⏳ Pending       |
| **Week 13-14** | Phase 5: Real-Time Sim   | Pit strategy simulator           | + Real-time queries | ⏳ Pending       |
| **Week 15**    | Phase 6: Wildcards       | Driver DNA, extras               | + AI patterns | ⏳ Pending       |
| **Week 16+**   | **Phase 7: Live Data**   | **Real-time race data integration** | **Live race questions** | ⏳ **Future** |

---

## Phased Development Overview

### Phase 1: Foundation + Driver & Track Profiling (Weeks 1-4)
**Status**: 🔄 Starting Now
**Problem Statement**: See `PS1_Driver_Track_Profiling.md`

**Week 1**: Data Pipeline
- Build multi-track data ingestion pipeline (all 12 races)
- Data cleaning and standardization
- Database setup (DuckDB)
- Lap-level aggregation
- Calculate driver/track metrics

**Week 2**: Driver/Track Cards
- Web application framework (Streamlit)
- Side navigation component
- Driver cards grid (FIFA-style)
- Track cards grid
- Basic search/filter

**Week 3**: Detail Views
- Individual driver detail pages (6 widgets)
- Individual track detail pages (6 widgets)
- Click interactions
- Custom CSS polish

**Week 4**: Simple Search
- "Ask Questions" added to side nav
- Keyword-based question answering
- Supports: "Who is fastest?", "Show Driver X", "Compare X vs Y", "Track records"

**Side Nav Active**: Drivers ✅, Tracks ✅, Ask Questions ✅

---

### Phase 2: Driver Training & Insights (Weeks 5-6)
**Status**: ⏳ Pending
**Problem Statement**: See `PS2_Driver_Training_Insights.md`

**Week 5**: Training Module
- Racing line comparison tool (GPS overlay)
- Sector delta analysis
- Input quality scorecards (throttle/brake/steering)
- Basic improvement recommendations

**Week 6**: Deploy + Finish Training
- **Morning**: Deploy to AWS EC2
- **Afternoon**: Complete Training features
- Progress tracking across season
- Enhanced search: "Training suggestions for Driver X?"

**Side Nav Active**: Drivers ✅, Tracks ✅, Ask Questions ✅, Training ✅

---

### Phase 3: Pre-Event Prediction (Weeks 7-9)
**Status**: ⏳ Pending
**Problem Statement**: See `PS3_Pre_Event_Prediction.md`

**What Gets Built**:
- Prediction models foundation
- Qualifying predictions
- Race pace forecasts
- Strategy recommendations
- Weather impact analysis
- Enhanced search: "Who will win Race 2?", "Predict Driver X performance"

**Side Nav Active**: All previous + Predictions ✅

---

### Phase 4: Post-Event Analysis (Weeks 10-12)
**Status**: ⏳ Pending
**Problem Statement**: See `PS4_Post_Event_Analysis.md`

**What Gets Built**:
- Interactive race timeline
- Position and gap tracking
- Strategy analysis
- Performance heatmaps
- Automated race reports
- Enhanced search: "What happened in Race X?", "Key moments at Barber?"

**Side Nav Active**: All previous + Analytics ✅

---

### Phase 5: Real-Time Analytics Simulator (Weeks 13-14)
**Status**: ⏳ Pending
**Problem Statement**: See `PS5_Real_Time_Analytics.md`

**What Gets Built** (extends Analytics module):
- Race replay simulator
- Pit window optimizer
- Performance alerts
- Competitor tracking
- Scenario simulator
- Enhanced search: "Should Driver X pit now?", "Optimal pit window?"

**Side Nav Active**: Same (Real-Time is part of Analytics)

---

### Phase 6: Wildcard Innovations (Week 15)
**Status**: ⏳ Pending
**Problem Statement**: See `PS6_Wildcard_Innovations.md`

**What Gets Built**:
- Driver DNA profiling
- ML pattern discovery
- Track evolution visualization
- Fan engagement tools
- Community features
- Enhanced search: "Driver X driving style?", "Similar drivers to X?"

**Side Nav Active**: All modules ✅ (Extras unlocked)

---

### Phase 7: Live Data Integration (Week 16+)
**Status**: ⏳ Future
**Goal**: Connect to real-time race data streams for live monitoring

**What Gets Built**:
- Live telemetry data ingestion (WebSocket/Kafka)
- Live leaderboard updates
- Real-time gap tracking
- Live pit stop predictions
- Real-time strategy recommendations
- Live performance alerts

**Architecture Change**:
```
Historical Data (Weeks 1-15):
  CSV files → DuckDB → Streamlit

Live Data (Week 16+):
  Race Timing API → Kafka/WebSocket → DuckDB (streaming) → Streamlit (auto-refresh every 1-5s)
```

**Enhanced Search - Live Questions**:
- "What's Driver 2's current position?" (LIVE)
- "Gap to leader right now?"
- "Should Driver 5 pit this lap?" (LIVE decision)
- "Current tire age for Driver 13?"
- "Live sector times comparison"
- "Fastest lap this session?"

**Deployment**: AWS EC2 with real-time data pipeline + WebSocket connections

---

## Search Feature Evolution Summary

The **"Ask Questions"** feature grows more intelligent with each phase:

| Phase | Search Understands |
|-------|-------------------|
| **Week 4** | Drivers, Tracks, Records (basic facts) |
| **Week 5-6** | + Training insights and recommendations |
| **Week 7-9** | + Predictions and forecasts |
| **Week 10-12** | + Race analytics and history |
| **Week 13-14** | + Real-time simulator queries |
| **Week 15** | + AI patterns and driver DNA |
| **Week 16+** | + LIVE race data questions |

**Implementation**: Single search bar in side nav that becomes smarter as new data sources are added.

---

## Technology Stack (Confirmed)

**What Gets Built** (extends Analytics module):
- Race replay simulator
- Pit window optimizer
- Performance alerts
- Competitor tracking
- Scenario simulator

**Side Nav Active**: All except Extras

---

### Phase 6: Wildcard Innovations (Weeks 17-18)
**Status**: 🔒 Not Started
**Problem Statement**: See `PS6_Wildcard_Innovations.md`

**What Gets Built**:
- Driver DNA profiling
- ML pattern discovery
- Track evolution visualization
- Fan engagement tools
- Community features

**Side Nav Active**: All modules ✅

---

## Technical Stack Recommendations

### Option 1: Modern Web Stack (More Control)
**Frontend**:
- React.js + TypeScript
- Tailwind CSS (for FIFA-style card designs)
- Chart.js / Recharts (visualizations)
- Leaflet (GPS track maps)

**Backend**:
- Python (FastAPI or Flask)
- SQLite/DuckDB (data storage)
- Pandas (data processing)

**Pros**: Full control, professional quality, scalable
**Cons**: More setup time, frontend + backend separation

---

### Option 2: Rapid Prototype Stack (Faster MVP)
**Framework**:
- Streamlit (Python all-in-one)
- Plotly (interactive charts)
- Folium (maps)

**Data**:
- DuckDB or SQLite
- Pandas

**Pros**: Faster to build, single language (Python), good for data apps
**Cons**: Less UI flexibility

---

### Recommended: **Start with Option 2 (Streamlit), Migrate to Option 1 if Needed**

**Why**:
- Get to Phase 1 deliverables in 2-3 weeks instead of 4
- Validate UX and data insights quickly
- Can rebuild with React later if needed
- Streamlit can handle FIFA-style cards with custom CSS

---

## Data Processing Architecture

### Multi-Track Data Pipeline Strategy

```
Layer 1: RAW DATA (70M+ records across 12 races)
   ↓
Layer 2: PRE-PROCESSED AGGREGATES (Lap summaries, sector stats)
   ↓
Layer 3: ANALYTICAL FEATURES (Driver profiles, track characteristics)
   ↓
Layer 4: INSIGHTS & VISUALIZATIONS (Web application)
```

**Key Strategies**:
1. **Pre-aggregate telemetry** → Lap-level summaries (reduces 70M to ~7K records)
2. **Lazy loading**: Load only necessary tracks/races for specific analyses
3. **Database approach**: SQLite/DuckDB for efficient querying
4. **Incremental processing**: Process one race at a time, combine results

---

## Success Metrics

### Phase 1 MVP Success Criteria
✅ User can navigate to "Drivers" and see all 22 driver cards
✅ Clicking a driver card opens detailed profile with 6 widgets
✅ User can navigate to "Tracks" and see all 6 track cards
✅ Clicking a track card opens detailed profile with 6 widgets
✅ "Training", "Predictions", "Analytics", "Extras" show as locked
✅ All data loads in < 3 seconds

### Overall Application Success Metrics

**User Engagement**:
- Drivers use tool for pre-race preparation
- Engineers reference analytics for strategy decisions
- Clear, actionable insights generated within seconds

**Technical Performance**:
- Load any driver/track profile in < 2 seconds
- Process full season data in < 30 seconds
- Support 10+ concurrent users

**Insight Quality**:
- Identify 5+ actionable improvements per driver per track
- Predict Race 2 outcomes with 75%+ accuracy
- Generate compelling race narratives automatically

---

## Current Status & Next Actions

### Completed ✅
- [x] Problem statements defined (PS1-PS6)
- [x] Data inventory complete (6 tracks, 12 races, 70M records)
- [x] UI vision defined (FIFA-style cards, widget layout)
- [x] Phased development roadmap created

### Ready to Start Phase 1 🚀
**Next Immediate Actions**:
1. **Tech Stack Decision**: Confirm Streamlit vs React
2. **Repository Setup**: Initialize project structure
3. **Data Quality Check**: Run assessment on all 12 races
4. **Week 1 Kickoff**: Begin data pipeline development

---

## Document References

- **PS1**: Driver & Track Profiling → `PS1_Driver_Track_Profiling.md`
- **PS2**: Driver Training & Insights → `PS2_Driver_Training_Insights.md`
- **PS3**: Pre-Event Prediction → `PS3_Pre_Event_Prediction.md`
- **PS4**: Post-Event Analysis → `PS4_Post_Event_Analysis.md`
- **PS5**: Real-Time Analytics → `PS5_Real_Time_Analytics.md`
- **PS6**: Wildcard Innovations → `PS6_Wildcard_Innovations.md`

---

**Document Version**: v1.0 - Development Roadmap & Data Summary
**Last Updated**: 2025-10-21
**Status**: Ready to Begin Phase 1
