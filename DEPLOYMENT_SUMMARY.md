# 🎯 Deployment Configuration Summary

## All Customizations Applied ✅

Your deployment script is now fully flexible and configured for your needs!

---

## 1. ✅ Region: us-west-1

**Status**: Configured and auto-detected

**How it works:**
```bash
# Auto-detects from AWS CLI
DETECTED_REGION=$(aws configure get region)
REGION=${AWS_REGION:-$DETECTED_REGION}
# Default: us-west-1
```

**Usage:**
```bash
# Automatic (uses your configured region)
./deploy/aws_setup.sh

# Override
AWS_REGION=us-west-1 ./deploy/aws_setup.sh
```

---

## 2. ✅ PostgreSQL Version: Flexible

**Status**: Auto-detects latest or uses your specification

**How it works:**
```bash
# Auto-detect latest available
POSTGRES_VERSION=$(aws rds describe-db-engine-versions ...)
# Or use specified version
```

**Usage:**
```bash
# Automatic (latest version)
./deploy/aws_setup.sh

# Specify version
POSTGRES_VERSION=15.5 ./deploy/aws_setup.sh
POSTGRES_VERSION=16 ./deploy/aws_setup.sh
```

---

## 3. ✅ Availability Zones: Smart Detection

**Status**: Auto-detects available zones per region

**How it works:**
```bash
# Queries AWS for available AZs
AZ_LIST=$(aws ec2 describe-availability-zones ...)
AZ1=$(echo $AZ_LIST | awk '{print $1}')  # us-west-1a
AZ2=$(echo $AZ_LIST | awk '{print $2}')  # us-west-1c
```

**Result:**
- us-west-1: Uses zones `a` and `c`
- us-east-1: Uses zones `a` and `b`
- Any region: Uses first 2 available zones

---

## Configuration Options

### All Environment Variables

```bash
# Region (default: auto-detect from AWS CLI → us-west-1)
export AWS_REGION=us-west-1

# PostgreSQL version (default: auto-detect latest)
export POSTGRES_VERSION=15.5

# Run deployment
./deploy/aws_setup.sh
```

### One-Line Deployment

```bash
# With all options
AWS_REGION=us-west-1 POSTGRES_VERSION=15.5 ./deploy/aws_setup.sh

# Let it auto-detect everything
./deploy/aws_setup.sh
```

---

## What Gets Created

### In us-west-1 Region:

```
VPC (10.0.0.0/16)
├── Public Subnets
│   ├── 10.0.1.0/24 in us-west-1a
│   └── 10.0.2.0/24 in us-west-1c
├── Private Subnets
│   ├── 10.0.11.0/24 in us-west-1a (RDS)
│   └── 10.0.12.0/24 in us-west-1c (RDS)
├── Internet Gateway
├── Route Tables
└── Security Groups (EC2 + RDS)

RDS PostgreSQL
├── Version: Latest available (or specified)
├── Instance: db.t3.micro
├── Storage: 20 GB gp3
├── Multi-AZ: us-west-1a, us-west-1c
└── Backups: 7 days retention
```

---

## Pre-Flight Checklist

### Before Running Script:

- [ ] AWS CLI installed (`brew install awscli`)
- [ ] AWS configured (`aws configure`)
- [ ] Region set to us-west-1
- [ ] IAM permissions (EC2, RDS, VPC)
- [ ] OpenAI API key in `.env`

### Verify:

```bash
# Check AWS CLI
aws --version

# Check credentials
aws sts get-caller-identity

# Check region
aws configure get region
# Should show: us-west-1

# Check available PostgreSQL versions
aws rds describe-db-engine-versions \
  --engine postgres \
  --query 'DBEngineVersions[-1].EngineVersion' \
  --output text \
  --region us-west-1
```

---

## Running the Deployment

### Standard Deployment (Recommended)

```bash
cd /Users/geunwon/Desktop/Sapiens/MVP

# Run with auto-detection
./deploy/aws_setup.sh
```

**What happens:**
1. Detects region: us-west-1
2. Detects PostgreSQL: Latest (e.g., 16.1)
3. Detects AZs: us-west-1a, us-west-1c
4. Creates all infrastructure
5. Saves config to `aws_config.txt`

**Time**: 10-15 minutes

### Custom Deployment

```bash
# Specify PostgreSQL 15
POSTGRES_VERSION=15 ./deploy/aws_setup.sh

# Different region
AWS_REGION=us-east-1 ./deploy/aws_setup.sh

# Both
POSTGRES_VERSION=15.5 AWS_REGION=us-west-1 ./deploy/aws_setup.sh
```

---

## Expected Output

