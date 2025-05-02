from multiprocessing.connection import Client
from rest_framework import serializers

from apps.employee.models import Employee
from apps.operation.models import Operation
from apps.service.models import Service, ServicesClientMonthlyInvoice


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = "__all__"
