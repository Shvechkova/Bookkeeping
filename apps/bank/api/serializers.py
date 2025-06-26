from rest_framework import serializers
from apps.bank.models import CategPercentGroupBank, GroupeOperaccount   

class GroupeOperaccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupeOperaccount
        fields = "__all__"      
        
        

class CategPercentGroupBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategPercentGroupBank
        fields = "__all__"     