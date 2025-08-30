# CRM Celery Setup Guide

steps to:
    
- InstallRedis and dependencies.
- Run migrations (python manage.py migrate).
- Start Celery worker (celery -A crm worker -l info).
- Start Celery Beat (celery -A crm beat -l info).
- Verify logs in /tmp/crm_report_log.txt.

## Prerequisites
- Redis server installed and running
- Python dependencies installed

## Installation Steps

1. Install Redis:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server

   # macOS
   brew install redis
   brew services start redis

Install Python dependencies:

```bash
pip install -r requirements.txt
```
Run migrations:
```bash
python manage.py migrate
```
Start Celery worker:

```bash
celery -A crm worker -l info
```
Start Celery Beat (in separate terminal):


```bash
celery -A crm beat -l info
```
Verify logs in /tmp/crm_report_log.txt

Monitoring
Check worker status:
```bash
celery -A crm status
```
View scheduled tasks: 
```bash
celery -A crm inspect scheduled
```
