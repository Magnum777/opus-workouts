# AWS & Cloud Solutions Playbook

*Created by Nova during Night‑School (2026‑05‑05)*

---

## Goal
Prepare a concise, actionable reference for AWS basics and common cloud‑solution patterns so you can quickly design, deploy, and operate cloud workloads (especially for SRE / job‑ready roles).

---

## 1️⃣ Core AWS Services (must‑know)
| Service | Category | Typical Use‑Case |
|---------|----------|----------------|
| **EC2** | Compute | Virtual servers –‑‑ pick AMI, instance type, VPC, security‑group. |
| **Lambda** | Serverless Compute | Event‑driven functions, API back‑ends, data pipelines. |
| **S3** | Object Storage | Static assets, backups, data lake, website hosting (static). |
| **RDS** | Managed DB | Relational DB (Postgres, MySQL, Aurora) with automated backups & scaling. |
| **DynamoDB** | NoSQL | Key‑value / document store, fast reads/writes, serverless scaling. |
| **VPC** | Networking | Isolated network, subnets, routing, NAT, security‑groups, NACLs. |
| **IAM** | Identity & Access | Users, groups, roles, policies –‑ least‑privilege. |
| **CloudWatch** | Monitoring | Metrics, logs, alarms, dashboards. |
| **CloudFormation** | IaC (declarative) | Define stacks in YAML/JSON. |
| **Terraform** (3rd‑party) | IaC (declarative) | Multi‑cloud, state‑file, modules. |
| **Elastic Load Balancer (ALB/NLB)** | Load Balancing | Distribute traffic, SSL termination. |
| **SNS / SQS** | Messaging | Pub‑sub, queueing, decoupling services. |
| **CodePipeline / CodeBuild / CodeDeploy** | CI/CD | Automated build‑test‑deploy pipelines. |
| **CloudFront** | CDN | Low‑latency global content delivery. |
| **AWS Organizations** | Multi‑account mgmt | Consolidated billing, Service Control Policies. |

---

## 2️⃣ IAM & Security Best Practices
1. **Root Account** –‑ lock away, enable MFA, never use for day‑to‑day work.
2. **Principle of Least Privilege** –‑ start with AWS‑managed policies, then trim.
3. **Use Roles, Not Long‑Lived Keys** –‑ EC2/ECS/EKS assume roles; developers use IAM Identity Center (SSO).
4. **Enable MFA** on privileged users and roles.
5. **Password Policy** –‑ at least 14 chars, symbols, rotation every 90 days if not using SSO.
6. **IAM Access Analyzer** –‑ continuously validate policies for unintended access.
7. **Conditional Keys** –‑ restrict by IP, VPC, MFA‑present, time of day.
8. **Separate Accounts** –‑ prod vs dev vs test via AWS Organizations; apply SCPs.
9. **Logging** –‑ enable CloudTrail (multi‑region, S3 data events) and Config Rules for compliance.
10. **Encryption** –‑ enable default EBS encryption, S3 bucket encryption (SSE‑S3 or SSE‑KMS), and use KMS for secrets.

---

## 3️⃣ Infrastructure‑as‑Code (IaC)
### CloudFormation (native)
- **Template format**: YAML (preferred) or JSON.
- **StackSets** for multi‑account rollout.
- **Change Sets** to preview before applying.
- **Drift detection** to catch manual changes.

### Terraform (cross‑cloud)
- **State Management**: Store in S3 + DynamoDB lock table.
- **Modules**: Re‑use VPC, IAM, EC2, Lambda modules.
- **Workspaces**: Separate envs (dev, staging, prod).
- **Plan‑Apply workflow**: `terraform plan` → review → `terraform apply`.

---

## 4️⃣ CI/CD Pipelines (AWS‑centric)
1. **Source** –‑ GitHub/CodeCommit repo webhook triggers CodePipeline.
2. **Build** –‑ CodeBuild runs Docker or native runtimes, runs unit tests, lint, security scans (e.g., Trivy).
3. **Deploy** –‑ Choose target:
   - **EC2 / ECS** –‑ CodeDeploy with Blue/Green.
   - **Lambda** –‑ Deploy via SAM/Serverless Framework.
   - **Static Site** –‑ Deploy to S3 + CloudFront (invalidations).
