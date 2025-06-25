from django.db import models


# Create your models here.
class Customer(models.Model):
    id = models.AutoField(primary_key=True)  # ID duy nhất
    created_at = models.DateTimeField(auto_now_add=True)  # Tự động thêm ngày tạo
    updated_at = models.DateTimeField(auto_now=True)  # Tự động cập nhật ngày sửa
    phone_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(
        max_length=255, null=True, blank=True
    )  # Tên đầy đủ
    points = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.customer_name
