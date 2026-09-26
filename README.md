# Cloud Cartographer

A cloud migration readiness study for a small application stack. The goal was to stress test the app
locally, find where it actually breaks, measure real resource usage, and then work out what it would cost to run it
properly on AWS and GCP.

This project came before [Voyager](https://github.com/yourusername/voyager), where I actually deployed the
infrastructure to GCP. This is the analysis that informed those decisions.

---

## What this project covers

The sample app (React frontend, Go backend, PostgreSQL) was run locally with a full monitoring stack attached:
Prometheus, Loki, Grafana, and a Postgres exporter. Load was generated using Locust with a realistic user flow:
register, login, check session, logout, failed login attempts. Everything ran in Docker Compose across three separate
stacks sharing a network.

The point was to get real numbers before making any cloud decisions, not estimates pulled from documentation.

From there I mapped the stack to equivalent services on both AWS and GCP, built out a full monthly cost breakdown across
test, prod, and shared environments, and compared where each provider wins and loses.

| Report                    | Wiki                                                                                      |
|---------------------------|-------------------------------------------------------------------------------------------|
| Infrastructure Analysis   | [here](https://github.com/DreXtrime/cloud-cartographer/wiki/1.-Infrastructure-Analysis)   |
| Cloud Provider Comparison | [here](https://github.com/DreXtrime/cloud-cartographer/wiki/2.-Cloud-Provided-Comparison) |
| Migration Cost Analysis   | [here](https://github.com/DreXtrime/cloud-cartographer/wiki/3.-Migration-Cost-Analysis)   |
| Risk Assessment           | [here](https://github.com/DreXtrime/cloud-cartographer/wiki/4.-Risk-Assessment)           |

---

## What I found

**The app broke earlier than expected.** The backend has no database connection pool limit configured. Under concurrent
load, connections pile up and the backend stops responding to POST requests at around 10-15 concurrent users. In a cloud
deployment this would need a connection pooler like PgBouncer or Cloud SQL Proxy before horizontal scaling is actually
useful.

**The monitoring stack costs more to run than the app itself.** The application uses around 60MB of RAM total across
frontend and backend. Prometheus, Loki, and Grafana together need 600MB to 1GB. That affected node sizing decisions more
than the app did.

**GCP comes out cheaper overall, but not for the reason I expected.** The test environment is significantly cheaper on
GCP ($167 vs $259/month) mostly because GCP gives you one free GKE control plane and a free e2-micro instance. In
production the gap closes and AWS actually wins on database and block storage pricing. The place GCP wins big is NAT
Gateway: AWS charges per AZ and it adds up fast across multiple availability zones.

**The biggest cost driver at production scale is not compute.** It's the supporting infrastructure: managed Kubernetes
control planes, NAT Gateways, HA databases, load balancers, and monitoring storage. The actual application workload is
cheap. The surrounding stuff is not.

---

## Cost summary

|                        | AWS             | GCP             |
|------------------------|-----------------|-----------------|
| Test environment       | ~$259/month     | ~$167/month     |
| Production environment | ~$432/month     | ~$442/month     |
| Shared resources       | ~$35/month      | ~$37/month      |
| **Total**              | **~$726/month** | **~$637/month** |

Full breakdowns by component are in the docs.

---

## Repository layout

```
sample-app-main/    The application that was analyzed (frontend, backend, db)
monitoring/         Local monitoring stack (Prometheus, Loki, Grafana, Promtail)
locust/             Load testing setup
docs/
  00-glossary.md              Terms and acronyms used throughout
  01-infrastructure-analysis.md   Resource metrics, bottleneck findings, full specs
  02-cloud-provider-comparison.md AWS vs GCP service mapping, pricing models, hidden costs
  03-migration-cost-analysis.md   Monthly cost breakdown by component for both providers
  04-risk-assessment.md           Cost controls, scaling criteria, billing alerts
```

---

## Related

[Voyager](https://github.com/drextrime/voyager) is the follow-up project where I actually built and deployed the GCP
infrastructure analyzed here, using Terraform, GKE, ArgoCD, and GitLab CI.