Cloudflare DNS
    |
    v
eventmgr.pflaumax.dev → public IP
    |
    v
Nginx (in container, port80/443)
    |
    v
Gunicorn + Django (in container)
    |
    v
PostgreSQL (available in container or not)
