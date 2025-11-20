# Mirror Sync System

Purpose: continuously mirror repositories (git, package indexes, etc.) to local mirrors with conflict resolution and monitoring.

## Components
- `mirror_sync_daemon.py` — main background daemon (systemd service available)
- `sync_config.py` — config generator for `/etc/dakin/mirror_sync_config.json`
- `conflict_resolver.py` — conflict resolution strategies
- `bandwidth_manager.py` — bandwidth shaping helpers
- `sync_status_monitor.py` — minimal HTTP status endpoint
- `systemd/mirror-sync.service` — systemd unit

## Install
1. Place repository under `/opt/mirror-sync-system`
2. Edit `/etc/dakin/mirror_sync_config.json` via `python3 sync_config.py`
3. Install requirements: `python3 -m pip install -r requirements.txt`
4. Copy systemd unit to `/etc/systemd/system/mirror-sync.service` and `systemctl enable --now mirror-sync.service`

## Notes
- The system uses SQLite at `/var/lib/dakin/mirror_sync.db` for small state persistence.
- Logs at `/var/log/dakin_mirror_sync.log`.
- Designed to be resilient; adjust retry/backoff via config.
