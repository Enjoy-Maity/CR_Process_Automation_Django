"""
sync_replica.py  —  Django management command for checking / recovering replication.

Usage:
    python manage.py sync_replica             # Print replication status
    python manage.py sync_replica --resync    # Force a full resync of replica from master
                                              # (use when replica is severely lagged / broken)
"""
import subprocess
import shutil
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path


def _find_docker_compose() -> list[str]:
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


def _compose_dir() -> Path:
    base = Path(settings.BASE_DIR)
    if (base / "docker-compose.yml").exists():
        return base
    return base.parent


class Command(BaseCommand):
    help = "Check PostgreSQL streaming replication status or force a replica resync."

    def add_arguments(self, parser):
        parser.add_argument(
            "--resync", action="store_true",
            help=(
                "Stop the replica container, wipe its volume, and let it re-clone "
                "from master. Use only if the replica is severely out of sync or broken."
            )
        )

    def handle(self, *args, **options):
        dc = _find_docker_compose()
        compose_dir = _compose_dir()

        if not dc:
            self.stderr.write(self.style.ERROR("docker / docker-compose not found in PATH."))
            sys.exit(1)

        if options["resync"]:
            self._force_resync(dc, compose_dir)
        else:
            self._print_status(dc, compose_dir)

    # ------------------------------------------------------------------
    def _print_status(self, dc, compose_dir):
        """Print pg_stat_replication and model row counts."""
        self.stdout.write(self.style.MIGRATE_HEADING("\nReplication status on db-master:"))
        r = subprocess.run(
            dc + [
                "exec", "-T", "db-master",
                "psql", "-U", "admin", "-d", "master_db", "-c",
                "SELECT application_name, state, sent_lsn, write_lsn, flush_lsn,"
                " replay_lsn, sync_state FROM pg_stat_replication;"
            ],
            cwd=str(compose_dir)
        )
        if r.returncode != 0:
            self.stderr.write(self.style.ERROR("Could not query db-master. Is it running?"))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("\nDjango model row counts:"))
        try:
            from dashboard.models import MasterCRDatabase, SelectedDateTable
            m_master = MasterCRDatabase.objects.using("default").count()
            m_replica = MasterCRDatabase.objects.using("replica").count()
            s_master = SelectedDateTable.objects.using("default").count()

            self.stdout.write(f"  MasterCRDatabase  — master: {m_master}, replica: {m_replica}")
            self.stdout.write(f"  SelectedDateTable — master: {s_master}")

            if m_master == m_replica:
                self.stdout.write(self.style.SUCCESS("  ✅ Master and replica are in sync."))
            else:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️  Row count mismatch. Replica may be lagging. "
                    f"  Difference: {abs(m_master - m_replica)} rows. "
                    f"  Run with --resync if the lag does not resolve."
                ))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Could not query Django models: {exc}"))

    # ------------------------------------------------------------------
    def _force_resync(self, dc, compose_dir):
        """Stop replica, wipe its volume, restart so it re-clones from master."""
        self.stdout.write(self.style.WARNING(
            "\n⚠️  Forcing full resync: db-replica will re-clone from db-master.\n"
            "   This is safe — master data is never touched."
        ))
        # 1. Stop and remove only the replica container
        self.stdout.write("  Stopping db-replica container...")
        subprocess.run(dc + ["rm", "-sf", "db-replica"], cwd=str(compose_dir))

        # 2. Wipe the replica volume
        self.stdout.write("  Wiping db_replica_volume...")
        volume_name = "cr_process_automation_db_replica_volume"
        subprocess.run(["docker", "volume", "rm", volume_name], check=False)

        # 3. Restart replica (init-replica.sh will clone fresh from master)
        self.stdout.write("  Starting fresh db-replica (cloning from master)...")
        subprocess.run(dc + ["up", "-d", "db-replica"], cwd=str(compose_dir))

        self.stdout.write(self.style.SUCCESS(
            "\n  Replica is re-cloning. This may take a minute for large datasets.\n"
            "  Monitor progress:  docker compose logs -f db-replica"
        ))