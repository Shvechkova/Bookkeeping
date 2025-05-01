from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status


from apps.client.api.serializers import ClientSerializer
from apps.client.models import Client
from apps.employee.api.serializers import EmployeeSerializer
from apps.employee.models import CategoryEmployee, Employee








class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.none()
    serializer_class = EmployeeSerializer
    http_method_names = ["get", "post", "put"]

    # # менеджер клиента для заполненного
    # @action(detail=False, methods=["get"], url_path=r"(?P<pk>\d+)/manager_li")
    # def client_manager_list(self, request, pk):
    #     pk = self.kwargs["pk"]
    #     queryset = Client.objects.filter(id=pk)
    #     serializer = self.serializer_class(queryset, many=True)
    #     return Response(serializer.data)

        # список менеджеров для выбора при заполнении
    @action(detail=False, methods=["get"], url_path=r"manager_list")
    def manager_list(
        self,
        request,
    ):
        print("manager_list")
        category_employee_manager = CategoryEmployee.objects.get(name="Менеджмент")
        manager = Employee.objects.filter(employeeincategory__category=category_employee_manager.id)

        serializer = EmployeeSerializer(manager, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path=r"responsible_list")
    def responsible_list(
        self,
        request,
    ):
        print("responsible_list")
        category_employee_manager = CategoryEmployee.objects.get(name="Ответственные контрактов")
        manager = Employee.objects.filter(employeeincategory__category=category_employee_manager.id)

        serializer = EmployeeSerializer(manager, many=True)
        return Response(serializer.data)