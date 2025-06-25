from rest_framework import serializers
from django.db.models import Q

from roles.models import Role
from roles.serializers.response_serializers import RoleResponseSerializer
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    roles = RoleResponseSerializer(
        many=True
    )  # Sử dụng RoleResponseSerializer để trả 1 số thông tin roles

    class Meta:
        model = Account
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}  # Không trả về mật khẩu trong response
        }


class UpdateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = fields = ["username", "full_name", "email", "avatar"]


class RegisterSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Danh sách mã code của các role (list of strings)",
    )
    class Meta:
        model = Account
        fields = ["username", "full_name", "email", "password", "roles"]
        extra_kwargs = {
            "password": {"write_only": True}  # Không trả về mật khẩu trong response
        }

    def create(self, validated_data):
        # Lấy danh sách role_codes từ validated_data
        role_codes = validated_data.pop("roles", [])
        account = super().create(validated_data)
        print(validated_data)

        # Gắn các roles cho account
        user_role, created = Role.objects.get_or_create(
            code="USER", defaults={"roleName": "Default"}
        )
        roles = Role.objects.filter(Q(code__in=role_codes) | Q(code="USER"))
        account.roles.set(roles)

        return account
