"""
CMDB 测试数据脚本
用法：python manage.py shell < seed_data.py
   或：python seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from cmdb.models import Clazz, Attribute, Card, CardLookup
from auth_app.models import User

print("=" * 50)
print("开始生成 CMDB 测试数据...")
print("=" * 50)

# ========== 1. 创建超级用户（如果不存在）==========
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("✅ 创建超级用户：admin / admin123456")
else:
    print("ℹ️  超级用户 admin 已存在")

admin_user = User.objects.get(username='admin')

# ========== 2. 清空旧数据（可选）==========
CardLookup.objects.all().delete()
Card.objects.all().delete()
Attribute.objects.all().delete()
Clazz.objects.all().delete()
print("✅ 清空旧测试数据")

# ========== 3. 创建配置类 ==========
# 类1：服务器
server_clazz = Clazz.objects.create(
    name='server',
    description='物理服务器 / 虚拟机',
    is_active=True,
    created_by=admin_user,
    updated_by=admin_user
)
print(f"✅ 创建配置类：{server_clazz.name}")

# 类2：数据库
db_clazz = Clazz.objects.create(
    name='database',
    description='数据库实例',
    is_active=True,
    created_by=admin_user,
    updated_by=admin_user
)
print(f"✅ 创建配置类：{db_clazz.name}")

# 类3：交换机
switch_clazz = Clazz.objects.create(
    name='switch',
    description='网络交换机',
    is_active=True,
    created_by=admin_user,
    updated_by=admin_user
)
print(f"✅ 创建配置类：{switch_clazz.name}")

# ========== 4. 为每个类创建属性 ==========
# 服务器属性
server_attrs = [
    {'name': 'ip', 'display_name': 'IP地址', 'data_type': 'string', 'display_type': 'text', 'is_required': True, 'order': 1},
    {'name': 'cpu', 'display_name': 'CPU核数', 'data_type': 'int', 'display_type': 'text', 'is_required': True, 'order': 2},
    {'name': 'memory', 'display_name': '内存(GB)', 'data_type': 'int', 'display_type': 'text', 'is_required': True, 'order': 3},
    {'name': 'disk', 'display_name': '磁盘(GB)', 'data_type': 'int', 'display_type': 'text', 'is_required': False, 'order': 4},
    {'name': 'os', 'display_name': '操作系统', 'data_type': 'string', 'display_type': 'select', 'options': ['CentOS 7', 'CentOS 8', 'Ubuntu 20.04', 'Ubuntu 22.04'], 'order': 5},
    {'name': 'env', 'display_name': '环境', 'data_type': 'string', 'display_type': 'select', 'options': ['prod', 'staging', 'dev'], 'order': 6},
]
for attr_data in server_attrs:
    Attribute.objects.create(clazz=server_clazz, **attr_data)
print(f"✅ 为服务器创建 {len(server_attrs)} 个属性")

# 数据库属性
db_attrs = [
    {'name': 'db_type', 'display_name': '数据库类型', 'data_type': 'string', 'display_type': 'select', 'options': ['MySQL', 'PostgreSQL', 'Redis', 'MongoDB'], 'is_required': True, 'order': 1},
    {'name': 'version', 'display_name': '版本', 'data_type': 'string', 'display_type': 'text', 'is_required': True, 'order': 2},
    {'name': 'port', 'display_name': '端口', 'data_type': 'int', 'display_type': 'text', 'is_required': True, 'order': 3},
    {'name': 'server', 'display_name': '所属服务器', 'data_type': 'string', 'display_type': 'text', 'is_required': False, 'order': 4},
]
for attr_data in db_attrs:
    Attribute.objects.create(clazz=db_clazz, **attr_data)
print(f"✅ 为数据库创建 {len(db_attrs)} 个属性")

# 交换机属性
switch_attrs = [
    {'name': 'ip', 'display_name': '管理IP', 'data_type': 'string', 'display_type': 'text', 'is_required': True, 'order': 1},
    {'name': 'model', 'display_name': '型号', 'data_type': 'string', 'display_type': 'text', 'is_required': True, 'order': 2},
    {'name': 'ports', 'display_name': '端口数', 'data_type': 'int', 'display_type': 'text', 'is_required': False, 'order': 3},
]
for attr_data in switch_attrs:
    Attribute.objects.create(clazz=switch_clazz, **attr_data)
print(f"✅ 为交换机创建 {len(switch_attrs)} 个属性")

# ========== 5. 创建实例卡片（Card）==========
# 服务器实例
server1 = Card.objects.create(
    clazz=server_clazz,
    code='web-server-01',
    is_active=True,
    created_by=admin_user,
    updated_by=admin_user
)
server1_attrs = {
    'ip': '192.168.1.101',
    'cpu': '16',
    'memory': '32',
    'disk': '500',
    'os': 'CentOS 7',
    'env': 'prod',
}
for attr_name, value in server1_attrs.items():
    attr = Attribute.objects.get(clazz=server_clazz, name=attr_name)
    CardLookup.objects.create(card=server1, attribute=attr, value=value)
print(f"✅ 创建实例：{server1.code}")

server2 = Card.objects.create(
    clazz=server_clazz,
    code='web-server-02',
    is_active=True,
    created_by=admin_user,
    updated_by=admin_user
)
server2_attrs = {
    'ip': '192.168.1.102',
    'cpu': '16',
    'memory': '32',
    'disk': '500',
    'os': 'Ubuntu 22.04',
    'env': 'prod',
}
for attr_name, value in server2_attrs.items():
    attr = Attribute.objects.get(clazz=server_clazz, name=attr_name)
    CardLookup.objects.create(card=server2, attribute=attr, value=value)
print(f"✅ 创建实例：{server2.code}")

# 数据库实例
db1 = Card.objects.create(
    clazz=db_clazz,
    code='mysql-master-01',
    is_active=True,
    created_by=admin_user,
    updated_by=admin_user
)
db1_attrs = {
    'db_type': 'MySQL',
    'version': '8.0.35',
    'port': '3306',
    'server': 'web-server-01',
}
for attr_name, value in db1_attrs.items():
    attr = Attribute.objects.get(clazz=db_clazz, name=attr_name)
    CardLookup.objects.create(card=db1, attribute=attr, value=value)
print(f"✅ 创建实例：{db1.code}")

# 交换机实例
switch1 = Card.objects.create(
    clazz=switch_clazz,
    code='core-switch-01',
    is_active=True,
    created_by=admin_user,
    updated_by=admin_user
)
switch1_attrs = {
    'ip': '192.168.1.1',
    'model': 'Cisco Catalyst 9300',
    'ports': '48',
}
for attr_name, value in switch1_attrs.items():
    attr = Attribute.objects.get(clazz=switch_clazz, name=attr_name)
    CardLookup.objects.create(card=switch1, attribute=attr, value=value)
print(f"✅ 创建实例：{switch1.code}")

# ========== 6. 统计 ==========
print("\n" + "=" * 50)
print("测试数据生成完成！")
print("=" * 50)
print(f"配置类（Clazz）：{Clazz.objects.count()} 个")
print(f"属性（Attribute）：{Attribute.objects.count()} 个")
print(f"实例（Card）：{Card.objects.count()} 个")
print(f"属性值（CardLookup）：{CardLookup.objects.count()} 条")
print("\n📊 数据概览：")
for clazz in Clazz.objects.all():
    card_count = clazz.cards.count()
    attr_count = clazz.attributes.count()
    print(f"  - {clazz.name}: {attr_count} 个属性, {card_count} 个实例")
print("\n🚀 现在可以访问：")
print("  - Admin 后台：http://localhost:8000/admin/")
print("  - Swagger API：http://localhost:8000/api/docs/")
print("  - 登录账号：admin / admin123456")
