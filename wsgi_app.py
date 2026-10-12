#!/usr/bin/env python3
"""Cross-platform WSGI launcher for CR Process Automation.

Runs the Django WSGI application on Windows and Linux with a single command.
The WSGI server is selected automatically for the host platform:

    * Linux / macOS (including a Linux VM or WSL2 guest running inside a
      Windows host) -> Gunicorn (gthread worker)
    * Windows                                              -> Waitress (threads)

Static files are served by WhiteNoise (see settings.py), so the app is
self-contained - an external reverse proxy (nginx) is optional. When nginx is
used we recommend binding to 127.0.0.1 (``--host 127.0.0.1``); otherwise bind
to 0.0.0.0 (the default) so clients on the network - and, for a VM/WSL guest,
the Windows host via port forwarding - can connect.

Examples
--------
    python wsgi_app.py                      # auto server, 0.0.0.0:8000
    python wsgi_app.py --migrate --collectstatic
    python wsgi_app.py --host 127.0.0.1 --port 9000   # behind nginx
    python wsgi_app.py --server waitress               # force a server

Environment variables (used as defaults): WSGI_HOST, WSGI_PORT, WSGI_WORKERS,
WSGI_THREADS, WSGI_TIMEOUT, WSGI_SERVER.
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = REPO_ROOT / "cr_process_automation"

# Make the Django project importable no matter the current working directory.
for _path in (str(REPO_ROOT), str(PROJECT_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cr_process_automation.settings")


def _env_bool(name: str, default: str = "False") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _default_workers() -> int:
    # The app keeps per-user task state in memory (RUN_REGISTRY) and runs
    # Playwright tasks in background threads, so it must run as ONE process
    # with many threads. Multiple worker processes would split that state and
    # break the dashboard polling. Override only if you move state to a shared
    # store (e.g. Redis / the database).
    return 1


def _lan_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def _print_banner(host: str, port: int, server: str) -> None:
    urls = []
    if host in ("0.0.0.0", "::", ""):
        urls.append(f"http://127.0.0.1:{port}/")
        lan = _lan_ip()
        if lan != "127.0.0.1":
            urls.append(f"http://{lan}:{port}/")
    else:
        urls.append(f"http://{host}:{port}/")

    print("=" * 68)
    print(f"  CR Process Automation  |  WSGI server: {server}")
    print(f"  Bind address: {host}:{port}")
    for url in urls:
        print(f"  Reachable at: {url}")
    print("=" * 68, flush=True)


def _prepare(migrate: bool, collectstatic: bool) -> None:
    """Run optional one-off management commands before serving."""
    import django

    django.setup()

    if migrate:
        from django.core.management import call_command

        print("[init] Applying database migrations (default)...", flush=True)
        call_command("migrate", interactive=False)
        # The replica is optional; never block startup on it.
        try:
            print("[init] Applying database migrations (replica)...", flush=True)
            call_command("migrate", database="replica", interactive=False)
        except Exception as exc:  # pragma: no cover - best effort
            print(f"[init] Skipped replica migration: {exc}", flush=True)

    if collectstatic:
        from django.core.management import call_command

        print("[init] Collecting static files...", flush=True)
        call_command("collectstatic", interactive=False, verbosity=0)


def _serve_gunicorn(host: str, port: int, workers: int, threads: int, timeout: int) -> None:
    from gunicorn.app.base import BaseApplication

    if workers > 1:
        print(
            "[warn] WSGI_WORKERS > 1 is not recommended: in-memory task state is "
            "per-process. Use a single worker with many threads.",
            flush=True,
        )

    class _Application(BaseApplication):
        def load_config(self):
            cfg = {
                "bind": f"{host}:{port}",
                "workers": workers,
                "worker_class": "gthread",
                "threads": threads,
                "timeout": timeout,
                "graceful_timeout": 30,
                "keepalive": 5,
                "preload_app": True,
                "accesslog": "-",
                "errorlog": "-",
                "loglevel": os.getenv("WSGI_LOG_LEVEL", "info"),
            }
            for key, value in cfg.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key, value)

        def load(self):
            from cr_process_automation.wsgi import application

            return application

    _Application().run()


def _serve_waitress(host: str, port: int, threads: int, timeout: int) -> None:
    from waitress import serve

    from cr_process_automation.wsgi import application

    serve(
        application,
        host=host,
        port=port,
        threads=max(threads, 1),
        channel_timeout=max(timeout, 30),
        clear_untrusted_proxy_headers=True,
    )


def _select_server(requested: str) -> str:
    requested = (requested or "auto").strip().lower()
    if requested in ("gunicorn", "waitress"):
        return requested
    if sys.platform == "win32":
        return "waitress"
    # Linux / macOS: prefer Gunicorn when available.
    try:
        import gunicorn  # noqa: F401

        return "gunicorn"
    except ImportError:
        return "waitress"


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cross-platform WSGI launcher for CR Process Automation.",
    )
    parser.add_argument("--host", default=os.getenv("WSGI_HOST", "0.0.0.0"),
                        help="Interface to bind (default: 0.0.0.0, or WSGI_HOST).")
    parser.add_argument("--port", type=int, default=_env_int("WSGI_PORT", 9000),
                        help="Port to bind (default: 9000, or WSGI_PORT).")
    parser.add_argument("--server", default=os.getenv("WSGI_SERVER", "auto"),
                        choices=["auto", "gunicorn", "waitress"],
                        help="WSGI server to use (default: auto by platform).")
    parser.add_argument("--workers", type=int, default=_env_int("WSGI_WORKERS", _default_workers()),
                        help="Gunicorn worker processes (default: 1; keep 1 for this app).")
    parser.add_argument("--threads", type=int, default=_env_int("WSGI_THREADS", 8),
                        help="Worker threads (default: 8, or WSGI_THREADS).")
    parser.add_argument("--timeout", type=int, default=_env_int("WSGI_TIMEOUT", 120),
                        help="Request/timeout seconds (default: 120, or WSGI_TIMEOUT).")
    parser.add_argument("--migrate", action="store_true",
                        default=_env_bool("WSGI_RUN_MIGRATE"),
                        help="Run 'manage.py migrate' before serving.")
    parser.add_argument("--collectstatic", action="store_true",
                        default=_env_bool("WSGI_RUN_COLLECTSTATIC"),
                        help="Run 'manage.py collectstatic' before serving.")
    parser.add_argument("--no-collectstatic", dest="collectstatic", action="store_false",
                        help="Do not collect static files before serving.")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    _prepare(migrate=args.migrate, collectstatic=args.collectstatic)

    server = _select_server(args.server)
    _print_banner(args.host, args.port, server)

    try:
        if server == "gunicorn":
            _serve_gunicorn(args.host, args.port, args.workers, args.threads, args.timeout)
        else:
            _serve_waitress(args.host, args.port, args.threads, args.timeout)
    except KeyboardInterrupt:
        print("\n[shutdown] Server stopped.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
