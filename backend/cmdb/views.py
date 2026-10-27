"""
CMDB API Views
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Clazz, Attribute, Card, AutoCollectParseRule
from .serializers import ClazzSerializer, AttributeSerializer, CardSerializer, AutoCollectParseRuleSerializer


class ClazzView(viewsets.ModelViewSet):
    """配置类 CRUD"""
    queryset = Clazz.objects.all()
    serializer_class = ClazzSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AttributeView(viewsets.ModelViewSet):
    """属性 CRUD"""
    queryset = Attribute.objects.select_related('clazz').all()
    serializer_class = AttributeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['clazz', 'data_type', 'is_required']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(clazz_id=class_id)
        return queryset


class CardView(viewsets.ModelViewSet):
    """实例卡片 CRUD"""
    queryset = Card.objects.select_related('clazz', 'created_by', 'updated_by').all()
    serializer_class = CardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['clazz', 'is_active']
    search_fields = ['code', 'clazz__name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(clazz_id=class_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class AutoCollectParseRuleView(viewsets.ModelViewSet):
    """自动采集解析规则 CRUD。"""
    queryset = AutoCollectParseRule.objects.all()
    serializer_class = AutoCollectParseRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['script_type', 'rule_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'script_type', 'created_at', 'updated_at']
    ordering = ['name']
