#!/usr/bin/env python
"""
Скрипт для проверки статики Django админки
"""

import os
import sys
import django

def check_admin_static():
    """Проверяем доступность статики админки"""
    print("🔍 Проверка статики Django админки...")
    
    try:
        # Настраиваем Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
        django.setup()
        print("✅ Django настроен успешно")
        
        # Получаем путь к Django
        django_path = os.path.dirname(django.__file__)
        print(f"📁 Django path: {django_path}")
        
        # Проверяем различные возможные пути к статике админки
        possible_paths = [
            os.path.join(django_path, 'contrib', 'admin', 'static', 'admin'),
            os.path.join(django_path, 'contrib', 'admin', 'static'),
            os.path.join(django_path, 'admin', 'static'),
        ]
        
        for path in possible_paths:
            print(f"\n🔍 Проверяем путь: {path}")
            if os.path.exists(path):
                print(f"✅ Путь существует!")
                
                # Считаем файлы
                file_count = 0
                css_files = []
                js_files = []
                
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_count += 1
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, path)
                        
                        if file.endswith('.css'):
                            css_files.append(rel_path)
                        elif file.endswith('.js'):
                            js_files.append(rel_path)
                
                print(f"📊 Всего файлов: {file_count}")
                print(f"🎨 CSS файлов: {len(css_files)}")
                print(f"⚡ JS файлов: {len(js_files)}")
                
                if css_files:
                    print(f"📋 Примеры CSS файлов: {css_files[:5]}")
                if js_files:
                    print(f"📋 Примеры JS файлов: {js_files[:5]}")
                
                # Проверяем ключевые файлы
                key_files = ['css/base.css', 'css/dashboard.css', 'js/core.js', 'js/admin/RelatedObjectLookups.js']
                for key_file in key_files:
                    full_path = os.path.join(path, key_file)
                    if os.path.exists(full_path):
                        print(f"✅ Ключевой файл найден: {key_file}")
                    else:
                        print(f"❌ Ключевой файл отсутствует: {key_file}")
                
                return path
            else:
                print(f"❌ Путь не существует")
        
        print("\n❌ Не удалось найти статику админки!")
        return None
        
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return None

def check_venv_django():
    """Проверяем Django в виртуальном окружении"""
    print("\n🔍 Проверка Django в виртуальном окружении...")
    
    try:
        # Проверяем установленные пакеты
        import pkg_resources
        django_version = pkg_resources.get_distribution('django').version
        print(f"📦 Django версия: {django_version}")
        
        # Проверяем путь к Django
        django_path = os.path.dirname(django.__file__)
        print(f"📁 Django path: {django_path}")
        
        # Проверяем структуру папок
        contrib_path = os.path.join(django_path, 'contrib')
        if os.path.exists(contrib_path):
            print(f"✅ Папка contrib найдена: {contrib_path}")
            
            contrib_contents = os.listdir(contrib_path)
            print(f"📋 Содержимое contrib: {contrib_contents}")
            
            admin_path = os.path.join(contrib_path, 'admin')
            if os.path.exists(admin_path):
                print(f"✅ Папка admin найдена: {admin_path}")
                
                admin_contents = os.listdir(admin_path)
                print(f"📋 Содержимое admin: {admin_contents}")
                
                static_path = os.path.join(admin_path, 'static')
                if os.path.exists(static_path):
                    print(f"✅ Папка static найдена: {static_path}")
                    
                    static_contents = os.listdir(static_path)
                    print(f"📋 Содержимое static: {static_contents}")
                    
                    admin_static_path = os.path.join(static_path, 'admin')
                    if os.path.exists(admin_static_path):
                        print(f"✅ Папка admin/static/admin найдена: {admin_static_path}")
                        return True
                    else:
                        print(f"❌ Папка admin/static/admin не найдена")
                else:
                    print(f"❌ Папка static не найдена")
            else:
                print(f"❌ Папка admin не найдена")
        else:
            print(f"❌ Папка contrib не найдена")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
    
    return False

if __name__ == '__main__':
    print("🚀 Запуск проверки статики Django админки...")
    
    # Проверяем в текущем окружении
    admin_path = check_admin_static()
    
    # Проверяем структуру виртуального окружения
    venv_ok = check_venv_django()
    
    print("\n" + "="*50)
    if admin_path and venv_ok:
        print("🎉 Статика админки доступна и готова к сборке!")
        print(f"📁 Путь: {admin_path}")
    else:
        print("❌ Проблемы с доступностью статики админки")
        print("💡 Рекомендации:")
        print("   1. Убедитесь, что Django установлен в виртуальном окружении")
        print("   2. Проверьте, что виртуальное окружение активировано")
        print("   3. Попробуйте переустановить Django: pip install --force-reinstall django")
