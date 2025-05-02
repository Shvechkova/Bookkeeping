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

router = routers.DefaultRouter()
router.registry.extend(client_router.registry)
router.registry.extend(employee_router.registry)
router.registry.extend(service_router.registry)
router.registry.extend(operation_router.registry)


urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls", namespace="core")),
    path("client/", include("apps.client.urls", namespace="client")),
    path("employee/", include("apps.employee.urls", namespace="employee")),
    path("service/", include("apps.service.urls", namespace="service")),
    path("operation/", include("apps.operation.urls", namespace="operation")),
    path("api/", include(router.urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    pass
    # urlpatterns += re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # urlpatterns += re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
