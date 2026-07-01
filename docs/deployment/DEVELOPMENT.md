# Development Environment Setup

## Prerequisites
- Docker and Docker Compose
- Node.js 16+
- Python 3.9+
- PostgreSQL client
- Redis client (optional)

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- Backend API (http://localhost:8000)
- Frontend application (http://localhost:3000)
- Nginx reverse proxy (http://localhost)

### Manual Development Setup

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:3000

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

Access API at http://localhost:8000
Swagger docs at http://localhost:8000/docs

#### Data Pipeline Setup
```bash
cd data-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize Airflow
export AIRFLOW_HOME=.
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
airflow scheduler &
airflow webserver
```

Access Airflow UI at http://localhost:8080

## Environment Variables

Create `.env` files in each module:

### Backend `.env`
```
DATABASE_URL=postgresql://dashboard_user:secure_password@localhost:5432/portfolio_analytics
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key
RATE_LIMIT_ENABLED=True
RATE_LIMIT_MAX_REQUESTS=240
RATE_LIMIT_WINDOW_SECONDS=60
```

### Frontend `.env`
```
VITE_API_BASE_URL=/api/v1
VITE_APP_ENV=development
```

## Database Initialization

```bash
cd backend
alembic upgrade head
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### PostgreSQL Connection Error
- Ensure PostgreSQL is running: `docker ps | grep postgres`
- Check connection string in `.env`
- Reset connection: `docker exec dashboard-postgres pg_isready`

### Redis Connection Error
- Ensure Redis is running: `docker ps | grep redis`
- Test Redis: `redis-cli ping`

### Port Already in Use
- Change ports in `docker-compose.yml`
- Or kill existing processes: `lsof -i :3000` / `lsof -i :8000`

## Performance Tips

1. **Frontend**: Use React DevTools to profile components
2. **Backend**: Use Uvicorn with `--workers` for production
3. **Database**: Enable query logging to identify slow queries
4. **Redis**: Monitor cache hit rate

## Documentation

- [Backend API](./docs/api-specs)
- [Architecture](./docs/architecture)
- [Deployment Guide](./docs/deployment)
