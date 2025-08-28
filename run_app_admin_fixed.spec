# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
import os
import sys

# Настраиваем Django для корректного сбора статики
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Импортируем Django только если он доступен
try:
    import django
    django.setup()
    print("Django setup completed successfully")
except Exception as e:
    print(f"Django setup failed: {e}")

datas = [
    ('project/settings.py', 'project'),
    ('project/urls.py', 'project'),
    ('project/wsgi.py', 'project'),
    ('.env', '.'),
    ('apps/bank/templates', 'apps/bank/templates'),
    ('apps/client/templates', 'apps/client/templates'),
    ('apps/core/templates', 'apps/core/templates'),
    ('apps/service/templates', 'apps/service/templates'),
    # Копируем содержимое папок статики, а не сами папки
    ('apps/bank/static/bank', 'django_static/bank'),
    ('apps/client/static/client', 'django_static/client'),
    ('apps/core/static/core', 'django_static/core'),
    ('apps/service/static/service', 'django_static/service'),
]

binaries = []
hiddenimports = [
    'environ', 'pymysql', 'MySQLdb', 
    'project.urls', 'project.wsgi', 
    'apps.bank', 'apps.bank.admin', 'apps.bank.apps', 'apps.bank.models', 'apps.bank.urls', 'apps.bank.views', 'apps.bank.api', 'apps.bank.api.serializers', 'apps.bank.api.view_sets', 'apps.bank.templatetags', 'apps.bank.templatetags.dict_filters', 
    'apps.client', 'apps.client.admin', 'apps.client.apps', 'apps.client.models', 'apps.client.urls', 'apps.client.views', 'apps.client.api', 'apps.client.api.serializers', 'apps.client.api.view_sets', 
    'apps.core', 'apps.core.admin', 'apps.core.apps', 'apps.core.models', 'apps.core.urls', 'apps.core.views', 'apps.core.middleware', 'apps.core.templatetags', 'apps.core.templatetags.category_service', 'apps.core.templatetags.convert_list_to_string', 'apps.core.templatetags.dict_extras', 'apps.core.templatetags.format_filters', 'apps.core.templatetags.suborders_extras', 
    'apps.employee', 'apps.employee.admin', 'apps.employee.apps', 'apps.employee.models', 'apps.employee.urls', 'apps.employee.views', 'apps.employee.api', 'apps.employee.api.serializers', 'apps.employee.api.view_sets', 
    'apps.operation', 'apps.operation.admin', 'apps.operation.apps', 'apps.operation.models', 'apps.operation.urls', 'apps.operation.views', 'apps.operation.api', 'apps.operation.api.serializers', 'apps.operation.api.view_sets', 
    'apps.service', 'apps.service.admin', 'apps.service.apps', 'apps.service.models', 'apps.service.urls', 'apps.service.views', 'apps.service.api', 'apps.service.api.serializers', 'apps.service.api.view_sets'
]

# Собираем статику Django админки вручную
try:
    import django
    django_path = os.path.dirname(django.__file__)
    admin_static_path = os.path.join(django_path, 'contrib', 'admin', 'static', 'admin')
    
    if os.path.exists(admin_static_path):
        datas.append((admin_static_path, 'django_static/admin'))
        print(f"✅ Admin static path added: {admin_static_path}")
        
        # Проверяем содержимое папки админки
        admin_files = []
        for root, dirs, files in os.walk(admin_static_path):
            for file in files:
                rel_path = os.path.relpath(root, admin_static_path)
                if rel_path == '.':
                    admin_files.append(file)
                else:
                    admin_files.append(os.path.join(rel_path, file))
        
        print(f"📁 Found {len(admin_files)} admin static files")
        if admin_files:
            print(f"📋 Sample files: {admin_files[:5]}")
    else:
        print(f"❌ Admin static path not found: {admin_static_path}")
        
        # Альтернативный поиск
        possible_paths = [
            os.path.join(django_path, 'contrib', 'admin', 'static', 'admin'),
            os.path.join(django_path, 'contrib', 'admin', 'static'),
            os.path.join(django_path, 'admin', 'static'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"🔍 Found alternative admin path: {path}")
                datas.append((path, 'django_static/admin'))
                break
                
except Exception as e:
    print(f"⚠️ Error collecting admin static: {e}")

# Собираем все данные Django
print("🔄 Collecting Django data...")
tmp_ret = collect_all('django')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]
print(f"📦 Django: {len(tmp_ret[0])} data files, {len(tmp_ret[1])} binaries, {len(tmp_ret[2])} imports")

# Собираем все данные DRF
print("🔄 Collecting DRF data...")
tmp_ret = collect_all('rest_framework')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]
print(f"📦 DRF: {len(tmp_ret[0])} data files, {len(tmp_ret[1])} binaries, {len(tmp_ret[2])} imports")

# Собираем данные приложений
print("🔄 Collecting apps data...")
datas += collect_data_files('apps')
hiddenimports += collect_submodules('apps')
print(f"📦 Apps: {len([d for d in datas if 'apps' in str(d)])} data files")

print(f"🎯 Total datas: {len(datas)}")
print(f"🎯 Total hiddenimports: {len(hiddenimports)}")

a = Analysis(
    ['run_app.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['pyi_hooks'],
    hooksconfig={},
    runtime_hooks=['runtime_django_settings.py'],
    excludes=['debug_toolbar', 'celery', 'redis', 'psycopg2'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run_app_admin_fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
