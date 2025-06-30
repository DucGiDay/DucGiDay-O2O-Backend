from django.urls import path
from .views import CategoryDetailAPIView, CategoryListCreateAPIView

app_name = "category"

urlpatterns = [
    path("category", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path(
        "category/<int:pk>",
        CategoryDetailAPIView.as_view(),
        name="category-detail-update-delete",
    ),
]
