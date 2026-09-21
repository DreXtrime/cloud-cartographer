# Migration Cost Analysis

## 1. CapEx vs OpEx

Traditional infrastructure is a capital expenditure (CapEx) model. You buy servers, networking equipment,
and licenses upfront, depreciate them over several years, and pay ongoing maintenance costs. The hardware is yours, but
so is the risk of it becoming obsolete or failing.

Cloud is an operational expenditure (OpEx) model, you pay monthly for what you use with no upfront hardware costs.
This shifts the risk to the provider and makes scaling up or down straightforward. The tradeoff is that cloud costs
are endless, whereas owned hardware eventually pays itself off.

For this infrastructure, the OpEx model makes sense. The workload is variable (up to 1000 concurrent users but likely
much less outside peak hours), the team is small, and the operational overhead of managing physical servers would
outweigh any long-term cost savings from ownership. Although since the application is so simple most of the cost
comes from additional utilities like the monitoring stack.

---

## 2. Monthly Cost Estimate

All prices are on-demand unless noted. Region: eu-west-1 (AWS) / europe-west4 (GCP).

### 2.1 Test Environment

| Component                                                     | AWS             | GCP             |
|---------------------------------------------------------------|-----------------|-----------------|
| EKS/GKE control plane                                         | $73             | $0 (free tier)  |
| main node (t3.medium / e2-medium)                             | $30             | $27             |
| monitoring node (t3.medium / e2-medium)                       | $30             | $27             |
| tools node (t3.small / e2-small)                              | $15             | $13             |
| RDS / Cloud SQL (db.t3.small / db-g1-small)                   | $30             | $30             |
| NAT Gateway                                                   | $33             | $10             |
| Load balancer                                                 | $18             | $15             |
| Monitoring storage (Prometheus 50GB, Loki 200GB, Grafana 5GB) | $20             | $43             |
| Container registry (shared, split)                            | $1              | $1              |
| DNS (public + private zones)                                  | $1              | $1              |
| WireGuard VM                                                  | $8              | $0 (free tier)  |
| **Test total**                                                | **~$259/month** | **~$167/month** |

GCP's free GKE cluster credit and free e2-micro for WireGuard make a significant difference at the test level.

### 2.2 Production Environment

| Component                                                     | AWS       | GCP             |
|---------------------------------------------------------------|-----------|-----------------|
| EKS/GKE control plane                                         | $73       | $73             |
| main nodes (t3.small × 2 / e2-small × 2)                      | $30       | $26             |
| monitoring nodes (t3.medium × 2 / e2-medium × 2)              | $60       | $54             |
| tools node (t3.small / e2-small)                              | $15       | $13             |
| RDS Multi-AZ / Cloud SQL HA (db.t3.medium / db-standard-2)    | $85       | $189            |
| NAT Gateway (3 AZs)                                           | $99       | $3              |
| External load balancer                                        | $18       | $15             |
| Internal load balancer                                        | $15       | $12             |
| Monitoring storage (Prometheus 50GB, Loki 200GB, Grafana 5GB) | $20       | $43             |
| Container registry (shared, split)                            | $1        | $1              |
| DNS (public + private zones)                                  | $1        | $1              |
| Public IPv4 addresses (~4 IPs)                                | $15       | $12             |
| **Production total**                                          | **~$432** | **~$442/month** |

### 2.3 Shared Resources

| Component                          | AWS            | GCP            |
|------------------------------------|----------------|----------------|
| GitLab VM (t3.medium / e2-medium)  | $30            | $27            |
| GitLab storage (50GB EBS / pd-ssd) | $4             | $9             |
| Container registry storage (~1GB)  | $1             | $1             |
| **Shared total**                   | **~$35/month** | **~$37/month** |

### 2.4 Total Monthly

|                        | AWS             | GCP             |
|------------------------|-----------------|-----------------|
| Test environment       | $259            | $167            |
| Production environment | $432            | $442            |
| Shared resources       | $35             | $37             |
| **Grand total**        | **~$726/month** | **~$637/month** |

GCP comes out slightly cheaper overall, mainly due to the free test cluster and cheaper NAT. AWS is cheaper in
production due to significantly lower database and block storage costs.

---

## 3. Cost Optimizations

Applying reserved instances (AWS) or committed use discounts (GCP) to production nodes and the database brings
production compute costs down by roughly 40%:

|                                | AWS (1yr reserved) | GCP (1yr CUD)   |
|--------------------------------|--------------------|-----------------|
| Production compute savings     | ~$35/month         | ~$30/month      |
| Database savings               | ~$30/month         | ~$55/month      |
| **Optimized production total** | **~$367/month**    | **~$395/month** |

Using spot instances for the test environment node groups reduces test compute costs by 60-70%:

|                            | AWS (spot) | GCP (spot) |
|----------------------------|------------|------------|
| Test compute (all 3 nodes) | ~$8/month  | ~$7/month  |
| Saving vs on-demand        | ~$37/month | ~$30/month |

---

## 4. Hidden and Accumulating Costs

**Log storage growth** - Loki is configured to retain logs for one year. Starting from near zero, storage grows
continuously. At the measured ingestion rate of ~1-5KB/s, annual log storage reaches roughly 150-200GB per environment.
The estimates above already account for this at steady state, but in year one costs start lower and grow month over
month.

**Database backup storage** - production is configured with 30 daily backups and 7 days of PITR logs. At ~100GB
database size this adds roughly $10-15/month in backup storage that grows with the database.

**Scaling events** - the production compute estimates assume minimum node counts. During traffic spikes the autoscaler
adds nodes, each billed by the hour. At peak load (1000 concurrent users), the main node group may temporarily scale to
3-4 nodes, adding to the monthly bill depending on duration.

**Container image storage** - ECR and Artifact Registry storage grows with each image push. CI/CD pipelines that build
on every commit accumulate image layers quickly without a cleanup policy. Without lifecycle rules, this can reach many
GB quickly,
not that expensive but worth mentioning.

**Idle test environment** - the test environment runs 24/7 in these estimates. Shutting it down outside working hours
would cut test compute costs.

---

## 5. Full Cloud vs On-premises

Running this infrastructure on-premises would require purchasing servers, networking equipment, UPS systems, and
potentially
physical hosting in a data center. For a small team, the upfront CapEx for equivalent HA infrastructure would likely
reach 10's of thousands, with ongoing power, cooling, and maintenance costs on top.

At ~$700/month for full cloud, the break-even against on-premises ownership could be years
before accounting for the engineering time saved by using managed services for Kubernetes, the database, and container
registry. For a startup or small company, cloud is almost always the right choice at this scale.

The main drawbacks of full cloud implementation are cost unpredictability (scaling events, storage growth, and data
transfer can cause bill spikes) and the ongoing OpEx commitment, unlike owned hardware, the bill never stops.

---