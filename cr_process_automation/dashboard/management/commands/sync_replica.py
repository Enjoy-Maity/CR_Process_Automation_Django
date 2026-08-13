from django.core.management.base import BaseCommand
import sqlite3
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Syncs Master SQLite DB to Replica"

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        master_path = os.path.join(base_dir, "db.master.sqlite3")
        replica_path = os.path.join(base_dir, "db.replica.sqlite3")

        if not os.path.exists(master_path):
            self.stdout.write(self.style.ERROR("Master DB not found. Run migrations first."))
            return

        master_conn = sqlite3.connect(master_path)
        replica_conn = sqlite3.connect(replica_path)

        try:
            master_conn.backup(replica_conn)
            self.stdout.write(self.style.SUCCESS("Replica synced successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Sync failed: {e}"))
        finally:
            master_conn.close()
            replica_conn.close()   
            