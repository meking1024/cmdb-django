"""
Custom Exception Handling
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    response = exception_handler(exc, context)
    
    if response is not None:
        error_data = {
            'success': False,
            'message': response.data.get('detail', '请求失败'),
            'code': response.status_code
        }
        return Response(error_data, status=response.status_code)
    
    return Response({
        'success': False,
        'message': '服务器内部错误',
        'code': 500
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
