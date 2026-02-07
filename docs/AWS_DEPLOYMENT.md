## AWS Deployment Guide - Complete Step-by-Step

This guide will help you deploy Sapiens MVP to AWS with PostgreSQL database.

## Prerequisites

- AWS Account
- AWS CLI installed and configured
- OpenAI API Key
- Basic knowledge of SSH and Linux

## Architecture Overview

```
Internet
    ↓
[Application Load Balancer]
    ↓
[EC2 Instance (t3.small)]  ←→  [RDS PostgreSQL (db.t3.micro)]
    ↓                              ↑
[Auto Scaling Group]           [Private Subnet]
    ↓
[Public Subnet]
```

## Cost Estimate

- EC2 t3.small: ~$15/month
- RDS db.t3.micro: ~$15/month
- Data transfer: ~$5/month
- **Total: ~$35-40/month**

---

## Step 1: Install AWS CLI

### Mac
```bash
brew install awscli
```

### Linux
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Windows
Download from: https://aws.amazon.com/cli/

---

## Step 2: Configure AWS CLI

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: Get from AWS Console → IAM → Users → Security credentials
- **AWS Secret Access Key**: From same place
- **Default region**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

Test it:
```bash
aws sts get-caller-identity
```

---

## Step 3: Set Up AWS Infrastructure

Run the automated setup script:

```bash
cd /Users/geunwon/Desktop/Sapiens/MVP
./deploy/aws_setup.sh
```

This script will create:
- ✅ VPC with public and private subnets
- ✅ Internet Gateway
- ✅ Security Groups (EC2 and RDS)
- ✅ RDS PostgreSQL database
- ✅ All networking configuration

**Time: 10-15 minutes**

The script will output a file `aws_config.txt` with all your configuration details.

---

## Step 4: Create EC2 Instance

### Option A: Using AWS Console (Easier)

1. Go to https://console.aws.amazon.com/ec2
2. Click **Launch Instance**
3. Configure:
   - **Name**: `sapiens-mvp`
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t3.small
   - **Key Pair**: Create new or select existing
   - **Network**: Select the VPC created by script
   - **Subnet**: Select public subnet from aws_config.txt
   - **Auto-assign Public IP**: Enable
   - **Security Group**: Select the EC2 security group from aws_config.txt
   - **Storage**: 20 GB gp3

4. Click **Launch Instance**

### Option B: Using AWS CLI

```bash
# Get AMI ID for Ubuntu 22.04
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images[0].ImageId' \
  --output text)

# Launch instance (replace values from aws_config.txt)
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.small \
  --key-name YOUR_KEY_PAIR \
  --security-group-ids YOUR_EC2_SG_ID \
  --subnet-id YOUR_PUBLIC_SUBNET_ID \
  --associate-public-ip-address \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=sapiens-mvp}]'
```

---

## Step 5: Connect to EC2 Instance

### Get Public IP

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=sapiens-mvp" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

### SSH into instance

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## Step 6: Set Up EC2 Instance

Run these commands on your EC2 instance:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip git nginx

# Install PostgreSQL client
sudo apt install -y postgresql-client

# Clone your repository (or upload code)
git clone YOUR_REPO_URL
# Or use scp to upload:
# scp -r -i your-key.pem ~/Desktop/Sapiens/MVP ubuntu@EC2_IP:~/

cd sapiens-mvp  # Or MVP directory

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary gunicorn

# Create .env file
nano .env
```

Add to `.env`:
```bash
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/sapiens
ENVIRONMENT=production
LOG_LEVEL=INFO
DEFAULT_MODEL=gpt-4o
```

(Get DATABASE_URL from `aws_config.txt`)

---

## Step 7: Initialize Database

```bash
# Test database connection
python backend/db/init_db.py
```

You should see:
```
✅ Database initialized successfully!
```

---

## Step 8: Set Up Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/sapiens.service
```

Add this content:

```ini
[Unit]
Description=Sapiens MVP API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MVP
Environment="PATH=/home/ubuntu/MVP/venv/bin"
EnvironmentFile=/home/ubuntu/MVP/.env
ExecStart=/home/ubuntu/MVP/venv/bin/gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sapiens
sudo systemctl start sapiens
sudo systemctl status sapiens
```

