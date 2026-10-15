import sqlite3
from ipaddress import ip_address
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# keep the database next to this python file
PROJECT_FOLDER = Path(__file__).parent
DATABASE = PROJECT_FOLDER / "events.db"
SEVERITIES = ["informational", "low", "medium", "high", "critical"]

app = FastAPI(title="SIEM Dashboard")
app.mount("/static", StaticFiles(directory=PROJECT_FOLDER / "static"), name="static")


def connect_database():
    connection = sqlite3.connect(DATABASE)
    # this lets us read columns by name instead of by position
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = connect_database()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                source_ip TEXT,
                event_type TEXT,
                severity TEXT,
                message TEXT
            )
        """)
        connection.commit()
    finally:
        connection.close()


# FastAPI checks incoming JSON against these fields
class Event(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    source_ip: str = Field(min_length=1, max_length=45)
    event_type: str = Field(min_length=1, max_length=100)
    severity: str = Field(min_length=1, max_length=20)
    message: str = Field(min_length=1, max_length=1000)


@app.get("/")
def home():
    return FileResponse(PROJECT_FOLDER / "static" / "index.html")


@app.post("/api/events", status_code=201)
def add_event(event: Event):
    if event.severity not in SEVERITIES:
        raise HTTPException(status_code=422, detail="Invalid severity")

    try:
        address = str(ip_address(event.source_ip))
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid IP address")

    connection = connect_database()
    try:
        # the question marks keep user input separate from the SQL command
        result = connection.execute(
            """INSERT INTO events (source, source_ip, event_type, severity, message)
               VALUES (?, ?, ?, ?, ?)""",
            (event.source, address, event.event_type, event.severity, event.message),
        )
        connection.commit()
        return {"id": result.lastrowid}
    finally:
        connection.close()


@app.get("/api/events")
def get_events(severity: str = ""):
    if severity and severity not in SEVERITIES:
        raise HTTPException(status_code=422, detail="Invalid severity")

    connection = connect_database()
    try:
        if severity:
            rows = connection.execute(
                "SELECT * FROM events WHERE severity = ? ORDER BY id DESC LIMIT 100",
                (severity,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT 100"
            ).fetchall()

        events = []
        for row in rows:
            events.append(dict(row))
        return events
    finally:
        connection.close()


@app.get("/api/alerts")
def get_alerts():
    connection = connect_database()
    try:
        # one simple rule: five failed logins from the same IP in five minutes
        rows = connection.execute("""
            SELECT source_ip, COUNT(*) AS failed_logins
            FROM events
            WHERE event_type = 'login_failed'
              AND timestamp >= datetime('now', '-5 minutes')
            GROUP BY source_ip
            HAVING COUNT(*) >= 5
            ORDER BY failed_logins DESC, source_ip
        """).fetchall()

        alerts = []
        for row in rows:
            alerts.append(dict(row))
        return alerts
    finally:
        connection.close()


if __name__ == "__main__":
    create_table()
    # only accept connections from this computer
    uvicorn.run(app, host="127.0.0.1", port=8000)
