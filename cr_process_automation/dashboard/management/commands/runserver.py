import shutil
import subprocess
import sys
from pathlib import Path
from django.conf import settings
from django.core.management.commands.runserver import Command as BaseRunserverCommand


def _find_docker_compose() -> list[str]:
    """Detect whether 'docker compose' (v2 plugin) or 'docker-compose' is available."""
    if shutil.which("docker"):
        r = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    return []


def _locate_compose_dir() -> Path:
    """Find the directory that contains docker-compose.yml."""
    base = Path(settings.BASE_DIR)
    if (base / "docker-compose.yml").exists():
        return base
    if (base.parent / "docker-compose.yml").exists():
        return base.parent
    return base


class Command(BaseRunserverCommand):
    help = (
        "Starts the PostgreSQL streaming-replication cluster (db-master + db-replica), "
        "runs the Django development server, then stops the containers on exit."
    )

    def handle(self, *args, **options):
        dc = _find_docker_compose()
        compose_dir = _locate_compose_dir()

        if not dc:
            self.stderr.write(
                self.style.ERROR(
                    "docker / docker-compose not found in PATH. "
                    "Please install Docker Desktop (Windows) or Docker / Podman (Linux)."
                )
            )
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("🚀 Starting PostgreSQL containers..."))
        try:
            subprocess.run(
                dc + ["up", "-d"],
                cwd=str(compose_dir),
                check=True
            )
        except subprocess.CalledProcessError as exc:
            self.stderr.write(self.style.ERROR(f"❌ Failed to start containers: {exc}"))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("⏳ Waiting for db-master to be ready..."))
        self._wait_for_service(dc, compose_dir, "db-master",
                               ["pg_isready", "-U", "admin", "-d", "master_db"])

        self.stdout.write(self.style.SUCCESS("⏳ Waiting for db-replica to connect..."))
        self._wait_for_replica(dc, compose_dir)

        try:
            super().handle(*args, **options)
        finally:
            self.stdout.write(self.style.WARNING("\n📦 Stopping PostgreSQL containers (data preserved)..."))
            subprocess.run(
                dc + ["down", "--remove-orphans"],
                cwd=str(compose_dir)
            )
            self.stdout.write(self.style.SUCCESS("👋 Clean shutdown complete. Data is safe in Docker named volumes."))

    def _wait_for_service(self, dc, compose_dir, service, cmd,
                          timeout=90, interval=3):
        """Poll a command inside a container until it exits 0."""
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            r = subprocess.run(
                dc + ["exec", "-T", service] + cmd,
                capture_output=True, cwd=str(compose_dir)
            )
            if r.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f"  ✅ {service} is ready."))
                return
            time.sleep(interval)
        self.stderr.write(self.style.ERROR(f"❌ {service} did not become ready within {timeout}s."))
        sys.exit(1)

    def _wait_for_replica(self, dc, compose_dir, timeout=120, interval=3):
        """Wait until db-replica appears as a streaming standby in pg_stat_replication."""
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            r = subprocess.run(
                dc + [
                    "exec", "-T", "db-master",
                    "psql", "-U", "admin", "-d", "master_db",
                    "-tAc",
                    "SELECT count(*) FROM pg_stat_replication WHERE state='streaming';"
                ],
                capture_output=True, text=True, cwd=str(compose_dir)
            )
            if r.returncode == 0 and r.stdout.strip() == "1":
                self.stdout.write(self.style.SUCCESS("  ✅ db-replica is streaming."))
                return
            time.sleep(interval)
        self.stdout.write(self.style.WARNING(
            "  ⚠️  db-replica standby not confirmed yet "
            "(may still be cloning — check 'docker compose logs db-replica')."
        ))