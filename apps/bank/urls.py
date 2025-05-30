from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers


app_name = "bank"
router = routers.DefaultRouter()
router.register(r"v1/groupeoperaccount", view_sets.GroupeOperaccountViews)


urlpatterns = [
    path("storage/", views.storage, name="storage"),
    
    path("inside/", views.inside, name="inside"),
    path("inside/oper_accaunt/", views.oper_accaunt, name="oper_accaunt"),
    path("inside/salary/", views.salary, name="salary"),
    path("inside/nalog/", views.nalog, name="nalog"),
    
    path("outside/", views.outside, name="outside"),
    path("outside/ooo/", views.outside_ooo, name="outside_ooo"),
    path("outside/ip/", views.outside_ip, name="outside_ip"),
    path("outside/nal/", views.outside_nal, name="outside_nal"),
    
    # path("<slug:slug>/", views.service_one, name="service_one"),
]
