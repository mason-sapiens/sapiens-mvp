# ✅ Updated for us-west-1

## Changes Made

### 1. **Auto-Region Detection** ✅

**Before:**
```bash
REGION=${AWS_REGION:-us-east-1}  # Hardcoded default
```

**After:**
```bash
# Auto-detect region from AWS CLI config, or use us-west-1 as default
DETECTED_REGION=$(aws configure get region 2>/dev/null || echo "us-west-1")
REGION=${AWS_REGION:-$DETECTED_REGION}
```

**What this means:**
- ✅ Script reads YOUR AWS CLI configuration
- ✅ Uses us-west-1 if no region configured
- ✅ Can override with: `AWS_REGION=your-region ./deploy/aws_setup.sh`

---

### 2. **Smart Availability Zone Detection** ✅

**The Problem:**
- us-west-1 has zones: `us-west-1a`, `us-west-1c` (NO us-west-1b!)
- Old script assumed all regions have `a` and `b`
- Would FAIL in us-west-1

**The Solution:**
```bash
# Get available availability zones for this region
echo "🔍 Detecting availability zones..."
AZ_LIST=$(aws ec2 describe-availability-zones \
    --region $REGION \
    --filters "Name=state,Values=available" \
    --query 'AvailabilityZones[].ZoneName' \
    --output text)

# Get first two AZs
AZ1=$(echo $AZ_LIST | awk '{print $1}')
AZ2=$(echo $AZ_LIST | awk '{print $2}')
```

**What this means:**
- ✅ Queries AWS for ACTUAL available zones
- ✅ Works in us-west-1 (a and c)
- ✅ Works in us-east-1 (a and b)
- ✅ Works in ANY AWS region!

---

### 3. **Updated Subnet Creation** ✅

**Before:**
```bash
--availability-zone ${REGION}a  # Assumed 'a' exists
--availability-zone ${REGION}b  # Assumed 'b' exists
```

**After:**
```bash
--availability-zone $AZ1  # Uses detected zone 1
--availability-zone $AZ2  # Uses detected zone 2
```

**Output:**
```
  Public Subnet 1: subnet-xxx (AZ: us-west-1a)
  Public Subnet 2: subnet-xxx (AZ: us-west-1c)
  Private Subnet 1: subnet-xxx (AZ: us-west-1a)
  Private Subnet 2: subnet-xxx (AZ: us-west-1c)
```

---

## How to Use

### Option 1: Automatic (Recommended)

If your AWS CLI is configured for us-west-1:

```bash
# Check your region
aws configure get region
# Should show: us-west-1

# Run script (automatically uses us-west-1)
./deploy/aws_setup.sh
```

### Option 2: Explicit Override

```bash
# Force use us-west-1
AWS_REGION=us-west-1 ./deploy/aws_setup.sh
```

### Option 3: Set Region First

```bash
# Configure AWS CLI
aws configure set region us-west-1

# Run script
./deploy/aws_setup.sh
```

---

## Verification

### Check AWS CLI Region

```bash
aws configure get region
# Expected: us-west-1
```

### Check Availability Zones

```bash
aws ec2 describe-availability-zones --region us-west-1 \
  --query 'AvailabilityZones[].ZoneName' \
  --output table

# Output:
# ---------------------
# |DescribeAvailabilityZones|
# +-------------------+
# |  us-west-1a       |
# |  us-west-1c       |
# +-------------------+
```

### Test Script Detection

```bash
# Dry run - see what region will be used
DETECTED_REGION=$(aws configure get region 2>/dev/null || echo "us-west-1")
echo "Will use region: $DETECTED_REGION"
```

---

## What Gets Created (in us-west-1)

```
us-west-1 Region
│
├── VPC (10.0.0.0/16)
│   │
│   ├── Public Subnets
│   │   ├── 10.0.1.0/24 in us-west-1a
│   │   └── 10.0.2.0/24 in us-west-1c
│   │
│   └── Private Subnets (for RDS)
│       ├── 10.0.11.0/24 in us-west-1a
│       └── 10.0.12.0/24 in us-west-1c
│
├── RDS PostgreSQL
│   └── Multi-AZ deployment (us-west-1a, us-west-1c)
│
└── Security Groups
    ├── EC2 Security Group
    └── RDS Security Group
```

