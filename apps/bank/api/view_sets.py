from rest_framework import viewsets
from apps.bank.models import CategPercentGroupBank, GroupeOperaccount
from apps.bank.api.serializers import CategPercentGroupBankSerializer, GroupeOperaccountSerializer
from rest_framework.response import Response

class GroupeOperaccountViews(viewsets.ModelViewSet):
    queryset = GroupeOperaccount.objects.all()
    serializer_class = GroupeOperaccountSerializer
    
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
            self.perform_create(serializer)
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
            self.perform_update(serializer)
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)