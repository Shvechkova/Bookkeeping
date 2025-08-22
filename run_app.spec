# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

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
hiddenimports = ['environ', 'pymysql', 'MySQLdb', 'project.urls', 'project.wsgi', 'apps.bank', 'apps.bank.admin', 'apps.bank.apps', 'apps.bank.models', 'apps.bank.urls', 'apps.bank.views', 'apps.bank.api', 'apps.bank.api.serializers', 'apps.bank.api.view_sets', 'apps.bank.templatetags', 'apps.bank.templatetags.dict_filters', 'apps.client', 'apps.client.admin', 'apps.client.apps', 'apps.client.models', 'apps.client.urls', 'apps.client.views', 'apps.client.api', 'apps.client.api.serializers', 'apps.client.api.view_sets', 'apps.core', 'apps.core.admin', 'apps.core.apps', 'apps.core.models', 'apps.core.urls', 'apps.core.views', 'apps.core.middleware', 'apps.core.templatetags', 'apps.core.templatetags.category_service', 'apps.core.templatetags.convert_list_to_string', 'apps.core.templatetags.dict_extras', 'apps.core.templatetags.format_filters', 'apps.core.templatetags.suborders_extras', 'apps.employee', 'apps.employee.admin', 'apps.employee.apps', 'apps.employee.models', 'apps.employee.urls', 'apps.employee.views', 'apps.employee.api', 'apps.employee.api.serializers', 'apps.employee.api.view_sets', 'apps.operation', 'apps.operation.admin', 'apps.operation.apps', 'apps.operation.models', 'apps.operation.urls', 'apps.operation.views', 'apps.operation.api', 'apps.operation.api.serializers', 'apps.operation.api.view_sets', 'apps.service', 'apps.service.admin', 'apps.service.apps', 'apps.service.models', 'apps.service.urls', 'apps.service.views', 'apps.service.api', 'apps.service.api.serializers', 'apps.service.api.view_sets']
datas += collect_data_files('django.contrib.admin')
datas += collect_data_files('apps')
hiddenimports += collect_submodules('apps')
tmp_ret = collect_all('django')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rest_framework')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['run_app.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['pyi_hooks'],
    hooksconfig={},
    runtime_hooks=['runtime_django_settings.py'],
    excludes=['debug_toolbar', 'celery', 'redis'],
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
    name='run_app',
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
