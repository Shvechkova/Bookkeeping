from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers


app_name = "operation"
router = routers.DefaultRouter()
router.register(r"v1/operation", view_sets.ОperationViewSet)


urlpatterns = [
    # path("", views.service_all, name="service_all"),
    # path("<slug:slug>/", views.service_one, name="service_one"),
]
