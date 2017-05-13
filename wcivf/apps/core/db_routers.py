class LoggerRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'core':
            return 'logger'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'core':
            return 'logger'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label == 'core':
            return db == 'logger'
        return None
