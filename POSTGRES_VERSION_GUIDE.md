# PostgreSQL Version Configuration

## ✅ Now Fully Flexible!

The deployment script now automatically uses the **latest available PostgreSQL version** or allows you to specify any version you want.

---

## How It Works

### Default Behavior (Automatic - Latest Version)

```bash
# Simply run the script
./deploy/aws_setup.sh
```

**What happens:**
1. Script queries AWS for all available PostgreSQL versions
2. Automatically selects the **latest stable version**
3. Creates RDS instance with that version

**Output:**
```
🔍 Detecting latest PostgreSQL version...
  Selected PostgreSQL version: 16.1
💾 Creating RDS PostgreSQL Instance...
  PostgreSQL version: 16.1
  Instance class: db.t3.micro
  Storage: 20 GB gp3
```

---

## Specify a Specific Version

### Option 1: Environment Variable (Temporary)

```bash
# Use PostgreSQL 15.4
POSTGRES_VERSION=15.4 ./deploy/aws_setup.sh

# Use PostgreSQL 16.1
POSTGRES_VERSION=16.1 ./deploy/aws_setup.sh

# Use PostgreSQL 14.9
POSTGRES_VERSION=14.9 ./deploy/aws_setup.sh

# Use major version only (gets latest patch)
POSTGRES_VERSION=15 ./deploy/aws_setup.sh
```

### Option 2: Export (Persistent for Session)

```bash
# Set for current terminal session
export POSTGRES_VERSION=15.4

# Run script (uses 15.4)
./deploy/aws_setup.sh
```

### Option 3: Edit Script (Permanent)

Edit `deploy/aws_setup.sh` line ~35:

```bash
# Change this line:
POSTGRES_VERSION=${POSTGRES_VERSION:-}

# To (example):
POSTGRES_VERSION=${POSTGRES_VERSION:-15.4}
```

---

## Check Available Versions

### List All PostgreSQL Versions

```bash
# List all available versions in your region
aws rds describe-db-engine-versions \
  --engine postgres \
  --query 'DBEngineVersions[?Status==`available`].EngineVersion' \
  --output table \
  --region us-west-1
```

**Output:**
```
-------------------
|DescribeDBEngineVersions|
+-----------------+
|  12.17          |
|  13.13          |
|  14.10          |
|  15.5           |
|  16.1           |
+-----------------+
```

### Get Latest Version

```bash
# Get the latest available version
aws rds describe-db-engine-versions \
  --engine postgres \
  --query 'DBEngineVersions[?Status==`available`] | [-1].EngineVersion' \
  --output text \
  --region us-west-1
```

### Check Version Details

```bash
# Get details about a specific version
aws rds describe-db-engine-versions \
  --engine postgres \
  --engine-version 15.5 \
  --region us-west-1
```

---

## Version Selection Guide

### PostgreSQL 16 (Latest)
- **Recommended for**: New projects
- **Benefits**: Latest features, best performance
- **Compatibility**: Requires PostgreSQL 16+ drivers

### PostgreSQL 15 (Stable)
- **Recommended for**: Production apps
- **Benefits**: Very stable, well-tested
- **Compatibility**: Most tools support 15

### PostgreSQL 14 (Mature)
- **Recommended for**: Conservative deployments
- **Benefits**: Long-term support, proven stability
- **Compatibility**: Universal support

### PostgreSQL 13 or earlier
- **Recommended for**: Legacy compatibility only
- **Note**: Consider upgrading for security

---

## Examples

### Use Latest (Default)

```bash
./deploy/aws_setup.sh
# Uses latest available (e.g., 16.1)
```

### Use Specific Major Version

```bash
# Uses latest 15.x
POSTGRES_VERSION=15 ./deploy/aws_setup.sh

# Uses latest 16.x
POSTGRES_VERSION=16 ./deploy/aws_setup.sh
```

### Use Exact Version

```bash
# Uses exactly 15.4
POSTGRES_VERSION=15.4 ./deploy/aws_setup.sh

# Uses exactly 14.10
POSTGRES_VERSION=14.10 ./deploy/aws_setup.sh
```

### Multiple Deployments

```bash
# Production: Stable version
POSTGRES_VERSION=15.5 AWS_REGION=us-west-1 ./deploy/aws_setup.sh

# Staging: Latest version
POSTGRES_VERSION=16.1 AWS_REGION=us-west-2 ./deploy/aws_setup.sh

# Dev: Auto-detect latest
AWS_REGION=us-east-1 ./deploy/aws_setup.sh
```

---

## Verify PostgreSQL Version After Deployment

### Check RDS Instance Version

```bash
# Get version from RDS
aws rds describe-db-instances \
  --db-instance-identifier sapiens-mvp-db \
  --query 'DBInstances[0].EngineVersion' \
  --output text \
  --region us-west-1
```

### Connect and Check

```bash
# Connect to database
psql "$DATABASE_URL"

# Check version in PostgreSQL
SELECT version();

# Expected output:
# PostgreSQL 15.5 on x86_64-pc-linux-gnu...
```

### Check from Application

```python
# In Python
import psycopg2
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute("SELECT version()")
print(cur.fetchone()[0])
```

---

## Upgrading PostgreSQL Version

### Minor Version Upgrades (Automatic)

AWS automatically applies minor version updates during maintenance windows.

