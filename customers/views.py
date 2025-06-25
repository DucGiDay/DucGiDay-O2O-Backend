from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from customers.serializers.customers_serializers import CustomerSerializer
from .models import Customer

# Create your views here.
class CustomerView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Tạo customer mới",
        request_body=CustomerSerializer,
        responses={201: CustomerSerializer, 400: "Dữ liệu không hợp lệ"},
    )
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomrDetailView(APIView):
    def get(self, request, phone_number):
        customer = get_object_or_404(Customer, phone_number=phone_number)
        serializer = CustomerSerializer(
            customer,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, phone_number):
        customer = get_object_or_404(Customer, phone_number=phone_number)
        customer.delete()
        return Response(
            {"message": "Customer deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )