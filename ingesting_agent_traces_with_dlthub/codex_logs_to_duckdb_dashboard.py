import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import html
    import marimo as mo
    import dlt
    return dlt, html, mo


@app.cell
def _(dlt):
    pipeline = dlt.attach("codex_logs_to_duckdb")
    dataset = pipeline.dataset()
    return dataset, pipeline


@app.cell
def _(mo):
    mo.Html(
        """
        <h1>Codex Logs Report</h1>
        <p>Local report for <code>codex_raw.codex_log_events</code>.</p>
        """
    )
    return


@app.cell
def _(dataset):
    summary_rows = dataset(
        """
        SELECT
            COUNT(*) AS total_records,
            COUNT(DISTINCT relative_path) AS source_files,
            COUNT(DISTINCT session_id) FILTER (WHERE session_id IS NOT NULL) AS sessions,
            SUM(CASE WHEN is_json_valid THEN 0 ELSE 1 END) AS invalid_json_records,
            MIN(file_mtime) AS earliest_file_mtime,
            MAX(file_mtime) AS latest_file_mtime
        FROM codex_log_events
        """
    ).fetchall()
    summary = summary_rows[0]
    return (summary,)


@app.cell
def _(html, mo, summary):
    def _card(label, value):
        return f"""
        <div class="metric-card">
          <div class="metric-label">{html.escape(label)}</div>
          <div class="metric-value">{html.escape(str(value))}</div>
        </div>
        """

    _cards = "".join(
        [
            _card("Records", f"{summary[0]:,}"),
            _card("Source files", f"{summary[1]:,}"),
            _card("Sessions", f"{summary[2]:,}"),
            _card("Invalid JSON", f"{summary[3]:,}"),
        ]
    )
    mo.Html(
        f"""
        <style>
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 8px 0 16px;
        }}
        .metric-card {{
            border: 1px solid #d7dde8;
            border-radius: 8px;
            padding: 12px;
            background: #ffffff;
        }}
        .metric-label {{
            color: #5f6b7a;
            font-size: 13px;
            margin-bottom: 6px;
        }}
        .metric-value {{
            color: #142033;
            font-size: 26px;
            font-weight: 700;
        }}
        .bar-row {{
            display: grid;
            grid-template-columns: minmax(120px, 260px) 1fr 80px;
            gap: 10px;
            align-items: center;
            margin: 7px 0;
        }}
        .bar-label {{
            overflow-wrap: anywhere;
            color: #253044;
            font-size: 13px;
        }}
        .bar-track {{
            height: 18px;
            background: #eef2f7;
            border-radius: 5px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            background: #2f6fbb;
        }}
        .bar-value {{
            color: #253044;
            font-size: 13px;
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}
        .report-note {{
            color: #5f6b7a;
            font-size: 13px;
            margin-top: 4px;
        }}
        table.codex-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        table.codex-table th, table.codex-table td {{
            border-bottom: 1px solid #d7dde8;
            padding: 7px 8px;
            text-align: left;
            vertical-align: top;
        }}
        table.codex-table th {{
            color: #253044;
            background: #f6f8fb;
        }}
        @media (max-width: 760px) {{
            .metric-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .bar-row {{
                grid-template-columns: minmax(90px, 150px) 1fr 68px;
            }}
        }}
        </style>
        <div class="metric-grid">{_cards}</div>
        <div class="report-note">
          File modification window: {html.escape(str(summary[4]))} to {html.escape(str(summary[5]))}
        </div>
        """
    )
    return


@app.cell
def _(dataset):
    event_type_rows = dataset(
        """
        SELECT
            COALESCE(event_type, '(missing)') AS event_type,
            COUNT(*) AS events
        FROM codex_log_events
        GROUP BY 1
        ORDER BY events DESC
        LIMIT 12
        """
    ).fetchall()
    return (event_type_rows,)


