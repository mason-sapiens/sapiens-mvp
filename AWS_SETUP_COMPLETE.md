# ✅ AWS Deployment Files - Complete

I've created everything you need to deploy Sapiens MVP to AWS with PostgreSQL database!

---

## 📦 What's Been Created

### Database Setup
✅ `backend/db/models.py` - PostgreSQL database models
✅ `backend/db/database.py` - Database connection manager
✅ `backend/db/init_db.py` - Database initialization script

### Deployment Files
✅ `Dockerfile` - Docker container configuration
✅ `docker-compose.yml` - Multi-container setup (app + database)
✅ `deploy/aws_setup.sh` - Automated AWS infrastructure setup
✅ `deploy/nginx.conf` - Reverse proxy configuration

### Documentation
✅ `docs/AWS_DEPLOYMENT.md` - Complete deployment guide (detailed)
✅ `DEPLOYMENT_QUICKSTART.md` - Quick start guide (15 minutes)

### Updated
✅ `requirements.txt` - Added PostgreSQL driver (psycopg2-binary)

---

## 🚀 Quick Start (Choose One)

### Option A: Docker Deployment (EASIEST - 15 minutes)

```bash
# 1. Install AWS CLI
brew install awscli  # Mac
# or download from https://aws.amazon.com/cli/

# 2. Configure AWS
aws configure
# Enter your AWS Access Key ID and Secret

# 3. Set up AWS infrastructure (VPC, RDS, Security Groups)
cd /Users/geunwon/Desktop/Sapiens/MVP
./deploy/aws_setup.sh

# This creates everything automatically!
# Saves config to aws_config.txt

# 4. Launch EC2 instance (Ubuntu 22.04, t3.small)
# - Use AWS Console: https://console.aws.amazon.com/ec2
# - Or use AWS CLI (see DEPLOYMENT_QUICKSTART.md)

# 5. SSH into EC2 and deploy
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
exit && ssh -i your-key.pem ubuntu@YOUR_EC2_IP  # Re-login

# Upload code (from your Mac)
# From local machine:
scp -r -i your-key.pem ~/Desktop/Sapiens/MVP ubuntu@YOUR_EC2_IP:~/

# Back on EC2:
cd MVP
echo "OPENAI_API_KEY=your_key_here" > .env
docker-compose up -d
docker-compose exec app python backend/db/init_db.py

# Done! Test it:
curl http://YOUR_EC2_IP/health
```

### Option B: Manual Deployment (30 minutes)

Follow the detailed guide: `docs/AWS_DEPLOYMENT.md`

---

## 📋 Deployment Checklist

### Before You Start
- [ ] AWS Account created
- [ ] AWS CLI installed (`brew install awscli`)
- [ ] AWS configured (`aws configure`)
- [ ] OpenAI API key ready

### Infrastructure (Automated)
- [ ] Run `./deploy/aws_setup.sh`
- [ ] Save `aws_config.txt` file
- [ ] Note RDS endpoint and password

### Application
- [ ] Launch EC2 instance
- [ ] Install Docker
- [ ] Upload code
- [ ] Create `.env` file
- [ ] Run `docker-compose up -d`
- [ ] Initialize database
- [ ] Test endpoints

### Optional (Production)
- [ ] Set up custom domain
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring
- [ ] Configure auto-scaling
- [ ] Set up backups

---

## 💰 Cost Estimate

### Development Setup (~$20/month)
- **EC2** t3.micro: $7/month
- **RDS** db.t3.micro: $13/month
- **Total**: ~$20/month

### Production Setup (~$35/month)
- **EC2** t3.small: $15/month
- **RDS** db.t3.micro: $13/month
- **Data Transfer**: $5/month
- **Total**: ~$35/month

### Cost Saving Tips
- Use Spot Instances (70% cheaper)
- Auto-shutdown during nights
- Use Reserved Instances (72% savings for 1-year)

---

## 🎯 What Happens When You Deploy

### Infrastructure Created by aws_setup.sh:

```
┌─────────────────────────────────────┐
│        Your AWS Account             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │         VPC                  │   │
│  │                              │   │
│  │  ┌──────────────┐            │   │
│  │  │ Public       │            │   │
│  │  │ Subnet       │            │   │
│  │  │  (EC2 App)   │            │   │
│  │  └──────┬───────┘            │   │
│  │         │                    │   │
│  │  ┌──────┴───────┐            │   │
│  │  │ Private      │            │   │
│  │  │ Subnet       │            │   │
│  │  │ (RDS DB)     │            │   │
│  │  └──────────────┘            │   │
│  │                              │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
        ↓
    Internet
```

