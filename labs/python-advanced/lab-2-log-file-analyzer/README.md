# Log File Analyzer

> Lab 2 – Python Advanced · AmaliTech Apprenticeship Programme
> Regex & Functional Programming · Generators · Decorators · itertools

---

## Project Structure

```
log-file-analyzer/
├── src/
│   ├── patterns.py     # Compiled regex patterns (named groups)
│   ├── parser.py       # Raw line → structured dict
│   ├── decorators.py   # @timer, @log_call, lru_cache alias
│   ├── generators.py   # File reading, batching, itertools utilities
│   ├── pipeline.py     # map / filter / reduce transformations
│   └── analyzer.py     # Orchestration + JSON report
├── tests/
│   ├── test_patterns.py
│   ├── test_pipeline.py
│   └── test_generators.py
├── sample_data/
│   └── access.log      # 1 100-line Apache Combined Log sample
├── reports/
│   └── report.json     # Generated on each run
├── main.py
└── requirements.txt
```

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py          # run analysis + batch demo
python -m pytest        # run 47 tests
```

---

## Regex Pattern Explanations

### `LOG_LINE` – Apache Combined Log Format

```
(?P<ip>\d{1,3}(?:\.\d{1,3}){3})   → client IPv4 address
\[(?P<timestamp>[^\]]+)\]          → timestamp inside brackets
"(?P<method>[A-Z]+)                → HTTP verb (GET, POST …)
(?P<url>\S+)                       → request path / query string
(?P<protocol>HTTP/\d\.\d)"        → protocol version
(?P<status>\d{3})                  → 3-digit status code
(?P<size>\d+|-)                    → response bytes (or -)
"(?P<referrer>[^"]*)"             → Referer header
"(?P<agent>[^"]*)"                → User-Agent header
```

All groups are **named** (`?P<name>`) so callers use `m["ip"]` instead of `m.group(1)`.

### `TIMESTAMP` – component extraction

Breaks `01/Jan/2024:08:30:45 +0000` into `day`, `month`, `year`, `hour`, `minute`, `second`, `tz`.

### Validation helpers

| Pattern | Purpose |
|---|---|
| `IP_VALIDATE` | Strict IPv4 dotted-quad (0–255 per octet) |
| `EMAIL_VALIDATE` | RFC-5321-ish `local@domain.tld` |
| `URL_VALIDATE` | `http://` or `https://` URLs |

### Cleaning

`QUERY_STRIP` (`\?.*$`) removes query strings before URL grouping.
`MULTI_SLASH` (`/{2,}`) normalises repeated slashes.

---

## Functional Pipeline

```
read_log_lines(path)          ← generator: yields raw strings O(1) memory
        │
        ▼
  to_entries(lines)           ← map(): parse_line() over each raw string
        │
        ├──▶ by_status / by_method / by_status_range   ← filter()
        │         │
        │         └──▶ errors_only / client_errors / server_errors
        │                   (functools.partial specialisations)
        │
        └──▶ count_by / total_bytes / top_urls / top_ips  ← reduce()
```

`functools.partial` creates zero-argument filter specialisations:

```python
errors_only   = partial(by_status_range, lo=400, hi=599)
server_errors = partial(by_status_range, lo=500, hi=599)
client_errors = partial(by_status_range, lo=400, hi=499)
```

---

## Generator vs List – Memory Comparison

| Approach | Memory | Notes |
|---|---|---|
| `list(open(file))` | O(n) – entire file in RAM | Fast random access, bad for large files |
| `read_log_lines(path)` generator | O(1) – one line at a time | Scales to multi-GB logs |
| `batch(entries, 100)` | O(batch_size) | Controlled memory with `itertools.islice` |

The `batch_demo` in `main.py` shows 11 batches of 100 entries each processed without ever holding the full dataset in memory.

---

## Decorators

| Decorator | Effect |
|---|---|
| `@timer` | Logs wall-clock time via `time.perf_counter()` |
| `@log_call` | Traces call arguments and return value at DEBUG level |
| `@cache(maxsize=128)` | `functools.lru_cache` – memoises pure functions like `status_label` |

`total_bytes` is decorated with both `@timer` and `@log_call` to demonstrate chaining.

---

## itertools Usage

| Function | Where used | Purpose |
|---|---|---|
| `itertools.islice` | `batch()` | Slice fixed-size chunks from a generator |
| `itertools.chain.from_iterable` | `chain_logs()` | Combine multiple log files lazily |
| `itertools.groupby` | `group_by()` | Group sorted entries by a key field |
| `itertools.takewhile` | `takewhile_date()` | Stop iteration once date exceeds upper bound |
