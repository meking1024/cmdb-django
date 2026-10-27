#!/bin/bash

echo "================================"
echo "🚀 CMDB - Docker 数据库初始化"
echo "================================"
echo ""

cd /Users/macyang/claude-demo/cmdb-django/backend

# 1. 启动 Docker 数据库
echo "1. 启动 PostgreSQL 和 Redis..."
docker-compose up -d postgres

# 等待数据库就绪
echo "   等待数据库就绪..."
sleep 10

# 2. 创建扩展
echo "2. 创建数据库扩展..."
docker-compose exec -T postgres psql -U cmdbuser -d cmdb << 'EOF'
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
