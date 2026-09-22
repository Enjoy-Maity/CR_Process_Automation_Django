import subprocess
import sys
from pathlib import Path
from django.conf import settings
from django.core.management.commands.runserver import Command as BaseRunserverCommand

class Command(BaseRunserverCommand):
    help = "Starts PostgreSQL containers, runs the Django development server, and tears down containers on exit."

    def handle(self, *args, **options):
        # Locate the project root folder (where docker-compose.yml lives, one level above BASE_DIR)
        project_root = Path(settings.BASE_DIR).parent

        print("🚀 Starting PostgreSQL Docker containers...")
        try:
            subprocess.run(["docker-compose", "up", "-d"], cwd=project_root, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start Docker containers: {e}")
            sys.exit(1)

        try:
            # Pass all arguments (e.g., port numbers like 9000) to Django's native runserver
            super().handle(*args, **options)
        finally:
            print("\n📦 Stopping PostgreSQL Docker containers...")
            subprocess.run(["docker-compose", "down"], cwd=project_root)
            print("👋 Clean shutdown complete.")