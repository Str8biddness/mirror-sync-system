#!/usr/bin/env python3
"""
conflict_resolver.py
Automatic conflict resolution engine for mirrored repositories.

Strategy:
- For git repos, prefer remote 'origin' as source of truth for bare mirrors.
- For package indexes, compare checksums and prefer highest-availability copy.
- This module exposes a small API used by mirror_sync_daemon.
"""

from __future__ import annotations
import logging
import subprocess
import os
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("conflict-resolver")

def hash_file(path: str):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def resolve_git_conflict(path: str):
    # Simplistic: attempt a forced fetch from origin then prune stale refs
    try:
        subprocess.check_call(f"git -C {path} remote update --prune", shell=True)
        subprocess.check_call(f"git -C {path} fetch --all --prune", shell=True)
        logger.info("Resolved git conflicts for %s", path)
        return True
    except subprocess.CalledProcessError:
        logger.exception("Failed to resolve git conflict at %s", path)
        return False
