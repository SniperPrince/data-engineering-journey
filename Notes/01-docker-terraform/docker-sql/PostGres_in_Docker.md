### What each flag does

| Flag | Purpose |
|---|---|
| `-e POSTGRES_USER=root` | Sets the DB username (env variable read by the postgres image) |
| `-e POSTGRES_PASSWORD=root` | Sets the DB password |
| `-e POSTGRES_DB=ny_taxi` | Creates a database named `ny_taxi` on startup |
| `-v ny_taxi_postgres_data:/var/lib/postgresql` | Mounts a named volume so DB data persists |
| `-p 5432:5432` | Maps host port 5432 → container port 5432. Connecting to localhost:5432 reaches the container's Postgres |
| `postgres:18` | The image to run (Postgres v18) |

### Why we need the volume
Containers are stateless — when the container stops, all data inside dies. Without a volume,
every restart of the Postgres container would give you a fresh, empty database.
The volume persists `/var/lib/postgresql` (where Postgres stores its data files) outside the container.

## Bind Mount vs Named Volume

Both solve the same problem: making container data survive container removal.
The difference is WHO manages the host-side storage.

### Named Volume — `-v name:/container/path`
- Docker manages WHERE on host machine it's stored
- I don't pick the location, don't see the files easily
- Cleaner, faster on Mac/Windows
- Example: `-v ny_taxi_postgres_data:/var/lib/postgresql`
- Left side = just a **NAME** (no slashes, no path)

### Bind Mount — `-v /host/path:/container/path`
- I explicitly pick the host folder
- I can browse, edit, backup the files directly via my OS
- Slower on Mac/Windows (cross-filesystem overhead)
- Example: `-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql`
- Left side = a real **PATH** on my machine

### Visual rule (the shortcut)
- **No slash on left** → named volume
- **Has slash / pwd / dot on left** → bind mount

### When to use which
- **Named volume:** Production, default choice, cleaner
- **Bind mount:** Development, when I want to inspect database files directly

## Installing pgcli

`pgcli` is the command-line client for Postgres. We install it via uv: 
uv add --dev pgcli

### Why `--dev`?
The `--dev` flag marks pgcli as a **development dependency** — only needed for local
exploration, not for running the pipeline in production. It gets added to the
`[dependency-groups]` section of `pyproject.toml` instead of the main `dependencies` section.

Effect: when someone runs `uv sync --locked` in production, pgcli won't be installed.
Keeps the production environment lean.

## Connecting to Postgres
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi

| Flag | Meaning |
|---|---|
| `uv run` | Executes the command inside the venv (so it finds pgcli) |
| `-h localhost` | Host — since Postgres runs locally via Docker port mapping |
| `-p 5432` | Port — must match the host side of `-p 5432:5432` |
| `-u root` | Username — same as POSTGRES_USER |
| `-d ny_taxi` | Database name — same as POSTGRES_DB |

**Password is not in the command** — pgcli prompts after running. This is a security
practice (avoids passwords ending up in shell history or logs). Enter `root` when prompted.

## Basic SQL Commands

Once connected via pgcli:

```sql
-- List tables in the database
\dt

-- Create a test table
CREATE TABLE test (id INTEGER, name VARCHAR(50));

-- Insert data
INSERT INTO test VALUES (1, 'Hello Docker');

-- Query data
SELECT * FROM test;

-- Exit pgcli
\q
```

`\dt` and `\q` are pgcli/psql meta-commands (start with backslash).
Everything else is standard SQL.

## Closing and Restarting — the Persistence Test

To stop the container: `Ctrl+C` in the terminal where it's running.

After stopping:
- The container is gone (because we used `--rm`)
- BUT the named volume `ny_taxi_postgres_data` still exists
- Running the same `docker run` command again creates a fresh container that re-attaches to the same volume
- All previously-created tables and data should still be there

This is how volumes earn their keep.

## Hands-On Test (Proves I Actually Understand Volumes)

1. Start the Postgres container with the named volume command
2. Connect via pgcli, create the `test` table, insert a row
3. `\q` to exit pgcli
4. `Ctrl+C` to stop the container (with `--rm` it gets removed automatically)
5. Re-run the same `docker run` command — fresh container, same volume
6. Connect with pgcli, run `SELECT * FROM test;`
7. **Row should still be there.** If yes → volumes work. If empty → mount was wrong.

## Key Takeaways

- Postgres in Docker = no local install needed, full DB in one command
- Always mount a volume — without it, every restart is a fresh database
- Named volumes for default use, bind mounts when I need to see the files
- pgcli is the dev tool to talk to the DB; install with `uv add --dev` to keep it out of production
- The persistence test is the only real way to know I understand volumes