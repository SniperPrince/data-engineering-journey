# Module 1.3 — Dockerizing the Pipeline

## Why containerize?
The pipeline runs locally — but how do we share it / run it on cloud / run it reproducibly?
→ Put it inside a Docker image so it runs identically everywhere.

## Simple Dockerfile (using pip)

| Instruction | Purpose |
|---|---|
| `FROM python:3.13.11-slim` | Base image — start from official Python image |
| `RUN pip install pandas pyarrow` | Install deps during image build |
| `WORKDIR /app` | Set working directory inside container |
| `COPY pipeline.py pipeline.py` | Copy source file into image |
| `ENTRYPOINT ["python", "pipeline.py"]` | Default command when container runs |

## Build and Run
- `docker build -t test:pandas .` → image name `test`, tag `pandas`. Without tag, defaults to `latest`.
- `docker run -it test:pandas some_number` → runs pipeline with CLI argument

## Dockerfile with uv (Production Pattern)

Key differences from pip version:
- Use `COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/` to pull uv binary from official uv image (multi-stage build)
- `ENV PATH="/app/.venv/bin:$PATH"` so container can find packages installed by uv
- Copy dep files (`pyproject.toml`, `uv.lock`, `.python-version`) BEFORE source code
- `RUN uv sync --locked` → installs exact versions from `uv.lock`, fails if lock is stale
- `ENTRYPOINT ["uv", "run", "python", "pipeline.py"]`

## Important Concepts

### Layer caching
Docker caches each instruction's output. Copying dep files BEFORE source code means:
- Code change → only re-copy code (fast)
- Dep change → re-install deps (slow, but rare)
Wrong order would re-install deps on every code change.

### uv inside container — why?
Not for isolation (container already does that). Reasons:
1. **Reproducibility** — `uv.lock` pins exact versions
2. **Speed** — uv is faster than pip
3. **Consistency** — same lock file works on laptop, CI, prod

### Multi-stage build pattern
`COPY --from=other_image /file /destination` lets you grab pre-built files from another image
instead of installing from scratch. Faster, smaller final image.



## Self-Question: Do I need uv.lock to dockerize? Can I just install deps manually inside a container?

**My idea:**
Instead of writing a full Dockerfile with uv, just run:
`docker run -it --rm -v $(pwd):/app --entrypoint=bash python:3.13-slim`
Then inside the container: `pip install pandas pyarrow` → `python pipeline.py 10`

**Answer:** Yes, this works — but it's a different *kind* of solution.

### Two distinct approaches:

| Approach | What it is | Use case |
|---|---|---|
| **A: Container as temp sandbox** (my idea above) | Spin up base image, mount code, install deps fresh each time | Prototyping, quick tests, debugging, exploring |
| **B: Build an image** (article's way) | Package code + deps into a self-contained image via Dockerfile | Production, sharing with team, cloud deployment, CI/CD |

### Why approach B for production:
- **Reproducible** — same image runs identically anywhere, anytime
- **Shippable** — push image once, anyone/anything can pull and run
- **Fast** — deps are pre-installed in the image, not installed on every run
- **Versioned** — `my-pipeline:v1`, `my-pipeline:v2`, easy rollback

### Without uv.lock — three options:
1. **Use the pip Dockerfile** — simpler, no uv needed. Article shows this version.
2. **My manual approach** — equivalent to writing the pip Dockerfile, just not persisted as a file.
3. **Generate the lock first** — run `uv init` and `uv add pandas pyarrow` locally, which auto-creates `uv.lock`. Then use the uv Dockerfile.

### The deep insight:
A Dockerfile is just a **recorded script** of the manual steps I'd do anyway.
Each instruction (FROM, RUN, COPY, etc.) = one step I could do by hand inside a base container.
The Dockerfile exists so:
- I (or my team) can rebuild the same environment without remembering what I typed
- The image becomes a portable, versioned artifact

### Hidden gotcha with my manual approach:
On Monday `pip install pandas` gives v2.1. On Tuesday someone publishes pandas v2.2 that breaks my pipeline. Tuesday's run fails — same command, different result.

**This is why production uses pinned versions** (`requirements.txt` with `==` versions, or `uv.lock`). Without pinning, "it worked yesterday" can become "it broke today" through no fault of yours.

## Self-Question: Can I develop INSIDE the container instead of on local?

**Three approaches:**

1. **Local-first** (article's way) — write code on laptop → Dockerfile → build. 95% of real work.

2. **Container-with-mount** — `docker run -v $(pwd):/app ...` lets me edit files locally
   but they persist into the container. Useful when I want to match prod Python exactly.

3. **Container-only** — like Approach 2 but without `-v`. Everything dies on exit. Useless for real work, fine for exploring.

**The modern answer:** Dev Containers (VS Code feature) or GitHub Codespaces.
Combines best of local + container — IDE features work, but code runs in container.
This is what `docker-workshop` was — Codespaces = cloud Dev Container.

**Key insight:** The choice between dev-local vs dev-in-container is about
matching prod environment. The Dockerfile is just the recipe; where you write
your code is independent of that.