"""
Authentication Modules
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt


class TokenAuthentication(BaseAuthentication):
    """Token 认证"""
    
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        
        if not token:
            return None
        
        # 解析 token
        try:
            payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token 已过期')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Token 无效')
        
        return None  # TODO: 从 payload 中获取用户


class SessionAuthentication(BaseAuthentication):
    """Session 认证 - Django 原生"""
    pass
