# Night School Playbook – AWS Basics & Cloud Solutions

**Purpose**: Provide a concise, actionable reference for getting up‑to‑speed with Amazon Web Services (AWS) core services, security best practices, infrastructure‑as‑code, CI/CD pipelines, monitoring, cost optimization, and multi‑cloud considerations. Designed for nightly self‑study sessions and quick lookup while building or maintaining cloud‑enabled projects.

---

## 1. Core AWS Services Overview

| Service | Category | Typical Use‑Case |
|--------|----------|-----------------|
| **EC2** | Compute | Virtual servers, custom AMIs, auto‑scaling groups |
| **S3** | Storage | Object storage, static website hosting, data lake |
| **Lambda** | Serverless Compute | Event‑driven functions, API back‑ends, cron jobs |
| **RDS** | Managed Databases | PostgreSQL, MySQL, Aurora – relational DBaaS |
| **DynamoDB** | NoSQL Database | Key‑value / document store, high‑throughput apps |
| **VPC** | Networking | Isolated networking, subnets, security groups, NAT |
| **IAM** | Identity & Access | Users, roles, policies, temporary credentials |
| **CloudFront** | CDN | Global content delivery, edge caching |
| **ECS / EKS** | Container Orchestration | Docker containers on Fargate or EC2, Kubernetes |
| **SQS / SNS** | Messaging | Queues, pub/sub, fan‑out patterns |
| **CloudWatch** | Monitoring & Logging | Metrics, alarms, log groups |
| **AWS Config** | Governance | Resource configuration history & compliance |
| **CodeCommit / CodeBuild / CodeDeploy / CodePipeline** | CI/CD | Source control, build, deployment pipelines |
| **Route 53** | DNS | Hosted zones, health‑checks, traffic routing |

---

## 2. IAM – Security Foundations

1. **Principle of Least Privilege** – Grant only needed permissions.
2. **Use Roles over Users** for services & EC2 instances.
3. **Managed Policies** for common sets, custom policies for fine‑grained control.
4. **MFA** for all privileged IAM users.
5. **Service‑Linked Roles** for AWS services (e.g., Lambda, ECS).
6. **Permission Boundaries** to limit maximum allowed actions.
7. **IAM Access Analyzer** → detect unintended public access.
8. **Rotate Access Keys** regularly; prefer IAM Roles + STS tokens.

---

## 3. Networking Fundamentals (VPC)

- **CIDR Planning** – Use non‑overlapping ranges (e.g., 10.0.0.0/16).
- **Public vs Private Subnets** – Public for ALBs/NAT, private for DB & app servers.
- **Security Groups** – Stateful, attach to ENIs.
- **Network ACLs** – Stateless, for subnet‑level filtering.
- **VPC Peering / Transit Gateway** – Connect multiple VPCs.
- **Interface Endpoints (AWS PrivateLink)** – Access AWS services without internet.

---

## 4. Infrastructure as Code (IaC)

### Terraform (recommended)
```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
# … additional resources …
```
- Store state in **S3** with **DynamoDB table** for locking.
- Use **modules** for reusable patterns (VPC, ECS cluster, etc.).

### CloudFormation (AWS‑native)
```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket-${AWS::Region}
```
- Leverage **Change Sets** for safe updates.
- Parameterize with **SSM Parameter Store**.

---

## 5. CI/CD Pipelines

### CodePipeline Example (S3 → Lambda)
1. **Source** – CodeCommit repo.
2. **Build** – CodeBuild (install deps, run tests).
3. **Deploy** – CloudFormation stack update (Lambda function).

### GitHub Actions + AWS CLI (cross‑platform)
```yaml
name: Deploy Lambda
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: sam build && sam deploy --no-confirm-changeset --stack-name my-stack --capabilities CAPABILITY_IAM
```
- Prefer **IAM Role** for GitHub OIDC rather than long‑lived keys.

---

## 6. Monitoring, Logging & Alerting

- **CloudWatch Metrics** – CPU, Network, Lambda Duration, SQS ApproximateNumberOfMessages.
- **CloudWatch Alarms** – Thresholds → SNS topics (email/Slack).
- **Logs** – CloudWatch Log Groups; enable **structured logging** (JSON) for query.
- **X‑Ray** – Distributed tracing for Lambda & ECS.
- **Grafana + Prometheus** – For custom dashboards (via Managed Service Prometheus).
- **AWS Health Dashboard** – Service‑level incidents.

---

## 7. Cost Optimization

| Technique | Tool / Action |
|-----------|----------------|
| **Right‑size** instances | Compute Optimizer, Trusted Advisor |
| **Spot Instances** for fault‑tolerant workloads |
| **Savings Plans** – 1‑yr/3‑yr commitment |
| **S3 Lifecycle** – Transition to IA/Glacier |
| **Lambda Power Tuning** – Adjust memory for cost/performance |
| **Budget Alerts** – Set budgets in Cost Explorer, SNS notifications |
| **Tagging** – Enforce cost allocation tags (project, env) |
| **Serverless Off‑load** – Replace idle EC2 with Lambda/ECS Fargate |

---

## 8. Multi‑Cloud & Hybrid Considerations

- Use **Terraform** as a single source of truth across AWS, GCP, Azure.
- **Data synchronization** – AWS Direct Connect / VPN for on‑prem to VPC.
- **Identity federation** – OIDC between AWS and Azure AD or Okta.
- **Cloud‑agnostic CI/CD** – GitHub Actions, CircleCI with provider‑specific steps.
- **Observability stack** – OpenTelemetry agents to send traces to a central collector.

---

## 9. Study & Practice Checklist

1. **Create a free AWS account** (or use existing). Enable MFA.
2. **Set up CLI** – `aws configure` with IAM user limited to `ReadOnlyAccess`.
3. **Launch a VPC** via CloudFormation/Terraform.
4. **Deploy a simple EC2 + S3 static site**.
5. **Create a Lambda function** triggered by S3 upload (Hello‑World).
6. **Build a CI pipeline** that updates the Lambda on push.
7. **Configure CloudWatch alarm** for Lambda errors → SNS email.
8. **Run Cost Explorer** to view free‑tier usage and set a budget.
9. **Document** each step in a markdown file under `docs/night-school/aws/notes/`.

---

## 10. References
- AWS Well‑Architected Framework – https://aws.amazon.com/architecture/well-architected/
- Terraform AWS Provider Docs – https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- AWS Serverless Application Model (SAM) – https://aws.amazon.com/serverless/sam/
- AWS Security Best Practices – https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-bestpractices.html
- Cost Optimization Guide – https://aws.amazon.com/pricing/cost-optimization/

---

*End of Playbook – ready for the next NightSchool session.*