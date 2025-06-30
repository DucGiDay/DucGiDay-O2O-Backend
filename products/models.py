# product/models.py
from django.db import models
from category.models import Category


class Product(models.Model):
    STATUS_CHOICES = (
        (0, "Ngừng bán"),
        (1, "Đang bán"),
        (2, "Hết hàng"),
    )

    name = models.CharField(max_length=255)
    image_url = models.CharField(max_length=500, blank=True)
    original_price = models.FloatField(default=0)
    discount_price = models.FloatField(default=0)
    final_price = models.FloatField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
