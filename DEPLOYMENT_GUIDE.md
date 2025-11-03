# BI Dashboard System - Deployment Guide

## 🚀 Production Deployment

Complete guide for deploying both applications to production.

## Prerequisites

### Infrastructure
- **Database**: MySQL 8.0+ (managed service recommended)
- **Servers**: 
  - ETL API: Linux server with Python 3.11+
  - Dashboard: Node.js hosting (Vercel, DigitalOcean, AWS, etc.)
- **Domain**: Custom domain with SSL certificate
- **Storage**: For uploaded files (S3 or local storage)

### Accounts Needed
- Domain registrar
- SSL certificate provider (or Let's Encrypt)
- Database hosting (AWS RDS, DigitalOcean, etc.)
- Application hosting provider

## Pre-Deployment Checklist

### Security
- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY (ETL)
- [ ] Generate strong NEXTAUTH_SECRET (Dashboard)
- [ ] Review and update CORS settings
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Review database permissions

### Configuration
- [ ] Set production database URL
- [ ] Configure email service (if using)
- [ ] Set up file storage (S3 or equivalent)
- [ ] Configure backup strategy
- [ ] Set up monitoring/logging
- [ ] Configure environment variables

### Testing
- [ ] Run all tests
- [ ] Load testing
- [ ] Security audit
- [ ] Cross-browser testing
- [ ] Mobile responsiveness test

## Database Setup

### 1. Create Production Database

```sql
CREATE DATABASE bi_dashboard 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

CREATE USER 'bi_user'@'%' IDENTIFIED BY 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON bi_dashboard.* TO 'bi_user'@'%';
FLUSH PRIVILEGES;
```

### 2. Initialize Database

```bash
cd etl-app
python init_db.py
```

This creates:
- All 15 database tables
- Default roles and permissions
- Super admin user

### 3. Change Default Credentials

```sql
UPDATE users 
SET password_hash = '$argon2id$v=19$m=65536,t=3,p=4$...' 
WHERE email = 'admin@example.com';
```

Or create new admin via API after deployment.

## ETL Application Deployment

### Option 1: Ubuntu Server with Nginx

#### 1. Prepare Server
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx
```

#### 2. Clone and Setup
```bash
cd /var/www
sudo git clone <your-repo> bi-etl
cd bi-etl/etl-app

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configure Environment
```bash
sudo nano .env
```

```env
DATABASE_URL=mysql+pymysql://bi_user:PASSWORD@your-db-host:3306/bi_dashboard
SECRET_KEY=<generate-with: openssl rand -base64 32>
UPLOAD_DIR=/var/www/bi-etl/uploads
TEMPLATE_DIR=/var/www/bi-etl/templates
```

#### 4. Create Systemd Service
```bash
sudo nano /etc/systemd/system/bi-etl.service
```

```ini
[Unit]
Description=BI ETL API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/bi-etl/etl-app
Environment="PATH=/var/www/bi-etl/etl-app/venv/bin"
ExecStart=/var/www/bi-etl/etl-app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 5. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/bi-etl
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 100M;
}
```

#### 6. Enable and Start
```bash
sudo systemctl enable bi-etl
sudo systemctl start bi-etl
sudo ln -s /etc/nginx/sites-available/bi-etl /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

#### 7. Add SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Option 2: Docker Deployment

#### Dockerfile for ETL
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Build and Run
```bash
docker build -t bi-etl .
docker run -d -p 8000:8000 --env-file .env bi-etl
```

## Dashboard Application Deployment

### Option 1: Vercel (Recommended)

#### 1. Install Vercel CLI
```bash
npm i -g vercel
```

#### 2. Configure Project
```bash
cd dashboard-app
```

Create `vercel.json`:
```json
{
  "env": {
    "DATABASE_URL": "@database-url",
    "NEXTAUTH_URL": "https://yourdomain.com",
    "NEXTAUTH_SECRET": "@nextauth-secret",
    "ETL_API_URL": "https://api.yourdomain.com/api/v1"
  },
  "build": {
    "env": {
      "DATABASE_URL": "@database-url"
    }
  }
}
```

#### 3. Add Environment Secrets
```bash
vercel env add DATABASE_URL
vercel env add NEXTAUTH_SECRET
```

#### 4. Deploy
```bash
vercel --prod
```

### Option 2: Ubuntu Server with PM2

#### 1. Prepare Server
```bash
sudo apt install nodejs npm
sudo npm install -g pm2
```

#### 2. Build Application
```bash
cd dashboard-app
npm install
npx prisma generate
npm run build
```

#### 3. Configure PM2
```bash
pm2 start npm --name "bi-dashboard" -- start
pm2 save
pm2 startup
```

#### 4. Configure Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Option 3: DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings:
   - Build Command: `npm run build`
   - Run Command: `npm start`
3. Add environment variables
4. Deploy

## Environment Variables Reference

### ETL Application (.env)
```env
# Database
DATABASE_URL=mysql+pymysql://user:pass@host:3306/bi_dashboard

# Security
SECRET_KEY=<strong-random-string-32-chars-min>

# Storage
UPLOAD_DIR=./uploads
TEMPLATE_DIR=./templates
MAX_UPLOAD_SIZE=104857600

# File Types
ALLOWED_EXTENSIONS=xlsx,xls,csv
```

### Dashboard Application (.env)
```env
# Database (same as ETL)
DATABASE_URL="mysql://user:pass@host:3306/bi_dashboard"

# NextAuth
NEXTAUTH_URL="https://yourdomain.com"
NEXTAUTH_SECRET=<strong-random-string-32-chars-min>

# API Integration
ETL_API_URL="https://api.yourdomain.com/api/v1"

# App Info
NEXT_PUBLIC_APP_NAME="BI Dashboard"
NEXT_PUBLIC_APP_VERSION="1.0.0"
```

## Post-Deployment Tasks

### 1. Verify Deployment
```bash
# Check ETL API
curl https://api.yourdomain.com/health

# Check Dashboard
curl https://yourdomain.com
```

### 2. Create Initial Admin
If default admin was changed:
```bash
curl -X POST https://api.yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "full_name": "Admin User",
    "password": "secure-password"
  }'
