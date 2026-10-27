"""
Django REST Framework Serializers
"""
from django.db import transaction
from rest_framework import serializers
from .models import (
    Clazz, Attribute, Card, CardHistory, Lookup, CardLookup, AuditLog,
    TopoLayer, TopoRelation, AutoCollectCertificate, AutoCollectTarget,
    AutoCollectParseRule, AutoCollectTask, AutoCollectTaskInstance, ScheduledJob,
)


class ClazzSerializer(serializers.ModelSerializer):
    """配置类序列化器"""
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    updated_by_name = serializers.ReadOnlyField(source='updated_by.username')
    
    class Meta:
        model = Clazz
        fields = [
            'id', 'name', 'description', 'is_active',
            'created_at', 'updated_at', 'created_by_name', 'updated_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AttributeSerializer(serializers.ModelSerializer):
    """属性序列化器"""
    class Meta:
        model = Attribute
        fields = [
            'id', 'clazz', 'name', 'display_name', 'data_type',
            'display_type', 'is_required', 'is_visible', 'default_value',
            'options', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CardSerializer(serializers.ModelSerializer):
    """实例卡片序列化器"""
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    updated_by_name = serializers.ReadOnlyField(source='updated_by.username')
    attributes = serializers.SerializerMethodField()
    attribute_values = serializers.DictField(write_only=True, required=False)
    
    class Meta:
        model = Card
        fields = [
            'id', 'clazz', 'code', 'is_active',
            'created_at', 'updated_at', 'created_by_name', 'updated_by_name',
            'attributes', 'attribute_values'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        values = attrs.get('attribute_values')
        if self.instance is None:
            clazz = attrs.get('clazz')
            values = values or {}
            required = Attribute.objects.filter(clazz=clazz, is_required=True).values_list('name', flat=True)
            missing = [name for name in required if not str(values.get(name, '')).strip()]
            if missing:
                raise serializers.ValidationError({'attribute_values': f'必填属性未填写：{", ".join(missing)}'})
        return attrs
    
    def get_attributes(self, obj):
        """获取卡片的所有属性"""
        return [
            {
                'attribute_id': lookup.attribute_id,
                'attribute_name': lookup.attribute.name,
                'value': lookup.value
            }
            for lookup in obj.lookups.all()
        ]

    def _save_values(self, card, values):
        attributes = {item.name: item for item in Attribute.objects.filter(clazz=card.clazz)}
        unknown = set(values) - set(attributes)
        if unknown:
            raise serializers.ValidationError({'attribute_values': f'未知属性：{", ".join(sorted(unknown))}'})
        for name, value in values.items():
            CardLookup.objects.update_or_create(
                card=card, attribute=attributes[name], defaults={'value': '' if value is None else str(value)}
            )

    @transaction.atomic
    def create(self, validated_data):
        values = validated_data.pop('attribute_values', {})
        card = super().create(validated_data)
        self._save_values(card, values)
        CardHistory.objects.create(
            card=card, version=1,
            content={'code': card.code, 'attribute_values': values},
            modified_by=validated_data.get('created_by'),
        )
        return card

    @transaction.atomic
    def update(self, instance, validated_data):
        values = validated_data.pop('attribute_values', None)
        card = super().update(instance, validated_data)
        if values is not None:
            self._save_values(card, values)
        CardHistory.objects.create(
            card=card, version=card.histories.count() + 1,
            content={'code': card.code, 'attribute_values': {
                row.attribute.name: row.value for row in card.lookups.select_related('attribute')
            }},
            modified_by=validated_data.get('updated_by'),
        )
        return card


class CardHistorySerializer(serializers.ModelSerializer):
    """卡片历史序列化器"""
    modified_by_name = serializers.ReadOnlyField(source='modified_by.username')
    confirmed_by_name = serializers.ReadOnlyField(source='confirmed_by.username')
    
    class Meta:
        model = CardHistory
        fields = [
            'id', 'card', 'version', 'begin_date', 'content',
            'modified_by_name', 'confirmed_by_name', 'comment'
        ]
        read_only_fields = ['id', 'begin_date', 'version']


class AuditLogSerializer(serializers.ModelSerializer):
    """审计日志序列化器"""
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'action', 'resource_type',
            'resource_id', 'details', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ============================================
# 拓扑图/关系配置序列化器
# ============================================

class TopoLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopoLayer
        fields = ['id', 'name', 'description', 'is_default', 'clazzes', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TopoRelationSerializer(serializers.ModelSerializer):
    source_clazz_name = serializers.ReadOnlyField(source='source_clazz.name')
    target_clazz_name = serializers.ReadOnlyField(source='target_clazz.name')

    class Meta:
        model = TopoRelation
        fields = ['id', 'name', 'source_clazz', 'source_clazz_name', 'target_clazz', 'target_clazz_name',
                  'relation_type', 'condition_expression', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================
# 数据采集序列化器
# ============================================

class AutoCollectCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoCollectCertificate
        fields = ['id', 'name', 'protocol', 'platform', 'username', 'port', 'enable_https',
                  'terminal_type', 'charset_name', 'database_name', 'last_test_time', 'is_active']
        read_only_fields = ['id', 'last_test_time']


class AutoCollectTargetSerializer(serializers.ModelSerializer):
    certificate_name = serializers.ReadOnlyField(source='certificate.name')
    parse_rule_name = serializers.ReadOnlyField(source='parse_rule.name')

    class Meta:
        model = AutoCollectTarget
        fields = ['id', 'name', 'description', 'target_type', 'ip_address', 'card_class', 'filter_expression',
                  'certificate', 'certificate_name', 'collect_script', 'parse_rule', 'parse_rule_name',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AutoCollectParseRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoCollectParseRule
        fields = ['id', 'name', 'rule_type', 'script_type', 'script_parameters',
                  'script_content', 'script_arguments', 'parse_data_format', 'original_data_format',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AutoCollectTaskSerializer(serializers.ModelSerializer):
    target_count = serializers.SerializerMethodField()
    target_names = serializers.SerializerMethodField()

    class Meta:
        model = AutoCollectTask
        fields = ['id', 'name', 'task_type', 'description', 'cron_expression', 'interval_seconds',
                  'run_servers', 'target_count', 'target_names', 'parse_rule', 'result_map',
                  'status', 'last_run_time', 'next_run_time', 'run_count', 'error_message', 'is_active']

    def get_target_count(self, obj):
        return obj.targets.count()

    def get_target_names(self, obj):
        return [t.name for t in obj.targets.all()]


class AutoCollectTaskInstanceSerializer(serializers.ModelSerializer):
    task_name = serializers.ReadOnlyField(source='task.name')
    target_name = serializers.ReadOnlyField(source='target.name')

    class Meta:
        model = AutoCollectTaskInstance
        fields = ['id', 'task', 'task_name', 'target', 'target_name', 'status',
                  'start_time', 'end_time', 'duration', 'log_content', 'error_message']
        read_only_fields = ['id']


# ============================================
# 定时任务序列化器
# ============================================

class ScheduledJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledJob
        fields = ['id', 'name', 'task_type', 'description', 'cron_expression', 'status',
                  'last_run_time', 'next_run_time', 'run_count', 'error_message', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'run_count']
