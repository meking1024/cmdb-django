"""
CMDB Admin Configuration
在 Django Admin 中注册所有 CMDB 模型
"""
from django.contrib import admin
from .models import (
    Clazz, Attribute, Card, CardLookup, CardHistory,
    Lookup, Permission, ClazzPermission, AuditLog
)


@admin.register(Clazz)
class ClazzAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['clazz', 'name', 'display_name', 'data_type', 'is_required', 'order']
    list_filter = ['clazz', 'data_type', 'is_required']
    search_fields = ['name', 'display_name']
    ordering = ['clazz', 'order']


class CardLookupInline(admin.TabularInline):
    model = CardLookup
    extra = 0


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['code', 'clazz', 'is_active', 'created_by', 'created_at']
    list_filter = ['clazz', 'is_active', 'created_at']
    search_fields = ['code']
    inlines = [CardLookupInline]
    ordering = ['-created_at']


@admin.register(CardHistory)
class CardHistoryAdmin(admin.ModelAdmin):
    list_display = ['card', 'version', 'begin_date', 'modified_by']
    list_filter = ['begin_date']
    search_fields = ['card__code']
    ordering = ['-version']


@admin.register(Lookup)
class LookupAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'value', 'order', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'value']
    ordering = ['type', 'order']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'description']
    search_fields = ['name', 'codename']


@admin.register(ClazzPermission)
class ClazzPermissionAdmin(admin.ModelAdmin):
    list_display = ['clazz', 'user', 'permission']
    list_filter = ['clazz', 'permission']
    search_fields = ['user__username', 'clazz__name']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'resource_id', 'ip_address', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user__username', 'resource_id']
    readonly_fields = ['user', 'action', 'resource_type', 'resource_id', 'details', 'ip_address', 'created_at']
    ordering = ['-created_at']
