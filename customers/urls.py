from django.urls import path
from .views import CustomerView, CustomrDetailView

app_name = "customers"

urlpatterns = [
    path("customers", CustomerView.as_view(), name="customer-list-create"),
    path("customers/<str:phone_number>", CustomrDetailView.as_view(), name="account-detail"),
]
