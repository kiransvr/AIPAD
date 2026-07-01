# Backend MVC Alignment Map

This project keeps the existing three-tier deployment model:

1. Presentation tier: React frontend
2. Application tier: FastAPI backend
3. Data tier: PostgreSQL/Redis and data pipeline

Within the backend application tier, code is now organized with MVC-aligned layering:

- Routes (API layer): `backend/src/api/routes`
  - HTTP concerns only (request/response, auth dependencies, parameter parsing)
- Controllers (Controller layer): `backend/src/controllers`
  - Orchestrate use-cases and delegate to services
- Services (Service layer): `backend/src/services`
  - Business logic and workflow rules
- Repositories (Data access layer): `backend/src/repositories`
  - Reserved for database/query abstractions
- Models (Domain/data models): `backend/src/models`
  - Reserved for ORM/domain entities

## Current mappings

- Auth
  - Route: `api/routes/auth_routes.py`
  - Controller: `controllers/auth_controller.py`
  - Service: `services/auth_service.py`
  - Domain helpers: `auth.py`

- Health
  - Route: `api/routes/health_routes.py`
  - Controller: `controllers/health_controller.py`

- Portfolio Analytics
  - Routes: `api/routes/par_routes.py`, `api/routes/npl_routes.py`
  - Controller: `controllers/analytics_controller.py`
  - Services: `services/par_service.py`, `services/npl_service.py`

- Upload
  - Route: `api/routes/upload_routes.py`
  - Controller: `controllers/upload_controller.py`
  - Service: `services/upload_service.py`

- Branch
  - Route: `api/routes/branch_routes.py`
  - Controller: `controllers/branch_controller.py`
  - Service: `services/branch_service.py`

- Regional
  - Route: `api/routes/regional_routes.py`
  - Controller: `controllers/regional_controller.py`
  - Service: `services/regional_service.py`

- Growth
  - Route: `api/routes/growth_routes.py`
  - Controller: `controllers/growth_controller.py`
  - Service: `services/growth_service.py`

- Gender
  - Route: `api/routes/gender_routes.py`
  - Controller: `controllers/gender_controller.py`
  - Service: `services/gender_service.py`

- Inclusion
  - Route: `api/routes/inclusion_routes.py`
  - Controller: `controllers/inclusion_controller.py`
  - Service: `services/inclusion_service.py`

- Officer
  - Route: `api/routes/officer_routes.py`
  - Controller: `controllers/officer_controller.py`
  - Service: `services/officer_service.py`