---

## Step 9: Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/sapiens
```

Add:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/sapiens /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 10: Test Deployment

```bash
# From your local machine
curl http://YOUR_EC2_PUBLIC_IP/health

# Should return:
# {"status":"healthy","version":"0.1.0"}

# Test chat endpoint
curl -X POST http://YOUR_EC2_PUBLIC_IP/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Product Manager"}'
```

---

## Step 11: Set Up HTTPS (Optional but Recommended)

### Get a domain name
1. Register a domain (e.g., Namecheap, Route53)
2. Point it to your EC2 Public IP

### Install Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d yourdomain.com

# Follow prompts
```

Certbot will automatically configure Nginx for HTTPS.

---

## Step 12: Set Up Monitoring

### CloudWatch Logs

Install CloudWatch agent:

```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure it
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Basic Monitoring Script

```bash
# Create monitoring script
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
# Check if service is running
if ! systemctl is-active --quiet sapiens; then
    echo "Sapiens service is down! Restarting..."
    sudo systemctl restart sapiens
fi
EOF

chmod +x ~/monitor.sh

# Add to crontab (run every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/ubuntu/monitor.sh") | crontab -
```

---

## Step 13: Set Up Backups

### Database Backups

RDS automatically backs up daily. To create manual backup:

```bash
aws rds create-db-snapshot \
  --db-instance-identifier sapiens-mvp-db \
  --db-snapshot-identifier sapiens-backup-$(date +%Y%m%d)
```

### Application Backups

```bash
# Backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup application code
tar -czf $BACKUP_DIR/app-$DATE.tar.gz ~/MVP

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/app-$DATE.tar.gz s3://your-backup-bucket/

# Keep only last 7 days
find $BACKUP_DIR -name "app-*.tar.gz" -mtime +7 -delete
EOF

chmod +x ~/backup.sh

# Run daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup.sh") | crontab -
```

---

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u sapiens -n 50 --no-pager

# Check if port is in use
sudo lsof -i :8000

# Restart service
sudo systemctl restart sapiens
```

### Database connection failed

```bash
# Test connection
psql "$DATABASE_URL"

# Check security group allows connections
# Check RDS is in same VPC
```

### High costs

```bash
# Check current costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost"

# Consider:
# - Using t3.micro instead of t3.small
# - Using db.t3.micro with less storage
# - Setting up auto-shutdown during non-business hours
```

---

## Scaling Options

### Vertical Scaling (More Power)

```bash
# Stop instance
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID

# Change instance type
aws ec2 modify-instance-attribute \
  --instance-id YOUR_INSTANCE_ID \
  --instance-type t3.medium

# Start instance
aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID
```

### Horizontal Scaling (More Instances)

1. Create AMI from current instance
2. Create Launch Template
3. Create Auto Scaling Group
4. Create Application Load Balancer
5. Configure Target Group

---

## Cleanup (If Needed)

To delete everything:

```bash
# Terminate EC2 instance
aws ec2 terminate-instances --instance-ids YOUR_INSTANCE_ID

# Delete RDS (creates final snapshot)
aws rds delete-db-instance \
  --db-instance-identifier sapiens-mvp-db \
  --final-db-snapshot-identifier sapiens-final-snapshot

# Delete VPC (after resources are deleted)
# Delete subnets, route tables, internet gateway, then VPC
```

---

## Summary Checklist

- [ ] AWS CLI installed and configured
- [ ] Infrastructure created (VPC, subnets, security groups, RDS)
- [ ] EC2 instance launched
- [ ] Application deployed
- [ ] Database initialized
- [ ] Systemd service configured
- [ ] Nginx configured
- [ ] HTTPS set up (optional)
- [ ] Monitoring configured
- [ ] Backups configured
- [ ] API tested and working

---

## Next Steps

1. Set up custom domain
2. Configure auto-scaling
3. Add Redis for caching
4. Set up CI/CD pipeline
5. Add monitoring dashboards
6. Configure rate limiting
7. Add user authentication

**Your Sapiens MVP is now live on AWS! 🚀**
