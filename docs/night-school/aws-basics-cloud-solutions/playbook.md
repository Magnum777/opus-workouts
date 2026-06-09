# Night School Playbook – AWS Basics & Cloud Solutions (Generated 2026-05-01)

**Purpose**: Provide a compact, up‑to‑date learning guide for the "AWS basics & cloud solutions" topic, consolidating core service overviews, security, IaC, CI/CD, monitoring, cost‑optimization, and multi‑cloud considerations. This playbook is intended for nightly self‑study sessions and quick reference while building cloud‑enabled projects.

---

## 1️⃣ Core AWS Services Overview
| Service | Category | Typical Use |
|--------|----------|------------|
| **EC2** | Compute | Virtual servers, custom AMIs, auto‑scaling groups |
| **S3** | Storage | Object storage, static website hosting, data lake |
| **Lambda** | Serverless Compute | Event‑driven functions, API back‑ends, cron jobs |
| **RDS** | Managed Databases | PostgreSQL, MySQL, Aurora |
| **DynamoDB** | NoSQL Database | High‑throughput key‑value store |
| **VPC** | Networking | Isolated networking, subnets, security groups |
| **IAM** | Identity & Access | Users, groups, roles, policies, MFA |
| **CloudFront** | CDN | Global edge caching for static & dynamic content |
| **ECS / EKS** | Containers | Docker on Fargate or EC2, Kubernetes |
| **SQS / SNS** | Messaging | Queues and pub/sub patterns |
| **CloudWatch** | Monitoring | Metrics, logs, alarms |
| **AWS Config** | Governance | Resource configuration tracking |
| **CodeCommit / CodeBuild / CodePipeline** | CI/CD | Source, build, deployment orchestration |
| **Route 53** | DNS | Hosted zones, health checks, traffic routing |

---

## 2️⃣ Identity & Access Management (IAM)
- **Principle of Least Privilege** – grant only needed actions.
- Prefer **IAM Roles** over long‑lived user credentials for services & EC2.
- Use **Managed Policies** for common sets; create **Custom Policies** for fine‑grained control.
- Enable **MFA** on privileged accounts.
- Leverage **Service‑Linked Roles** for AWS services.
- **Permission Boundaries** to cap maximum permissions.
- Regularly audit with **IAM Access Analyzer** and **Access Advisor**.

---

## 3️⃣ Networking (VPC)
- Plan CIDR blocks (e.g., 10.0.0.0/16) to avoid overlap.
- Separate **Public** (ALB/NAT) and **Private** subnets (DB, app servers).
- Use **Security Groups** (stateful) for instance‑level rules; **Network ACLs** for subnet‑level.
- Enable **VPC Flow Logs** for traffic visibility.
- Optional: **Interface VPC Endpoints (PrivateLink)** for AWS services without internet.

---

## 4️⃣ Infrastructure as Code (IaC)
### Terraform (recommended)
```hcl
provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source   = "terraform-aws-modules/vpc/aws"
  name     = "nightschool-vpc"
  cidr     = "10.0.0.0/16"
  azs      = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]
}
```
- Store state in **S3** with **DynamoDB** locking.
- Build reusable modules for VPC, ECS cluster, RDS, etc.

### CloudFormation (AWS‑native)
```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: nightschool-static-${AWS::Region}
```
- Use **Change Sets** for safe updates.
- Parameterize with **SSM Parameter Store** for secrets.

---

## 5️⃣ CI/CD Pipelines
### CodePipeline (AWS native)
1. **Source** – CodeCommit repo.
2. **Build** – CodeBuild (run tests, package).
3. **Deploy** – CloudFormation stack for Lambda or ECS.

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
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeploy
          aws-region: us-east-1
      - run: sam build && sam deploy --no-confirm-changeset --stack-name nightschool-stack --capabilities CAPABILITY_IAM
```
- Prefer **OIDC federation** for GitHub → AWS role (no static keys).

---

## 6️⃣ Monitoring, Logging & Alerting
- **CloudWatch Metrics**: CPUUtilization, Memory, Lambda Duration, SQS ApproximateNumberOfMessages.
- **Alarms** → SNS (email/Slack) for thresholds (e.g., EC2 CPU > 80%).
- **Logs**: Structured JSON logs in CloudWatch Log Groups.
- **X‑Ray** for distributed tracing (Lambda + API Gateway).
- **CloudTrail** for audit logging of API calls.
- Optional: **Grafana + Managed Prometheus** for custom dashboards.

---

## 7️⃣ Cost Management
| Technique | Tool |
|-----------|------|
| Right‑size instances | Compute Optimizer, Trusted Advisor |
| Spot Instances for fault‑tolerant workloads |
| Savings Plans / Reserved Instances |
| S3 Lifecycle policies (Standard → IA → Glacier) |
| Lambda memory tuning |
| Budgets & alerts | Cost Explorer, SNS |
| Tag‑based cost allocation (project, env) |

---

## 8️⃣ Multi‑Cloud & Hybrid Concepts
- Use **Terraform** as a single source of truth across AWS, Azure, GCP.
- **Data sync**: AWS Direct Connect / VPN to on‑prem or other clouds.
- **Identity federation**: OIDC between AWS and Azure AD / Okta.
- **Observability**: OpenTelemetry agents to a centralized backend.
- **Portable workloads**: Containerize with Docker, orchestrate via Kubernetes (EKS + GKE + AKS).

---

## 9️⃣ Practical Labs (NightSchool hands‑on)
1. **Static site** – S3 bucket + CloudFront distribution.
2. **EC2 web server** – launch, SSH, configure security groups.
3. **Lambda + S3 trigger** – process uploaded images.
4. **Terraform VPC module** – create VPC, subnets, IGW, route tables.
5. **CI/CD** – GitHub Actions deploy a SAM/Lambda app.
6. **Cost estimate** – use Cost Explorer to model a simple web app.

---

## 📚 Resources & References
- AWS Documentation: https://docs.aws.amazon.com
- AWS Well‑Architected Framework (PDF)
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/latest
- AWS SAM CLI: https://aws.amazon.com/serverless/sam/
- Qwiklabs AWS labs: https://qwiklab.com
- A Cloud Guru / Udemy AWS Foundations courses

---

*Created by Nova during NightSchool session `e495724c-860e-4802-acb1-dda2d1b292e0` on 2026‑05‑01. Next steps: pick a lab, execute, and record observations in `docs/night-school/aws-basics-cloud-solutions/notes.md`.*