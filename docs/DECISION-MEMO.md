# Apex Operations API — Technical Decision Memo

## 1. Objective

Build a small, reproducible API deployment that demonstrates practical
Junior DevOps engineering skills within the assessment scope.

The solution focuses on containerization, automated validation, safe
releases, rollback, security, observability, and operational documentation.

## 2. Architecture Decisions

### FastAPI
Selected FastAPI to provide a lightweight API with clear health,
readiness, and task endpoints.

### PostgreSQL
Selected PostgreSQL as the application database. Docker Compose provides
a local database service and persistent volume.

### Docker
The API is packaged in a Docker image using a slim Python base image.
The application runs as a dedicated non-root user.

### Docker Compose
Selected Docker Compose to make the API and database reproducible in the
local assessment environment without requiring paid cloud infrastructure.

### GitHub Actions
Selected GitHub Actions to automate dependency installation, linting,
automated tests, container building, image scanning, and image publishing.

### Prometheus Metrics and Structured Logs
Added request counters labelled by endpoint and HTTP status.
Structured JSON logs provide timestamps, severity, message, and version.

## 3. Release and Rollback Strategy

Releases use versioned Docker image tags.

The release script builds and starts the selected version and checks
application health. The rollback script restores the previously recorded
local image version.

This approach provides a simple and executable rollback process suitable
for the assessment environment.

## 4. Security Decisions

- Run the API as a non-root user.
- Use a read-only container root filesystem.
- Drop Linux capabilities.
- Enable no-new-privileges.
- Keep PostgreSQL on an internal Docker network.
- Bind the API to localhost on the host.
- Store local configuration in an ignored `.env` file.
- Use restricted GitHub Actions permissions.
- Scan the container image using Trivy.

## 5. Testing Strategy

Automated tests cover:
- Application health response
- Application version information
- Prometheus metrics endpoint
- Database failure handling
- Invalid task input
- Unknown route handling

A separate intentional failing test was executed to demonstrate that
the test runner detects failures. It was removed afterwards.

## 6. Observability and Recovery

The application provides:
- `/health` for application health
- `/ready` for database readiness
- `/metrics` for Prometheus metrics
- JSON application logs

A database outage was simulated. The readiness endpoint returned HTTP 503.
After restarting the database, readiness recovered successfully.

## 7. Assumptions and Trade-offs

- The assessment is limited to a local Docker Compose deployment.
- No Apex production systems, customer data, credentials, or paid cloud
  resources are used.
- PostgreSQL is used instead of a production managed database service.
- The API is restricted to localhost rather than exposed publicly.
- Prometheus metrics are exposed for collection; a full Prometheus server
  and alert manager are outside the current implementation scope.
- Local Docker image rollback is appropriate for this single-host
  demonstration but is not a distributed production deployment strategy.

## 8. Future Improvements

With additional time, the solution could include:
- Centralized metrics collection and alert delivery.
- Automated secret management through a managed secrets service.
- Database backup and restore automation.
- TLS and authenticated access for external clients.
- Integration and load testing.
- A production-grade deployment platform with health-aware traffic
  switching and automated recovery.

## 9. Conclusion

The implementation demonstrates a repeatable local deployment,
automated CI validation, container security controls, observability,
and executable versioned release and rollback procedures.

The solution is intended as a practical assessment implementation,
not a claim of production readiness.
