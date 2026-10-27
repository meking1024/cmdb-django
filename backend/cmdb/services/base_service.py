"""
Base Service Module
"""
from typing import Dict, Any, Optional


class BaseService:
    """基础服务类"""
    
    @staticmethod
    def success(data: Any = None, message: str = '操作成功') -> Dict[str, Any]:
        """返回成功响应"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return response
    
    @staticmethod
    def error(message: str = '操作失败', code: str = 'ERROR') -> Dict[str, Any]:
        """返回错误响应"""
        return {
            'success': False,
            'message': message,
            'code': code
        }
    
    @staticmethod
    def validate_required(data: Dict[str, Any], fields: list) -> Optional[Dict[str, Any]]:
        """验证必填字段"""
        for field in fields:
            if field not in data or data[field] is None or data[field] == '':
                return BaseService.error(f'字段 {field} 不能为空')
        return None
