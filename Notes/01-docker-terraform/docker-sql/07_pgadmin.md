# Module 1.7 — pgAdmin + Docker Networks

## Why pgAdmin?
pgcli is a CLI tool. pgAdmin is a **web-based GUI** to interact with Postgres:
- Browse tables visually
- Run SQL queries with syntax highlighting
- View schemas, indexes, constraints
- Manage users and permissions

In production, DBAs use pgAdmin. We use it here to inspect ingested data.

## Step 1: Run pgAdmin in a Container
docker run -it --rm 
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" 
-e PGADMIN_DEFAULT_PASSWORD="root" 
-v pgadmin_data:/var/lib/pgadmin 
-p 8085:80 
dpage/pgadmin4

### Flags explained

| Flag | Purpose |
|---|---|
| `-e PGADMIN_DEFAULT_EMAIL` | Login email for pgAdmin web UI |
| `-e PGADMIN_DEFAULT_PASSWORD` | Login password |
| `-v pgadmin_data:/var/lib/pgadmin` | Named volume — saves server connections + preferences across restarts |
| `-p 8085:80` | Map laptop's port 8085 → container's port 80 (pgAdmin's default web port) |
| `dpage/pgadmin4` | The official pgAdmin image |

Now open `http://localhost:8085` in browser → log in with the email/password.

## Step 2: The Networking Problem

If you log into pgAdmin now and try to register the Postgres server with `host=localhost`,
it WON'T work. Why?

- **`localhost` inside the pgAdmin container** = pgAdmin container itself
- Postgres is in a **different** container
- They're isolated by default → can't see each other

**Mental model:** Each container is an isolated apartment. Inside Apartment B, `localhost`
means "this apartment." If the kitchen (Postgres) is in Apartment A, B can't find it
unless they're on a shared hallway (network).

## Step 3: Create a Docker Network

A Docker network is a virtual shared "hallway" containers can be placed on.
Once both are on the same network, Docker provides internal DNS so they can find each
other by container name.

docker network create pg-network
### Useful network commands
| Command | Purpose |
|---|---|
| `docker network ls` | List all networks |
| `docker network rm <name>` | Remove a network |
| `docker network inspect <name>` | See containers on a network |

## Step 4: Re-run Both Containers on the Same Network

Stop the existing containers first. Then re-run with `--network=pg-network` AND a `--name`.

### Postgres on the network:
docker run -it 
-e POSTGRES_USER="root" 
-e POSTGRES_PASSWORD="root" 
-e POSTGRES_DB="ny_taxi" 
-v ny_taxi_postgres_data:/var/lib/postgresql 
-p 5432:5432 
--network=pg-network 
--name pgdatabase 
postgres:18

### pgAdmin on the same network (in another terminal):
docker run -it 
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" 
-e PGADMIN_DEFAULT_PASSWORD="root" 
-v pgadmin_data:/var/lib/pgadmin 
-p 8085:80 
--network=pg-network 
--name pgadmin 
dpage/pgadmin4


### Why `--name` matters
Without `--name`, Docker auto-generates a random name like `awesome_einstein`. With `--name`,
we set a stable hostname. Other containers on the same network can now reach this one by
that name. We chose `pgdatabase` and `pgadmin` because they're descriptive.

## Step 5: Register the Postgres Server in pgAdmin

Open `localhost:8085` in browser → log in:

1. Right-click **Servers** → **Register** → **Server**
2. **General tab:** Name = anything (e.g., "Local Docker Postgres")
3. **Connection tab:**
   - Host: `pgdatabase` ← the container *name*, NOT `localhost`
   - Port: `5432`
   - Username: `root`
   - Password: `root`
4. Save → you should see `ny_taxi` database with your `yellow_taxi_data` table

## The Key Insight (Memorize This)

> A container's `localhost` = that container itself.
> To reach another container, both must be on the same Docker network,
> and you use the **other container's name** as the hostname.

In our setup:
- From pgAdmin → reach Postgres at `pgdatabase:5432` ✅
- From Postgres → reach pgAdmin at `pgadmin:80` (if needed)
- From your laptop → either still works as `localhost:5432` and `localhost:8085` because we mapped ports

## Interview-Critical Points

- **Docker provides internal DNS** for containers on the same user-defined network.
- The DNS uses **container names** set via `--name`.
- **Default bridge network has NO automatic DNS** — that's why we create a custom network with `docker network create`.
- Port mappings (`-p`) only affect host ↔ container traffic, not container ↔ container.
- Inside a network, containers talk over their internal IPs/names without going through host port mappings.

## The Google.com Analogy (My Own)

When you type `google.com` in a browser, DNS translates it to an IP address.
Docker networks work the same way: `pgdatabase` is a "hostname" that Docker's
internal DNS resolves to the Postgres container's actual address on the network.

The container name = the domain name. The container itself = the server.
Without the network, no DNS, no resolution, no connection.