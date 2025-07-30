# DCPS VPS Deployment Guide

This guide provides step-by-step instructions for deploying the DCPS (Dental Caries Population Studies) web application to your VPS at `dcps.xeradb.com`.

## Prerequisites

- VPS with Ubuntu 20.04+ or similar Linux distribution
- Domain name configured: `dcps.xeradb.com`
- PostgreSQL database: `dcps_production`
- Database user: `dcps_user`
- Project directory: `/var/www/html/dcps`

## System Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Install Node.js for asset management (optional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## Database Setup

```bash
# Switch to postgres user and create database
sudo -u postgres psql

-- In PostgreSQL shell:
CREATE DATABASE dcps_production;
CREATE USER dcps_user WITH PASSWORD 'Choxos10203040';
GRANT ALL PRIVILEGES ON DATABASE dcps_production TO dcps_user;
ALTER USER dcps_user CREATEDB; -- For running migrations
\q
```


## Application Deployment

### 1. Clone and Setup Project

```bash
# Navigate to web directory
cd /var/www/

# Clone the repository (replace with your actual repo URL)
sudo git clone https://github.com/choxos/DCPS.git .
sudo chown -R $USER:$USER /var/www/dcps

# Navigate to project directory
cd /var/www/dcps

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Create environment file
cat > .env << EOF
DEBUG=False
SECRET_KEY='+35dhr3zu$(^dos06f3-&s19nc_m766lj&=6ggyb-@i(ljsz#)'
DB_NAME=dcps_production
DB_USER=dcps_user
DB_PASSWORD=Choxos10203040
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=dcps.xeradb.com,www.dcps.xeradb.com
EOF

# Secure the environment file
chmod 600 .env
```

### 3. Django Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test the application
python manage.py runserver 0.0.0.0:8000
```

## Gunicorn Configuration

### 1. Create Gunicorn Configuration

```bash
# Create gunicorn configuration file
cat > /var/www/html/dcps/gunicorn.conf.py << EOF
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "www-data"
group = "www-data"
tmp_upload_dir = None
logfile = "/var/www/html/dcps/logs/gunicorn.log"
loglevel = "info"
access_logfile = "/var/www/html/dcps/logs/access.log"
error_logfile = "/var/www/html/dcps/logs/error.log"
EOF

