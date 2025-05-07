from rest_framework import viewsets
from apps.bank.models import GroupeOperaccount
from apps.bank.api.serializers import GroupeOperaccountSerializer

class GroupeOperaccountViews(viewsets.ModelViewSet):
    queryset = GroupeOperaccount.objects.all()
    serializer_class = GroupeOperaccountSerializer