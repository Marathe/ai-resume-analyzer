# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- Docker (optional)

### Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/Marathe/ai-resume-analyzer.git
   cd ai-resume-analyzer
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run locally**
   - Backend: `flask run` (from backend directory)
   - Frontend: `npm start` (from frontend directory)

## Docker Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- PostgreSQL: localhost:5432

### Build individual images

```bash
# Backend
docker build -t resume-analyzer-backend ./backend

# Frontend
docker build -t resume-analyzer-frontend ./frontend
```

## Production Deployment

### Using AWS

1. **EC2 Instance**
   - Launch Ubuntu 20.04 LTS
   - Install Docker and Docker Compose
   - Clone repository
   - Configure RDS for PostgreSQL
   - Update .env with RDS credentials

2. **Environment variables**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/resume_analyzer
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Using Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:standard-0
   ```

2. **Deploy**
   ```bash
   git push heroku main
   ```

### Using AWS Elastic Beanstalk

```bash
eb init -p python-3.10 resume-analyzer
eb create resume-analyzer-env
eb deploy
```

## SSL/HTTPS Configuration

Use Let's Encrypt with Nginx:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

## Monitoring

- Use CloudWatch for AWS monitoring
- Set up error tracking with Sentry
- Monitor with Prometheus + Grafana

## Backup Strategy

- Automated PostgreSQL backups (daily)
- Store uploaded resumes in S3
- Version control for code

## Security Best Practices

- Always use HTTPS
- Keep dependencies updated
- Use strong database passwords
- Implement rate limiting
- Validate all file uploads
- Use environment variables for secrets