### What You Get:
1. **VPC** - Isolated network
2. **Public Subnets** - For EC2 instances (accessible from internet)
3. **Private Subnets** - For RDS database (secure, internal only)
4. **Security Groups** - Firewall rules
5. **RDS PostgreSQL** - Managed database with automatic backups
6. **Internet Gateway** - Connect to internet

---

## 🔧 Key Files Explained

### `Dockerfile`
Defines how to build the Docker container:
- Base: Python 3.10
- Installs dependencies
- Copies your code
- Exposes port 8000

### `docker-compose.yml`
Orchestrates multiple containers:
- **db**: PostgreSQL database
- **app**: Your Sapiens application
- **nginx**: Reverse proxy (optional)

Easy commands:
```bash
docker-compose up -d      # Start
docker-compose down       # Stop
docker-compose logs -f    # View logs
docker-compose restart    # Restart
```

### `deploy/aws_setup.sh`
Automated AWS setup:
- Creates VPC and networking
- Creates security groups
- Launches RDS PostgreSQL
- Saves all configuration

### `backend/db/models.py`
Database tables:
- user_states
- projects
- problem_definitions
- solution_designs
- milestones
- conversation_logs
- artifact_reviews
- state_transitions

---

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl http://YOUR_EC2_IP/health
# Expected: {"status":"healthy","version":"0.1.0"}
```

### 2. Create User
```bash
curl -X POST "http://YOUR_EC2_IP/api/users?user_id=test"
```

### 3. Send Message
```bash
curl -X POST http://YOUR_EC2_IP/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Product Manager"}'
```

### 4. Check Database
```bash
# On EC2
docker-compose exec db psql -U sapiens -c "SELECT COUNT(*) FROM user_states;"
```

---

## 📚 Documentation Guide

1. **Quick Start**: `DEPLOYMENT_QUICKSTART.md` (15 min guide)
2. **Detailed Guide**: `docs/AWS_DEPLOYMENT.md` (step-by-step)
3. **Database Setup**: Look at `backend/db/` files
4. **Docker**: `Dockerfile` and `docker-compose.yml`
5. **Architecture**: `docs/ARCHITECTURE.md`

---

## 🆘 Common Issues

### "AWS CLI not found"
```bash
brew install awscli
aws configure
```

### "Permission denied" on aws_setup.sh
```bash
chmod +x deploy/aws_setup.sh
```

### "Database connection failed"
- Check DATABASE_URL in .env
- Check RDS security group allows EC2 connection
- Check RDS is in same VPC

### "Docker command not found"
```bash
curl -fsSL https://get.docker.com | sudo sh
```

---

## 🎓 Next Steps After Deployment

1. **Set Up Domain**
   - Register domain (Namecheap, Route53)
   - Point to EC2 IP
   - Configure SSL with Let's Encrypt

2. **Enable HTTPS**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Set Up Monitoring**
   - CloudWatch logs
   - Health check monitoring
   - Cost alerts

4. **Configure Backups**
   - RDS automatic backups (enabled by default)
   - Application code backups
   - Database snapshots

5. **Scale Up**
   - Add Auto Scaling
   - Add Load Balancer
   - Use CDN (CloudFront)

---

## 💡 Pro Tips

### Use tmux for long-running processes
```bash
# Start session
tmux new -s sapiens

# Deploy
docker-compose up

# Detach: Ctrl+B then D
# Reattach: tmux attach -t sapiens
```

### Monitor resources
```bash
docker stats                    # Container resources
docker-compose logs -f app     # Application logs
htop                           # System resources
```

### Quick updates
```bash
# After code changes
git pull
docker-compose up -d --build
```

---

## 📞 Support

- **Quick Questions**: Check `DEPLOYMENT_QUICKSTART.md`
- **Detailed Steps**: See `docs/AWS_DEPLOYMENT.md`
- **Architecture**: Read `docs/ARCHITECTURE.md`
- **AWS Issues**: AWS Support or Stack Overflow

---

## ✅ Success Criteria

Your deployment is successful when:
- [ ] Health endpoint returns 200 OK
- [ ] Chat endpoint accepts messages
- [ ] Database has tables
- [ ] Logs show no errors
- [ ] Can create user and start conversation

---

## 🎉 You're Ready!

Everything is set up for AWS deployment:
- ✅ Database models created
- ✅ Docker configuration ready
- ✅ AWS automation scripts ready
- ✅ Complete documentation provided
- ✅ All dependencies updated

**Next step**: Follow `DEPLOYMENT_QUICKSTART.md` to deploy!

**Estimated time**: 15-30 minutes

**Cost**: $20-35/month

---

**Questions? Check the documentation files or AWS guides!**

**Ready to deploy? Start with: `./deploy/aws_setup.sh`** 🚀
