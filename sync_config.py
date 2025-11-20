#!/usr/bin/env python3
"""
sync_config.py
Configuration helper and simple scheduler wrapper for mirror-sync-system.

Generates a default config (JSON) at /etc/dakin/mirror_sync_config.json if it does not exist.
"""

import json
import os
from typing import Dict

DEFAULT_PATH = "/etc/dakin/mirror_sync_config.json"
DEFAULT_CONFIG = {
    "interval_seconds": 600,
    "repos": [
        {
            "name": "example/repo",
            "url": "https://github.com/example/example.git",
            "target": "/var/mirrors/example.git",
            "sync_command": ""
        }
    ],
    "bandwidth_limit_kbps": 0
}

def ensure_config(path: str = DEFAULT_PATH) -> Dict:
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as fh:
            json.dump(DEFAULT_CONFIG, fh, indent=2)
    with open(path) as fh:
        return json.load(fh)

if __name__ == "__main__":
    cfg = ensure_config()
    print("Config available at /etc/dakin/mirror_sync_config.json")
