
from django.urls import include, path



from . import views

app_name = 'core'

urlpatterns = [
    path("", views.index, name="index"),
    path("test/", views.test, name="test"),
    path("clear/", views.cache_delete, name="cache_delete"),
    
]