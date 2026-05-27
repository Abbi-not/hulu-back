"""
apps/market/serializers.py
"""

from rest_framework import serializers
from .models import Commodity, MarketPrice


class MarketPriceSerializer(serializers.ModelSerializer):
    name          = serializers.CharField(source="commodity.name")
    unit          = serializers.CharField(source="commodity.unit")
    icon          = serializers.CharField(source="commodity.icon")
    changePercent = serializers.SerializerMethodField()

    class Meta:
        model  = MarketPrice
        fields = [
            "name",
            "unit",
            "icon",
            "price",
            "change",
            "changePercent",
            "market",
            "country",
            "recorded_at",
            "source",
        ]

    def get_changePercent(self, obj) -> float:
        return obj.change_percent