from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.urls import path, include, re_path
from project import settings
from apps.client.urls import router as client_router
from apps.employee.urls import router as employee_router
from apps.service.urls import router as service_router
from apps.operation.urls import router as operation_router
from apps.bank.urls import router as bank_router
import os

router = routers.DefaultRouter()
router.registry.extend(client_router.registry)
router.registry.extend(employee_router.registry)
router.registry.extend(service_router.registry)
router.registry.extend(operation_router.registry)
router.registry.extend(bank_router.registry)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls", namespace="core")),
    path("client/", include("apps.client.urls", namespace="client")),
    path("employee/", include("apps.employee.urls", namespace="employee")),
    path("service/", include("apps.service.urls", namespace="service")),
    path("operation/", include("apps.operation.urls", namespace="operation")),
    path("bank/", include("apps.bank.urls", namespace="bank")),
    
    path("api/", include(router.urls)),
    # path("api/", include(router.urls)),
]

# Добавляем URL для статики в exe
if settings.DEBUG:
    try:
        urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns
    except Exception:
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Добавляем раздачу статики для exe
    from django.views.static import serve
    print("Adding static files URL patterns for exe")
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
    print(f"Static root: {settings.STATIC_ROOT}")
    print(f"URL patterns: {urlpatterns}")

# Принудительно добавляем URL для статики если DEBUG не определён
if not hasattr(settings, 'DEBUG') or settings.DEBUG is None:
    from django.views.static import serve
    print("Forcing static files URL patterns for exe")
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
    print(f"Static root (forced): {settings.STATIC_ROOT}")

# Всегда добавляем URL для статики в exe
if not os.path.exists(os.path.join(settings.BASE_DIR, "manage.py")):
    from django.views.static import serve
    print("Always adding static files URL patterns for exe")
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
    print(f"Static root (always): {settings.STATIC_ROOT}")
    print(f"Static URL: {settings.STATIC_URL}")
