from rest_framework import serializers
from apps.bank.models import GroupeOperaccount   

class GroupeOperaccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupeOperaccount
        fields = "__all__"      