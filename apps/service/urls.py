from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers


app_name = "service"
router = routers.DefaultRouter()
router.register(r"v1/service", view_sets.ServiceViewSet)
router.register(r"v1/service_month_client", view_sets.ServicesClientMonthlyInvoiceViewSet)
router.register(r"v1/subcontract", view_sets.SubcontractMonthViewSet)
router.register(r"v1/adv-platform", view_sets.SubcontractAdvPlatformView)

urlpatterns = [
    path("", views.service_all, name="service_all"),
    path("<slug:slug>/",views.service_one,name="service_one"),
    
   
]