# Create logs directory
mkdir -p /var/www/html/dcps/logs
sudo chown -R www-data:www-data /var/www/html/dcps/logs
```

### 2. Create Systemd Service

```bash
# Create systemd service file
sudo cat > /etc/systemd/system/dcps.service << EOF
[Unit]
Description=DCPS Dental Caries Population Studies
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/html/dcps
Environment="PATH=/var/www/html/dcps/venv/bin"
EnvironmentFile=/var/www/html/dcps/.env
ExecStart=/var/www/html/dcps/venv/bin/gunicorn --config /var/www/html/dcps/gunicorn.conf.py dcps.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable dcps
sudo systemctl start dcps
sudo systemctl status dcps
```

## Nginx Configuration

### 1. Create Nginx Site Configuration

```bash
# Create nginx configuration
sudo cat > /etc/nginx/sites-available/dcps << EOF
server {
    listen 80;
    server_name dcps.xeradb.com www.dcps.xeradb.com;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Serve static files directly
    location /static/ {
        alias /var/www/html/dcps/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Serve media files directly
    location /media/ {
        alias /var/www/html/dcps/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Handle favicon
    location = /favicon.ico {
        alias /var/www/html/dcps/staticfiles/images/favicon.ico;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Gzip compression
    gzip on;
    gzip_comp_level 6;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        application/json
        application/javascript
        text/xml
        application/xml
        application/xml+rss
        text/javascript;
    gzip_vary on;

    # Client max body size (for file uploads)
    client_max_body_size 10M;

    # Rate limiting (adjust as needed)
    limit_req zone=dcps_limit burst=20 nodelay;
}
EOF

# Add rate limiting to nginx main config
sudo sed -i '/http {/a\\tlimit_req_zone $binary_remote_addr zone=dcps_limit:10m rate=10r/s;' /etc/nginx/nginx.conf

# Enable the site
sudo ln -sf /etc/nginx/sites-available/dcps /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 2. SSL Certificate Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d dcps.xeradb.com -d www.dcps.xeradb.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

## File Permissions and Security

```bash
# Set proper ownership and permissions
sudo chown -R www-data:www-data /var/www/html/dcps
sudo chmod -R 755 /var/www/html/dcps

# Secure sensitive files
sudo chmod 600 /var/www/html/dcps/.env
sudo chmod 644 /var/www/html/dcps/manage.py
sudo chmod +x /var/www/html/dcps/manage.py

# Create media directory with proper permissions
sudo mkdir -p /var/www/html/dcps/media
sudo chown -R www-data:www-data /var/www/html/dcps/media
sudo chmod -R 755 /var/www/html/dcps/media
```

## Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status verbose
```

## Backup and Monitoring

### 1. Database Backup Script

```bash
# Create backup script
sudo cat > /usr/local/bin/dcps-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/dcps"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="dcps_production"
DB_USER="dcps_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
PGPASSWORD="your_db_password" pg_dump -h localhost -U $DB_USER $DB_NAME > $BACKUP_DIR/dcps_db_$DATE.sql

# Compress old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete

# Media files backup (if needed)
tar -czf $BACKUP_DIR/dcps_media_$DATE.tar.gz -C /var/www/html/dcps media/

echo "Backup completed: dcps_db_$DATE.sql"
EOF

# Make executable
sudo chmod +x /usr/local/bin/dcps-backup

# Add to crontab for daily backups
echo "0 2 * * * /usr/local/bin/dcps-backup" | sudo crontab -
```

### 2. Log Rotation

```bash
# Create logrotate configuration
sudo cat > /etc/logrotate.d/dcps << EOF
/var/www/html/dcps/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload dcps
    endscript
}
EOF
```

## Maintenance Commands

```bash
# Check application status
sudo systemctl status dcps
sudo systemctl status nginx

# View application logs
sudo journalctl -u dcps -f
tail -f /var/www/html/dcps/logs/gunicorn.log

# Restart services
sudo systemctl restart dcps
sudo systemctl restart nginx

# Update application
cd /var/www/html/dcps
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart dcps

# Django management commands
cd /var/www/html/dcps
source venv/bin/activate
python manage.py shell
python manage.py dbshell
```

## Environment Variables

Create a production settings override if needed:

```python
# dcps/settings_production.py
from .settings import *
import os

DEBUG = False

ALLOWED_HOSTS = ['dcps.xeradb.com', 'www.dcps.xeradb.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dcps_production',
        'USER': 'dcps_user',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files
STATIC_ROOT = '/var/www/html/dcps/staticfiles'
MEDIA_ROOT = '/var/www/html/dcps/media'

# Email configuration (if needed)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure www-data has proper ownership
2. **Database Connection**: Check database credentials and network connectivity
3. **Static Files Not Loading**: Verify nginx static file configuration and run collectstatic
4. **502 Bad Gateway**: Check if Gunicorn is running and binding to correct port

### Useful Debugging Commands

```bash
# Check if application is binding to port
sudo netstat -tlnp | grep :8000

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check application logs
sudo journalctl -u dcps --since "1 hour ago"

# Test database connection
sudo -u postgres psql dcps_production -c "SELECT version();"
```

## Security Considerations

1. Regularly update system packages
2. Use strong passwords for database and Django secret key
3. Keep SSL certificates updated
4. Monitor access logs for suspicious activity
5. Regular security audits and vulnerability assessments
6. Implement proper backup and disaster recovery procedures

## Post-Deployment Checklist

- [ ] Application loads correctly at https://dcps.xeradb.com
- [ ] Admin interface accessible at /admin/
- [ ] Static files (CSS, JS, images) loading properly
- [ ] Database migrations completed
- [ ] SSL certificate installed and working
- [ ] Backup scripts configured and tested
- [ ] Log rotation configured
- [ ] Firewall properly configured
- [ ] Monitoring and alerting set up (optional)

Your DCPS application should now be successfully deployed and accessible at https://dcps.xeradb.com! 