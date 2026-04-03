# AWS-Automation-Scripts# ☁️ AWS Automation Scripts — Python & Bash

> Production-ready automation scripts targeting AWS EC2, S3, and IAM.
> Built with Python (boto3) and Bash — applying infrastructure-as-code 
> principles for repeatable, auditable cloud environments.

---

## 📋 Overview

This repository contains automation scripts developed for real-world 
AWS infrastructure management tasks. Each script is documented, 
error-handled, and follows least-privilege IAM principles.

---

## 📁 Repository Structure

aws-automation-scripts/
├── ec2/
│   ├── ec2_manager.py        # Start, stop, list EC2 instances
│   └── ec2_snapshot.py       # Automated EBS snapshot management
├── s3/
│   ├── s3_backup.py          # File backup to S3 with versioning
│   └── s3_cleanup.py         # Automated old file cleanup
├── iam/
│   └── iam_audit.py          # IAM user and policy audit
├── bash/
│   └── aws_health_check.sh   # Quick AWS resource health check
└── README.md

---

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat&logo=amazon-aws&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=flat&logo=gnu-bash&logoColor=white)

| Tool | Purpose |
|---|---|
| Python 3.x | Core scripting language |
| boto3 | AWS SDK for Python |
| AWS CLI | Command-line AWS management |
| Bash | Shell automation & health checks |

---

## 🛡️ Security Principles Applied

- **Least-privilege IAM** — each script uses scoped permissions only
- **No hardcoded credentials** — AWS credentials via environment 
  variables or IAM roles only
- **`.gitignore`** — credentials and sensitive files excluded
- **Error handling** — all scripts include try/except blocks
- **Audit logging** — actions logged with timestamps

---

## 🚀 Scripts

### EC2 Management (`ec2/ec2_manager.py`)
- List all EC2 instances with status
- Start / stop instances by tag or ID
- Filter by region and state

### EC2 Snapshots (`ec2/ec2_snapshot.py`)
- Automated EBS volume snapshots
- Retention policy — delete snapshots older than N days
- Tag-based targeting

### S3 Backup (`s3/s3_backup.py`)
- Upload local files/directories to S3
- Versioning support
- Progress reporting

### S3 Cleanup (`s3/s3_cleanup.py`)
- Delete objects older than defined retention period
- Dry-run mode available before actual deletion
- Bucket and prefix targeting

### IAM Audit (`iam/iam_audit.py`)
- List all IAM users and last activity
- Identify users with no MFA enabled
- List attached policies per user

### AWS Health Check (`bash/aws_health_check.sh`)
- Quick status check across EC2, S3, IAM
- Outputs formatted summary report

---

## ⚙️ Setup
```bash
# Clone the repo
git clone https://github.com/MustafaTuzsuz/aws-automation-scripts

# Install dependencies
pip install boto3

# Configure AWS credentials (never hardcode)
aws configure
```

---

## 👤 Author

**Mustafa Talha Tuzsuz**  
Junior Cybersecurity & Cloud Engineer — Dublin, Ireland  
[LinkedIn](https://linkedin.com/in/tuzsuz) • [Email](mailto:tuzsuz@pm.me)
