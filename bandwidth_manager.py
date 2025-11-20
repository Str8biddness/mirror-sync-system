#!/usr/bin/env python3
"""
bandwidth_manager.py
Network bandwidth optimization helper.

Implements simple token-bucket-like pacing for subprocess downloads.
Also includes a wrapper to call 'rsync' or 'curl' with rate limits if configured.
"""

import os
import shutil
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bandwidth-manager")

def run_with_limit(cmd: str, limit_kbps: int = 0):
    """
    If limit_kbps > 0 and 'pv' is available, pipe through pv to limit throughput.
    Otherwise, try rsync --bwlimit for rsync commands.
    """
    if limit_kbps <= 0:
        return subprocess.call(cmd, shell=True)
    # Try rsync optimization
    if cmd.strip().startswith("rsync"):
        cmd += f" --bwlimit={limit_kbps}"
        return subprocess.call(cmd, shell=True)
    # Fallback: if pv present, use it (note: requires reshaping command output)
    pv = shutil.which("pv")
    if pv:
        wrapped = f"{cmd} | pv -L {limit_kbps}k"
        return subprocess.call(wrapped, shell=True)
    logger.warning("No bandwidth shaping available (pv not found). Running without limit.")
    return subprocess.call(cmd, shell=True)
