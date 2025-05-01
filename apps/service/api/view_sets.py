from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status


from apps.client.api.serializers import ClientSerializer
from apps.client.models import Client
from apps.employee.api.serializers import EmployeeSerializer
from apps.employee.models import CategoryEmployee, Employee
from apps.service.api.serializers import ServiceSerializer, ServicesClientMonthlyInvoiceSerializer
from apps.service.models import Service, ServicesClientMonthlyInvoice








class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    http_method_names = ["get", "post", "put"]


class ServicesClientMonthlyInvoiceViewSet(viewsets.ModelViewSet):
    queryset = ServicesClientMonthlyInvoice.objects.all()
    serializer_class = ServicesClientMonthlyInvoiceSerializer
    http_method_names = ["get", "post", "put", 'delete']
