-- CMDB 数据库初始化脚本

-- 仅用于全新 PostgreSQL 实例。项目默认使用独立数据库 cmdb_django，
-- 不要在已有旧系统的 cmdb 数据库中执行 Django 表迁移。
CREATE DATABASE cmdb_django OWNER cmdb;

\c cmdb_django;

-- 启用 UUID 扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 表结构将通过 Django migrations 创建
-- 运行以下命令初始化：
-- python manage.py makemigrations
-- python manage.py migrate
