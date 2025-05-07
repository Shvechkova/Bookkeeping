from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
# from .api import view_sets
from rest_framework import routers


app_name = "bank"
router = routers.DefaultRouter()
# router.register(r"v1/operation", view_sets.ОperationViewSet)


urlpatterns = [
    path("storage/", views.storage, name="storage"),
    path("inside/", views.inside, name="inside"),
    path("inside/oper_accaunt/", views.oper_accaunt, name="oper_accaunt"),
    path("inside/salary/", views.salary, name="salary"),
    # path("<slug:slug>/", views.service_one, name="service_one"),
]
