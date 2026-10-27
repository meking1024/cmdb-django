#!/bin/bash

echo "================================"
echo "CMDB Django 项目设置脚本"
echo "================================"
echo ""

# 1. 激活 conda 环境
echo "1. 激活 conda 环境..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate cmdb-env

# 2. 安装依赖
echo ""
echo "2. 安装 Python 依赖..."
pip install -r requirements.txt --default-timeout=100

# 3. 设置环境变量
echo ""
echo "3. 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已从 .env.example 创建 .env 文件"
    echo "请编辑 .env 文件配置数据库连接等参数"
else
    echo ".env 文件已存在"
fi

# 4. 创建日志目录
echo ""
echo "4. 创建日志目录..."
mkdir -p logs

# 5. 数据库迁移
echo ""
echo "5. 运行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 6. 创建超级用户（可选）
echo ""
read -p "是否创建超级用户？(y/n): " create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# 7. 收集静态文件
echo ""
echo "6. 收集静态文件..."
python manage.py collectstatic --noinput

echo ""
echo "================================"
echo "设置完成！"
echo "================================"
echo ""
echo "启动开发服务器:"
echo "  python manage.py runserver"
echo ""
echo "访问 API 文档:"
echo "  http://localhost:8000/api/docs/"
echo "  http://localhost:8000/redoc/"
