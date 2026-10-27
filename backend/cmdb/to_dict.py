"""
Helper function to convert models to dictionary
"""
from typing import Dict, Any


def to_dict(self) -> Dict[str, Any]:
    """Convert model instance to dictionary"""
    attrs = {}
    
    for field in self._meta.fields:
        value = getattr(self, field.attname, None)
        if value is None:
            attrs[field.name] = None
        elif hasattr(value, 'id'):
            attrs[field.name] = value.id
        else:
            attrs[field.name] = value
    
    for field in self._meta.many_to_many:
        related_name = field.related_name
        value = getattr(self, related_name, [])
        attrs[field.name] = [obj.id for obj in value.all()] if value else []
    
    attrs['id'] = self.id
    
    return attrs


# Monkey patch for models
import django.db.models
django.db.models.Model.to_dict = to_dict
