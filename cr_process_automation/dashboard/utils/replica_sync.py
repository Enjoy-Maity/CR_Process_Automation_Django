import sqlite3
import logging
import threading
from django.conf import settings
import os

logger = logging.getLogger(__name__)

# Thread lock to prevent simultaneous backup conflicts
_sync_lock = threading.Lock()

def sync_master_to_replica():
    """
    Syncs the master SQLite DB to the replica.
    Thread-safe using a lock to prevent concurrent backup conflicts.
    """
    base_dir = settings.BASE_DIR
    master_path = os.path.join(base_dir, "db.master.sqlite3")
    replica_path = os.path.join(base_dir, "db.replica.sqlite3")

    if not os.path.exists(master_path):
        logger.error("Master DB not found during replica sync.")
        return

    # Non-blocking lock: skip sync if one is already in progress
    acquired = _sync_lock.acquire(blocking=False)
    if not acquired:
        logger.warning("Replica sync skipped: another sync is already in progress.")
        return

    try:
        master_conn = sqlite3.connect(master_path)
        replica_conn = sqlite3.connect(replica_path)

        try:
            master_conn.backup(replica_conn)
            logger.info("Replica synced successfully after write operation.")
        except Exception as e:
            logger.error(f"Replica sync failed: {e}", exc_info=True)
        finally:
            master_conn.close()
            replica_conn.close()

    finally:
        _sync_lock.release()


def async_sync_master_to_replica():
    """
    Runs sync_master_to_replica() in a background thread.
    Prevents blocking the main request/response cycle.
    """
    sync_thread = threading.Thread(
        target=sync_master_to_replica,
        daemon=True,
        name="ReplicaSyncThread"
    )
    sync_thread.start()

        