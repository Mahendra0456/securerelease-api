import json
import logging
import os
import time

import psycopg2
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest
from starlette.responses import Response

VERSION = os.getenv("APP_VERSION", "dev")

app = FastAPI(title="Apex Operations API", version=VERSION)

REQS = Counter("http_requests_total", "Requests", ["path", "status"])


class Task(BaseModel):
    name: str


class JsonFmt(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": self.formatTime(record),
            "level": record.levelname,
            "msg": record.getMessage(),
            "version": VERSION,
        })


handler = logging.StreamHandler()
handler.setFormatter(JsonFmt())

log = logging.getLogger("apex")
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = False


def conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
    )


@app.middleware("http")
async def middleware(req: Request, nxt):
    start = time.time()
    resp = await nxt(req)

    REQS.labels(req.url.path, str(resp.status_code)).inc()

    log.info(
        f"{req.method} {req.url.path} "
        f"{resp.status_code} {int((time.time() - start) * 1000)}ms"
    )

    return resp


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.get("/ready")
def ready():
    try:
        with conn() as connection:
            with connection.cursor() as cur:
                cur.execute("SELECT 1")

        return {"status": "ready"}

    except Exception as exc:
        log.error(f"readiness failed: {exc}")
        raise HTTPException(status_code=503, detail="db unavailable")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")


DDL = """
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
)
"""


@app.post("/tasks")
def add(task: Task):
    try:
        with conn() as connection:
            with connection.cursor() as cur:
                cur.execute(DDL)
                cur.execute(
                    "INSERT INTO tasks(name) VALUES(%s) RETURNING id",
                    (task.name,),
                )
                task_id = cur.fetchone()[0]

        return {"id": task_id, "name": task.name}

    except Exception as exc:
        log.error(f"task creation failed: {exc}")
        raise HTTPException(status_code=500, detail="task creation failed")


@app.get("/tasks")
def lst():
    try:
        with conn() as connection:
            with connection.cursor() as cur:
                cur.execute(DDL)
                cur.execute("SELECT id, name FROM tasks ORDER BY id")
                rows = cur.fetchall()

        return [{"id": row[0], "name": row[1]} for row in rows]

    except Exception as exc:
        log.error(f"task retrieval failed: {exc}")
        raise HTTPException(status_code=500, detail="task retrieval failed")
