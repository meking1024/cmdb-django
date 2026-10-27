"""
CMDB API URL Configuration
使用 DRF Router 自动生成 ViewSet 路由
"""
from rest_framework.routers import DefaultRouter
from .views import ClazzView, AttributeView, CardView, AutoCollectParseRuleView

app_name = 'cmdb'

router = DefaultRouter()
router.register(r'classes', ClazzView, basename='class')
router.register(r'attributes', AttributeView, basename='attribute')
router.register(r'cards', CardView, basename='card')
router.register(r'autocollect/parse-rules', AutoCollectParseRuleView, basename='parse-rule')

urlpatterns = router.urls
