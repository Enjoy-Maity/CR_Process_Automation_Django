class CoWRouter:
    def db_for_read(self, model, **hints):
        # Force Django auth, sessions, contenttypes, and custom user model to master
        if model._meta.app_label in ['auth', 'sessions', 'contenttypes', 'admin'] or model._meta.model_name == 'usermanagement':
            return 'default'
        return 'replica'

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True if obj1._state.db in ("default", "replica") and obj2._state.db in ("default", "replica") else None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
