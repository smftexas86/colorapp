# C:\apps\colorform\app.py

import os
import struct
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pyodbc
from flask import Flask, request, render_template_string
from azure.identity import ManagedIdentityCredential

SQL_SERVER = os.getenv("SQL_SERVER", "smfsql1.database.windows.net")
SQL_DATABASE = os.getenv("SQL_DATABASE", "app")
MI_CLIENT_ID = os.getenv("MI_CLIENT_ID")
LISTEN_HOST = os.getenv("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", "8080"))

if not MI_CLIENT_ID:
    raise RuntimeError("MI_CLIENT_ID env var is required for user-assigned Managed Identity.")

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Favorite Color Form</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; max-width: 520px; }
    label { display:block; margin-top: 16px; }
    input { width: 100%; padding: 10px; margin-top: 6px; }
    button { margin-top: 20px; padding: 10px 14px; }
    .msg { margin-top: 20px; padding: 12px; border-radius: 6px; }
    .ok { background: #e7f7ea; }
    .err { background: #fde8e8; }
  </style>
</head>
<body>
  <h2>Submit your favorite color</h2>

  {% if message %}
    <div class="msg {{ 'ok' if ok else 'err' }}">{{ message }}</div>
  {% endif %}

  <form method="POST" action="/submit">
    <label>Name</label>
    <input name="name" maxlength="200" required />

    <label>Favorite color</label>
    <input name="color" maxlength="100" required />

    <button type="submit">Submit</button>
  </form>
  <div style="margin-top: 20px;">
  <a href="/results">View submitted results</a>
</div>
</body>
</html>
"""
RESULTS_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Submitted Results</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; max-width: 900px; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background: #f2f2f2; }
    .nav { margin-top: 20px; }
  </style>
</head>
<body>
  <h2>Submitted Results</h2>

  <table>
    <tr>
      <th>Name</th>
      <th>Favorite Color</th>
      <th>Submitted (CST)</th>
      <th>Submitted (UTC)</th>
    </tr>
    {% for row in rows %}
    <tr>
      <td>{{ row.PersonName }}</td>
      <td>{{ row.FavoriteColor }}</td>
      <td>{{ row.SubmittedAtCST }}</td>
      <td>{{ row.SubmittedAtUtc }}</td>
    </tr>
    {% endfor %}
  </table>

  <div class="nav">
    <a href="/">Back to form</a>
  </div>
</body>
</html>
"""

def _sql_access_token_struct() -> bytes:
    cred = ManagedIdentityCredential(client_id=MI_CLIENT_ID)
    token = cred.get_token("https://database.windows.net/.default").token
    token_bytes = token.encode("utf-16-le")
    return struct.pack("<I", len(token_bytes)) + token_bytes

def _conn():
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{SQL_SERVER},1433;"
        f"Database={SQL_DATABASE};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str, attrs_before={1256: _sql_access_token_struct()})

app = Flask(__name__)

@app.get("/")
def index():
    return render_template_string(PAGE, message=None, ok=True)

@app.post("/submit")
def submit():
    name = (request.form.get("name") or "").strip()
    color = (request.form.get("color") or "").strip()

    if not name or not color:
        return render_template_string(PAGE, message="Both fields are required.", ok=False), 400

    now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    now_cst = now_utc.astimezone(ZoneInfo("America/Chicago"))
    stamp_cst = now_cst.strftime("%m:%d:%Y %H:%M")

    try:
        with _conn() as cn:
            cur = cn.cursor()
            cur.execute(
                """
                INSERT INTO dbo.Submissions (PersonName, FavoriteColor, SubmittedAtCST, SubmittedAtUtc)
                VALUES (?, ?, ?, ?)
                """,
                name, color, stamp_cst, now_utc.replace(tzinfo=None),
            )
            cn.commit()
        return render_template_string(PAGE, message="Saved. Thanks!", ok=True)

    except Exception as e:
        return render_template_string(PAGE, message=f"DB error: {e}", ok=False), 500

    # absolute safety net (should never hit)
    return render_template_string(PAGE, message="Unexpected error: fell through submit()", ok=False), 500

@app.get("/results")
def results():
    try:
        with _conn() as cn:
            cur = cn.cursor()
            cur.execute("""
                SELECT TOP (100)
                    PersonName,
                    FavoriteColor,
                    SubmittedAtCST,
                    SubmittedAtUtc
                FROM dbo.Submissions
                ORDER BY SubmittedAtUtc DESC
            """)

            columns = [col[0] for col in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]

        return render_template_string(RESULTS_PAGE, rows=rows)

    except Exception asgit  e:
        return f"Error loading results: {e}", 500
    
import os
from flask import request




