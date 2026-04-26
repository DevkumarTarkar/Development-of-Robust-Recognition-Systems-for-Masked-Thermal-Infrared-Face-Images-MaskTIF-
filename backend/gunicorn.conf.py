# ------------------------------------------
# Gunicorn configuration
# For deployment servers like Render
# ------------------------------------------

# allow longer startup time
timeout = 120

# single worker for low memory plans
workers = 1

# bind port automatically from host
bind = "0.0.0.0:5001"

# keep logs visible
accesslog = "-"
errorlog = "-"
loglevel = "info"