from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from math import ceil
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404


from django_postgresql.common.helpers import str_to_bool
from django_postgresql.services.supabase_storage_service import SupabaseStorageService
from roles.models import Role
from .models import Account
from .serializers import AccountSerializer, RegisterSerializer, UpdateAccountSerializer
from auth_custom.decorators import check_role
from .swagger_schemas import (
    PAGE_PARAMETER,
    LIMIT_PARAMETER,
    KEYWORD_PARAMETER,
    ASSIGN_ROLE_BODY,
)


class AccountView(APIView):
    """
    API để xử lý danh sách tài khoản (GET) và tạo tài khoản mới (POST).
    """

    @swagger_auto_schema(
        operation_description="Lấy danh sách các tài khoản",
        manual_parameters=[PAGE_PARAMETER, LIMIT_PARAMETER, KEYWORD_PARAMETER],
        # responses={200: "Danh sách tài khoản trả về thành công"},
    )
    def get(self, request):
        page = request.query_params.get("page", 1)
        limit = request.query_params.get("limit", 10)
        keyword = request.query_params.get("keyword", None)
        try:
            page = int(page)
            limit = int(limit)
        except ValueError:
            return Response(
                {"error": "Page and limit must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        accounts = Account.objects.all()
        # Lọc theo keyword nếu có
        if keyword:
            accounts = accounts.filter(username__icontains=keyword)

        # Tính toán phân trang
        total_items = accounts.count()
        total_pages = ceil(total_items / limit)
        start = (page - 1) * limit
        end = start + limit
        paginated_accounts = accounts[start:end]
        serializer = AccountSerializer(paginated_accounts, many=True)
        return Response(
            {
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": limit,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Đăng ký",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Tên đăng nhập"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Mật khẩu"
                ),
                "full_name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Họ và tên"
                ),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                "roles": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Roles",
                ),
            },
            required=["username", "password"],
        ),
        # responses={200: openapi.Response(description='Đăng nhập thành công')}
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if Account.objects.filter(username=username).exists():
                return Response(
                    {"error": "User with this username already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Account.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AccountDetailView(APIView):
    """
    API để xử lý chi tiết, cập nhật và xóa tài khoản.
    """

    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        account = get_object_or_404(Account, pk=pk)
        serializer = AccountSerializer(
            account,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            account = get_object_or_404(Account, pk=pk)
            serializer = UpdateAccountSerializer(
                account, data=request.data, partial=True
            )

            # Lấy danh sách role_codes từ request
            role_codes = request.data.getlist("roles", [])
            if not isinstance(role_codes, list):
                return Response(
                    {"error": "role_codes must be a list."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Lấy các role từ database
            roles = Role.objects.filter(code__in=role_codes)
            if not roles.exists():
                return Response(
                    {"error": "One or more roles do not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Gắn các role cho người dùng
            account.roles.set(roles)

            avatar = request.FILES.get("avatar_file")
            is_delete_ava = str_to_bool(request.data.get("is_delete_ava", False))
            if serializer.is_valid():
                supabase_service = SupabaseStorageService()
                avatar_data = {}
                if account.avatar and (avatar or is_delete_ava):
                    path = [account.avatar.get("path")]
                    supabase_service.delete_file(bucket="img-bucket", path=path)
                    # serializer.validated_data["avatar"] = {}
                if avatar:
                    # Đẩy ảnh lên supabase, gán url và path vào avatar
                    avatar_response = supabase_service.upload_file(
                        bucket="img-bucket", file_name=avatar.name, file=avatar
                    )

                    # serializer.validated_data["avatar"] = avatar_response
                    avatar_data = avatar_response

                if avatar_data is not None:
                    serializer.save(avatar=avatar_data)
                else:
                    serializer.save()
                response_data = dict(serializer.data)
                response_data["roles"] = [
                    role.code for role in account.roles.all()
                ]
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Http404:
            return Response(
                {"error": "Account not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # def put(self, request, pk):
    #     account = get_object_or_404(Account, pk=pk)
    #     serializer = AccountSerializer(account, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        account = get_object_or_404(Account, pk=pk)
        account.delete()
        return Response(
            {"message": "Account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@method_decorator(check_role(["ADMIN", "SUPER_USER"]), name="dispatch")
class AssignRoleView(APIView):
    """
    API để gắn role cho người dùng.
    """

    @swagger_auto_schema(
        operation_description="API để gắn role cho người dùng.",
        request_body=ASSIGN_ROLE_BODY,
    )
    def put(self, request, pk):
        # Lấy người dùng dựa trên pk
        account = get_object_or_404(Account, pk=pk)

        # Lấy danh sách role_codes từ request
        role_codes = request.data.get("role_codes", [])
        if not isinstance(role_codes, list):
            return Response(
                {"error": "role_codes must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Lấy các role từ database
        roles = Role.objects.filter(code__in=role_codes)
        if not roles.exists():
            return Response(
                {"error": "One or more roles do not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Gắn các role cho người dùng
        # account.roles.add(*roles)
        account.roles.set(roles)

        # Serialize và trả về thông tin người dùng
        serializer = AccountSerializer(account)
        return Response(
            {
                "id": account.id,
                "username": account.username,
                "full_name": account.full_name,
                "roles": serializer.data.get("roles"),
                "created_at": account.created_at,
                "updated_at": account.updated_at,
            },
            status=status.HTTP_200_OK,
        )
