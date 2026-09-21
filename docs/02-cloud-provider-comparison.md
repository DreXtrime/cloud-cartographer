# Cloud Provider Comparison: AWS vs GCP

## 1. Provider Selection Rationale

Two providers were selected for this analysis: Amazon Web Services (AWS) and Google Cloud Platform (GCP).

**AWS** was chosen based on market leadership. AWS holds the largest share of the global cloud
market and is the most widely adopted provider among companies operating in the Baltic region.

**GCP** was chosen as the second provider for several reasons. Kubernetes originated at Google. Since this
infrastructure is Kubernetes heavy, with multiple node groups, autoscaling requirements, and multienvironment clusters,
GCP's native integration and operational tooling for Kubernetes is a bonus. GCP also tends to be more
cost competitive for compute in Europe, it is also something that is mentioned in many Estonian cloud first IT job
postings.

Prices are in dollars as that is the most common unit when returning searches.

---

## 2. Service Mapping

### 2.1 Kubernetes

| Requirement        | AWS                                | GCP                                                                     |
|--------------------|------------------------------------|-------------------------------------------------------------------------|
| Managed Kubernetes | EKS (Elastic Kubernetes Service)   | GKE Standard                                                            |
| Control plane fee  | $0.10/hr per cluster (~$73/month)  | $0.10/hr per cluster (~$73/month), first zonal cluster free per project |
| Node groups        | Managed Node Groups                | Node Pools                                                              |
| Autoscaling        | Cluster Autoscaler / Karpenter     | GKE Cluster Autoscaler                                                  |
| Multi-AZ           | Node groups spread across AZs      | Node pools spread across zones                                          |
| Forbidden modes    | EKS Auto Mode, Fargate             | GKE Autopilot                                                           |
| Node OS            | Amazon Linux                       | Container-Optimized OS                                                  |
| Networking (CNI)   | AWS VPC                            | VPC-native                                                              |
| Ingress            | AWS Load Balancer Controller + ALB | GKE Ingress + Cloud Load Balancing                                      |

### 2.2 Compute (EC2 / Compute Engine)

Node sizing is based on measured resource utilization and projected production requirements.

**Test environment nodes** - light workloads, cost efficiency priority:

| Node Group          | AWS Instance            | AWS On-Demand/mo | GCP Machine Type        | GCP On-Demand/mo |
|---------------------|-------------------------|------------------|-------------------------|------------------|
| main (1 node)       | t3.medium (2 vCPU, 4GB) | ~$30             | e2-medium (2 vCPU, 4GB) | ~$27             |
| monitoring (1 node) | t3.medium (2 vCPU, 4GB) | ~$30             | e2-medium (2 vCPU, 4GB) | ~$27             |
| tools (1 node)      | t3.small (2 vCPU, 2GB)  | ~$15             | e2-small (2 vCPU, 2GB)  | ~$13             |

**Production environment nodes** - HA, multi-AZ, scaled for 1000 concurrent users:

| Node Group           | AWS Instance                | AWS On-Demand/mo | GCP Machine Type            | GCP On-Demand/mo |
|----------------------|-----------------------------|------------------|-----------------------------|------------------|
| main (2 nodes)       | t3.small (2 vCPU, 2GB) × 2  | ~$30             | e2-small (2 vCPU, 2GB) × 2  | ~$26             |
| monitoring (2 nodes) | t3.medium (2 vCPU, 4GB) × 2 | ~$60             | e2-medium (2 vCPU, 4GB) × 2 | ~$54             |
| tools (1-2 nodes)    | t3.small (2 vCPU, 2GB) × 1  | ~$15             | e2-small (2 vCPU, 2GB) × 1  | ~$13             |

### 2.3 Database

| Requirement        | AWS                             | GCP                             |
|--------------------|---------------------------------|---------------------------------|
| Managed PostgreSQL | RDS for PostgreSQL              | Cloud SQL for PostgreSQL        |
| PostgreSQL version | 17                              | 17                              |
| HA option          | Multi-AZ                        | Regional HA                     |
| Backup             | Automated daily + PITR          | Automated daily + PITR          |
| Connection pooling | RDS Proxy ($0.015/vCPU-hr)      | Cloud SQL Proxy (free)          |
| Storage type       | gp3 SSD                         | SSD persistent disk             |
| Encryption at rest | Yes (default)                   | Yes (default)                   |
| Private access     | VPC, no public IP               | VPC, no public IP               |
| Scaling            | Vertical only (resize instance) | Vertical only (resize instance) |

**Test database:**