---

## Benefits of These Changes

### ✅ Region Flexibility
- Works with YOUR configured region
- Not hardcoded to us-east-1
- Can deploy to ANY AWS region

### ✅ Automatic AZ Discovery
- No manual AZ configuration needed
- Handles different AZ naming (a/b vs a/c)
- Always uses available zones

### ✅ Error Prevention
- Won't try to create subnets in non-existent zones
- Validates AZ availability before creation
- Clear error messages if issues occur

### ✅ Future-Proof
- Works with new AWS regions
- Adapts to AWS infrastructure changes
- No hardcoded assumptions

---

## Before Running

### 1. Verify AWS CLI Configuration

```bash
# Check all settings
aws configure list

# Check region specifically
aws configure get region
```

### 2. Test AWS Access

```bash
# Verify credentials work
aws sts get-caller-identity

# Check you can access us-west-1
aws ec2 describe-availability-zones --region us-west-1
```

### 3. Ensure Permissions

Your IAM user needs:
- ✅ AmazonEC2FullAccess
- ✅ AmazonRDSFullAccess
- ✅ AmazonVPCFullAccess

---

## Running the Script

```bash
cd /Users/geunwon/Desktop/Sapiens/MVP

# Run with automatic region detection
./deploy/aws_setup.sh
```

**Expected Output:**
```
🚀 Sapiens MVP - AWS Setup
================================
✅ AWS CLI configured

Configuration:
  Region: us-west-1
  App Name: sapiens-mvp
  DB Name: sapiens

ℹ️  Using region: us-west-1
   (To use different region: export AWS_REGION=your-region)

🔍 Detecting availability zones...
  Using AZs: us-west-1a, us-west-1c

📡 Creating VPC...
  VPC ID: vpc-xxxxx

🌐 Creating Internet Gateway...
  IGW ID: igw-xxxxx

🔌 Creating Subnets...
  Public Subnet 1: subnet-xxxxx (AZ: us-west-1a)
  Public Subnet 2: subnet-xxxxx (AZ: us-west-1c)
  Private Subnet 1: subnet-xxxxx (AZ: us-west-1a)
  Private Subnet 2: subnet-xxxxx (AZ: us-west-1c)

...

✅ Database created!
  Endpoint: sapiens-mvp-db.xxxxx.us-west-1.rds.amazonaws.com
```

---

## Troubleshooting

### "Could not find 2 availability zones"

**Check AZ availability:**
```bash
aws ec2 describe-availability-zones --region us-west-1
```

**Solution:**
Region needs at least 2 AZs. us-west-1 has 2 (a and c), so this should work.

### Script uses wrong region

**Check configured region:**
```bash
aws configure get region
```

**Set to us-west-1:**
```bash
aws configure set region us-west-1
```

**Or force it:**
```bash
AWS_REGION=us-west-1 ./deploy/aws_setup.sh
```

### UnauthorizedOperation errors

**Check IAM permissions:**
```bash
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

**Need these policies:**
- AmazonEC2FullAccess
- AmazonRDSFullAccess
- AmazonVPCFullAccess

---

## Summary

### What Changed:
1. ✅ Region detection: AWS CLI config → us-west-1 default
2. ✅ AZ discovery: Automatic detection of available zones
3. ✅ Subnet creation: Uses detected AZs (not hardcoded)

### What This Means:
- ✅ Script works in us-west-1 (your region)
- ✅ Script works in us-east-1 (or any region)
- ✅ No manual configuration needed
- ✅ Automatic and smart

### Next Steps:
1. Verify: `aws configure get region` shows us-west-1
2. Run: `./deploy/aws_setup.sh`
3. Wait: ~10-15 minutes for infrastructure creation
4. Deploy: Follow START_DEPLOYMENT.md

---

## Files Updated

- ✅ `deploy/aws_setup.sh` - Main deployment script
- ✅ `REGION_SETUP.md` - Region configuration guide (NEW)
- ✅ `UPDATES_FOR_US_WEST_1.md` - This file (NEW)

---

**You're ready to deploy in us-west-1!** 🚀

```bash
./deploy/aws_setup.sh
```
