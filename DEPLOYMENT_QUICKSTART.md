# 🚀 AWS Deployment Quick Start

Two deployment options: **Docker (Easiest)** or **Manual**

---

## Option 1: Docker Deployment (Recommended - 15 minutes)

### Prerequisites
- AWS Account
- Docker installed locally
- AWS CLI configured

### Step 1: Set Up AWS Infrastructure (10 min)

```bash
cd /Users/geunwon/Desktop/Sapiens/MVP

# Run AWS setup script
./deploy/aws_setup.sh
```

This creates:
- VPC with networking
- RDS PostgreSQL database
- Security groups

Save the output file `aws_config.txt`

### Step 2: Launch EC2 with Docker

**Via AWS Console:**
1. Launch Ubuntu 22.04 t3.small instance
2. Use security group from `aws_config.txt`
3. Enable public IP
4. Download key pair

**SSH into instance:**
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Step 3: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply group changes
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Step 4: Deploy Application

```bash
# Upload your code (from local machine)
scp -r -i your-key.pem ~/Desktop/Sapiens/MVP ubuntu@YOUR_EC2_IP:~/

# On EC2
cd MVP

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_key_here
DB_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://sapiens:your_password@db:5432/sapiens
ENVIRONMENT=production
DEFAULT_MODEL=gpt-4o
EOF

# Build and start
docker-compose up -d

# Initialize database
docker-compose exec app python backend/db/init_db.py

# Check status
docker-compose ps
docker-compose logs -f app
```

### Step 5: Test

```bash
# From local machine
curl http://YOUR_EC2_IP/health

# Should return: {"status":"healthy","version":"0.1.0"}
```

**Done! Your API is live at http://YOUR_EC2_IP**

---

## Option 2: Manual Deployment (30 minutes)

Follow detailed guide: `docs/AWS_DEPLOYMENT.md`

---

## Quick Reference

### Start/Stop Services

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f app

# Update after code changes
docker-compose up -d --build
```

### Database Management

```bash
# Connect to database
docker-compose exec db psql -U sapiens

# Backup
docker-compose exec db pg_dump -U sapiens sapiens > backup.sql

# Restore
docker-compose exec -T db psql -U sapiens sapiens < backup.sql

# View tables
docker-compose exec db psql -U sapiens -c "\dt"
```

### Monitoring

```bash
# Resource usage
docker stats

# App logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db

# Container status
docker-compose ps
```

---

## Cost Optimization

### Development (~ $20/month)
- EC2: t3.micro ($7)
- RDS: db.t3.micro ($15)

### Production (~ $35/month)
- EC2: t3.small ($15)
- RDS: db.t3.micro ($15)
- Data transfer: $5

### Cost Saving Tips

1. **Use Spot Instances** (70% cheaper)
```bash
aws ec2 request-spot-instances \
  --instance-count 1 \
  --type "one-time" \
  --launch-specification file://spot-config.json
```

2. **Auto-shutdown during nights**
```bash
# Stop at 8 PM
0 20 * * * aws ec2 stop-instances --instance-ids i-xxxxx

# Start at 8 AM
0 8 * * * aws ec2 start-instances --instance-ids i-xxxxx
```

3. **Use Reserved Instances** (up to 72% savings for 1-year commitment)

---

## Troubleshooting

### Container won't start

```bash
docker-compose logs app
# Check for:
# - Missing environment variables
# - Database connection issues
# - Port conflicts
```

### Database connection failed

```bash
# Check database is running
docker-compose ps db

# Check connection
docker-compose exec app psql $DATABASE_URL

# Restart database
docker-compose restart db
```

### Out of memory

```bash
# Check memory usage
docker stats

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Security Checklist

- [ ] Change default database password
- [ ] Set up HTTPS with Let's Encrypt
- [ ] Enable firewall (Security Groups)
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`
- [ ] Enable CloudWatch monitoring
- [ ] Set up automated backups
- [ ] Use IAM roles instead of access keys
- [ ] Enable MFA on AWS account

---

## Production Checklist

- [ ] Custom domain configured
- [ ] HTTPS/SSL enabled
- [ ] Database backups automated
- [ ] Monitoring dashboard set up
- [ ] Rate limiting configured
- [ ] Log aggregation set up
- [ ] Health checks enabled
- [ ] Auto-scaling configured (optional)
- [ ] CDN configured (optional)

---

## Scaling

### Vertical (More Power)

```bash
# Stop and resize EC2
aws ec2 stop-instances --instance-ids i-xxxxx
aws ec2 modify-instance-attribute --instance-id i-xxxxx --instance-type t3.medium
aws ec2 start-instances --instance-ids i-xxxxx

# Resize RDS
aws rds modify-db-instance \
  --db-instance-identifier sapiens-mvp-db \
  --db-instance-class db.t3.small \
  --apply-immediately
```

### Horizontal (More Instances)

1. Create AMI from instance
2. Create Launch Template
3. Create Auto Scaling Group
4. Add Application Load Balancer

---

## Support

- **Detailed Guide**: `docs/AWS_DEPLOYMENT.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **API Reference**: `docs/API.md`

---

**Need help? Check the detailed guide or AWS documentation.**

**Your Sapiens MVP is ready for production! 🚀**
