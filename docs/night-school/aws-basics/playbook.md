# Night School Playbook: AWS Basics & Cloud Solutions

**Audience:** Junior engineers preparing for cloud/SRE roles.  
**Goal:** Build a solid foundation in core AWS services, security, infrastructure‑as‑code, CI/CD, monitoring, cost management, and multi‑cloud awareness.  
**Timeframe:** ~4 weeks of focused study (≈10 h/week) with hands‑on labs.

---

## 1. AWS Core Services

| Service | Primary Use‑Case | Hands‑On Lab |
|---------|-----------------|--------------|
| **EC2** | Virtual servers, custom AMIs | Launch an EC2 instance, SSH, install a web server, create an AMI, terminate.
| **S3** | Object storage, static website hosting | Create a bucket, upload files, set public read, enable versioning & lifecycle.
| **Lambda** | Serverless compute, event‑driven functions | Write a simple Node/Python function that reacts to S3 PUT events.
| **RDS** | Managed relational databases | Deploy a MySQL/PostgreSQL instance, connect via `psql`/MySQL client, enable automated backups.
| **VPC** | Isolated networking, subnets, security groups | Build a VPC with public & private subnets, NAT gateway, and test connectivity.

### Resources
- AWS Free Tier (12 months) – all services above are free within limits.
- Official docs: https://docs.aws.amazon.com/
- Hands‑on tutorials: AWS Skill Builder (search “EC2 Basics”).

---

## 2. Identity & Access Management (IAM)

- **Principles:** least‑privilege, role‑based access, separation of duties.
- **Key Concepts:** Users, Groups, Policies, Roles, MFA, Service‑Linked Roles.
- **Lab:** Create a custom IAM policy that allows read‑only S3 access; attach to a group; test with the AWS CLI.
- **Best Practices:** 
  - Use groups, not per‑user policies.
  - Enforce MFA on privileged accounts.
  - Rotate access keys regularly or use temporary credentials (STS).

---

## 3. Infrastructure as Code (IaC)

### CloudFormation
- Declarative JSON/YAML templates.
- Deploy stacks, change sets, drift detection.
- **Lab:** Write a simple CloudFormation YAML that provisions an EC2 instance + Security Group.

### Terraform (recommended for multi‑cloud)
- HCL language, state management, modules.
- **Lab:** Use Terraform to create an S3 bucket and an IAM role; store state in an S3 backend with DynamoDB locks.

### Comparison Cheat‑Sheet
| Feature | CloudFormation | Terraform |
|---------|----------------|-----------|
| Native AWS | ✅ | ✅ (via provider) |
| Multi‑cloud | ❌ | ✅ |
| State Management | Implicit | Explicit (remote backends) |
| Community Modules | Limited | Vast |

---

## 4. CI/CD Pipelines

- **AWS CodePipeline** – native, integrates with CodeCommit, CodeBuild, CodeDeploy.
- **GitHub Actions** – cloud‑agnostic, can deploy to AWS via the AWS CLI or SAM.
- **Lab:** Build a pipeline that checks out code, runs unit tests, and deploys a Lambda function.
- **Key Concepts:** Stages, actions, approvals, artifact storage.

---

## 5. Monitoring & Observability

| Tool | Scope | Typical Metrics |
|------|-------|-----------------|
| **CloudWatch** | AWS services, custom logs/metrics | CPU, latency, error rates, custom app metrics.
| **X-Ray** | Distributed tracing for Lambda & EC2 | Service maps, latency analysis.
| **Grafana** (self‑hosted or managed) | Dashboards across sources | Combine CloudWatch, Prometheus, Loki.

### Lab:
- Enable CloudWatch Logs for a Lambda, create a metric filter for errors, set an alarm to trigger an SNS notification.

---

## 6. Cost Optimization

- **Free Tier awareness** – stay within limits during learning.
- **Rightsizing** – use instance types that match workload (t3.micro vs m5.large).
- **Reserved Instances / Savings Plans** – for predictable workloads.
- **AWS Budgets & Cost Explorer** – set alerts at 50 %/80 % of monthly budget.
- **Lab:** Create a budget that emails you when spend exceeds $5.

---

## 7. Multi‑Cloud Considerations

- **Why?** Avoid vendor lock‑in, leverage best‑of‑breed services.
- **Common patterns:** 
  - Use Terraform for a unified IaC layer.
  - Deploy workloads to Azure/AWS via a common CI pipeline.
  - Central monitoring with Grafana + Loki/Prometheus.
- **Key Differences:** IAM vs Azure AD, pricing models, networking (VPC vs VNets).
- **Lab (optional):** Spin up an equivalent storage bucket in Azure Blob and sync via `aws s3 sync` + `az storage blob upload`.

---

## 8. Study Plan & Milestones

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Core services (EC2, S3, Lambda) | Deploy a static website on S3 + Lambda edge.
| 2 | IAM & VPC | Secure VPC with bastion host; IAM role for Lambda.
| 3 | IaC (CloudFormation + Terraform) | Complete Terraform module repo on GitHub.
| 4 | CI/CD, Monitoring, Cost | Full CI pipeline with CloudWatch alarms and budget alert.
| 5 (optional) | Multi‑cloud basics | Simple cross‑cloud sync script.

### Assessment
- Pass AWS Certified Cloud Practitioner practice exam (score ≥ 80%).
- Build a mini‑project: serverless API (API Gateway + Lambda) with CI/CD and monitoring.

---

## 9. References & Further Reading

- **AWS Well‑Architected Framework** – https://aws.amazon.com/architecture/well-architected/
- **AWS Docs – Getting Started** – https://aws.amazon.com/getting-started/
- **Terraform Registry** – https://registry.terraform.io/
- **AWS re:Invent 2023 – Serverless Deep Dive** (YouTube)
- **Books:** *Amazon Web Services in Action* (Mann), *Terraform: Up & Running* (Yevgeniy).

---

*Prepared by Nova for Night School – 2026-04-28*