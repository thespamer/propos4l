# Docker Compose Configuration Guide

## Service Dependencies and Startup

The application uses Docker Compose to manage multiple services. Here's how the services are configured to ensure proper startup:

### Frontend Service
- Depends on backend with `condition: service_started`
- This ensures the frontend starts as soon as the backend container starts, without waiting for health checks
- Has its own health check that verifies the Next.js server is responding

### Backend Service
- Depends on both db and redis with `condition: service_healthy`
- Uses optimized health check parameters:
  - `interval: 5s`
  - `timeout: 3s`
  - `retries: 5`
  - `start_period: 10s`
- Inherits common backend configurations (logging, restart policy)

### Database Service (PostgreSQL)
- Has health check to verify database is ready
- No dependencies on other services
- Uses persistent volume for data storage

### Redis Service
- Has health check to verify Redis is responding
- No dependencies on other services
- Uses persistent volume for data storage

### Migrations Service
- Depends on both db and redis with `condition: service_healthy`
- Configured with `restart: "no"` to run once and stop
- Does NOT inherit common backend configurations to avoid unwanted restart behavior

## Common Backend Configuration
The `x-common-backend` configuration is shared among backend services (except migrations) and includes:
- `restart: unless-stopped` policy
- JSON file logging with rotation
- Init process enabled

## Volumes
All services use named volumes for persistent data storage:
- `postgres_data`: Database files
- `redis_data`: Redis data
- `pdf_storage`: PDF files
- `template_storage`: Template files
- `frontend_node_modules`: Node modules for frontend
- `frontend_next`: Next.js build cache
