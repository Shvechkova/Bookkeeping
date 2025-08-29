import os

# Используем настройки деплоя, если переменная окружения не переопределена
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings_to_deploy')



