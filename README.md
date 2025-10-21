# GR Cup Performance Intelligence Platform

A comprehensive web application for Toyota GR Cup Championship data analysis featuring driver profiling, training insights, predictions, and race analytics.

## Project Status: Week 1 - Data Pipeline 🔄

### Current Phase: Foundation + Driver & Track Profiling

**Development Timeline**: 15+ weeks across 6 phases

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Data Pipeline (Week 1)

```bash
python src/pipeline/ingest_data.py
```

This will:
- Process all 12 race events (6 tracks × 2 races)
- Aggregate 70M+ telemetry records to lap-level summaries
- Create `driver_stats.db` (DuckDB database)
- Calculate driver and track metrics

### 3. Launch Web Application (Week 2+)

```bash
streamlit run src/app/main.py
```

## Project Structure

```
MotorsportData/
├── src/
│   ├── pipeline/          # Data ingestion and processing
│   ├── database/          # DuckDB schema and queries
│   ├── utils/             # Helper functions
│   └── app/               # Streamlit web application
├── data/
│   ├── processed/         # Generated databases and aggregates
│   ├── barber-motorsports-park/
│   ├── circuit-of-the-americas/
│   ├── road-america/
│   ├── sebring/
│   ├── sonoma/
│   └── virginia-international-raceway/
├── docs/                  # Problem statements and documentation
└── tests/                 # Unit tests

```

## Dataset Overview

**6 Tracks × 2 Races = 12 Race Events**

| Track | Location | Records |
|-------|----------|---------|
| Barber Motorsports Park | Alabama | ~11.5M per race |
| Circuit of the Americas | Texas | ~17.8M per race |
| Road America | Wisconsin | ~9M per race |
| Sebring International | Florida | R2: ~8M |
| Sonoma Raceway | California | R1: ~14M, R2: ~7M |
| Virginia International Raceway | Virginia | ~11M per race |

**Total**: ~70M telemetry records, 7,000+ laps, 264 race results

## Data Files Per Race

- **High-Frequency Telemetry**: Vehicle dynamics (speed, G-forces, throttle, brake, etc.)
- **Lap/Section Analysis**: Timing with 3 sectors + 6 intermediate splits
- **Best Laps**: Top 10 laps per driver
- **Weather Data**: Environmental conditions
- **Lap Boundaries**: Session structure markers
- **Official Results**: Race outcomes and standings

## Development Phases

### Phase 1: Driver & Track Profiling (Weeks 1-4) 🔄
- ✅ Data pipeline
- ⏳ FIFA-style driver/track cards
- ⏳ Detail views with 6 widgets
- ⏳ Simple search feature

### Phase 2: Training & Insights (Weeks 5-6)
- Racing line comparison
- Sector delta analysis
- AWS EC2 deployment

### Phase 3: Predictions (Weeks 7-9)
- Qualifying forecasts
- Race pace predictions
- Strategy recommendations

### Phase 4: Post-Event Analysis (Weeks 10-12)
- Interactive race timeline
- Strategy effectiveness
- Automated race reports

### Phase 5: Real-Time Simulator (Weeks 13-14)
- Pit window optimizer
- Performance alerts
- Scenario simulator

### Phase 6: Wildcard Innovations (Week 15)
- Driver DNA profiling
- ML pattern discovery
- Fan engagement tools

### Phase 7: Live Data Integration (Week 16+)
- Real-time race monitoring
- Live strategy recommendations
- WebSocket/Kafka integration

## Technology Stack

- **Frontend**: Streamlit
- **Database**: DuckDB
- **Processing**: Pandas, NumPy
- **Visualization**: Plotly, Altair
- **Deployment**: AWS EC2

## Documentation

See `docs/` folder for detailed problem statements:
- PS1: Driver & Track Profiling
- PS2: Driver Training & Insights
- PS3: Pre-Event Prediction
- PS4: Post-Event Analysis
- PS5: Real-Time Analytics
- PS6: Wildcard Innovations

Full development roadmap: `DEVELOPMENT_ROADMAP_and_Data_Summary.md`

## License

Private project for Toyota GR Cup Championship analysis.
