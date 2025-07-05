# Gunicorn configuration for Tileshop RAG production deployment
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = min(2, multiprocessing.cpu_count())
worker_class = "gthread"
worker_connections = 1000
threads = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help control memory leaks
max_requests = 1000
max_requests_jitter = 50

# Restart workers after they've been alive this long
max_worker_memory = 400  # MB

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "tileshop-rag"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = "/tmp"

# Worker recycling
worker_tmp_dir = "/dev/shm"

# SSL (handled by Fly.io)
# No SSL configuration needed as Fly.io handles HTTPS termination

# Performance tuning
preload_app = True
enable_stdio_inheritance = True

# Graceful restarts
graceful_timeout = 30