**Example**: 15.4 → 15.5 (automatic)

### Major Version Upgrades (Manual)

```bash
# Upgrade from 15.x to 16.x
aws rds modify-db-instance \
  --db-instance-identifier sapiens-mvp-db \
  --engine-version 16.1 \
  --apply-immediately \
  --region us-west-1

# Or schedule for maintenance window
aws rds modify-db-instance \
  --db-instance-identifier sapiens-mvp-db \
  --engine-version 16.1 \
  --no-apply-immediately \
  --region us-west-1
```

**⚠️ Important:**
- Always backup before major upgrades
- Test in staging first
- Check application compatibility

---

## Compatibility

### Application Requirements

**Python (psycopg2):**
```bash
# Supports PostgreSQL 9.x - 16.x
pip install psycopg2-binary
```

**SQLAlchemy:**
```bash
# Supports PostgreSQL 9.6+
pip install sqlalchemy
```

**Django:**
```python
# Django 4.2+ supports PostgreSQL 12-16
# Django 4.1 supports PostgreSQL 11-15
```

### Our Application

The Sapiens MVP works with:
- ✅ PostgreSQL 12+
- ✅ PostgreSQL 13+
- ✅ PostgreSQL 14+
- ✅ PostgreSQL 15+ (recommended)
- ✅ PostgreSQL 16+ (latest)

**Recommended**: PostgreSQL 15.x for production

---

## Troubleshooting

### "Invalid engine version"

**Cause**: Version not available in your region

**Check available versions:**
```bash
aws rds describe-db-engine-versions \
  --engine postgres \
  --query 'DBEngineVersions[].EngineVersion' \
  --output table \
  --region us-west-1
```

**Solution**: Use a version from the list

### "Could not detect latest version"

**Cause**: API query failed

**Solution**: Specify version manually
```bash
POSTGRES_VERSION=15 ./deploy/aws_setup.sh
```

### Version mismatch with application

**Cause**: Application uses PostgreSQL-specific features

**Solution**: Match versions
```bash
# If app needs PostgreSQL 15
POSTGRES_VERSION=15 ./deploy/aws_setup.sh
```

---

## Best Practices

### ✅ DO:

1. **Use latest stable version** for new projects
   ```bash
   # Let script auto-detect
   ./deploy/aws_setup.sh
   ```

2. **Pin versions for production**
   ```bash
   # Specify exact version
   POSTGRES_VERSION=15.5 ./deploy/aws_setup.sh
   ```

3. **Test major upgrades in staging first**
   ```bash
   # Staging with new version
   POSTGRES_VERSION=16 ./deploy/aws_setup.sh
   # If good, upgrade production
   ```

4. **Document your version choice**
   ```bash
   # In your README or .env.example
   POSTGRES_VERSION=15.5  # Using 15.5 for stability
   ```

### ❌ DON'T:

1. **Don't use EOL versions** (< 12)
2. **Don't upgrade production directly** (test first)
3. **Don't mix major versions** in same app
4. **Don't ignore deprecation warnings**

---

## Version History

### PostgreSQL Releases

| Version | Released | Status | EOL Date |
|---------|----------|--------|----------|
| 16.x | Sep 2023 | Current | ~2028 |
| 15.x | Oct 2022 | Stable | ~2027 |
| 14.x | Sep 2021 | Stable | ~2026 |
| 13.x | Sep 2020 | Supported | Nov 2025 |
| 12.x | Oct 2019 | Supported | Nov 2024 |

**Source**: https://www.postgresql.org/support/versioning/

---

## Summary

### What Changed:

**Before:**
```bash
--engine-version 15.4  # Hardcoded
```

**After:**
```bash
# Auto-detect latest
POSTGRES_VERSION=$(aws rds describe-db-engine-versions ...)

# Or use specified
--engine-version $POSTGRES_VERSION
```

### Benefits:

✅ **Automatic**: Uses latest version by default
✅ **Flexible**: Specify any version you need
✅ **Future-proof**: Always get latest when available
✅ **Compatible**: Works with all PostgreSQL versions

### Usage:

```bash
# Automatic (latest version)
./deploy/aws_setup.sh

# Specific major version
POSTGRES_VERSION=15 ./deploy/aws_setup.sh

# Specific exact version
POSTGRES_VERSION=15.5 ./deploy/aws_setup.sh

# With region
POSTGRES_VERSION=15.5 AWS_REGION=us-west-1 ./deploy/aws_setup.sh
```

---

## Quick Reference

```bash
# List available versions
aws rds describe-db-engine-versions --engine postgres \
  --query 'DBEngineVersions[].EngineVersion' --output table

# Use latest (default)
./deploy/aws_setup.sh

# Use PostgreSQL 15
POSTGRES_VERSION=15 ./deploy/aws_setup.sh

# Use PostgreSQL 16
POSTGRES_VERSION=16 ./deploy/aws_setup.sh

# Use exact version
POSTGRES_VERSION=15.5 ./deploy/aws_setup.sh

# Check deployed version
aws rds describe-db-instances \
  --db-instance-identifier sapiens-mvp-db \
  --query 'DBInstances[0].EngineVersion' --output text
```

---

**Your PostgreSQL version is now fully flexible! 🚀**

The script will automatically use the latest version, or you can specify exactly what you need.
