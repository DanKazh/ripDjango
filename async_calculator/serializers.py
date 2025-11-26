from rest_framework import serializers
from .models import AsyncCalculationTask

class CalculationRequestSerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    resources = serializers.ListField(
        child=serializers.DictField()
    )
    token = serializers.CharField(max_length=255)

class ResourceCalculationSerializer(serializers.Serializer):
    resource_id = serializers.IntegerField()
    resource_name = serializers.CharField()
    tariff_cost = serializers.IntegerField()
    measurement = serializers.CharField()
    ratio = serializers.FloatField()
    needed_amount = serializers.IntegerField()
    calculated_cost = serializers.IntegerField(required=False)

class CalculationResultSerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    resources = serializers.ListField(
        child=ResourceCalculationSerializer()
    )
    token = serializers.CharField(max_length=255)
    total_cost = serializers.IntegerField()

class AsyncTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsyncCalculationTask
        fields = '__all__'