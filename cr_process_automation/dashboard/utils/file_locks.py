"""
Cross-platform advisory file locking.

Used to serialise writes to *shared* files (most importantly the shared
planning-sheet workbook that several automation tasks read and rewrite).
Two or more users may run tasks concurrently; the tasks themselves stay
independent, but access to a shared file is serialised through a lock file so
the workbook can never be read/written half-way by another process/thread.

Works on both Linux (fcntl) and Windows (msvcrt) so the same code path is used
in every deployment target. The lock is *advisory* and process-wide: it guards
against other processes/threads in this application, which is exactly the
multi-user scenario. Within a single process the OS lock is complemented by a
per-path threading lock so concurrent threads in the same process are also
serialised (fcntl locks are per-process on POSIX and would otherwise not block
sibling threads).
"""

from __future__ import annotations

import os
import threading
import time
from contextlib import contextmanager
from typing import Dict

if os.name == "nt":  # pragma: no cover - exercised on Windows only
    import msvcrt
else:  # pragma: no cover - exercised on POSIX only
    import fcntl


# Per-process registry of locks keyed by the resolved lock-file path, so two
# threads in the same worker cannot both hold the same advisory lock.
_PATH_LOCKS: Dict[str, threading.Lock] = {}
_PATH_LOCKS_GUARD = threading.Lock()


def _thread_lock_for(lock_path: str) -> threading.Lock:
    with _PATH_LOCKS_GUARD:
        lock = _PATH_LOCKS.get(lock_path)
        if lock is None:
            lock = threading.Lock()
            _PATH_LOCKS[lock_path] = lock
        return lock


def _acquire_os_lock(handle, timeout: float, poll: float) -> None:
    """Try to take the OS-level exclusive lock until *timeout* elapses."""
    deadline = time.monotonic() + max(timeout, 0.0)
    while True:
        try:
            if os.name == "nt":  # pragma: no cover - Windows only
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except OSError:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Timed out after {timeout}s waiting for file lock: {handle.name}"
                )
            time.sleep(poll)


def _release_os_lock(handle) -> None:
    try:
        if os.name == "nt":  # pragma: no cover - Windows only
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


@contextmanager
def file_lock(path, timeout: float = 300.0, poll: float = 0.1):
    """
    Context manager that holds an exclusive lock associated with *path*.

    The lock file is ``<path>.lock`` (created if needed). ``path`` itself does
    not have to exist. Raises ``TimeoutError`` if the lock cannot be obtained
    within *timeout* seconds.
    """
    resolved = os.path.abspath(str(path))
    lock_path = resolved + ".lock"
    parent = os.path.dirname(lock_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    thread_lock = _thread_lock_for(lock_path)
    if not thread_lock.acquire(timeout=timeout):
        raise TimeoutError(
            f"Timed out after {timeout}s waiting for file lock: {lock_path}"
        )
    handle = None
    try:
        handle = open(lock_path, "a+")
        try:
            handle.seek(0)
            if handle.read(1) == "":
                handle.write("0")
                handle.flush()
        except OSError:
            pass
        _acquire_os_lock(handle, timeout=timeout, poll=poll)
        yield resolved
    finally:
        if handle is not None:
            _release_os_lock(handle)
            handle.close()
        thread_lock.release()
