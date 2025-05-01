from multiprocessing.connection import Client
from rest_framework import serializers

from apps.employee.models import Employee
from apps.service.models import Service, ServicesClientMonthlyInvoice




class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"
        
class ServicesClientMonthlyInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesClientMonthlyInvoice
        fields = "__all__"