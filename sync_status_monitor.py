#!/usr/bin/env python3
"""
sync_status_monitor.py
Provides a tiny HTTP status endpoint (Flask) to report sync status stored in sqlite.
Designed to be run under a small WSGI (or directly for simplicity).
"""

from flask import Flask, jsonify
import sqlite3
import os

DB_PATH = os.environ.get("MIRROR_SYNC_DB", "/var/lib/dakin/mirror_sync.db")
app = Flask(__name__)

def get_states():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT repo,last_sync_ts,last_status,last_msg FROM sync_state")
    rows = c.fetchall()
    conn.close()
    return [{"repo": r[0], "last_sync_ts": r[1], "last_status": r[2], "last_msg": r[3]} for r in rows]

@app.route("/status")
def status():
    return jsonify(get_states())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8085)
