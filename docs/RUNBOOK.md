# Apex Operations API — Operations Runbook

## 1. Purpose

This runbook explains how to deploy, verify, release, roll back, and troubleshoot the Apex Operations API.

## 2. Prerequisites

- Ubuntu Linux
- Docker Engine
- Docker Compose
- Git

Verify installation:

- `docker --version`
- `docker compose version`
- `git --version`

## 3. Environment Configuration

Create the local environment file:

`cp .env.example .env`

Set a unique local database password in `.env`. The POSTGRES_PASSWORD and DB_PASSWORD values must match.

Never commit `.env` or real credentials to Git.

## 4. Deployment

Start the application:

`docker compose up -d --build`

Check containers:

`docker compose ps`

Check application health:

`curl -fsS http://127.0.0.1:8000/health`

Check database readiness:

`curl -fsS http://127.0.0.1:8000/ready`

Expected result: both endpoints return HTTP 200 when the application and database are healthy.

## 5. Versioned Release

Deploy a version:

`./scripts/release.sh v1.0.0`

Verify the running version:

`curl -fsS http://127.0.0.1:8000/health`

For a subsequent release, use a new version such as `v1.0.1`.

## 6. Rollback

Run the rollback script:

`./scripts/rollback.sh`

Verify the restored version:

`curl -fsS http://127.0.0.1:8000/health`

Check container status:

`docker compose ps`

The rollback script restores the previously recorded local Docker image.

## 7. Incident Response

### Database unavailable

Symptoms:
- `/ready` returns HTTP 503.
- Task operations may return HTTP 500.

Investigate:

- `docker compose ps`
- `docker compose logs --tail=50 db`
- `docker compose logs --tail=50 api`

Restore the database:

`docker compose start db`

Verify recovery:

- `docker compose ps`
- `curl -fsS http://127.0.0.1:8000/ready`

Expected result: `{"status":"ready"}`.

### API unavailable

Investigate:

- `docker compose ps`
- `docker compose logs --tail=50 api`

If appropriate, restart the API:

`docker compose restart api`

Verify:

`curl -fsS http://127.0.0.1:8000/health`

### Container repeatedly restarts

Inspect application and database logs:

- `docker compose logs --tail=100 api`
- `docker compose logs --tail=100 db`

Check environment configuration and container health before restarting services.

## 8. Observability

Application health: `/health`

Database readiness: `/ready`

Prometheus metrics: `/metrics`

Application logs:

`docker compose logs --tail=50 api`

Suggested alerts:
- API health-check failures
- Database readiness failures
- Increased HTTP 5xx responses
- High CPU or memory usage
- Repeated container restarts

## 9. Security

- Keep `.env` out of source control.
- Use unique strong credentials outside disposable local testing.
- Keep PostgreSQL on the internal Docker network.
- Keep API access restricted to localhost unless secure access is configured.
- Run the application as a non-root user.
- Review dependency and image scan results before release.
- Use least-privilege CI permissions.

## 10. Shutdown

Stop services:

`docker compose down`

To remove the database volume and its stored data:

`docker compose down -v`

Warning: this permanently deletes local PostgreSQL data.

## 11. Assessment Scope

This runbook covers the local Docker Compose assessment environment. It does not authorize access to Apex production systems. No production credentials, customer data, or paid cloud resources are required.
