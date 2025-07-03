from rest_framework import viewsets
from apps.bank.models import CategPercentGroupBank, GroupeOperaccount
from apps.bank.api.serializers import CategPercentGroupBankSerializer, GroupeOperaccountSerializer

class GroupeOperaccountViews(viewsets.ModelViewSet):
    queryset = GroupeOperaccount.objects.all()
    serializer_class = GroupeOperaccountSerializer
    
class CategPercentGroupBankViews(viewsets.ModelViewSet):
    queryset = CategPercentGroupBank.objects.all()
    serializer_class = CategPercentGroupBankSerializer
    http_method_names = ["get", "post", "delete", "update"]