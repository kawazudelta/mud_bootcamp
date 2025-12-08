# Phase 6: Scaling and Reality Check

## The Truth About MUD Scaling
MUDs are stateful, real-time applications. Unlike a standard REST API website, you cannot easily spin up 10 servers and load balance them. The "Room" object your character is in exists in the memory of **one** specific server process.

## Vertical Scaling (The Winner)
For 99.9% of MUDs, **Vertical Scaling** is the correct path.
*   **CPU:** Evennia is built on Twisted (single-threaded async event loop). Single-core performance matters more than core count.
*   **RAM:** This is your bottleneck. The entire world state (cached) lives here. If you grow to 1,000 players, you simply resize your Lightsail instance to 8GB or 16GB RAM. This takes 5 minutes of downtime and requires zero code changes.

## Horizontal Scaling (The Myth)
Do not attempt to "Load Balance" the Telnet or WebSocket ports across multiple Evennia servers. It will not work without a massive architectural rewrite (e.g., sharding the world so "North Zone" is Server A and "South Zone" is Server B, with a complex message bus between them).
*   **Exception:** You *can* offload the web website (wiki, character profiles) to a separate standard Django deployment if the web traffic is crushing the game server.

## CDN for Static Assets (Real Scaling)
Moving images/CSS to S3 + CloudFront is the single best "scaling" move you can make.
1.  **Storage:** Use `django-storages` and `boto3`.
2.  **Settings:**
    ```python
    INSTALLED_APPS += ['storages']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    ```
3.  **Result:** When a player opens the web client, their browser downloads 5MB of assets from Amazon's edge servers, not your single Lightsail instance.

## Monitoring & Observability
You don't need complex tools yet.
*   **HTOP:** Run `htop` on the server. If one core is at 100%, you are CPU bound.
*   **Logs:** Watch `server/logs/server.log`.
*   **Discord Alerts:** Use the webhook approach from Phase 4 to alert you if the server restarts unexpectedly.