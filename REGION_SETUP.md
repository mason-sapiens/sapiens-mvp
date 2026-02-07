# AWS Region Configuration

## ✅ Updated for us-west-1

The deployment script has been updated to work with your us-west-1 region!

---

## What Changed

### Automatic Region Detection
The script now:
1. **Auto-detects** your AWS CLI configured region
2. **Defaults to us-west-1** if no region is configured
3. **Auto-discovers** available availability zones for your region

### Smart Availability Zone Handling
- **Problem**: us-west-1 has zones `a` and `c` (not `b`!)
- **Solution**: Script now auto-detects available AZs
- **Works with**: us-west-1, us-east-1, or ANY AWS region

---

## How to Use

### Option 1: Use Your Configured Region (Automatic)

```bash
# Script will use your AWS CLI region
./deploy/aws_setup.sh
```

**Detects region from**: `aws configure get region`

### Option 2: Specify Region Manually

```bash
# Deploy to us-west-1
AWS_REGION=us-west-1 ./deploy/aws_setup.sh

# Or deploy to any region
AWS_REGION=us-east-1 ./deploy/aws_setup.sh
AWS_REGION=eu-west-1 ./deploy/aws_setup.sh
```

### Option 3: Set Default Region

```bash
# Configure AWS CLI with us-west-1
aws configure set region us-west-1

# Then run script (will use us-west-1)
./deploy/aws_setup.sh
```

---

## Verify Your Region

### Check Current AWS CLI Region

```bash
aws configure get region
# Should show: us-west-1
```

### Check All Configuration

```bash
aws configure list
# Shows:
#       Name                    Value             Type    Location
#       ----                    -----             ----    --------
#    profile                <not set>             None    None
# access_key     ****************XXXX shared-credentials-file
# secret_key     ****************XXXX shared-credentials-file
#     region                us-west-1      config-file    ~/.aws/config
```

### Test AWS Access in us-west-1

```bash
# List availability zones
aws ec2 describe-availability-zones --region us-west-1

# Should show:
# - us-west-1a
# - us-west-1c
```

---

## Region-Specific Information

### us-west-1 (N. California)
- **Availability Zones**: us-west-1a, us-west-1c
- **RDS**: ✅ PostgreSQL available
- **EC2**: ✅ t3 instances available
- **Cost**: Standard AWS pricing

### us-east-1 (N. Virginia)
- **Availability Zones**: us-east-1a, us-east-1b, us-east-1c, us-east-1d, us-east-1e, us-east-1f
- **Cost**: Often slightly cheaper
- **Most services**: First region to get new features

### Other Regions
The script works with ANY AWS region that has:
- ✅ At least 2 availability zones
- ✅ EC2 support
- ✅ RDS PostgreSQL support

---

## Deployment Steps (Updated)

### 1. Verify Your Region

```bash
# Check configured region
aws configure get region

# If not us-west-1, set it
aws configure set region us-west-1
```

### 2. Run Setup Script

```bash
cd /Users/geunwon/Desktop/Sapiens/MVP
./deploy/aws_setup.sh
```

**Output will show**:
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
...
```

### 3. Script Creates (in us-west-1)

✅ VPC in us-west-1
✅ Subnets in us-west-1a and us-west-1c
✅ RDS PostgreSQL in us-west-1
✅ Security groups
✅ Internet gateway
✅ All networking

---

## Troubleshooting

### "Could not find 2 availability zones"

**Cause**: Region doesn't have enough AZs or API issue

**Solution**:
```bash
# Verify AZs are available
aws ec2 describe-availability-zones --region us-west-1

# Try again
./deploy/aws_setup.sh
```

### "UnauthorizedOperation"

**Cause**: IAM user lacks permissions in us-west-1

**Solution**:
```bash
# Check IAM permissions
aws iam get-user

# Ensure policies are not region-restricted
```

### Wrong Region Being Used

**Solution 1**: Set explicitly
```bash
AWS_REGION=us-west-1 ./deploy/aws_setup.sh
```

**Solution 2**: Update AWS config
```bash
aws configure set region us-west-1
```

---

## Cost Comparison by Region

| Region | EC2 t3.small | RDS db.t3.micro | Total/month |
|--------|--------------|-----------------|-------------|
| us-west-1 | $15.18 | $13.00 | ~$35 |
| us-east-1 | $15.18 | $12.60 | ~$34 |
| us-west-2 | $15.18 | $13.00 | ~$35 |
| eu-west-1 | $15.62 | $14.04 | ~$37 |

**Note**: Prices vary slightly by region. us-east-1 is often cheapest.

---

## Multi-Region Deployment

### Deploy to Multiple Regions

```bash
# Deploy to us-west-1
AWS_REGION=us-west-1 ./deploy/aws_setup.sh

# Deploy to us-east-1
AWS_REGION=us-east-1 ./deploy/aws_setup.sh

# Deploy to eu-west-1
AWS_REGION=eu-west-1 ./deploy/aws_setup.sh
```

Each creates independent infrastructure in that region.

---

## Script Features

### ✅ What the Script Does Automatically

1. **Detects your AWS CLI region**
2. **Queries available AZs** in that region
3. **Creates resources** in correct AZs
4. **Validates** region has required services
5. **Saves configuration** with region info

### 🎯 Region Requirements

Script needs regions with:
- ✅ At least 2 availability zones
- ✅ VPC support
- ✅ EC2 t3 instances
- ✅ RDS PostgreSQL 15
- ✅ Internet Gateway support

**All major AWS regions meet these requirements.**

---

## Quick Reference

```bash
# Check current region
aws configure get region

# Change region
aws configure set region us-west-1

# Deploy (uses configured region)
./deploy/aws_setup.sh

# Deploy to specific region (override)
AWS_REGION=us-west-1 ./deploy/aws_setup.sh

# Verify what will be created
AWS_REGION=us-west-1 aws ec2 describe-availability-zones --region us-west-1
```

---

## Summary

### Before (Old Script)
- ❌ Hardcoded to us-east-1
- ❌ Assumed AZ suffixes a and b
- ❌ Would fail in us-west-1

### After (Updated Script)
- ✅ Auto-detects your region
- ✅ Auto-discovers available AZs
- ✅ Works in us-west-1 (and any region!)
- ✅ Defaults to us-west-1
- ✅ Can override with environment variable

---

## Ready to Deploy!

```bash
# Verify region
aws configure get region

# Should show: us-west-1

# Deploy
cd /Users/geunwon/Desktop/Sapiens/MVP
./deploy/aws_setup.sh
```

**Your infrastructure will be created in us-west-1!** 🚀
