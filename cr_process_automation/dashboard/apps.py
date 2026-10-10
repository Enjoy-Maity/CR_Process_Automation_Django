import logging
import threading

from django.apps import AppConfig

logger = logging.getLogger(__name__)

# Serialises the one-off NIAM reference seed across waitress/gunicorn threads.
_SEED_LOCK = threading.Lock()


# class DashboardConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'dashboard'

class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

    def ready(self):
        """
        Import signals when the app is fully loaded.
        This is the Django-recommended way to register signals.
        """
        import dashboard.signals  # noqa: F401

        # Seed NIAM reference tables (admin-editable data in niam_seed) lazily,
        # on the first database connection instead of from ready(): querying the
        # DB here triggers Django's "Accessing the database during app
        # initialization" warning, and a DB that is unreachable while booting
        # used to make the seed fail silently.
        from django.db.backends.signals import connection_created

        connection_created.connect(
            self._seed_niam_reference_tables,
            dispatch_uid="dashboard.seed_niam_reference_tables",
        )

    @staticmethod
    def _seed_niam_reference_tables(sender, connection, **kwargs):
        if connection.alias != "default":
            return
        with _SEED_LOCK:
            try:
                from dashboard.niam_seed import seed_niam_reference_tables

                seed_niam_reference_tables()
            except Exception:
                logger.exception("Failed to seed NIAM reference tables.")
