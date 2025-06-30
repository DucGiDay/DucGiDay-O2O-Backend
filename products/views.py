# product/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from django_postgresql.services.supabase_storage_service import SupabaseStorageService
from drf_yasg.utils import swagger_auto_schema

from .models import Product
from .serializers.products_serializers import ProductSerializer, CreateUpdateSerializer


class ProductListCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Tạo product bằng form data",
        # request_body=CreateUpdateSerializer,
        # responses={201: CreateUpdateSerializer, 400: "Dữ liệu không hợp lệ"},
    )
    def post(self, request):
        serializer = CreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        supabase_service = SupabaseStorageService()
        image = request.FILES.get("image_file")
        if image:
            image_response = supabase_service.upload_file(
                bucket="img-bucket", file_name=image.name, file=image
            )
        else:
            image_response = None
        serializer.validated_data["image"] = image_response

        if serializer.is_valid():
            product = serializer.save()
            return Response({"id": product.id}, status=status.HTTP_201_CREATED)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class ProductDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
