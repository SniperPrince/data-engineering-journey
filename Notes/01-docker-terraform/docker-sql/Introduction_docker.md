# Module 1.1 — Introduction to Docker

## What is Docker?

- **Containerization software** — isolates apps like VMs do, but much leaner
- A **container** = a sandboxed environment where your app runs
- A **Docker image** = a snapshot/blueprint of a container
- Java analogy: image = class, container = object instance

## Why Docker? (3 core wins)

| Win | What it means |
|---|---|
| **Reproducibility** | Same environment everywhere — "works on my machine" problem solved |
| **Isolation** | Apps run independently, no conflicts with host system |
| **Portability** | Works anywhere Docker is installed — laptop, server, cloud |

**Where Docker is used in DE world:**
- CI/CD integration tests
- Running pipelines on the cloud (AWS Batch, Kubernetes)
- Spark jobs
- Serverless (AWS Lambda, GCP Functions)

## Basic Commands — The Shape, Not Memorized

| Goal | Command |
|---|---|
| Check Docker version | `docker --version` |
| Run a simple test | `docker run hello-world` |
| Run an interactive Ubuntu shell | `docker run -it ubuntu` |
| Run Python container | `docker run -it python:3.9.16` |

**`-it` flag = interactive + terminal**
- `-i` = keep input open (so you can type)
- `-t` = give me a real terminal (proper prompt)
- Rule: if you'd want to type commands inside → use `-it`

## Stateless Containers (CRITICAL CONCEPT)

- **Containers do NOT save changes when killed.**
- Restart a container → fresh state, all changes gone
- This is a FEATURE not a bug — keeps host system safe
- Example: even `rm -rf /` inside container doesn't hurt your host

**Why it matters:** If you store data inside a container, you lose it on restart. Use **volumes** to persist data (see below).

## Managing Containers

| Goal | Command |
|---|---|
| List running containers | `docker ps` |
| List ALL containers (incl. stopped) | `docker ps -a` |
| Delete all stopped containers | `docker rm $(docker ps -aq)` |
| Auto-delete container when it exits | `docker run --rm ...` |

**Pattern to remember:** Always add `--rm` for one-off runs. Saves cleanup later.

## Base Images

- Many official images available: `ubuntu`, `python:3.9.16`, `postgres:13`, `node:18`, etc.
- **`-slim` variants** = smaller images, less bloat
  - Example: `python:3.9.16-slim`
- Each image has a default **entrypoint** (the command it runs by default)
  - `python:3.9.16` → drops you into Python REPL by default
  - To override and get bash instead: `--entrypoint=bash`

**Command shape for overriding entrypoint:**

docker run -it --rm --entrypoint=bash python:3.9.16-slim

## Volumes — How To Persist Data

**The problem:** containers are stateless. Data dies on restart.
**The solution:** mount a **volume** = a folder on your host machine that's connected to a folder inside the container.

**Command shape:**
docker run -v <host_path>:<container_path> <image>

**Concrete example from module:**
docker run -it --rm 
-v $(pwd)/test:/app/test 
--entrypoint=bash 
python:3.9.16-slim


- `$(pwd)/test` = `test` folder in your current directory (host side)
- `/app/test` = where that folder appears inside the container
- Changes to files in either location are visible in both — they're the same folder

**Why volumes matter for DE:** Postgres data, raw files, processed outputs — anything you want to keep across container restarts goes in a volume.

## Mental Model Recap

| Question | Answer |
|---|---|
| What is a container? | Lightweight isolated environment, like a tiny VM |
| What is an image? | Blueprint for a container |
| What happens to changes inside a container? | Lost when container dies (stateless) |
| How to keep data alive? | Use volumes (`-v host:container`) |
| When do I need `-it`? | When I want to type commands inside |
| When do I add `--rm`? | One-off runs (so cleanup is automatic) |
| How to use bash instead of default? | `--entrypoint=bash` |