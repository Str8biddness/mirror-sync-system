
---

# Repository: `Str8biddness/mirror-sync-system`

## File: `mirror_sync_daemon.py`
```python
#!/usr/bin/env python3
"""
mirror_sync_daemon.py
Background sync daemon for repository mirroring.

Features:
- Runs as a long-lived process (designed to be run under systemd)
- Uses a scheduler to periodically sync configured repositories
- Basic persistence of last-run times in SQLite
- Graceful shutdown, logging, and simplistic retry/backoff
"""

from __future__ import annotations
import logging
import os
import signal
import sqlite3
import time
import threading
from typing import List
import subprocess
import sys
import json
from apscheduler.schedulers.background import BackgroundScheduler

CONFIG_PATH = os.environ.get("MIRROR_SYNC_CONFIG", "/etc/dakin/mirror_sync_config.json")
DB_PATH = os.environ.get("MIRROR_SYNC_DB", "/var/lib/dakin/mirror_sync.db")
LOGFILE = os.environ.get("MIRROR_SYNC_LOG", "/var/log/dakin_mirror_sync.log")

logging.basicConfig(level=logging.INFO, filename=LOGFILE, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mirror-sync")

shutdown_flag = threading.Event()

def load_config(path: str) -> dict:
    if not os.path.exists(path):
        logger.error("Config file not found: %s", path)
        return {"repos": []}
    with open(path) as fh:
        return json.load(fh)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS sync_state (
        repo TEXT PRIMARY KEY,
        last_sync_ts INTEGER,
        last_status TEXT,
        last_msg TEXT
    )
    """)
    conn.commit()
    conn.close()

def update_state(repo: str, status: str, msg: str = ""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO sync_state (repo,last_sync_ts,last_status,last_msg) VALUES (?,?,?,?)",
              (repo, int(time.time()), status, msg))
    conn.commit()
    conn.close()

def run_sync_command(repo_cfg: dict) -> None:
    repo = repo_cfg.get("name", repo_cfg.get("url"))
    target = repo_cfg.get("target")
    cmd = repo_cfg.get("sync_command")  # allows overrides
    if not cmd:
        cmd = f"git clone --mirror {repo_cfg['url']} {target}" if not os.path.exists(target) else f"cd {target} && git remote update"
    logger.info("Syncing %s -> %s", repo, target)
    try:
        # execute in shell for convenience; production deployments should avoid shell=True if inputs are untrusted
        subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
        update_state(repo, "success", "OK")
        logger.info("Sync succeeded for %s", repo)
    except subprocess.CalledProcessError as exc:
        logger.exception("Sync failed for %s", repo)
        update_state(repo, "failure", str(exc))

def sync_all():
    cfg = load_config(CONFIG_PATH)
    repos = cfg.get("repos", [])
    for r in repos:
        run_sync_command(r)

def graceful_shutdown(signum, frame):
    logger.info("Received shutdown signal")
    shutdown_flag.set()

def main():
    logger.info("Starting mirror sync daemon")
    init_db()
    cfg = load_config(CONFIG_PATH)
    interval = cfg.get("interval_seconds", 600)
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_all, 'interval', seconds=interval, id='sync_all_job', max_instances=1, coalesce=True)
    scheduler.start()
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    try:
        while not shutdown_flag.is_set():
            time.sleep(1)
    finally:
        scheduler.shutdown(wait=False)
        logger.info("Mirror sync daemon stopped")

if __name__ == "__main__":
    main()
