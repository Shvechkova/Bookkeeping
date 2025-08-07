from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers


app_name = "bank"
router = routers.DefaultRouter()
router.register(r"v1/groupeoperaccount", view_sets.GroupeOperaccountViews)
router.register(r"v1/percentgroupbank", view_sets.CategPercentGroupBankViews)
router.register(r"v1/percentemployee", view_sets.PercentEmployeeViews)

urlpatterns = [
    
    
    path("inside/", views.inside, name="inside"),
    path("inside/oper_accaunt/", views.oper_accaunt, name="oper_accaunt"),
    path("inside/salary/", views.salary, name="salary"),
    path("inside/nalog/", views.nalog, name="nalog"),
    
    path("outside/", views.outside, name="outside"),
    path("outside/ooo/", views.outside_ooo, name="outside_ooo"),
    path("outside/ip/", views.outside_ip, name="outside_ip"),
    path("outside/nal/", views.outside_nal, name="outside_nal"),
    
    path("storage/", views.storage_all, name="storage"),
    path("storage/banking", views.storage_banking, name="storage_banking"),
    path("storage/bonus", views.storage_bonus, name="storage_bonus"),
    path("storage/servise", views.storage_servise, name="storage_servise"),
    
    # path("<slug:slug>/", views.service_one, name="service_one"),
]   