|                    | AWS RDS                   | GCP Cloud SQL                      |
|--------------------|---------------------------|------------------------------------|
| Instance           | db.t3.small (2 vCPU, 2GB) | db-g1-small (1 vCPU shared, 1.7GB) |
| On-demand/month    | ~$26                      | ~$26                               |
| Storage (20GB SSD) | ~$2.30                    | ~$3.40                             |
| Backups (7 days)   | Included up to DB size    | ~$0.08/GB/month                    |
| **Total est.**     | **~$30/month**            | **~$30/month**                     |

**Production database (HA):**

|                          | AWS RDS Multi-AZ           | GCP Cloud SQL HA              |
|--------------------------|----------------------------|-------------------------------|
| Instance                 | db.t3.medium (2 vCPU, 4GB) | db-standard-2 (2 vCPU, 7.5GB) |
| On-demand/month          | ~$60                       | ~$140                         |
| Storage (100GB SSD)      | ~$12                       | ~$17                          |
| Backups (30 days + PITR) | ~$10                       | ~$12                          |
| **Total est.**           | **~$85/month**             | **~$172/month**               |

### 2.4 Container Registry

|                                         | AWS ECR                            | GCP Artifact Registry               |
|-----------------------------------------|------------------------------------|-------------------------------------|
| Type                                    | Private registry                   | Private registry                    |
| Storage                                 | $0.10/GB/month                     | $0.10/GB/month                      |
| Data transfer (same region, to EKS/GKE) | Free                               | Free                                |
| Data transfer (internet)                | $0.09/GB                           | $0.08/GB                            |
| Free tier                               | 500MB/month (first 12 months only) | None                                |
| Image scanning                          | Basic free, Enhanced $0.09/image   | Container Analysis API, $0.26/image |
| IAM integration                         | AWS IAM                            | Google IAM                          |

Both registries charge identically for storage.  
For a small application with two images (frontend, backend) totaling roughly 500MB-1GB of compressed layers, monthly
storage cost is negligible

### 2.5 Networking

| Component              | AWS                                                | GCP                                            |
|------------------------|----------------------------------------------------|------------------------------------------------|
| VPC                    | Amazon VPC (free)                                  | VPC Network (free)                             |
| Subnets                | Public/private per AZ                              | Regional subnets                               |
| NAT Gateway            | $0.045/hr + $0.045/GB processed                    | Cloud NAT: $0.0014/hr + $0.045/GB              |
| External Load Balancer | ALB: $0.008/LCU-hr + $0.018/hr                     | Cloud Load Balancing: $0.025/rule/hr           |
| Internal Load Balancer | NLB or ALB internal                                | Internal TCP/UDP load balancer                 |
| Public DNS             | Route 53: $0.50/zone/month + $0.40/1M queries      | Cloud DNS: $0.20/zone/month + $0.40/1M queries |
| Private DNS            | Route 53 private hosted zone: $0.10/zone + queries | Cloud DNS private zone: $0.20/zone             |
| Static public IPs      | $0.005/hr per IP (~$3.65/month)                    | $0.004/hr per IP (~$3/month)                   |
| Cross-AZ traffic       | $0.01/GB each direction                            | Free within same region                        |

### 2.6 DNS and Domains

|                              | AWS Route 53              | GCP Cloud DNS               |
|------------------------------|---------------------------|-----------------------------|
| Public hosted zone           | $0.50/zone/month          | $0.20/zone/month            |
| Private hosted zone          | $0.10/zone/month          | $0.20/zone/month            |
| DNS queries (first 1B/month) | $0.40/1M                  | $0.40/1M                    |
| Domain registration          | Supported (varies by TLD) | Supported via Cloud Domains |

For this infrastructure, two public zones and two private zones are needed (one per environment).

### 2.7 Storage (Persistent Volumes and Object Storage)

|                          | AWS                     | GCP                                |
|--------------------------|-------------------------|------------------------------------|
| Block storage (EBS/PD)   | gp3: $0.08/GB/month     | pd-ssd: $0.17/GB/month             |
| Block storage IOPS       | gp3: 3000 IOPS included | pd-ssd: included, scales with size |
| Object storage           | S3: $0.023/GB/month     | Cloud Storage: $0.020/GB/month     |
| Object storage retrieval | S3 Standard: free reads | Cloud Storage: free reads          |

### 2.8 VPN

|                     | AWS Client VPN          | GCP Cloud VPN         | Self-managed WireGuard |
|---------------------|-------------------------|-----------------------|------------------------|
| Endpoint cost       | $0.10/hr (~$73/month)   | $0.05/hr (~$36/month) | VM cost only           |
| Per-connection cost | $0.05/hr per connection | Included              | Included               |
| Complexity          | Low (managed)           | Low (managed)         | Medium                 |
| Recommended for     | Large teams             | Medium teams          | Small teams            |

