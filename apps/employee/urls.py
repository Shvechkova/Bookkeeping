
from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers


app_name = "employee"
router = routers.DefaultRouter()
router.register(r"v1/employee", view_sets.EmployeeViewSet)

urlpatterns = [
    # path("", views.clients, name="clients"),
    
   
]
