"""
System Architecture Overview

## High-Level Architecture

### Components

1. **Frontend Layer**
   - React.js with TypeScript
   - Vite build tool
   - Real-time UI updates
   - Responsive design

2. **API Gateway**
   - Nginx reverse proxy
   - Request routing
   - Load balancing (in production)

3. **Backend Services**
   - FastAPI application
   - RESTful APIs
   - Real-time WebSocket support

4. **Caching Layer**
   - Redis cache
   - KPI metric caching
   - Session management

5. **Data Warehouse**
   - PostgreSQL database
   - Normalized schema
   - Time-series data

6. **Data Pipeline**
   - Apache Airflow orchestration
   - ETL processes
   - Data quality checks

## Data Flow

```
┌─────────────┐
│   Sources   │  (Loan system, branch data)
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Data Ingestion   │  (Airflow DAG)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   Data Lake      │  (Raw data storage)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Transformation   │  (Clean, enrich, aggregate)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Data Warehouse   │  (PostgreSQL)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ KPI Calculation  │  (Computed metrics)
└──────┬───────────┘
       │
       ├─────────────► Redis Cache
       │
       └─────────────► API Layer
                           │
                           ▼
                        Frontend
```

## Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build**: Vite 4
- **State**: Zustand
- **Visualization**: Recharts, Plotly
- **Maps**: Mapbox GL
- **UI Components**: Material-UI / Shadcn
- **Testing**: Vitest, Playwright

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **ORM**: SQLModel + SQLAlchemy
- **Async**: asyncio
- **Task Queue**: Celery (optional)
- **Testing**: pytest

### Data Pipeline
- **Orchestration**: Apache Airflow
- **Processing**: Pandas, Polars
- **Scheduling**: Cron-based

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev) / Kubernetes (prod)
- **Database**: PostgreSQL 13+
- **Cache**: Redis 7
- **Proxy**: Nginx

### Monitoring
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: Python logging + ELK Stack
- **Tracing**: OpenTelemetry (optional)

## Deployment Architecture

### Development
- Single docker-compose deployment
- All services in one network
- Exposed ports for debugging

### Production
- Kubernetes cluster
- Multiple replicas per service
- Load balancing
- Auto-scaling
- Persistent volumes for data
"""
