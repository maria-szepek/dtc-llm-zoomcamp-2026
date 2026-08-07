# Analysis Plan: codex_logs_to_duckdb

## Connection
pipeline: codex_logs_to_duckdb
dataset: codex_raw
destination: duckdb

## Profile Summary
| table | rows | key columns | notes |
|-------|------|-------------|-------|
| codex_log_events | 7,326 | relative_path, file_name, record_number, raw_json, is_json_valid, event_type, event_timestamp, session_id, top_level_keys | one raw event table; role is empty for all rows; 0 invalid JSON rows; source_file may contain local paths |

## Questions
1. [x] What is the overall volume and validity of the ingested Codex logs? -> Report metric cards
2. [x] Which event types dominate the logs? -> Chart 1
3. [x] How does event volume change by day? -> Chart 2
4. [x] Which source files contribute the most records? -> Chart 3
5. [x] Which top-level JSON keys appear most often? -> Chart 4

## Data Gaps
The raw table does not currently extract nested message text, model names, token usage, tool names, or latency metrics into first-class columns. Those can be added later by extending the pipeline's JSON metadata extraction.

## Chart 1: Event Type Mix
question: Which event types dominate the logs?
type: bar
x: event_type
y: count(*)
source: codex_log_events

```sql
SELECT
    COALESCE(event_type, '(missing)') AS event_type,
    COUNT(*) AS events
FROM codex_log_events
GROUP BY 1
ORDER BY events DESC
LIMIT 12
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("events:Q", title="Events"),
    y=alt.Y("event_type:N", sort="-x", title="Event type"),
    tooltip=["event_type:N", "events:Q"]
).properties(title="Event Type Mix")
```

## Chart 2: Daily Event Volume
question: How does event volume change by day?
type: line
x: event_day
y: count(*)
source: codex_log_events

```sql
SELECT
    CASE
        WHEN COALESCE(event_timestamp, ingested_at) LIKE '____-__-__%' THEN SUBSTR(COALESCE(event_timestamp, ingested_at), 1, 10)
        ELSE 'unknown'
    END AS event_day,
    COUNT(*) AS events
FROM codex_log_events
GROUP BY 1
ORDER BY 1
```

```altair
alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("event_day:N", title="Day"),
    y=alt.Y("events:Q", title="Events"),
    tooltip=["event_day:N", "events:Q"]
).properties(title="Daily Event Volume")
```

## Chart 3: Records by Source File
question: Which source files contribute the most records?
type: bar
x: records
y: relative_path
source: codex_log_events

```sql
SELECT
    relative_path,
    COUNT(*) AS records,
    MAX(file_size_bytes) AS file_size_bytes
FROM codex_log_events
GROUP BY 1
ORDER BY records DESC
LIMIT 10
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("records:Q", title="Records"),
    y=alt.Y("relative_path:N", sort="-x", title="Source file"),
    tooltip=["relative_path:N", "records:Q", "file_size_bytes:Q"]
).properties(title="Records by Source File")
```

## Chart 4: Top-Level JSON Key Frequency
question: Which top-level JSON keys appear most often?
type: bar
x: records
y: json_key
source: codex_log_events

```sql
WITH split_keys AS (
    SELECT UNNEST(STRING_SPLIT(top_level_keys, ',')) AS json_key
    FROM codex_log_events
    WHERE top_level_keys IS NOT NULL AND top_level_keys != ''
)
SELECT
    json_key,
    COUNT(*) AS records
FROM split_keys
GROUP BY 1
ORDER BY records DESC
LIMIT 20
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("records:Q", title="Records"),
    y=alt.Y("json_key:N", sort="-x", title="JSON key"),
    tooltip=["json_key:N", "records:Q"]
).properties(title="Top-Level JSON Key Frequency")
```