**Self-managed WireGuard on a small VM.** For a small development team accessing internal services (Grafana,
ArgoCD), AWS Client VPN at is difficult to justify, GCP Cloud VPN is more
reasonable but still adds cost. A WireGuard VM on a little VM runs for ~$7-8/month and provides
equivalent functionality for a small number of developers.

### 2.9 GitLab (Self managed)

|             | AWS                             | GCP                             |
|-------------|---------------------------------|---------------------------------|
| VM instance | t3.medium (2 vCPU, 4GB) ~$30/mo | e2-medium (2 vCPU, 4GB) ~$24/mo |
| Storage     | EBS gp3 50GB: ~$4/mo            | pd-ssd 50GB: ~$8.50/mo          |
| **Total**   | **~$34/month**                  | **~$57/month**                  |

GitLab self-managed is cheaper on AWS due to the EBS vs pd-ssd storage price difference. GitLab CI runners run
as Kubernetes pods in the tools node group and have no additional VM cost.

### 2.10 Monitoring Stack

The monitoring stack (Grafana, Prometheus, Loki, Promtail, exporters) runs as pods in the monitoring node group. No
additional cloud service costs beyond the node compute and persistent storage volumes.

| Storage volume                      | AWS (gp3)         | GCP (pd-ssd)      |
|-------------------------------------|-------------------|-------------------|
| Prometheus data (50GB per env)      | ~$4/month         | ~$8.50/month      |
| Loki data (200GB per env, 1yr logs) | ~$16/month        | ~$34/month        |
| Grafana (5GB per env)               | ~$0.40/month      | ~$0.85/month      |
| **Per environment total**           | **~$20.40/month** | **~$43.35/month** |

AWS's cheaper block storage makes a meaningful impact on monitoring storage costs,
particularly for Loki with 1-year log retention.

---

## 3. Free Tier Analysis

### 3.1 AWS Free Tier

| Service                      | Free Tier                      | Duration  | Applicable?                     |
|------------------------------|--------------------------------|-----------|---------------------------------|
| EC2 t2.micro                 | 750 hours/month                | 12 months | No - insufficient for K8s nodes |
| RDS (Single-AZ, db.t2.micro) | 750 hours/month + 20GB storage | 12 months | Partially - DB only for testing |
| ECR                          | 500MB storage                  | 12 months | Yes - covers images initially   |
| S3                           | 5GB storage, 20K GET, 2K PUT   | 12 months | Minimal benefit                 |
| Route 53                     | None                           | N/A       | No                              |
| EKS                          | None - $0.10/hr always         | N/A       | No                              |
| NAT Gateway                  | None                           | N/A       | No                              |
| Data transfer out            | First 100GB/month              | Always    | Yes - at our traffic volumes    |

AWS free tier provides limited benefit for this infrastructure. The most valuable always-free
tier is the first 100GB/month outbound data transfer.

### 3.2 GCP Free Tier

| Service                   | Free Tier                               | Duration | Applicable?                             |
|---------------------------|-----------------------------------------|----------|-----------------------------------------|
| GKE (one zonal cluster)   | $74.40/month credit per billing account | Always   | Yes - covers test cluster control plane |
| Compute Engine (e2-micro) | 1 instance/month in select regions      | Always   | Yes - WireGuard VM                      |
| Cloud Storage             | 5GB regional, 5000 Class A ops          | Always   | Minimal                                 |
| Cloud SQL                 | None                                    | N/A      | No                                      |
| Cloud NAT                 | None                                    | N/A      | No                                      |
| Artifact Registry         | None                                    | N/A      | No                                      |
| Data transfer out         | First 1GB/month                         | Always   | Negligible                              |
| New account credits       | $300                                    | 90 days  | Yes - covers initial testing            |

GCP's most valuable always-free offering for this project is the GKE zonal cluster credit,
which fully covers the control plane cost of one cluster. Applied to the test environment, this saves
$73/month ongoing, more valuable than AWS's time-limited free tier items.

The free e2-micro instance can run the WireGuard VPN, eliminating that cost entirely on GCP.

---

## 4. Pricing Model Comparison

### 4.1 On Demand vs Reserved vs Spot

**On-Demand**

Pay per hour with no commitment. Highest cost, most flexibility. For test environments and unpredictable workloads.

| Provider | Model name | Commitment | Savings |
|----------|------------|------------|---------|
| AWS      | On-Demand  | None       | 0%      |
| GCP      | On-Demand  | None       | 0%      |

**Reserved / Committed Use**

