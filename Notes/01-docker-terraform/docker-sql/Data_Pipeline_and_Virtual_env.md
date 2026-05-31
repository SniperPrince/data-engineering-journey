# Module 1.2 — Virtual Environments and Data Pipelines

## What is a Data Pipeline?
A service that takes data in and outputs more data.
Example flow: CSV → Pipeline → (Parquet file / Postgres / Data Warehouse)

In this workshop, our pipelines will:
- Download CSV from the web
- Transform/clean using pandas
- Load into Postgres
- Process in chunks for large files

## Building a Simple Pipeline
- Created `pipeline/pipeline.py`
- Used `sys.argv[1]` to accept a CLI argument (`day`)
- Used pandas: created a DataFrame, then saved to parquet via `df.to_parquet(...)`

## Why Virtual Environments?
- We need pandas + pyarrow to run the pipeline
- Installing globally with `pip install pandas pyarrow` works BUT causes conflicts if different projects need different versions
- Solution: a **virtual environment** — isolated Python env per project, separate from system Python

## uv — Modern Python Package Manager
- Written in Rust, much faster than pip
- Handles venvs automatically

### Setup
| Command | What it does |
|---|---|
| `pip install uv` | Install uv itself (global, one-time) |
| `uv init --python=3.13` | Initialize project — creates `pyproject.toml` + `.python-version` |
| `uv add pandas pyarrow` | Add dependencies — updates `pyproject.toml` and installs in venv |
| `uv run python pipeline.py 10` | Run a script INSIDE the venv |
| `uv run which python` | Shows the venv's python (vs system `which python`) |

### Proof of Isolation
Running these side by side:
- `uv run which python` → points to venv path
- `which python` → points to system Python
Different paths = isolation working.

## Git Hygiene
- Parquet files are binary outputs, don't commit them
- Add `*.parquet` to `.gitignore`

## Key Takeaway
Without virtual environments, every project shares the same global Python — recipe for dependency hell.
With uv, each project gets its own isolated environment, reproducibly defined in `pyproject.toml`.