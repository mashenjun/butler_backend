from rest_framework import serializers
from ocr_processor.utils import createLogger
from .models import (
    Person,
    ProcessedReceipt,
)

logger = createLogger(__name__);

class receiptSerializer(serializers.Serializer):
    superMarket = serializers.CharField(required=True)
    picFile = serializers.ImageField(required=True)

    def validate_picFile(self, value):
        """
        Check that the picFile type. Should be jpg
        """
        if value.content_type ==None:
            raise serializers.ValidationError("The uploaded image should be image/jpg")
        if 'jpg' not in value.content_type and 'jpeg' not in value.content_type:
            raise serializers.ValidationError("The uploaded image should be image/jpg")
        return value

class processedReceiptSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessedReceipt
        fields = '__all__'



class PersonCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = '__all__'

