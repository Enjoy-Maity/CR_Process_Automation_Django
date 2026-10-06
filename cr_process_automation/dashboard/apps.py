from django.apps import AppConfig


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

        # Seed NIAM reference tables when empty (admin-editable data in niam_seed).
        try:
            from dashboard.niam_seed import seed_niam_reference_tables
            seed_niam_reference_tables()
        except Exception:
            pass
