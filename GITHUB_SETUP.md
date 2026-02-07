# GitHub Setup and CI/CD Configuration

This guide will help you connect your project to GitHub and set up automatic deployments to AWS.

## Prerequisites

- GitHub account
- AWS credentials
- EC2 instance running at: `3.101.121.64`
- SSH key: `~/.ssh/sapiens-mvp-key.pem`

---

## Step 1: Authenticate with GitHub

Run this command and follow the prompts:

```bash
gh auth login --web
```

You'll get a one-time code. Open https://github.com/login/device and enter the code.

---

## Step 2: Create GitHub Repository

```bash
gh repo create sapiens-mvp --public --source=. --remote=origin
```

Or create manually at: https://github.com/new
- Repository name: `sapiens-mvp`
- Visibility: Public (or Private)
- Don't initialize with README (we already have one)

---

## Step 3: Push Code to GitHub

If you created the repo manually, add it as remote:

```bash
git remote add origin https://github.com/YOUR_USERNAME/sapiens-mvp.git
```

Then push:

```bash
git push -u origin main
```

---

## Step 4: Configure GitHub Secrets

Go to your repository on GitHub:
`https://github.com/YOUR_USERNAME/sapiens-mvp/settings/secrets/actions`

Add these secrets:

### 4.1 AWS_ACCESS_KEY_ID
Your AWS access key ID

### 4.2 AWS_SECRET_ACCESS_KEY
Your AWS secret access key

### 4.3 EC2_HOST
```
3.101.121.64
```

### 4.4 SSH_PRIVATE_KEY
Copy the contents of your SSH key:

```bash
cat ~/.ssh/sapiens-mvp-key.pem
```

Paste the entire output (including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`)

---

## Step 5: Set Up Git on EC2

SSH into your EC2 instance and configure Git:

```bash
ssh -i ~/.ssh/sapiens-mvp-key.pem ubuntu@3.101.121.64

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Navigate to project directory
cd ~/MVP

# Initialize Git repository
git init
git remote add origin https://github.com/YOUR_USERNAME/sapiens-mvp.git
git fetch origin
git reset --hard origin/main
```

---

## Step 6: Test the Deployment

Now, whenever you push to the `main` branch, GitHub Actions will automatically:

1. Checkout your code
2. Connect to EC2 via SSH
3. Pull latest changes
4. Rebuild Docker containers
5. Restart services
6. Run health checks

Test it:

```bash
# Make a small change
echo "# Test" >> README.md
git add README.md
git commit -m "Test automatic deployment"
git push origin main
```

Go to: `https://github.com/YOUR_USERNAME/sapiens-mvp/actions` to watch the deployment.

---

## Manual Deployment

If you need to deploy manually:

```bash
ssh -i ~/.ssh/sapiens-mvp-key.pem ubuntu@3.101.121.64

cd ~/MVP
git pull origin main
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
```

---

## Architecture Overview

```
┌─────────────┐
│   GitHub    │
│ Repository  │
└──────┬──────┘
       │ Push to main
       ▼
┌─────────────────┐
│ GitHub Actions  │
│   CI/CD Runner  │
└──────┬──────────┘
       │ SSH Deploy
       ▼
┌─────────────────────┐
│   EC2 Instance      │
│  3.101.121.64       │
│                     │
│  ┌──────────────┐   │
│  │   Nginx      │   │
│  │   :80        │   │
│  └──────┬───────┘   │
│         │           │
│  ┌──────▼───────┐   │
│  │ FastAPI App  │   │
│  │   :8000      │   │
│  └──────┬───────┘   │
│         │           │
│  ┌──────▼───────┐   │
│  │ PostgreSQL   │   │
│  │   :5432      │   │
│  └──────────────┘   │
└─────────────────────┘
       │
       ▼
┌─────────────────┐
│   RDS Database  │
│   PostgreSQL    │
└─────────────────┘
```

---

## Monitoring Deployments

### View GitHub Actions logs
```
https://github.com/YOUR_USERNAME/sapiens-mvp/actions
```

### Check EC2 logs
```bash
ssh -i ~/.ssh/sapiens-mvp-key.pem ubuntu@3.101.121.64
sudo docker logs sapiens_app --tail 50 -f
```

### Health Check
```bash
curl http://3.101.121.64/health
```

---

## Troubleshooting

### Deployment fails with "Permission denied"
Make sure the SSH_PRIVATE_KEY secret is correctly set with the full key content.

### Services don't start
Check Docker logs:
```bash
ssh -i ~/.ssh/sapiens-mvp-key.pem ubuntu@3.101.121.64
sudo docker logs sapiens_app
sudo docker logs sapiens_db
```

### Port conflicts
Make sure ports 80, 8000, and 5432 are available:
```bash
sudo netstat -tulpn | grep -E ':(80|8000|5432)'
```

---

## Security Notes

- **Never commit** `.env` files or credentials to GitHub
- **Rotate SSH keys** regularly
- **Use GitHub Secrets** for all sensitive data
- **Enable branch protection** for the main branch
- **Review pull requests** before merging

---

## Next Steps

After setup is complete:

1. ✅ Code is on GitHub
2. ✅ Automatic deployments configured
3. ✅ EC2 connected to GitHub
4. 🎯 Make changes and push to see automatic deployment in action!

---

## Useful Commands

### Check deployment status
```bash
gh run list --limit 5
```

### View latest deployment logs
```bash
gh run view --log
```

### Manually trigger deployment
```bash
gh workflow run deploy.yml
```

### Roll back to previous version
```bash
ssh -i ~/.ssh/sapiens-mvp-key.pem ubuntu@3.101.121.64
cd ~/MVP
git log --oneline -5
git reset --hard COMMIT_HASH
sudo docker compose down && sudo docker compose up -d --build
```
