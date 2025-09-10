# import pymysql

# pymysql.install_as_MySQLdb()

# Условный импорт Celery для совместимости с exe
try:
    from .celery import app as celery_app
    __all__ = ['celery_app']
except (ImportError, ModuleNotFoundError):
    celery_app = None
    __all__ = []