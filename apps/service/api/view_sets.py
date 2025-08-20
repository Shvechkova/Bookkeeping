import datetime
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from django.core.cache import cache
from apps.core.utils import error_alert, log_alert


def clear_bank_cache():
    """
    Сбрасывает кеш для всех банковских страниц
    """
    try:
        year_now = datetime.datetime.now().year
        # Сбрасываем кеш для всех банков (1, 2, 3)
        for bank_id in [1, 2, 3]:
            cache_key = f"bank_{bank_id}_context_{year_now}"
            cache.delete(cache_key)
        
       
    except Exception as e:
        location = "clear_bank_cache"
        info = f"Ошибка при сбросе кеша банковских страниц: {e}"
        error_alert(e, location, info)


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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Сбрасываем кеш после создания записи
        clear_bank_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Сбрасываем кеш после обновления записи
        clear_bank_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Сбрасываем кеш после удаления записи
        clear_bank_cache()
        return response


class SubcontractMonthViewSet(viewsets.ModelViewSet):
    queryset = SubcontractMonth.objects.all()
    serializer_class = SubcontractMonthSerializer
    http_method_names = ["get", "post", "put", "delete"]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Сбрасываем кеш после создания записи
        clear_bank_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Сбрасываем кеш после обновления записи
        clear_bank_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Сбрасываем кеш после удаления записи
        clear_bank_cache()
        return response

    @action(detail=False, methods=["get"], url_path=r"(?P<pk>\d+)/subcontract_li")
    def subcontract_list(self, request, pk):
        pk = self.kwargs["pk"]
        queryset = SubcontractMonth.objects.filter(month_bill=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path=r"(?P<pk>\d+)/subcontract_list_category_employee")
    def subcontract_list_category_employee(self, request, pk):
        # pk = self.kwargs["pk"]
        queryset = SubcontractMonth.objects.filter(month_bill=pk,category_employee__isnull = False)
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

        # Сбрасываем кеш после обновления контрактов
        clear_bank_cache()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubcontractAdvPlatformView(viewsets.ModelViewSet):
    queryset = AdvPlatform.objects.all()
    serializer_class = AdvPlatformSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Сбрасываем кеш после создания записи
        clear_bank_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Сбрасываем кеш после обновления записи
        clear_bank_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Сбрасываем кеш после удаления записи
        clear_bank_cache()
        return response

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
