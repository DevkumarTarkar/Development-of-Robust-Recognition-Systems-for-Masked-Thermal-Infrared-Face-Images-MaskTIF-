# Gunicorn configuration to prevent timeouts during cold starts on Render's free tier
timeout = 120
workers = 1