@app.cell
def _(html, mo, event_type_rows):
    def _bar_chart(rows, label_index, value_index, title):
        max_value = max((row[value_index] for row in rows), default=1)
        body = []
        for row in rows:
            label = html.escape(str(row[label_index]))
            value = int(row[value_index])
            width = 100 * value / max_value if max_value else 0
            body.append(
                f"""
                <div class="bar-row">
                  <div class="bar-label">{label}</div>
                  <div class="bar-track"><div class="bar-fill" style="width: {width:.2f}%"></div></div>
                  <div class="bar-value">{value:,}</div>
                </div>
                """
            )
        return f"<h2>{html.escape(title)}</h2>{''.join(body)}"

    mo.Html(_bar_chart(event_type_rows, 0, 1, "Event Type Mix"))
    return


@app.cell
def _(dataset):
    daily_rows = dataset(
        """
        SELECT
            CASE
                WHEN COALESCE(event_timestamp, ingested_at) LIKE '____-__-__%' THEN SUBSTR(COALESCE(event_timestamp, ingested_at), 1, 10)
                ELSE 'unknown'
            END AS event_day,
            COUNT(*) AS events
        FROM codex_log_events
        GROUP BY 1
        ORDER BY 1
        """
    ).fetchall()
    return (daily_rows,)


@app.cell
def _(html, mo, daily_rows):
    def _bar_chart(rows, label_index, value_index, title):
        max_value = max((row[value_index] for row in rows), default=1)
        body = []
        for row in rows:
            label = html.escape(str(row[label_index]))
            value = int(row[value_index])
            width = 100 * value / max_value if max_value else 0
            body.append(
                f"""
                <div class="bar-row">
                  <div class="bar-label">{label}</div>
                  <div class="bar-track"><div class="bar-fill" style="width: {width:.2f}%"></div></div>
                  <div class="bar-value">{value:,}</div>
                </div>
                """
            )
        return f"<h2>{html.escape(title)}</h2>{''.join(body)}"

    mo.Html(_bar_chart(daily_rows, 0, 1, "Daily Event Volume"))
    return


@app.cell
def _(dataset):
    source_file_rows = dataset(
        """
        SELECT
            relative_path,
            COUNT(*) AS records,
            MAX(file_size_bytes) AS file_size_bytes
        FROM codex_log_events
        GROUP BY 1
        ORDER BY records DESC
        LIMIT 10
        """
    ).fetchall()
    return (source_file_rows,)


@app.cell
def _(html, mo, source_file_rows):
    def _format_bytes(size_bytes):
        size = float(size_bytes or 0)
        for unit in ("B", "KiB", "MiB", "GiB"):
            if size < 1024 or unit == "GiB":
                return f"{size:.1f} {unit}"
            size /= 1024

    _rows = "".join(
        f"""
        <tr>
          <td>{html.escape(str(path))}</td>
          <td>{records:,}</td>
          <td>{html.escape(_format_bytes(file_size_bytes))}</td>
        </tr>
        """
        for path, records, file_size_bytes in source_file_rows
    )
    mo.Html(
        f"""
        <h2>Records by Source File</h2>
        <table class="codex-table">
          <thead><tr><th>Source file</th><th>Records</th><th>File size</th></tr></thead>
          <tbody>{_rows}</tbody>
        </table>
        """
    )
    return


@app.cell
def _(dataset):
    json_key_rows = dataset(
        """
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
        """
    ).fetchall()
    return (json_key_rows,)


@app.cell
def _(html, mo, json_key_rows):
    def _bar_chart(rows, label_index, value_index, title):
        max_value = max((row[value_index] for row in rows), default=1)
        body = []
        for row in rows:
            label = html.escape(str(row[label_index]))
            value = int(row[value_index])
            width = 100 * value / max_value if max_value else 0
            body.append(
                f"""
                <div class="bar-row">
                  <div class="bar-label">{label}</div>
                  <div class="bar-track"><div class="bar-fill" style="width: {width:.2f}%"></div></div>
                  <div class="bar-value">{value:,}</div>
                </div>
                """
            )
        return f"<h2>{html.escape(title)}</h2>{''.join(body)}"

    mo.Html(_bar_chart(json_key_rows, 0, 1, "Top-Level JSON Key Frequency"))
    return


if __name__ == "__main__":
    app.run()
