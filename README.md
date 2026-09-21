# Cloud Cartographer

A cloud migration readiness project: analyzing infrastructure, comparing cloud providers, and estimating real costs

The goal was to take a small but realistic application stack, stress test it, find where it breaks,
and then figure out what it would actually cost to run it on AWS and GCP
at production scale.

---

## Project Structure

```
/
├── sample-app-main/        # The sample application (frontend, backend, db)
├── monitoring/             # Monitoring stack  
├── locust/                 # Artificial load testing setup  
├── docs/
│   ├── 00-glossary.md
│   ├── 01-infrastructure-analysis.md
│   ├── 02-cloud-provider-comparison.md
│   ├── 03-migration-cost-analysis.md
│   └── 04-risk-assessment.md
```

---

## Local Benchmarking Setup

The project runs across three separate Docker Compose stacks (the provided setup is what I used for benchmarking locally, not for
prod deployment):

**Start the application:**

```bash
cd sample-app-main
docker compose up -d
```

**Start monitoring:**

```bash
cd monitoring
docker compose up -d
```

**Run load tests:**

```bash
cd locust
docker compose up -d
# Open http://localhost:8089
```

All three stacks share the `sample-app-main_default` network.

**Monitoring endpoints:**

- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- Locust: http://localhost:8089

---

## Key Findings

**Performance bottleneck** - the backend has no database connection pool limit configured (`SetMaxOpenConns` is
commented out). Under concurrent load, connections pile up and the backend stops responding to POST requests at around
10-15 concurrent users. In a cloud deployment this would require a connection pooler (PgBouncer, RDS Proxy, or Cloud SQL
Proxy) before horizontal scaling is effective.

**Resource usage** - the application itself is lightweight (frontend ~9MB RAM, backend ~7MB RAM). The monitoring stack
consumes more resources than the application it monitors. Prometheus, Loki, and Grafana together need around 600MB-1GB
RAM, which drives node sizing decisions more than the app does.

**Cloud costs** - at production scale (1000 concurrent users, HA configuration, 1 year log retention), the estimated
monthly cost is ~$726 on AWS and ~$675 on GCP. The biggest cost driver is not compute but infrastructure overhead -
managed Kubernetes control planes, NAT Gateways, HA databases, and persistent storage for the monitoring stack.

**AWS vs GCP** - AWS wins on block storage pricing and database cost. GCP wins on NAT Gateway cost, Kubernetes tooling
maturity, and a more useful free tier.

---

## Documentation

| Document                                                          | Contents                                                                                                            |
|-------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| [Glossary](docs/00-glossary.md)                                   | Definitions for all acronyms and terms used across the project                                                      |
| [Infrastructure Analysis](docs/01-infrastructure-analysis.md)     | Resource utilization metrics, bottleneck findings, dependency map, security requirements, full infrastructure specs |
| [Cloud Provider Comparison](docs/02-cloud-provider-comparison.md) | AWS vs GCP service mapping, free tier analysis, pricing model comparison, hidden costs                              |
| [Migration Cost Analysis](docs/03-migration-cost-analysis.md)     | Monthly cost breakdown by component for both providers, optimization opportunities, hidden cost projections         |
| [Risk Assessment](docs/04-risk-assessment.md)                     | Cost controls, billing alerts, resource tagging, cleanup policies, scaling criteria, testing methodology            |
