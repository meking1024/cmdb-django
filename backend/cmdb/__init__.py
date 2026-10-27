"""
CMDB Application
Configuration management system for IT assets and configurations
"""
from django.apps import AppConfig

class CMDBConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'
    verbose_name = 'CMDB'
    verbose_name_plural = 'CMDB'
