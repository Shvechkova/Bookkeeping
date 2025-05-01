from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers


app_name = "client"
router = routers.DefaultRouter()
router.register(r"v1/client", view_sets.ClientViewSet)
router.register(r"v1/contract", view_sets.ContractViewSet)

urlpatterns = [
    path("", views.clients, name="clients"),
    
   
]
