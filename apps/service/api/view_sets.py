from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status


from apps.client.api.serializers import ClientSerializer
from apps.client.models import Client
from apps.employee.api.serializers import CategoryEmployeeSerializer, EmployeeSerializer
from apps.employee.models import CategoryEmployee, Employee
from apps.service.api.serializers import AdvPlatformSerializer, ServiceSerializer, ServicesClientMonthlyInvoiceSerializer, SubcontractMonthSerializer
from apps.service.models import AdvPlatform, Service, ServicesClientMonthlyInvoice, SubcontractMonth


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    http_method_names = ["get", "post", "put"]


class ServicesClientMonthlyInvoiceViewSet(viewsets.ModelViewSet):
    queryset = ServicesClientMonthlyInvoice.objects.all()
    serializer_class = ServicesClientMonthlyInvoiceSerializer
    http_method_names = ["get", "post", "put", 'delete']


class SubcontractMonthViewSet(viewsets.ModelViewSet):
    queryset = SubcontractMonth.objects.all()
    serializer_class = SubcontractMonthSerializer
    http_method_names = ["get", "post", "put", "delete"]

    @action(detail=False, methods=["get"], url_path=r"(?P<pk>\d+)/subcontract_li")
    def subcontract_list(self, request, pk):
        pk = self.kwargs["pk"]
        queryset = SubcontractMonth.objects.filter(month_bill=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["post", "put"], url_path=r"upd_subs")
    def upd_contracts(
        self,
        request,
        *args,
        **kwargs,
    ):
        data = request.data

        for contracts in data:
            id = contracts["id"]
            if id == "":
                serializer = self.serializer_class(data=contracts)
                if serializer.is_valid():
                    serializer.save()
            else:
                contract = SubcontractMonth.objects.get(pk=id)
                serializer = self.serializer_class(
                    instance=contract, data=contracts, partial=True
                )
                if serializer.is_valid():
                    serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubcontractAdvPlatformView(viewsets.ModelViewSet):
    queryset = AdvPlatform.objects.all()
    serializer_class = AdvPlatformSerializer

    @action(detail=False, methods=["get"], url_path=r"adv")
    def subcontract_platform(self, request):

        queryset = AdvPlatform.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path=r"other")
    def subcontract_employee(self, request):
        queryset = CategoryEmployee.objects.all()
        serializer_class = CategoryEmployeeSerializer
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)
