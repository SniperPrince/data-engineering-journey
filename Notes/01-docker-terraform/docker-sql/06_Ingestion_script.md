# Module 1.6 — From Jupyter Notebook to Production Script

## Why convert notebook → script?
Notebooks are great for exploration but bad for production:
- Can't run on a schedule (cron, Airflow, etc.)
- Hard to pass parameters
- Cells can run out of order — fragile
- Not version-control friendly

A `.py` script is what we actually deploy and schedule.

## Step 1: Convert Notebook to Script
uv run jupyter nbconvert --to=script upload-data.ipynb

This creates `upload-data.py` with all the notebook's code as one flat script.

Then rename to a proper name:
mv upload-data.py ingest_data.py

## Step 2: Clean Up the Generated Script

The auto-converted file is messy. We need to:

### a) Move all imports to the top
```python
import pandas as pd
from sqlalchemy import create_engine
from time import time
import click
```

### b) Wrap everything in a function
Bare top-level code is hard to reuse and test. Wrap the logic in a `run()` function:

```python
def run(year, month, pg_user, pg_password, pg_host,
        pg_port, pg_db, target_table, chunksize):
    # ... ingestion logic here
```

### c) Parameterize hard-coded values
Replace hard-coded `root`, `localhost`, `5432`, `ny_taxi`, etc. with function parameters.

```python
engine = create_engine(
    f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'
)
```

Note: variables use **underscores** (`pg_user`), not dashes. Dashes only appear in CLI flags later.

### d) Use parameters in `pd.read_csv` and `to_sql`
```python
df_iter = pd.read_csv(url, chunksize=chunksize, ...)
df_chunk.to_sql(name=target_table, con=engine, if_exists='append')
```

`dtype` and `parse_dates` stay defined globally outside `run()` since they don't change.

## Step 3: Add CLI Argument Parsing with click

### Why click?
Without it, you'd parse `sys.argv` manually — no defaults, no help text, no type validation. Click handles all of it via decorators.

### Adding click to the project
uv add click

### The decorators

```python
@click.command()
@click.option('--pg-user', default='root', help='Username for DB')
@click.option('--pg-password', default='root', help='Password for DB')
@click.option('--pg-host', default='localhost', help='Host for DB')
@click.option('--pg-port', default=5432, type=int, help='Port for DB')
@click.option('--pg-db', default='ny_taxi', help='Database name')
@click.option('--target-table', default='yellow_taxi_data',
              help='Name of the table to write to')
@click.option('--year', type=int, help='Year of the data')
@click.option('--month', type=int, help='Month of the data')
@click.option('--chunksize', default=100000, type=int, help='Rows per chunk')
def run(pg_user, pg_password, pg_host, pg_port, pg_db,
        target_table, year, month, chunksize):
    # ... ingestion logic
```

### Key click rules to remember
- **CLI side uses dashes:** `--pg-user`
- **Python side uses underscores:** `pg_user`
- **Click auto-translates** between the two
- `type=int` validates input is an integer, fails fast otherwise
- `default=...` makes the flag optional
- `help='...'` shows up in `--help` output

### What `@click.command()` does
It's a decorator — wraps the `run` function and turns it into a CLI command.
Click reads `sys.argv`, matches each `--flag` to your `@click.option`, validates types,
and calls `run()` with the right values.

It also auto-generates a `--help` page for free.

### The entry point
```python
if __name__ == '__main__':
    run()
```

This pattern means: "if this file is run directly (not imported), call `run()`."
Click takes over from there.

## Step 4: Run the Script
uv run python ingest_data.py 
--pg-user=root 
--pg-password=root 
--pg-host=localhost 
--pg-port=5432 
--pg-db=ny_taxi 
--target-table=yellow_taxi_data 
--year=2021 
--month=1

Any flag with `default=` can be omitted to use the default.

## Key Takeaways

1. **Notebook → script** is mandatory for production. Notebooks are for exploration only.
2. **Wrap everything in a `run()` function** — makes it reusable and importable.
3. **Parameterize everything** — no hard-coded credentials or paths.
4. **click handles CLI parsing** — never write manual `sys.argv` code.
5. **Dashes ↔ underscores:** CLI uses `--pg-user`, Python uses `pg_user`. Click translates.

## Interview-Critical Points

- **Why click over argparse?** Click is more declarative (decorators), supports nested commands, better error messages. argparse is fine but verbose.
- **Why not pass env vars instead of CLI flags?** Both are valid. CLI flags for one-off runs. Env vars (via os.environ) for containerized/cloud deployments where you can't easily edit the command. Real pipelines often use both.
- **Why `if __name__ == '__main__':`?** Standard Python idiom. Lets the file be both imported as a module AND run as a script. Always do this for entry points.