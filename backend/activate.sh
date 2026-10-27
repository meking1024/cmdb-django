#!/bin/bash

echo "激活 CMDB 环境..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate cmdb-env

echo ""
echo "环境信息:"
echo "  - Python 版本: $(python --version)"
echo "  - Django 版本: $(python -c 'import django; print(django.VERSION)')"
echo "  - Conda 环境: $(conda info --envs | grep '*')"
echo ""
echo "可用命令:"
echo "  - python manage.py runserver      # 启动服务器"
echo "  - python manage.py migrate         # 数据库迁移"
echo "  - python manage.py createsuperuser # 创建用户"
echo "  - python test_api.py              # 测试 API"
