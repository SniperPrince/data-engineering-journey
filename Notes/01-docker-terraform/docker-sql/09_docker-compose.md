# Module 1.9 — Docker Compose

## Why docker-compose?
Running 2-3 containers manually means typing long `docker run` commands every time,
managing the network creation, setting names, remembering port mappings.
**docker-compose** lets us describe all of that in a single YAML file.

One file → one command → all containers running, networked, ready.

## The docker-compose.yaml File

```yaml
services:
  pgdatabase:
    image: postgres:18
    environment:
      POSTGRES_USER: "root"
      POSTGRES_PASSWORD: "root"
      POSTGRES_DB: "ny_taxi"
    volumes:
      - "ny_taxi_postgres_data:/var/lib/postgresql"
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: "admin@admin.com"
      PGADMIN_DEFAULT_PASSWORD: "root"
    volumes:
      - "pgadmin_data:/var/lib/pgadmin"
    ports:
      - "8085:80"

volumes:
  ny_taxi_postgres_data:
  pgadmin_data:
```

### What each section means

| Section | Purpose |
|---|---|
| `services:` | Top-level — each container = one "service" |
| `image:` | Which Docker image to run |
| `environment:` | Env vars (replaces `-e` flags in `docker run`) |
| `volumes:` (under service) | Mount points (replaces `-v` flag) |
| `ports:` | Port mappings (replaces `-p` flag) |
| `volumes:` (top-level) | Declare named volumes used by services |

### YAML syntax rules to remember
- **Indentation matters** — 2 spaces, consistent
- **`key: value` with a space after the colon** (no space = parser error)
- **Top-level `volumes:` declaration:** named volumes get a trailing colon with no value
- **Quoted strings for safety:** prevents YAML from misinterpreting numbers or special chars

## What Compose Does Automatically

The key magic — these all happen without you specifying them:

1. **Creates a network** — named `<dirname>_default` (if you're in folder `pipeline`,
   network name is `pipeline_default`)
2. **Puts all services on this network**
3. **Sets up DNS** so services reach each other by service name (`pgdatabase`, `pgadmin`)
4. **Manages container names** (auto-named `pipeline-pgdatabase-1` etc.)

This replaces the manual `docker network create` + `--network=...` + `--name=...` from Module 1.7.

## Key Commands

| Command | What it does |
|---|---|
| `docker-compose up` | Start all services in foreground (logs visible, Ctrl+C to stop) |
| `docker-compose up -d` | Start in detached mode (background) |
| `docker-compose down` | Stop and remove all containers (volumes preserved) |
| `docker-compose down -v` | Stop AND remove volumes (data lost!) |
| `docker-compose logs` | View logs of all services |
| `docker-compose ps` | List running services |

Run all of these from the directory where `docker-compose.yaml` lives.

## Running the Ingest Script Against Compose Services

The ingest container is NOT defined in `docker-compose.yaml` — it's a separate
one-off run. So we need to manually attach it to compose's auto-created network.

```bash
# 1. Find the network name
docker network ls
# Look for something like: pipeline_default

# 2. Run the ingest container on that network
docker run -it --rm \
  --network=pipeline_default \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-password=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips \
    --year=2021 \
    --month=1
```

**Why `--pg-host=pgdatabase` still works:** the ingest container joins the same
compose network, so the service name `pgdatabase` resolves correctly.

## Benefits of Docker Compose (Memorize These)

1. **One command to start everything** — `docker-compose up`
2. **Declarative infrastructure** — the YAML *is* the documentation
3. **Version-controllable** — commit `docker-compose.yaml` to Git
4. **Reproducible** — anyone with Docker can spin up the same setup
5. **Self-documenting** — service names + dependencies are visible

## Common Pitfalls

- **Spaces around colons:** `POSTGRES_USER:"root"` (no space) breaks. Always `key: value`.
- **Indentation mix:** tabs vs spaces — use only spaces, 2 consistently.
- **Forgetting volume declarations:** if you mount a named volume, declare it under top-level `volumes:`.
- **Wrong network name:** after `docker-compose up`, the network is `<dir>_default`, not `pg-network`.
- **Forgetting `docker-compose down -v`** when you want a clean DB — without `-v`, volumes persist forever.

## Interview-Critical Points

- **Compose vs Kubernetes:** compose is for single-machine multi-container setups.
  K8s is for multi-machine clusters. Compose is dev/test; K8s is production scale.
- **Compose auto-creates a network** — service names work as hostnames.
- **The compose file replaces multiple `docker run` commands** — declarative > imperative.
- **`docker-compose down` vs `docker-compose down -v`** — know the difference. `-v` is destructive.

## The Bigger Picture

Module 1.9 is the natural conclusion of 1.7 (manual networks). Compose takes the
network + naming pattern and makes it implicit. Real production pipelines use this
pattern OR a more advanced orchestrator like Kubernetes.

For now: you can spin up Postgres + pgAdmin with one command. That's a real DE skill.