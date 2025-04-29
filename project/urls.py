from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.urls import path, include, re_path
from project import settings

router = routers.DefaultRouter()
# router.registry.extend(client_router.registry)
urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path("", include("apps.core.urls", namespace="core")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    pass
    # urlpatterns += re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # urlpatterns += re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    