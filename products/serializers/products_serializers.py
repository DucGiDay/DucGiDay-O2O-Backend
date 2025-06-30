from rest_framework import serializers

from category.serializers import CategorySerializer
from ..models import Product


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = "__all__"


class CreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(help_text="ID của category")
    status = serializers.IntegerField(
        help_text="0: Ngừng bán ; 1: Đang bán; 2: Hết hàng"
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "image_url",
            "original_price",
            "discount_price",
            "final_price",
            "status",
            "category",
        ]
