from multiprocessing.connection import Client
from rest_framework import serializers

from apps.employee.models import CategoryEmployee, Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class CategoryEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryEmployee
        fields = "__all__"
