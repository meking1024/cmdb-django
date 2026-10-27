"""
Custom Django Middleware
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.http import JsonResponse
import json
import ipaddress
from urllib.parse import urlparse


class AuditLogMiddleware(MiddlewareMixin):
    """审计日志中间件"""
    
    def dispatch(self, request, get_response):
        if request.user.is_authenticated:
            # 记录请求
            request.audit_user = request.user
            request.audit_action = request.method
            request.audit_url = request.path
            request.audit_data = request.body.decode('utf-8') if request.body else None
        
        response = get_response(request)
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """请求日志中间件"""
    
    def process_request(self, request):
        # 记录请求信息
        pass
    
    def process_response(self, request, response):
        # 记录响应信息
        return response


class APIErrorHandler(MiddlewareMixin):
    """API 错误处理中间件"""
    
    def process_exception(self, request, exception):
        if request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'error': str(exception),
                'code': 'ERROR'
            }, status=500)
        return None
