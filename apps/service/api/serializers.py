from multiprocessing.connection import Client
from rest_framework import serializers

from apps.employee.models import Employee
from apps.service.models import AdvPlatform, Service, ServicesClientMonthlyInvoice, SubcontractMonth




class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

class ServicesClientMonthlyInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesClientMonthlyInvoice
        fields = "__all__"


class SubcontractMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcontractMonth
        fields = "__all__"


class AdvPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvPlatform
        fields = "__all__"
