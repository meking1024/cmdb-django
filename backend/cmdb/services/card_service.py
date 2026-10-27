"""
Card Service - Business Logic for Card Operations
"""
from typing import List, Dict, Any
from django.db import transaction
from .base_service import BaseService


class CardService(BaseService):
    """Card Service Layer"""
    
    @staticmethod
    def create_card(clazz_id: int, data: Dict[str, Any], user) -> Dict[str, Any]:
        """创建新的配置实例"""
        from cmdb.models import Card, CardHistory, Attribute

        with transaction.atomic():
            # 创建卡片
            card = Card.objects.create(
                clazz_id=clazz_id,
                code=data.get('code'),
                created_by=user,
                updated_by=user
            )

            # 保存属性值（EAV 模型：通过 CardLookup 关联 Attribute）
            for attr_name, attr_value in data.get('attributes', {}).items():
                try:
                    attribute = Attribute.objects.get(clazz_id=clazz_id, name=attr_name)
                except Attribute.DoesNotExist:
                    raise ValueError(f'属性 {attr_name} 不存在于该类中')
                card.lookups.create(
                    attribute=attribute,
                    value=str(attr_value)
                )

            # 创建历史记录
            CardHistory.objects.create(
                card=card,
                version=1,
                content=data,
                modified_by=user
            )

        return {
            'success': True,
            'data': card.to_dict()
        }
    
    @staticmethod
    def get_card_list(clazz_id: int = None, page: int = 1, page_size: int = 20, 
                      search: str = None) -> Dict[str, Any]:
        """获取卡片列表"""
        from cmdb.models import Card
        
        queryset = Card.objects.filter(is_active=True)
        
        if clazz_id:
            queryset = queryset.filter(clazz_id=clazz_id)
        
        if search:
            queryset = queryset.filter(code__icontains=search)
        
        total = queryset.count()
        cards = queryset.order_by('-created_at')[
            (page - 1) * page_size: page * page_size
        ]
        
        return {
            'success': True,
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'items': [card.to_dict() for card in cards]
            }
        }
    
    @staticmethod
    def get_card_by_id(card_id: int) -> Dict[str, Any]:
        """根据ID获取卡片详情"""
        from cmdb.models import Card
        
        card = Card.objects.filter(id=card_id).first()
        if not card:
            return {'success': False, 'message': '卡片不存在'}
        
        return {
            'success': True,
            'data': card.to_dict()
        }
    
    @staticmethod
    def update_card(card_id: int, data: Dict[str, Any], user) -> Dict[str, Any]:
        """更新卡片"""
        from cmdb.models import Card, CardHistory, Attribute

        card = Card.objects.filter(id=card_id).first()
        if not card:
            return {'success': False, 'message': '卡片不存在'}

        with transaction.atomic():
            # 更新卡片
            card.code = data.get('code', card.code)
            card.updated_by = user
            card.save()

            # 更新属性值：先删旧的，再建新的
            card.lookups.all().delete()

            for attr_name, attr_value in data.get('attributes', {}).items():
                try:
                    attribute = Attribute.objects.get(clazz_id=card.clazz_id, name=attr_name)
                except Attribute.DoesNotExist:
                    raise ValueError(f'属性 {attr_name} 不存在于该类中')
                card.lookups.create(
                    attribute=attribute,
                    value=str(attr_value)
                )

            # 创建历史记录
            CardHistory.objects.create(
                card=card,
                version=card.histories.count() + 1,
                content=data,
                modified_by=user
            )

        return {
            'success': True,
            'data': card.to_dict()
        }
    
    @staticmethod
    def delete_card(card_id: int) -> Dict[str, Any]:
        """删除卡片"""
        from cmdb.models import Card
        
        card = Card.objects.filter(id=card_id).first()
        if not card:
            return {'success': False, 'message': '卡片不存在'}
        
        card.delete()
        
        return {'success': True, 'message': '删除成功'}
