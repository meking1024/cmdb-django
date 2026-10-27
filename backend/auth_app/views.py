"""
Auth App Views
认证相关 API：登录、登出、获取当前用户、用户管理
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.db.models import Q

from .models import User
from .serializers import UserSerializer


class IsAdminOrSelf(permissions.BasePermission):
    """自定义权限：管理员可以操作所有，普通用户只能操作自己"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj == request.user


class AuthViewSet(viewsets.ViewSet):
    """
    认证相关 API
    - POST /api/auth/auth/login/    登录
    - POST /api/auth/auth/logout/   登出
    - GET  /api/auth/auth/me/       获取当前用户
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        username = request.data.get('username', '')
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'success': False, 'message': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {'success': False, 'message': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'success': False, 'message': '账号已被禁用'},
                status=status.HTTP_403_FORBIDDEN
            )

        login(request, user)
        get_token(request)  # 刷新 CSRF token

        return Response({
            'success': True,
            'message': '登录成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
            }
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出"""
        logout(request)
        return Response({'success': True, 'message': '登出成功'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """获取当前登录用户信息"""
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理 API
    - GET    /api/auth/users/         用户列表
    - POST   /api/auth/users/         创建用户
    - GET    /api/auth/users/{id}/    用户详情
    - PUT    /api/auth/users/{id}/    更新用户
    - DELETE /api/auth/users/{id}/    删除用户
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]

    def get_queryset(self):
        """普通用户只能看自己，管理员可以看所有"""
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            return qs.filter(id=self.request.user.id)
        # 支持搜索
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search))
        return qs

    def create(self, request, *args, **kwargs):
        """创建用户（仅管理员）"""
        if not request.user.is_staff:
            return Response(
                {'success': False, 'message': '无权限创建用户'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username', '')
        password = request.data.get('password', '')
        email = request.data.get('email', '')

        if not username or not password:
            return Response(
                {'success': False, 'message': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'success': False, 'message': '用户名已存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        serializer = self.get_serializer(user)
        return Response(
            {'success': True, 'data': serializer.data},
            status=status.HTTP_201_CREATED
        )