4. **Approval Gate** –‑ Manual approval step for prod.
5. **Notifications** –‑ SNS → Slack/Discord for status.

---

## 5️⃣ Monitoring, Logging & Alerting
| Aspect | Service | Recommended Config |
|--------|---------|--------------------|
| Metrics | CloudWatch | Custom namespace for app, enable detailed monitoring on EC2. |
| Logs | CloudWatch Logs | Centralize from Lambda, ECS, Docker (`awslogs` driver). |
| Tracing | X‑Ray | Enable for Lambda & ECS services to see end‑to‑end request flow. |
| Dashboards | CloudWatch, Grafana (via Prometheus remote‑write) | Build low‑latency dashboards for CPU, latency, error rate. |
| Alerts | CloudWatch Alarms + SNS | < 5% CPU → scale‑out, ≥ 5% error rate → Slack alert. |

---

## 6️⃣ Cost‑Optimization Checklist
- **Free Tier** –‑ use t2.micro/t3.micro, 5 GB S3, 750 h Lambda per month.
- **Right‑size** –‑ Use Compute Optimizer recommendations, auto‑scaling groups.
- **Spot Instances** –‑ For fault‑tolerant workloads, save up to 90%.
- **Savings Plans / Reserved Instances** –‑ Commit 1‑3 yr for steady workloads.
- **S3 Lifecycle** –‑ Move older objects to Infrequent Access or Glacier.
- **Lambda Power Tuning** –‑ Find minimal memory for your function.
- **Tagging** –‑ Tag every resource (project, env, owner) → Cost Explorer reports.
- **Use Cost Anomaly Detection** –‑ Set alerts for spikes.

---

## 7️⃣ Multi‑Cloud / Hybrid Patterns (quick glance)
- **Federated Identity** –‑ Use AWS IAM Identity Center + external IdP (Okta, Azure AD).
- **Data Replication** –‑ S3 Cross‑Region Replication (CRR) for durability; use CloudFront Edge caches.
- **Terraform Workspaces** –‑ Same code base can provision Azure/AWS resources via provider blocks.
- **Service Mesh** –‑ Istio on EKS for multi‑cloud service communication.
- **Backup/DR** –‑ Store snapshots in another cloud (e.g., Azure Blob) via Azure Data Factory.

---

## 8️⃣ Quick “Starter” Blueprint (example)
```yaml
# terraform/main.yaml – minimal VPC + Linux EC2 + SSM access
terraform {
  required_version = ">= 1.5"
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "aws-cloud/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tf-locks"
  }
}

provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "night-school-vpc"
  cidr   = "10.0.0.0/16"
  azs    = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]
  enable_nat_gateway = true
}

resource "aws_instance" "bastion" {
  ami           = "ami-0c02fb55956c7d316" # Amazon Linux 2
  instance_type = "t3.micro"
  subnet_id     = module.vpc.public_subnets[0]
  vpc_security_group_ids = [aws_security_group.bastion.id]
  associate_public_ip_address = true
  iam_instance_profile = aws_iam_instance_profile.bastion.name
  tags = {
    Name = "night-school-bastion"
    Project = "NightSchool"
  }
}

resource "aws_iam_instance_profile" "bastion" {
  name = "night-school-bastion"
  role = aws_iam_role.bastion.name
}

resource "aws_iam_role" "bastion" {
  name = "night-school-bastion"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_security_group" "bastion" {
  name        = "bastion-sg"
  description = "SSH access from my home IP"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.my_home_ip}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```
*Deploy:* `terraform init && terraform apply -auto-approve`

---

## 9️⃣ Reference Links (quick access)
- AWS Well‑Architected Framework – https://aws.amazon.com/architecture/well-architected/
- IAM Best Practices – https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- Terraform AWS Provider Docs – https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Serverless Application Model (SAM) – https://aws.amazon.com/serverless/sam/
- Cost Explorer – https://aws.amazon.com/aws-cost-management/

---

*End of Playbook – keep this file in `docs/night-school/aws-cloud-solutions/` and update as you learn new services or patterns.*
