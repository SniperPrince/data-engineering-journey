# Module 1.8 — Dockerizing the Ingestion Script

## Why?
After Module 1.6 we have:
- **Postgres** running in a Docker container ✅
- **Ingestion script** running on the laptop (NOT in a container) ❌

For production, **everything runs in containers** — for reproducibility, deployment,
and CI/CD. So we package the ingest script as a Docker image.

## Step 1: Write the Dockerfile

```dockerfile
FROM python:3.13.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked

# Now copy the script
COPY ingest_data.py ./

ENTRYPOINT ["uv", "run", "python", "ingest_data.py"]
```

### What each instruction does

| Instruction | Purpose |
|---|---|
| `FROM python:3.13.11-slim` | Base image with Python pre-installed |
| `COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/` | Multi-stage build — grab uv binary from official uv image, drop into `/bin/` |
| `WORKDIR /app` | Set working directory inside container |
| `ENV PATH="/app/.venv/bin:$PATH"` | Add venv bin folder to PATH so executables are found |
| `COPY pyproject.toml uv.lock .python-version ./` | Copy dependency files first |
| `RUN uv sync --locked` | Install exact pinned versions from lock file |
| `COPY ingest_data.py ./` | Copy the script LAST (after deps) for layer caching |
| `ENTRYPOINT [...]` | Default command when container runs |

### Why deps copied before script (layer caching)
- Docker caches each instruction's output as a layer
- If `pyproject.toml` doesn't change → cached "install deps" layer is reused (fast)
- If only `ingest_data.py` changes → only the COPY of script is invalidated, deps stay cached
- Wrong order would re-install deps on every code change (slow)

## Step 2: Build the Image	
docker build -t taxi_ingest:v001 .


- `-t taxi_ingest:v001` = name `taxi_ingest`, tag `v001`
- `.` = build context (current directory — where Dockerfile lives)

## Step 3: The Hard Part — Connecting from Container to Container

If you naively try to run with `--pg-host=localhost`, it FAILS. Here's why:

### `localhost` means different things in different places

| Where you run | What `localhost` means |
|---|---|
| On your laptop | Your laptop |
| Inside the ingest container | The ingest container itself |
| Inside the Postgres container | The Postgres container itself |

When the dockerized script says `localhost:5432`, it looks inside its OWN container for
Postgres. There's no Postgres there. **Connection refused.**

### The Fix — Use the Docker Network

From Module 1.7, both containers go on `pg-network`. The script container uses the
Postgres container's name (`pgdatabase`) as the hostname. 

docker run -it 
--network=pg-network 
taxi_ingest:v001 
--pg-user=root 
--pg-password=root 
--pg-host=pgdatabase 
--pg-port=5432 
--pg-db=ny_taxi 
--target-table=yellow_taxi_data 
--year=2021 
--month=1


**Key changes from the laptop-run command:**
- Added `--network=pg-network` so the container can reach `pgdatabase`
- Changed `--pg-host` from `localhost` → `pgdatabase`

Everything else is the same — click flags work identically.

## Common Pitfall

Trying `--pg-host=localhost` from inside a container is the #1 beginner mistake.
The error usually looks like: "Connection refused on localhost:5432".
The fix is always: use the network + container name, not localhost.

## Workflow Summary

1. Postgres container running on `pg-network`, name `pgdatabase`
2. Build the ingest image: `docker build -t taxi_ingest:v001 .`
3. Run the ingest image on the same network with `--pg-host=pgdatabase`
4. Script connects via Docker DNS, ingests data, exits when done

## Interview-Critical Points

- **`localhost` inside a container ≠ `localhost` on the host.** Each container has its own loopback.
- **Container-to-container communication requires a shared user-defined network.**
- **Inside the network, use container names as hostnames** (Docker provides DNS).
- **Multi-stage builds** (`COPY --from=other_image`) avoid installing tools inside your image —
  grab pre-built binaries instead. Smaller, faster images.
- **Layer caching:** copy slowly-changing files first (deps), fast-changing files last (code).

## The Bigger Picture

Module 1.8 is where everything from 1.1-1.7 comes together:
- Dockerfile (1.3)
- uv + lock file (1.2, 1.3)
- Multi-stage builds (1.3)
- Volumes (1.4)
- Postgres in container (1.4)
- Postgres + pandas pipeline (1.5)
- CLI script with click (1.6)
- Docker networks (1.7)
- And now: fully containerized ingestion talking to containerized DB

Once this works, you have a real production-shaped pipeline. Module 1.9 onwards (Docker Compose)
just makes this easier to spin up.