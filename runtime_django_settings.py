import os

# Установить модуль настроек Django до загрузки хука PyInstaller
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')