```

Then update user status to 'active' in database.

### 3. Test Integration
1. Login to dashboard
2. Create data model
3. Upload test file
4. View dashboard
5. Export PDF

### 4. Set Up Monitoring

#### Application Monitoring
- Use PM2 monitoring for Node.js
- Use systemd journaling for Python
- Set up application logs

#### Database Monitoring
- Enable slow query log
- Monitor connection pool
- Set up automated backups

#### Uptime Monitoring
- UptimeRobot
- Pingdom
- Custom healthcheck endpoints

### 5. Configure Backups

#### Database Backup Script
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u bi_user -p bi_dashboard > /backups/bi_dashboard_$DATE.sql
```

Add to cron:
```bash
0 2 * * * /path/to/backup.sh
```

#### File Storage Backup
```bash
rsync -avz /var/www/bi-etl/uploads/ /backups/uploads/
```

## Security Hardening

### 1. Firewall Configuration
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL/TLS Configuration
- Force HTTPS
- Use strong cipher suites
- Enable HSTS headers
- Configure security headers

### 3. Rate Limiting
Configure nginx rate limiting:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20;
}
```

### 4. Database Security
- Use strong passwords
- Limit database user permissions
- Enable SSL connections
- Regular security updates

## Performance Optimization

### 1. Database
- Add indexes on frequently queried columns
- Optimize connection pool size
- Enable query cache
- Regular ANALYZE tables

### 2. ETL API
- Enable response compression
- Use CDN for static assets
- Implement caching strategy
- Scale workers based on load

### 3. Dashboard
- Enable Next.js image optimization
- Use CDN for static assets
- Implement caching headers
- Enable compression

## Monitoring and Logging

### Logging Configuration

#### ETL API Logging
```python
# In app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/bi-etl/app.log'),
        logging.StreamHandler()
    ]
)
```

#### Dashboard Logging
Use PM2 logs or systemd journal:
```bash
pm2 logs bi-dashboard
journalctl -u bi-dashboard -f
```

### Metrics to Monitor
- Request response time
- Database query time
- Error rates
- Active users
- Upload success rate
- Dashboard load time

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Check DATABASE_URL format
- Verify database credentials
- Check firewall rules
- Verify database is running

**Authentication Not Working**
- Verify NEXTAUTH_SECRET is set
- Check NEXTAUTH_URL matches domain
- Verify database connection
- Check password hash format

**File Upload Fails**
- Check MAX_UPLOAD_SIZE
- Verify upload directory permissions
- Check disk space
- Review nginx client_max_body_size

**Charts Not Rendering**
- Check browser console for errors
- Verify Plotly.js is loaded
- Check data format
- Test with sample data

## Maintenance

### Regular Tasks
- **Daily**: Check error logs
- **Weekly**: Review audit logs, check disk space
- **Monthly**: Database optimization, security updates
- **Quarterly**: Full backup test, security audit

### Update Procedure
1. Test updates in staging
2. Backup database
3. Put application in maintenance mode
4. Deploy updates
5. Run migrations
6. Verify functionality
7. Remove maintenance mode

## Rollback Procedure

If deployment fails:

1. **Database Rollback**
```bash
mysql -u bi_user -p bi_dashboard < backup_YYYYMMDD.sql
```

2. **Application Rollback**
```bash
# ETL
sudo systemctl stop bi-etl
git checkout <previous-tag>
sudo systemctl start bi-etl

# Dashboard
pm2 stop bi-dashboard
git checkout <previous-tag>
npm install
npm run build
pm2 start bi-dashboard
```

## Support and Resources

- **ETL API Docs**: https://api.yourdomain.com/api/docs
- **Dashboard**: https://yourdomain.com
- **Health Checks**: 
  - ETL: https://api.yourdomain.com/health
  - Dashboard: https://yourdomain.com
- **Monitoring Dashboard**: [Your monitoring URL]

## Conclusion

Following this guide ensures a secure, performant, and maintainable production deployment of the BI Dashboard System.

**Remember**: Always test in staging before deploying to production!
