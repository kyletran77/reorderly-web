from rest_framework import serializers
from .models import WaitlistEntry


class WaitlistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistEntry
        fields = ['email', 'shopify_store', 'sku_count', 'source']

    def validate_email(self, value):
        return value.lower().strip()
