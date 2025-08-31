# CRM Celery Setup Guide

steps to:
    
Install Redis and dependencies.
Run migrations (python manage.py migrate).
Start Celery worker (celery -A crm worker -l info).
Start Celery Beat (celery -A crm beat -l info).
Verify logs in /tmp/crm_report_log.txt.

## Prerequisites
- Redis server installed and running
- Python dependencies installed

## Installation Steps

1. Install Redis:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   OR sudo apt install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server

   # macOS
   brew install redis
   brew services start redis

2. Install Python dependencies:

```bash
pip3 install -r requirements.txt
```
3. Run migrations:
```bash
python3 manage.py migrate
```
4. Start Celery worker:

```bash
celery -A crm worker -l info
```
5. Start Celery Beat (in separate terminal):


```bash
celery -A crm beat -l info
```

6. Monitoring

Check worker status:
```bash
celery -A crm status
```
View scheduled tasks: 
```bash
celery -A crm inspect scheduled
```

7. Verify logs in /tmp/crm_report_log.txt.
```bash
cat /tmp/crm_report_log.txt.
```
OR

```bash
watch /tmp/crm_report_log.txt.
```
 
