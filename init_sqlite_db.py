#!/usr/bin/env python
"""
Скрипт для инициализации SQLite базы данных
Используйте для создания базы данных с тестовыми данными
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
os.environ['USE_SQLITE'] = 'true'  # Принудительно используем SQLite

# Инициализация Django
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User

def init_database():
    """Инициализация базы данных"""
    print("🚀 Инициализация SQLite базы данных...")
    
    try:
        # Создаем миграции
        print("📝 Создание миграций...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Применяем миграции
        print("🔄 Применение миграций...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Создаем суперпользователя
        print("👤 Создание суперпользователя...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("✅ Суперпользователь создан:")
            print("   Логин: admin")
            print("   Пароль: admin123")
        else:
            print("ℹ️  Суперпользователь уже существует")
        
        print("🎉 База данных успешно инициализирована!")
        print("📁 Файл базы данных: db.sqlite3")
        print("🔑 Войдите в админку: http://127.0.0.1:8000/admin/")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        sys.exit(1)

if __name__ == '__main__':
    init_database()
