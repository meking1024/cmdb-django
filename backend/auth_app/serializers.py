"""
Auth App Serializers
"""
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff']
        read_only_fields = ['id', 'is_active', 'is_staff']
