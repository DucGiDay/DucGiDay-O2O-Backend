from django.urls import path
from .views import ProductDetailAPIView, ProductListCreateAPIView

app_name = "products"

urlpatterns = [
    path("products", ProductListCreateAPIView.as_view(), name="products-list-create"),
    path(
        "products/<int:pk>",
        ProductDetailAPIView.as_view(),
        name="products-detail-update-delete",
    ),
]
