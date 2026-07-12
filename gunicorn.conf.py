import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Worker processes: 2 * CPU cores + 1 (recommended for I/O-bound apps)
workers = 2 * multiprocessing.cpu_count() + 1
worker_class = "sync"

# Timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = "flask-app.log"
errorlog = "flask-app.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "flask-app"

# Security
limit_request_line = 4094
limit_request_fields = 100
