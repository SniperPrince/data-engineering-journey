# Module 1.5 — Data Ingestion (NY Taxi → Postgres)

## Goal
Take a 1.4M-row CSV (NY Yellow Taxi data, January 2021) and ingest it into the
Postgres container from Module 1.4 — in chunks, without crashing on memory.

## Setup: Jupyter Notebook
uv add --dev jupyter
uv run jupyter notebook

Why `--dev`? Same as pgcli — Jupyter is for exploration/dev, not production.

## The Dataset

- **Source:** NYC TLC Yellow Taxi data, January 2021 (~1.4M rows)
- **Format:** Gzipped CSV (`.csv.gz`) — pandas reads it directly without manual unzip
- **Why CSV not parquet:** Real source used to be CSV; switched to parquet later.
  We use CSV here for the pre-processing practice.

## Step 1: Explore the Data

```python
import pandas as pd

prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz', nrows=100)

df.head()      # first rows
df.dtypes      # column types
df.shape       # (rows, columns)
```

## Step 2: Fix the DtypeWarning

When reading the FULL file (no `nrows`), pandas warns:
> DtypeWarning: Columns (6) have mixed types. Specify dtype option on import.

**Why this matters:**
- Pandas auto-detects types by scanning the column.
- Mixed values (e.g., integers + empty strings) → pandas downgrades to `object` (slow, memory-heavy).
- Solution: tell pandas the type explicitly.

```python
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    # ... etc
}

parse_dates = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]

df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz',
                 nrows=100, dtype=dtype, parse_dates=parse_dates)
```

`parse_dates` is separate because pandas needs to actively *parse* date strings into datetime
objects — not just assign a type.

## Step 3: Connect to Postgres
uv add sqlalchemy "psycopg[binary,pool]"

| Tool | Role |
|---|---|
| `psycopg` | Python driver for Postgres (low-level adapter) |
| `[binary, pool]` extras | Pre-compiled binaries (fast install) + connection pooling |
| `sqlalchemy` | Higher-level abstraction over psycopg — pandas uses this |

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg://root:root@localhost:5432/ny_taxi')
```

Format: `dialect+driver://user:password@host:port/database`

## Step 4: Preview the Schema (Don't Run It Yet)

```python
print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
```

This returns the CREATE TABLE statement as a string. Doesn't execute. Good defensive practice
— review before committing.

## Step 5: Create the Empty Table

```python
df.head(0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
```

**The `head(0)` trick:**
- `df.head(0)` = same columns, zero rows
- `.to_sql()` generates a CREATE TABLE based on the columns + dtypes
- `if_exists='replace'` drops any existing table and creates fresh
- Zero rows → table is empty but schema is correct

Without `head(0)`, the full 100-row sample would be inserted too.

## Step 6: Set Up Chunked Reading

```python
df_iter = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz',
                      dtype=dtype, parse_dates=parse_dates,
                      iterator=True, chunksize=100000)
```

- `iterator=True` returns a generator object, not a DataFrame
- `chunksize=100000` = each iteration gives 100k rows
- 1.4M rows / 100k = ~14 chunks

**Why chunking?** Without it, the full file loads into RAM. For larger files
(say 50GB on a 16GB laptop), this crashes. Chunking = streaming. Constant memory.

## Step 7: The Complete Ingestion Loop

```python
first = True

for df_chunk in df_iter:
    if first:
        df_chunk.head(0).to_sql(name='yellow_taxi_data',
                                con=engine, if_exists='replace')
        first = False
        print("Table created")

    df_chunk.to_sql(name='yellow_taxi_data',
                    con=engine, if_exists='append')
    print(f"Inserted: {len(df_chunk)}")
```

### `if_exists` parameter — know all three
- `'fail'` (default) — error if table exists
- `'replace'` — DROP existing table and CREATE new one (DESTRUCTIVE)
- `'append'` — add rows to existing table

We use `replace` once (for first-time table creation) and `append` for all data inserts.

## Alternative: Using `next()` Instead Of A Flag

```python
first_chunk = next(df_iter)  # pull one chunk out

# create table from this chunk's schema
first_chunk.head(0).to_sql(name='yellow_taxi_data',
                           con=engine, if_exists='replace')
first_chunk.to_sql(name='yellow_taxi_data',
                   con=engine, if_exists='append')

# loop the remaining chunks
for df_chunk in df_iter:
    df_chunk.to_sql(name='yellow_taxi_data',
                    con=engine, if_exists='append')
```

Cleaner separation: "create table" and "loop chunks" are visually distinct.
Senior engineers tend to prefer this over the `first = True` flag.

## Step 8: Progress Bar with tqdm

For long-running operations, visibility matters:

uv add tqdm

```python
from tqdm.auto import tqdm

for df_chunk in tqdm(df_iter):
    df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
```

`tqdm` wraps any iterable and shows a progress bar. Daily use in DE.

## Step 9: Verify the Data
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi

Then in pgcli:
```sql
SELECT count(*) FROM yellow_taxi_data;  -- should be ~1.4M
SELECT * FROM yellow_taxi_data LIMIT 5;
```

**Always verify ingestion worked.** Skipping this is a rookie mistake.

## Interview-Critical Takeaways

1. **Why chunk?** Memory. Streaming ingestion = constant memory regardless of file size.
2. **Why specify dtypes?** Performance + correctness. Auto-detection is slow and error-prone.
3. **`head(0)` trick:** Create table schema without inserting data.
4. **`if_exists`:** `replace` is destructive; `append` is safe. Use `replace` once, `append` always.
5. **SQLAlchemy + psycopg:** Abstraction layer (SQLAlchemy) + driver (psycopg) — both needed.
6. **Verify after ingestion** — always count rows or sample data.

## Common Pitfalls

- Forgetting `head(0)` → inserts duplicate data on first chunk
- Using `df` instead of `df_chunk` inside the loop → re-inserts same data
- Running `if_exists='replace'` inside the loop → wipes table on every chunk
- Not specifying dtypes → DtypeWarning + slow ingestion
- Skipping verification → silent failures go unnoticed