# Risk Assessment & Management Plan

## 1. Cost Management

The main risks are resources left running that nobody needs,
storage that grows indefinitely.

### Billing Alerts

Both AWS and GCP support budget alerts that send an email or trigger a notification when spending crosses a threshold.
These should be set up before any infrastructure is provisioned.

Recommended budgets:

| Environment | Monthly budget | Alert at   |
|-------------|----------------|------------|
| Test        | $300           | 80% ($240) |
| Production  | $600           | 80% ($480) |
| Shared      | $50            | 80% ($40)  |

Alerts at 80% give enough warning to investigate before the budget is actually exceeded. A second alert at 100% should
also be configured so there is no ambiguity when the limit is hit.

### What to Watch

The items most likely to cause unexpected cost increases:

- **NAT Gateway data processing** - charges per GB processed, easy to miss during high traffic periods
- **Loki storage** - grows continuously, no automatic cap
- **Database backup storage** - accumulates silently beyond the base instance cost
- **Autoscaling** - new nodes added during traffic spikes are billed by the hour, can add up if spikes are frequent
- **Idle test environment** - the test cluster running overnight or on the weekends could be complete waste

---

## 2. Resource Tagging

Every cloud resource should be tagged or labeled from the start. 

Minimum required tags:

| Tag           | Example values                               |
|---------------|----------------------------------------------|
| `environment` | test, prod, shared                           |
| `component`   | app, monitoring, tools, database, networking |
| `managed-by`  | terraform, manual                            |
| `owner`       | team name or person                          |

On AWS, tags can be used to filter the Cost Explorer to see spending broken down by environment or component.

---

## 3. Resource Optimization

### Test Environment

The test environment does not need to run 24/7. Shutting down compute nodes outside working hours.

Both providers have schedulers that can automate this

### Production Environment

Production nodes should be covered by reserved instances (AWS) or committed use discounts (GCP) after the first month
of running, once actual usage patterns are confirmed. Committing too early risks being locked into the wrong instance
size.

The main node group in production uses autoscaling with a minimum of 2 nodes. The minimum should be reviewed after the
first month and if average CPU stays below 20% it can likely be reduced to 1 node outside peak hours.

### Container Images

Without a cleanup policy, container registries accumulate old image versions indefinitely. A lifecycle policy should
delete images older than 30 days, keeping only the last 5 versions of each image.

---

## 4. Risk Mitigation

### Things That Will Go Wrong

**Cost spikes** - autoscaling adds nodes, a bug causes excessive logging, or a runaway process hits the database.
Billing alerts catch this but only after the fact. Setting hard limits on autoscaler maximum node counts prevents the
worst case.

**Database failover** - in production the database has HA configured, but failover is not instant. RDS Multi-AZ
typically takes 60-120 seconds to fail over.

**Log storage filling up** - Loki has no built-in storage cap. If the underlying persistent volume fills up, Loki stops
accepting logs and the pod crashes. Storage should be monitored and volume size increased before it becomes a problem.
Retention policies should be configured in Loki to automatically delete logs older than one year. A crash looping container 
generating thousands of lines per second will quickly consume available space

**Secrets in environment variables** - the sample application currently stores database credentials and JWT keys in
environment variables. In cloud these should be stored in AWS Secrets Manager or GCP Secret Manager and injected at
runtime, not hardcoded in deployment configs.

### Testing in Cloud

Cloud environments behave differently from local Docker Compose setups. Things to test before going live:

- Database connection pooling behavior under load, the connection pool bug identified locally will behave the same in
  cloud until resolved
- Autoscaling response time - how long does it take for a new node to become ready and start accepting pods
- Failover - manually trigger a database failover in the test environment and verify the application recovers

Run the same Locust test used for the performance baseline against the cloud environment after deployment. Results
should be compared against the local baseline to identify any regressions introduced by the cloud configuration.

---