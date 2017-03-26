from rest_framework import serializers


class receiptSerializer(serializers.Serializer):
    superMarket = serializers.CharField(required=True)
    picFile = serializers.ImageField(required=True)