```
🚀 Sapiens MVP - AWS Setup
================================
✅ AWS CLI configured

Configuration:
  Region: us-west-1
  App Name: sapiens-mvp
  DB Name: sapiens
  PostgreSQL Version: auto-detect latest

ℹ️  Using region: us-west-1
   (To use different region: export AWS_REGION=your-region)
   (To use specific PostgreSQL version: export POSTGRES_VERSION=15.4)

🔍 Detecting availability zones...
  Using AZs: us-west-1a, us-west-1c

🔍 Detecting latest PostgreSQL version...
  Selected PostgreSQL version: 16.1

📡 Creating VPC...
  VPC ID: vpc-xxxxx

🌐 Creating Internet Gateway...
  IGW ID: igw-xxxxx

🔌 Creating Subnets...
  Public Subnet 1: subnet-xxxxx (AZ: us-west-1a)
  Public Subnet 2: subnet-xxxxx (AZ: us-west-1c)
  Private Subnet 1: subnet-xxxxx (AZ: us-west-1a)
  Private Subnet 2: subnet-xxxxx (AZ: us-west-1c)

🛣️  Creating Route Table...
  Route Table ID: rtb-xxxxx

🔒 Creating Security Groups...
  EC2 Security Group: sg-xxxxx
  RDS Security Group: sg-xxxxx

🗄️  Creating DB Subnet Group...

💾 Creating RDS PostgreSQL Instance...
  PostgreSQL version: 16.1
  Instance class: db.t3.micro
  Storage: 20 GB gp3
  This may take 10-15 minutes...

  Waiting for database to be available...

✅ Database created!
  Endpoint: sapiens-mvp-db.xxxxx.us-west-1.rds.amazonaws.com

💾 Saving configuration...
✅ Configuration saved to aws_config.txt

⚠️  IMPORTANT: Save the database password securely!

📋 Next Steps:
1. Launch EC2 instance in public subnet
2. Set DATABASE_URL environment variable
3. Deploy application

Database URL (add to .env):
DATABASE_URL=postgresql://sapiens:password@endpoint:5432/sapiens
```

---

## After Deployment

### 1. Review Configuration

```bash
cat aws_config.txt
```

Should show:
- Region: us-west-1
- VPC ID, Subnet IDs
- Security Group IDs
- RDS Endpoint
- PostgreSQL Version
- Database credentials
- DATABASE_URL

### 2. Launch EC2 Instance

Follow: `START_DEPLOYMENT.md` → Step 3

**Key settings:**
- Region: us-west-1
- VPC: From aws_config.txt
- Subnet: Public subnet from aws_config.txt
- Security Group: EC2 SG from aws_config.txt
- Instance Type: t3.small
- AMI: Ubuntu 22.04

### 3. Deploy Application

Follow: `DEPLOYMENT_QUICKSTART.md`

```bash
# On EC2
docker-compose up -d
docker-compose exec app python backend/db/init_db.py
```

---

## Verification

### Check Resources

```bash
# Check VPC
aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=sapiens-mvp-vpc" \
  --region us-west-1

# Check RDS
aws rds describe-db-instances \
  --db-instance-identifier sapiens-mvp-db \
  --region us-west-1

# Check PostgreSQL version
aws rds describe-db-instances \
  --db-instance-identifier sapiens-mvp-db \
  --query 'DBInstances[0].EngineVersion' \
  --output text \
  --region us-west-1
```

### Test Database Connection

```bash
# From EC2 instance
psql "$DATABASE_URL"

# Run query
SELECT version();
```

---

## Documentation Reference

| Guide | Purpose |
|-------|---------|
| `START_DEPLOYMENT.md` | Complete deployment walkthrough |
| `REGION_SETUP.md` | Region configuration details |
| `POSTGRES_VERSION_GUIDE.md` | PostgreSQL version options |
| `DEPLOYMENT_QUICKSTART.md` | Quick reference |
| `docs/AWS_DEPLOYMENT.md` | Detailed manual deployment |

---

## Cost Estimate

**Monthly costs in us-west-1:**

| Resource | Type | Cost |
|----------|------|------|
| EC2 | t3.small | $15 |
| RDS | db.t3.micro | $13 |
| Storage | 20 GB | $2 |
| Data Transfer | - | $5 |
| **Total** | | **~$35/month** |

---

## Quick Commands

```bash
# Deploy with defaults (recommended)
./deploy/aws_setup.sh

# Deploy with PostgreSQL 15
POSTGRES_VERSION=15 ./deploy/aws_setup.sh

# Check configured region
aws configure get region

# List PostgreSQL versions
aws rds describe-db-engine-versions --engine postgres \
  --query 'DBEngineVersions[].EngineVersion' --output table

# Verify deployment
aws rds describe-db-instances \
  --db-instance-identifier sapiens-mvp-db \
  --query 'DBInstances[0].[EngineVersion,Endpoint.Address]' \
  --output table
```

---

## Summary

### ✅ Fully Configured Features:

1. **Region**: us-west-1 (auto-detected)
2. **PostgreSQL**: Latest version (or specify any version)
3. **Availability Zones**: Smart detection (us-west-1a, us-west-1c)
4. **Networking**: VPC, subnets, security groups
5. **Database**: RDS PostgreSQL with backups
6. **Flexibility**: Override any setting via environment variables

### 🎯 Ready to Deploy:

```bash
cd /Users/geunwon/Desktop/Sapiens/MVP
./deploy/aws_setup.sh
```

**That's it!** The script handles everything automatically. 🚀

---

**All customizations complete. Your deployment is ready!**
