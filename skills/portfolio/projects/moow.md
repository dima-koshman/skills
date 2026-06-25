# Moow: Data Analytics Platform for Electric Scooter Rental Operations

**[Source](https://gitlab.com/koshmandk/moow)** | **[Docs](https://gitlab.com/koshmandk/moow/-/wikis/pages)**

---

## Overview

| | |
|---|---|
| **Client** | Moow — Electric scooter rental startup |
| **Location** | Greece (Thessaloniki, Ioannina, Kastoria, Kozani, Trikala, Katerini) |
| **Role** | Data Engineer / Analytics Engineer |
| **Duration** | Multi-month engagement |
| **Tech Stack** | Python, AWS, PostgreSQL, VictoriaMetrics, Polars, GeoPandas, Scikit-learn, OR-Tools, Gradio |

---

## Project Description

Moow operates a fleet of electric scooters across multiple Greek cities, serving thousands of users through a mobile app. I designed and implemented the complete analytics infrastructure from the ground up — from cloud infrastructure to machine learning models — enabling data-driven fleet management and operational optimization.

---

## The Challenge

Moow needed to transition from intuition-based operations to data-driven decision making. Key challenges included:

- **No analytics infrastructure** — raw operational data in MySQL was not being utilized
- **Inefficient fleet distribution** — scooters often weren't where customers needed them
- **Manual task management** — field workers lacked optimized routes for maintenance and redistribution
- **No visibility into operations** — management couldn't track KPIs or identify problems
- **Scaling challenges** — expanding to new cities required understanding demand patterns

---

## Solution Architecture

A complete analytics stack built on AWS:

**Data Sources**
- MySQL (Operational DB)
- Scooter Telemetry (GPS, Battery)

**ETL Pipeline** (GitLab CI/CD + Docker)

**Data Storage**
- VictoriaMetrics (Time Series)
- PostgreSQL (Analytics DB)
- Google Sheets (Planning)

**Outputs**
- ML Models (Clustering, Forecasting)
- Yandex DataLens Dashboards
- Worker App (Gradio)

---

## Technical Implementation

### 1. Cloud Infrastructure (AWS)

Set up the complete cloud environment from scratch:

- **EC2 Instances** — Configured compute instances for data processing and applications
- **EBS Storage** — Persistent storage volumes for databases and Docker containers
- **Docker** — Containerized all services with Portainer for management
- **VictoriaMetrics** — Deployed high-performance time series database for scooter telemetry
- **PostgreSQL** — Analytics database for processed metrics and statistics
- **Networking** — Configured security groups, VPC, and SSL certificates (ZeroSSL)
- **Secrets Management** — AWS Parameter Store and Bitwarden integration

### 2. Data Engineering Pipeline

Built automated ETL pipelines running on GitLab CI/CD:

**Data Collection**
- Parsed JSON telemetry from scooters (GPS coordinates, speed, battery level, lock status, HDOP precision)
- Transformed nested MySQL data into structured time series
- Wrote to VictoriaMetrics with proper timestamps and labels
- Parallel batch processing with joblib for large datasets (100K+ rows)

**Data Processing (Polars)**
- High-performance DataFrame operations for large-scale data manipulation
- Complex aggregations: rides per parking, hourly occupancy, utilization rates
- Time-based categorization (workday/weekend, morning/afternoon/evening/night)
- Batch SQL queries with parallel processing

**Geospatial Analysis (GeoPandas)**
- Coordinate transformations (WGS84 ↔ Greek Transverse Mercator EPSG:2100)
- KD-tree spatial indexing for efficient nearest-neighbor queries
- Parking zone polygon operations (intersection, buffering, centroids)
- Ride path analysis using polyline decoding

### 3. Analytics & Metrics

Computed key operational metrics stored in PostgreSQL:

| Metric Category | Examples |
|---|---|
| **Parking Stats** | Scooter count by hour, average occupancy, utilization rate |
| **Ride Analytics** | Rides per parking, ride duration, distance traveled |
| **Fleet Health** | Battery levels, idle time, maintenance frequency |
| **Demand Patterns** | Peak hours by location, weekday vs weekend trends |

Connected PostgreSQL to **Yandex DataLens** for interactive dashboards accessible to management.

### 4. Machine Learning Models

**Parking Location Optimization**
- Applied **MeanShift clustering** to ride start/end points
- Identified areas with high demand but low scooter density
- Suggested new parking locations based on user behavior patterns
- Parameters tuned for Greek city densities (bandwidth, min_bin_freq)

**Demand Forecasting**
- Built time series models using **Darts library**
- City-specific forecasting for ride counts
- Incorporated seasonality, weather data (via Meteostat), and time categories
- Compared actual vs. planned scooter counts for capacity planning

**Demand Estimation**
- Proximity-based weighting using spatial distances
- Predicted demand at each parking based on historical patterns
- Optimized scooter distribution recommendations

### 5. Route Optimization for Field Workers

Built an intelligent routing system using **Google OR-Tools**:

- Solved Vehicle Routing Problem (VRP) for maintenance tasks
- Minimized travel distance for scooter pickup/redistribution
- Handled constraints: vehicle capacity (20-40 scooters), parking requirements
- Multi-worker assignment with task prioritization

### 6. Worker Web Application

Developed a **Gradio-based web app** for field workers:

- Real-time parking data with background refresh
- Current scooter locations and battery status
- Optimized route visualization with Google Maps integration
- Task management: view assigned scooters, mark completed
- Browser geolocation for worker position tracking
- SSL/HTTPS deployment for security

### 7. Automated Task Generation

Built an intelligent task assignment system:

- Automatically generated maintenance tasks based on:
  - Low battery levels
  - Scooters outside designated parking areas
  - Parkings below minimum scooter thresholds
- Priority scoring with configurable weights (via Google Sheets)
- Worker assignment optimization

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Cloud** | AWS EC2, EBS, Parameter Store, RDS |
| **Containers** | Docker, Portainer |
| **Databases** | PostgreSQL, MySQL, VictoriaMetrics |
| **Data Processing** | Python, Polars, Pandas, SQLAlchemy |
| **Geospatial** | GeoPandas, Shapely, Folium, SciPy KDTree |
| **ML/Forecasting** | Scikit-learn, Darts, OR-Tools |
| **CI/CD** | GitLab CI/CD, GitLab Runner |
| **Web** | Gradio, Google Maps API |
| **Visualization** | Yandex DataLens, Altair, Great Tables |
| **APIs** | Google Sheets API, VictoriaMetrics API |

---

## Business Impact

### Operational Efficiency
- **Automated data pipelines** eliminated manual reporting — hourly stats generated automatically
- **Route optimization** reduced worker travel time and fuel costs
- **Task automation** replaced manual task assignment with intelligent prioritization

### Data-Driven Decisions
- **Real-time dashboards** gave management visibility into fleet operations across all cities
- **Demand forecasting** enabled proactive scooter distribution before peak hours
- **Parking analytics** identified underperforming locations for optimization

### Scalability
- **City expansion support** — analytics infrastructure easily extended to new cities (Ioannina, Kastoria, Kozani, Trikala, Katerini)
- **ML-suggested parkings** accelerated new city setup with data-driven location recommendations

### Fleet Optimization
- **Clustering analysis** identified gaps in parking network, suggesting new locations
- **Utilization metrics** helped right-size fleet per city (target: 6-10 scooters at busy parkings)
- **Battery monitoring** reduced scooter downtime through proactive charging

---

## Code Stats

| Metric | Value |
|---|---|
| Python LOC | ~6,000 |
| Core modules | 18+ |
| CI/CD stages | 4-stage GitLab pipeline |
| Deployment | Docker production-ready |

Key modules:
- `moow.py` — Core data access and business logic (893 lines)
- `parking.py` — Parking analytics and statistics (539 lines)
- `routing.py` — Vehicle routing optimization (395 lines)
- `demand_prediction.py` — Time series forecasting (500+ lines)
- `router_app.py` — Worker web application
- `victoria_metrics_client.py` — Time series database integration

---

## Skills Demonstrated

### Data Engineering
- ETL pipeline design and implementation
- Time series data processing at scale
- Database design and optimization (PostgreSQL, MySQL)
- Batch processing with parallel execution

### Cloud & Infrastructure
- AWS services (EC2, EBS, RDS, Parameter Store)
- Docker containerization and orchestration
- CI/CD pipeline development (GitLab)
- SSL/TLS certificate management

### Analytics & Visualization
- Business intelligence dashboard creation
- KPI definition and metric computation
- Geospatial analysis and visualization

### Machine Learning
- Clustering algorithms (MeanShift)
- Time series forecasting (Darts)
- Optimization algorithms (OR-Tools VRP)
- Spatial demand estimation

### Software Development
- Python application development
- Web application development (Gradio)
- API integrations (Google Sheets, Maps, VictoriaMetrics)
- Clean code practices and documentation

---

## Lessons Learned

1. **Start with infrastructure** — Having VictoriaMetrics for time series data early enabled rich historical analysis
2. **Automate everything** — GitLab CI/CD pipelines ensured reliable, repeatable data processing
3. **Integrate with existing tools** — Google Sheets integration allowed business users to configure parameters without code changes
4. **Think geospatially** — Proper coordinate systems and spatial indexing were crucial for performance
5. **Build for operators** — The worker app needed to be simple and mobile-friendly for field use
