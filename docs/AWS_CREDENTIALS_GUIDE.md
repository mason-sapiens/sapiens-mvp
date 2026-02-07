# AWS Credentials Guide

## TL;DR

**Yes, AWS Access Keys are necessary** for AWS CLI. You get them FROM the IAM console.

**IAM Console** = Web interface where you CREATE access keys
**AWS Access Keys** = Credentials you USE in AWS CLI

They work together, not as replacements!

---

## Understanding AWS Authentication

### For AWS Console (Web Browser)
- **Username + Password** (or SSO)
- Click and use web interface

### For AWS CLI (Command Line)
- **Access Key ID + Secret Access Key**
- Run commands from terminal

---

## How to Get AWS Access Keys

### Method 1: Root User Access Keys (Quick Start)

**⚠️ Warning**: Root keys have full access. Use for testing only.

1. **Sign in to AWS Console**
   - Go to https://console.aws.amazon.com/
   - Use your email + password

2. **Navigate to Security Credentials**
   - Click your account name (top right)
   - Select **Security Credentials**

3. **Create Access Key**
   - Scroll to **Access keys** section
   - Click **Create access key**
   - Accept the warning
   - Click **Create access key**

4. **Download Credentials**
   - Click **Download .csv file**
   - Or copy:
     - Access Key ID
     - Secret Access Key

5. **Use in AWS CLI**
   ```bash
   aws configure
   # Paste Access Key ID
   # Paste Secret Access Key
   # Region: us-east-1
   # Format: json
   ```

---

### Method 2: IAM User (Recommended - More Secure)

**Why better?**
- Can limit permissions
- Can be revoked without affecting root account
- Best practice for security
- Auditable

#### Step-by-Step:

**1. Create IAM User**

```bash
# Option A: Via Console
Go to https://console.aws.amazon.com/iam/
→ Users → Create user

# Option B: Via CLI (if you have root access already)
aws iam create-user --user-name sapiens-deployer
```

**2. Attach Permissions**

For Sapiens deployment, you need:
- EC2 (launch instances)
- RDS (create databases)
- VPC (networking)

Via Console:
```
IAM → Users → sapiens-deployer
→ Add permissions → Attach policies directly
→ Select:
  ✓ AmazonEC2FullAccess
  ✓ AmazonRDSFullAccess
  ✓ AmazonVPCFullAccess
```

Via CLI:
```bash
aws iam attach-user-policy \
  --user-name sapiens-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam attach-user-policy \
  --user-name sapiens-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess

aws iam attach-user-policy \
  --user-name sapiens-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonVPCFullAccess
```

**3. Create Access Keys**

Via Console:
```
IAM → Users → sapiens-deployer
→ Security credentials tab
→ Create access key
→ Select "Command Line Interface (CLI)"
→ Create
→ Download CSV or copy keys
```

Via CLI:
```bash
aws iam create-access-key --user-name sapiens-deployer
# Save the output!
```

**4. Configure AWS CLI**

```bash
aws configure --profile sapiens
# Access Key ID: [paste IAM user access key]
# Secret Access Key: [paste secret]
# Region: us-east-1
# Format: json

# Use this profile
export AWS_PROFILE=sapiens

# Or use default profile
aws configure
# [same credentials]
```

---

### Method 3: IAM Roles (Advanced - For EC2)

**Best for**: Applications running ON AWS (like your deployed app)

**How it works:**
- Attach IAM Role to EC2 instance
- No access keys needed
- Credentials auto-rotate
- More secure

**Setup:**

1. **Create Role**
   ```bash
   # Via Console
   IAM → Roles → Create role
   → Trusted entity: AWS service → EC2
   → Add permissions (same as above)
   → Name: sapiens-ec2-role
   ```

2. **Attach to EC2**
   ```bash
   # When launching EC2
   → Advanced → IAM instance profile → sapiens-ec2-role

   # Or attach to existing
   aws ec2 associate-iam-instance-profile \
     --instance-id i-xxxxx \
     --iam-instance-profile Name=sapiens-ec2-role
   ```

3. **No AWS Configure Needed!**
   - AWS CLI on EC2 automatically uses the role
   - No keys to manage

---

## Security Best Practices

### ✅ DO:

1. **Use IAM Users, not root**
   ```bash
   # Create dedicated user for deployment
   aws iam create-user --user-name sapiens-deployer
   ```

2. **Use Least Privilege**
   - Only give permissions needed
   - Don't use `AdministratorAccess` unless necessary

3. **Rotate Keys Regularly**
   ```bash
   # Create new key
   aws iam create-access-key --user-name sapiens-deployer

   # Delete old key
   aws iam delete-access-key \
     --user-name sapiens-deployer \
     --access-key-id OLD_KEY_ID
   ```

4. **Enable MFA**
   ```bash
   # In IAM Console
   Users → Your user → Security credentials → Assign MFA device
   ```

5. **Use IAM Roles for EC2**
   - No keys to steal
   - Auto-rotating credentials

