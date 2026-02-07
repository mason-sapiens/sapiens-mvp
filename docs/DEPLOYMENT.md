# Deployment Guide

## Local Development

### Prerequisites

- Python 3.10+
- pip
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
cd MVP
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

5. Run the server:
```bash
python run.py
```

6. Visit `http://localhost:8000/docs` for API documentation

## Docker Deployment

### Build Docker Image

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/logs

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "run.py"]
EOF

# Build image
docker build -t sapiens-mvp:latest .
```

### Run with Docker

```bash
docker run -d \
  --name sapiens-api \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_api_key_here \
  -v $(pwd)/data:/app/data \
  sapiens-mvp:latest
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  # Future: Add PostgreSQL, Redis, etc.
```

Run with:
```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment (EC2)

1. Launch EC2 instance (Ubuntu 22.04, t3.medium)

2. SSH into instance and setup:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.10 python3-pip python3-venv

# Clone repository
git clone <your-repo-url>
cd MVP

# Setup application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run with systemd
sudo nano /etc/systemd/system/sapiens.service
```

3. Create systemd service:
```ini
[Unit]
Description=Sapiens MVP API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/MVP
Environment="PATH=/home/ubuntu/MVP/venv/bin"
EnvironmentFile=/home/ubuntu/MVP/.env
ExecStart=/home/ubuntu/MVP/venv/bin/python run.py

[Install]
WantedBy=multi-user.target
```

4. Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sapiens
sudo systemctl start sapiens
sudo systemctl status sapiens
```

5. Setup nginx reverse proxy:
```bash
sudo apt install -y nginx

sudo nano /etc/nginx/sites-available/sapiens
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/sapiens /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### AWS Deployment (ECS/Fargate)

1. Build and push Docker image to ECR

2. Create ECS task definition

3. Create ECS service

4. Configure Application Load Balancer

### Render.com Deployment

1. Connect GitHub repository

2. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`

3. Add environment variables:
   - `ANTHROPIC_API_KEY`

4. Deploy

### Railway Deployment

1. Connect GitHub repository

2. Add environment variables

3. Railway auto-detects Python and deploys

### Heroku Deployment

1. Create `Procfile`:
```
web: python run.py
```

2. Deploy:
```bash
heroku create sapiens-mvp
heroku config:set ANTHROPIC_API_KEY=your_key_here
git push heroku main
```

## Production Considerations

### Database Migration

For production, migrate from JSON files to PostgreSQL:

1. Install PostgreSQL:
```bash
pip install psycopg2-binary sqlalchemy asyncpg
```

2. Update `LoggingModule` to use database

3. Run migrations:
```bash
alembic upgrade head
```

### Caching

Add Redis for session caching:

```bash
pip install redis
```

### Monitoring

Add monitoring with:
- Sentry for error tracking
- Datadog/New Relic for APM
- Prometheus + Grafana for metrics

### Security

1. Add authentication:
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

2. Enable HTTPS with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. Add rate limiting:
```bash
pip install slowapi
```

### Scaling

1. Use gunicorn with multiple workers:
```bash
pip install gunicorn
gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Setup load balancer (AWS ALB, nginx, etc.)

3. Use Redis for shared session state

4. Consider message queue (RabbitMQ, AWS SQS) for async processing

### Backup Strategy

1. Automated database backups
2. S3 storage for artifacts
3. Log retention policy

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t sapiens-mvp .

      - name: Push to ECR
        run: |
          # Push to ECR commands

      - name: Deploy to ECS
        run: |
          # Update ECS service
```

## Environment Variables

### Required
- `ANTHROPIC_API_KEY`: Your Anthropic API key

### Optional
- `OPENAI_API_KEY`: OpenAI API key (for embeddings)
- `ENVIRONMENT`: `development` or `production`
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `CHROMA_PERSIST_DIR`: Vector store directory
- `LOG_STORAGE_DIR`: Logs directory

## Health Checks

Setup health check endpoint monitoring:

```bash
# Simple health check
curl http://localhost:8000/health

# From monitoring service
*/5 * * * * curl -f http://localhost:8000/health || alert
```

## Troubleshooting

### API won't start
- Check `ANTHROPIC_API_KEY` is set
- Check port 8000 is not in use
- Check Python version is 3.10+

### High memory usage
- Reduce `max_tokens` in settings
- Limit conversation history
- Add memory limits to Docker container

### Slow responses
- Check Claude API latency
- Add caching layer
- Optimize database queries

## Support

For deployment support, consult:
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Docker Documentation](https://docs.docker.com/)
