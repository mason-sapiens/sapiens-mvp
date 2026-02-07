# 🎯 START HERE - Deploy to AWS

## ✅ What You Have Now

✓ OpenAI API key added to `.env`
✓ Complete AWS deployment files
✓ PostgreSQL database setup
✓ Docker configuration
✓ Automated scripts

---

## 🚀 Deploy in 3 Steps (15 minutes)

### Step 1: Install AWS CLI (2 minutes)

```bash
# On your Mac
brew install awscli

# Configure with your AWS credentials
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`

**Get AWS keys here**: https://console.aws.amazon.com/iam/home#/security_credentials

---

### Step 2: Create AWS Infrastructure (10 minutes)

```bash
cd /Users/geunwon/Desktop/Sapiens/MVP

# Run automated setup
./deploy/aws_setup.sh
```

This creates:
- ✅ VPC with networking
- ✅ PostgreSQL database (RDS)
- ✅ Security groups
- ✅ All configuration

**Output**: File called `aws_config.txt` with all details

---

### Step 3: Launch & Deploy (5 minutes)

#### A. Launch EC2 Instance

1. Go to https://console.aws.amazon.com/ec2
2. Click **Launch Instance**
3. Settings:
   - Name: `sapiens-mvp`
   - AMI: **Ubuntu Server 22.04 LTS**
   - Instance type: **t3.small**
   - Key pair: Create new (download .pem file)
   - Network: Use VPC from `aws_config.txt`
   - Subnet: Use PUBLIC subnet from `aws_config.txt`
   - Security group: Use EC2 SG from `aws_config.txt`
   - Enable **Auto-assign public IP**
4. Click **Launch**

#### B. Connect & Deploy

```bash
# Get your EC2 public IP from AWS Console
# SSH into instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
exit

# SSH again (to apply group changes)
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Upload your code (from your Mac in new terminal)
scp -r -i your-key.pem ~/Desktop/Sapiens/MVP ubuntu@YOUR_EC2_IP:~/

# Back on EC2
cd MVP

# Create .env with your keys
nano .env
```

Add to .env:
```bash
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://sapiens:password@rds-endpoint:5432/sapiens
ENVIRONMENT=production
DEFAULT_MODEL=gpt-4o
```
(Get DATABASE_URL from `aws_config.txt`)

```bash
# Deploy!
docker-compose up -d

# Initialize database
docker-compose exec app python backend/db/init_db.py

# Test it
curl http://localhost:8000/health
```

---

## ✅ Test Your Deployment

### From your Mac:

```bash
# Health check
curl http://YOUR_EC2_PUBLIC_IP/health

# Create user
curl -X POST "http://YOUR_EC2_PUBLIC_IP/api/users?user_id=test"

# Send message
curl -X POST http://YOUR_EC2_PUBLIC_IP/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Product Manager"}'
```

**Success!** 🎉 Your API is live!

---

## 💰 What This Costs

**Monthly**: ~$35
- EC2 t3.small: $15
- RDS db.t3.micro: $13
- Data transfer: $5
- Storage: $2

**Free Tier**: First 12 months may be free if you're a new AWS customer

---

## 📊 What You've Built

```
┌────────────────────────────────────────┐
│            Internet                     │
└────────────┬───────────────────────────┘
             │
┌────────────▼───────────────────────────┐
│      AWS (Your Account)                 │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  EC2 Instance (Ubuntu)         │    │
│  │  - Docker                      │    │
│  │  - Your Sapiens App            │    │
│  │  - Nginx (reverse proxy)       │    │
│  └─────────┬──────────────────────┘    │
│            │                            │
│            │ (Internal Network)         │
│            │                            │
│  ┌─────────▼──────────────────────┐    │
│  │  RDS PostgreSQL Database       │    │
│  │  - Auto backups                │    │
│  │  - Encrypted                   │    │
│  │  - Private subnet              │    │
│  └────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔧 Useful Commands

### On EC2

```bash
# View logs
docker-compose logs -f app

# Restart application
docker-compose restart app

# Check status
docker-compose ps

# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Update after code changes
git pull
docker-compose up -d --build
```

### Database

```bash
# Connect to database
docker-compose exec db psql -U sapiens

# List tables
docker-compose exec db psql -U sapiens -c "\dt"

# Backup
docker-compose exec db pg_dump -U sapiens sapiens > backup.sql
```

---

## 🆘 Troubleshooting

### Can't connect to EC2
- Check security group allows port 22 (SSH)
- Check EC2 public IP is correct
- Check .pem file permissions: `chmod 400 your-key.pem`

### Docker won't start
```bash
sudo systemctl status docker
sudo systemctl start docker
```

### Database connection failed
- Check DATABASE_URL in .env matches aws_config.txt
- Check RDS endpoint is reachable
- Check security groups allow connection

### Application errors
```bash
docker-compose logs -f app
# Look for specific errors
```

---

## 📚 Full Documentation

- **Quick Guide**: `DEPLOYMENT_QUICKSTART.md`
- **Detailed Steps**: `docs/AWS_DEPLOYMENT.md`
- **Setup Summary**: `AWS_SETUP_COMPLETE.md`
- **Architecture**: `docs/ARCHITECTURE.md`

---

## 🎯 Success Checklist

- [ ] AWS CLI installed and configured
- [ ] aws_setup.sh completed successfully
- [ ] EC2 instance launched
- [ ] Docker installed on EC2
- [ ] Code uploaded to EC2
- [ ] .env file created with correct values
- [ ] docker-compose up -d successful
- [ ] Database initialized
- [ ] Health check returns 200 OK
- [ ] Can send messages via API

---

## 🚀 What's Next?

After deployment:
1. **Get a domain name** (optional but recommended)
2. **Set up HTTPS** with Let's Encrypt (free)
3. **Configure monitoring** (CloudWatch)
4. **Set up backups** (automated)
5. **Add auto-scaling** (for growth)

---

## 💡 Pro Tips

**Save money:**
- Use Spot Instances (70% cheaper)
- Auto-stop EC2 at night: `aws ec2 stop-instances --instance-ids i-xxx`
- Start Reserved Instances after testing (72% savings)

**Performance:**
- Add Redis for caching
- Use CDN (CloudFront) for static assets
- Enable RDS read replicas for scale

**Security:**
- Change default passwords
- Enable MFA on AWS account
- Use IAM roles instead of access keys
- Regular security updates: `sudo apt update && upgrade`

---

## ✨ You're Ready to Deploy!

1. Install AWS CLI: `brew install awscli`
2. Configure: `aws configure`
3. Run setup: `./deploy/aws_setup.sh`
4. Launch EC2 and deploy with Docker
5. Test and enjoy!

**Estimated time**: 15-20 minutes
**Cost**: ~$35/month
**Result**: Production-ready API on AWS with PostgreSQL! 🎉

---

**Need help?** Check the documentation files or AWS guides.

**Ready?** Start with: `brew install awscli && aws configure`

**Let's deploy! 🚀**