### ❌ DON'T:

1. **Share Access Keys**
   - Each person gets their own IAM user

2. **Commit Keys to Git**
   - Already in `.gitignore`
   - Use environment variables

3. **Use Root Keys Long-Term**
   - Create IAM user instead

4. **Give Full Access**
   - Be specific with permissions

---

## Quick Setup for Sapiens (Choose One)

### Option A: Quick Start (Root Keys)

```bash
# 1. Get root keys from console
https://console.aws.amazon.com/iam → Security Credentials

# 2. Configure
aws configure
# Enter keys

# 3. Deploy
./deploy/aws_setup.sh
```

**Time**: 5 minutes
**Security**: ⚠️ Medium (root access)

---

### Option B: Proper Setup (IAM User)

```bash
# 1. Create IAM user in console
https://console.aws.amazon.com/iam → Users → Create

# 2. Attach policies:
# - AmazonEC2FullAccess
# - AmazonRDSFullAccess
# - AmazonVPCFullAccess

# 3. Create access key for CLI

# 4. Configure
aws configure
# Enter IAM user keys

# 5. Deploy
./deploy/aws_setup.sh
```

**Time**: 10 minutes
**Security**: ✅ Good (limited access)

---

### Option C: Best Practice (IAM User + MFA)

```bash
# 1. Create IAM user (as above)

# 2. Enable MFA
IAM → Users → [user] → Security credentials → Assign MFA

# 3. Create access key

# 4. Configure
aws configure

# 5. For MFA-protected operations
aws sts get-session-token --serial-number arn:... --token-code 123456
# Use temporary credentials

# 6. Deploy
./deploy/aws_setup.sh
```

**Time**: 15 minutes
**Security**: ✅✅ Excellent

---

## Testing Your Credentials

```bash
# Test AWS CLI access
aws sts get-caller-identity

# Should return:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/sapiens-deployer"
# }

# Test EC2 access
aws ec2 describe-regions

# Test RDS access
aws rds describe-db-instances
```

If these work, you're ready to deploy!

---

## Troubleshooting

### "InvalidClientTokenId"
- Wrong Access Key ID
- Check for typos
- Recreate access key

### "SignatureDoesNotMatch"
- Wrong Secret Access Key
- Check for spaces/newlines
- Recreate access key

### "UnauthorizedOperation"
- User lacks permissions
- Attach required policies
- Check IAM permissions

### "No credentials found"
```bash
# Check configuration
aws configure list

# Reconfigure
aws configure
```

---

## Alternative: AWS CloudShell (No Keys Needed!)

**What is it?**
- Browser-based terminal in AWS Console
- Pre-configured with your credentials
- No local AWS CLI setup needed

**How to use:**

1. Sign in to AWS Console
2. Click CloudShell icon (top right, looks like `>_`)
3. Wait for terminal to load
4. Run commands:
   ```bash
   # Already authenticated!
   aws sts get-caller-identity

   # Clone your repo
   git clone YOUR_REPO

   # Run setup
   cd MVP
   ./deploy/aws_setup.sh
   ```

**Pros:**
- No local setup
- No key management
- Always latest AWS CLI

**Cons:**
- Must stay in browser
- Session timeout after inactivity
- Can't run local files directly

---

## For Sapiens Deployment

**Minimum Permissions Needed:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "rds:*",
        "vpc:*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Or use managed policies:**
- `AmazonEC2FullAccess`
- `AmazonRDSFullAccess`
- `AmazonVPCFullAccess`

---

## Summary

| Method | Setup Time | Security | Best For |
|--------|------------|----------|----------|
| Root Access Keys | 5 min | ⚠️ Low | Testing only |
| IAM User | 10 min | ✅ Good | Development |
| IAM User + MFA | 15 min | ✅✅ Best | Production |
| IAM Roles (EC2) | 15 min | ✅✅ Best | Production apps |
| CloudShell | 0 min | ✅ Good | Quick tasks |

**Recommendation for Sapiens:**
1. Start with IAM User (Method 2)
2. Add MFA after initial deployment
3. Use IAM Roles for EC2 instances

---

## Quick Command Reference

```bash
# Configure AWS CLI
aws configure

# Test credentials
aws sts get-caller-identity

# List profiles
aws configure list-profiles

# Use specific profile
export AWS_PROFILE=sapiens
aws s3 ls

# View current config
cat ~/.aws/credentials
cat ~/.aws/config

# Create new access key (via CLI)
aws iam create-access-key --user-name USERNAME

# List access keys
aws iam list-access-keys --user-name USERNAME

# Delete access key
aws iam delete-access-key --user-name USERNAME --access-key-id KEY_ID
```

---

**Bottom Line**:

✅ You NEED Access Keys (from IAM) for AWS CLI
✅ IAM Console is WHERE you CREATE them
✅ They work together, not as alternatives

**Start here**: Create IAM user → Get access keys → `aws configure` → Deploy!