| Provider | Model name                    | Term        | Savings   | Payment                              |
|----------|-------------------------------|-------------|-----------|--------------------------------------|
| AWS      | Reserved Instances            | 1 year      | ~37%      | No upfront, partial, or full upfront |
| AWS      | Reserved Instances            | 3 year      | ~57%      | No upfront, partial, or full upfront |
| AWS      | Compute Savings Plans         | 1 or 3 year | Up to 66% | Flexible - applies to any EC2        |
| GCP      | Committed Use Discounts (CUD) | 1 year      | ~37%      | No upfront - automatic               |
| GCP      | Committed Use Discounts (CUD) | 3 year      | ~55%      | No upfront - automatic               |

**Spot / Preemptible**

| Provider | Model          | Savings vs On-Demand | Interruption behavior              |
|----------|----------------|----------------------|------------------------------------|
| AWS      | Spot Instances | 60-90%               | 2-minute warning, then terminated  |
| GCP      | Spot VMs       | 60-91%               | 30-second warning, then terminated |

Both providers' spot/preemptible instances are suitable for the test environment node groups and the tools node group
(ArgoCD, runners).

### 4.2 Data Transfer Costs

The application serves small JSON payloads, session checks return ~400 bytes, login responses ~500 bytes. At 1000
concurrent users, realistic outbound traffic is around 20-25GB/month, well within both providers 100GB/month free
egress tier. Egress cost is effectively $0 for this workload.

The relevant transfer cost is AWS cross-AZ traffic
at $0.01/GB per direction. Prometheus scraping pods across AZs every 15 seconds adds an estimated $5-15/month. GCP does
not charge for cross-zone traffic within a region.

### 4.3 Supplementary and Hidden Costs

| Cost item                         | AWS                                 | GCP                                | Notes                                    |
|-----------------------------------|-------------------------------------|------------------------------------|------------------------------------------|
| Public IPv4 addresses             | $0.005/hr (~$3.65/mo each)          | $0.004/hr (~$2.92/mo each)         | Each load balancer, NAT gateway uses IPs |
| NAT Gateway                       | $3.94/mo × 3 AZs = ~$12/mo          | ~$1/mo × 3 zones = ~$3/mo          | Major cost difference                    |
| Secrets management                | Secrets Manager: $0.40/secret/month | Secret Manager: $0.06/10K accesses | GCP significantly cheaper                |
| Certificate management            | ACM: Free (for ALB/CloudFront)      | Certificate Manager: Free          | Both free with managed LBs               |
| Monitoring/logging                | CloudWatch: $0.30/GB ingested       | Cloud Logging: $0.01/GB after 50GB | GCP cheaper for logging                  |
| API Gateway                       | Not required                        | Not required                       | ArgoCD/GitLab handle CI/CD               |
| EKS add-ons (LB Controller, etc.) | Free but require setup              | Included in GKE                    | GKE simpler                              |
| RDS Proxy (connection pooling)    | $0.015/vCPU-hr                      | Cloud SQL Proxy: Free              | GCP advantage                            |
| Support plan                      | Developer: $29/mo min               | Standard: 3% of monthly bill       | Varies by usage                          |

---

## 5. Summary Comparison

| Category                 | AWS                       | GCP                              | Winner |
|--------------------------|---------------------------|----------------------------------|--------|
| Kubernetes control plane | $73/cluster/month         | $73/cluster/month (1 free)       | GCP    |
| Compute (on-demand)      | Cheaper (t3 family)       | More expensive (n2 family)       | AWS    |
| Compute (committed)      | Similar (37% off)         | Similar (37% off, more flexible) | GCP    |
| Database                 | Slightly cheaper          | Slightly more expensive          | AWS    |
| Block storage            | $0.08/GB (gp3)            | $0.17/GB (pd-ssd)                | AWS    |
| NAT Gateway              | $33/mo + $0.045/GB per AZ | $1/mo + $0.045/GB per AZ         | GCP    |
| Cross-AZ traffic         | $0.01/GB                  | Free                             | GCP    |
| Free tier (ongoing)      | Limited                   | GKE cluster + e2-micro           | GCP    |
| Documentation/tooling    | Excellent                 | Very good                        | AWS    |

Official pricing references:

~~- AWS pricing: https://aws.amazon.com/pricing/

- AWS EKS pricing: https://aws.amazon.com/eks/pricing/
- AWS RDS pricing: https://aws.amazon.com/rds/postgresql/pricing/
- AWS EC2 pricing: https://aws.amazon.com/ec2/pricing/on-demand/
- AWS data transfer pricing: https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer~~
- GCP pricing: https://cloud.google.com/pricing
- GKE pricing: https://cloud.google.com/kubernetes-engine/pricing
- GCP Compute Engine pricing: https://cloud.google.com/compute/vm-instance-pricing
- Cloud SQL pricing: https://cloud.google.com/sql/pricing
- GCP network pricing: https://cloud.google.com/vpc/network-pricing