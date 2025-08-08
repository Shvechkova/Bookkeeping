import datetime
from rest_framework import viewsets
from apps.bank.models import CategPercentGroupBank, GroupeOperaccount, PercentEmployee
from apps.bank.api.serializers import CategPercentGroupBankSerializer, GroupeOperaccountSerializer, PercentEmployeeSerializer
from rest_framework.response import Response
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
        
        location = "clear_bank_cache"
        info = f"Кеш банковских страниц сброшен для года {year_now}"
        log_alert(location, info)
    except Exception as e:
        location = "clear_bank_cache"
        info = f"Ошибка при сбросе кеша банковских страниц: {e}"
        error_alert(e, location, info)


class GroupeOperaccountViews(viewsets.ModelViewSet):
    queryset = GroupeOperaccount.objects.all()
    serializer_class = GroupeOperaccountSerializer
    
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


class PercentEmployeeViews(viewsets.ModelViewSet):
    queryset = PercentEmployee.objects.all()
    serializer_class = PercentEmployeeSerializer
    http_method_names = ["get", "post", "delete", "update"]


class CategPercentGroupBankViews(viewsets.ModelViewSet):
    queryset = CategPercentGroupBank.objects.all()
    serializer_class = CategPercentGroupBankSerializer
    http_method_names = ["get", "post", "delete", "update"]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # Проверяем и обрабатываем category_between
        if 'category_between' in data and data['category_between'] not in [None, '', 'null', 'None']:
            data["in_need_operations"] = True
        else:
            data['category_between'] = None
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            response = self.perform_create(serializer)
            # Сбрасываем кеш после создания записи
            clear_bank_cache()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        if 'category_between' in data and data['category_between'] not in [None, '', 'null', 'None']:
            data["in_need_operations"] = True
        else:
            data['category_between'] = None
        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            response = self.perform_update(serializer)
            # Сбрасываем кеш после обновления записи
            clear_bank_cache()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Сбрасываем кеш после удаления записи
        clear_bank_cache()
        return response