# docker-stats-monitor

## What is this?
A simple tool for capturing simple running statistics about running docker containers, and store them in an SQL database.

For now only memory usage and cpu usage are captured.

## Usage

### Using commandline

Simply run `python main.py`

The tool expects these environment variables to be set:
- `DOCKER_BASE_URL`: The url of the docker socket (in order to communicate with the docker daemon and use docker stats)
- `DATABASE_URL`: The url of the database to be used. The tool uses SQLAlchemy, so an [SQLAlchemy database URI syntax](https://docs.sqlalchemy.org/en/20/core/engines.html) is expected.
- `DATA_RETENTION` (Optional): Specifing the data retention in seconds (for how long data should be kept). 
If omitted, the default is 7 days.

### Using Docker Compose

Here's a typical docker compose configuration snippet

```yaml
  docker-stats-monitor:
    build: ../docker-stats-monitor
    restart: unless-stopped
    container_name: "docker-stats-monitor"
    environment:
      - "DATABASE_URL=<fill_in_database_url>"
      - "DOCKER_BASE_URL=unix:///var/run/docker.sock"
      - "PYTHONUNBUFFERED=1"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

