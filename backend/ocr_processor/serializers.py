from rest_framework import serializers


class receiptSerializer(serializers.Serializer):
    superMarket = serializers.CharField(required=True)
    picFile = serializers.ImageField(required=True)

    def validate_picFile(self, value):
        """
        Check that the picFile type. Should be jpg
        """
        if 'jpg' not in value.content_type:
            raise serializers.ValidationError("The uploaded image should be image/jpg")
        return value



