# Docker Deployment Guide for Raspberry Pi

## Quick Start

### 1. Initial Setup

```bash
# Create data directory for persistence
mkdir -p data/uploads

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Access the Application

- **Local:** http://localhost:8000
- **Network:** http://<raspberry-pi-ip>:8000

### 3. Useful Commands

```bash
# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f notetaker

# Check health status
docker-compose ps

# Access container shell
docker-compose exec notetaker /bin/bash

# Backup database
cp data/notes.db data/notes.db.backup
```

## Architecture

- **Single container:** FastAPI + Uvicorn + SQLite
- **Volumes:** Database and uploads persisted in `./data/`
- **Port:** 8000 (configurable in docker-compose.yml)
- **Restart policy:** unless-stopped (survives reboots)

## Production Considerations

### 1. Change Port (Optional)

Edit `docker-compose.yml`:
```yaml
ports:
  - "80:8000"  # External:Internal
```

### 2. Backup Strategy

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp data/notes.db "backups/notes_$DATE.db"
tar -czf "backups/uploads_$DATE.tar.gz" data/uploads/
```

### 3. Resource Limits (for Pi with limited RAM)

Add to `docker-compose.yml` under `notetaker` service:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 256M
    reservations:
      memory: 128M
```

### 4. Add Nginx Reverse Proxy (Optional)

For SSL/domain access, add nginx service to docker-compose.yml:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - notetaker
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs notetaker

# Check if port is already in use
netstat -tulpn | grep 8000
```

### Permission issues
```bash
# Fix ownership (run on Pi host)
sudo chown -R 1000:1000 data/
```

### Database locked errors
```bash
# Stop container, check for stale locks
docker-compose down
rm -f data/notes.db-journal
docker-compose up -d
```

## Upgrading

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Monitoring

```bash
# Resource usage
docker stats notetaker-app

# Health check
curl http://localhost:8000/api/health
```

