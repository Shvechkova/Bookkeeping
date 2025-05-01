from multiprocessing.connection import Client
from rest_framework import serializers

from apps.employee.models import Employee




class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"