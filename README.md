# 📦 CMDB 配置管理数据库平台

> 基于 **Django 5 + DRF** 后端与 **Streamlit** 前端的自主开发 CMDB（Configuration Management Database，配置管理数据库）平台。

CMDB 是 IT 运维体系的核心组件，用于统一管理 IT 资产与配置信息——从服务器、数据库、中间件到网络设备、应用系统，全部通过统一的元模型进行建模、采集、维护和审计。

本平台采用**三层元模型设计**（配置类 Clazz → 属性 Attribute → 实例 Card），开箱即用，支持通过配置而非编码快速扩展任意 IT 资产类型。

---

## ✨ 界面预览

### 📊 首页仪表盘

集中展示各类 IT 资产的统计概况：应用系统、网络设备、系统硬件设备、数据中心、机房，以及生产/开发测试环境下的中间件、数据库、操作系统、虚拟机资源等维度的实时数量。

![首页仪表盘](doc/screenshot-dashboard.png)

### 🖥️ CI 管理 - 实例列表

按分类浏览全部配置实例，支持全文检索、精确匹配、分页浏览，展示 CI 编号、IP 地址、所在环境、OS 类型、主机名、修改人/确认人等关键字段。

![CI实例列表](doc/screenshot-ci-list.png)

### 🧩 模型设计 - 类设计

可视化配置每个配置类的表单属性：属性编号、属性名称、是否可用、列表显示、自动采集、编辑模式、类型（文本 / 下拉框 / 日期时间 / 外键 / 文本域）等。

![模型设计-表单属性](doc/screenshot-model-design.png)

### ⏱️ 自动采集 - 作业管理

集中管理自动采集作业：资产盘点、网络设备巡检（TELNET）、Kafka 采集、Python 采集等，支持启动/停止、立即执行、编辑与日志查看。

![作业管理](doc/screenshot-job-manage.png)

### 🔐 系统设置 - 角色管理

细粒度的角色与权限管理：配置管理员（按运维域拆分：网络通讯、系统设备、内控安全、生产管理等）、只读用户、RESTful 接口用户等。

![角色管理](doc/screenshot-role-manage.png)

---

## 🚀 功能特性

- ✅ **三层元模型**：配置类（Clazz）→ 属性（Attribute）→ 实例（Card），可动态扩展任意 IT 资产类型
- ✅ **EAV 属性值模型**：CardLookup 支持任意实例的灵活属性值存储
- ✅ **版本历史**：CardHistory 记录每次变更快照，支持审计与回溯
- ✅ **完整 REST API**：基于 Django REST Framework 的 ViewSet + Router 自动路由
- ✅ **认证体系**：登录 / 登出 / 获取当前用户 / 用户管理（Session 认证）
- ✅ **数据字典**：Lookup 统一管理下拉选项、枚举值
- ✅ **权限控制**：Permission + ClazzPermission 类级权限
- ✅ **审计日志**：AuditLog 记录全部增删改查操作（含 IP 与详情）
- ✅ **API 文档**：Swagger UI + ReDoc 自动生成
- ✅ **Django Admin**：完整的管理后台，开箱即用
- ✅ **Streamlit 前端**：仪表盘 / 配置类管理 / 实例列表 / 动态表单新增实例
- ✅ **一键启动**：`./RUN.sh` 同时拉起 API 与前端
- ✅ **测试数据**：`seed_data.py` 一键生成演示数据

---

## 🛠️ 技术栈

| 层次 | 技术选型 |
|------|----------|
| Web 框架 | Django 5.0.3 |
| REST API | Django REST Framework 3.14 |
| 前端 | Streamlit 1.65 |
| 数据库 | SQLite（开发默认）/ PostgreSQL（生产） |
| 认证 | Django Auth（Session） |
| API 文档 | drf-spectacular（Swagger / ReDoc） |
| 语言 | Python 3.11 |

---

## ⚡ 快速开始

### 方式一：一键启动（推荐）

```bash
# 1. 克隆仓库
git clone <your-repo-url> cmdb-django
cd cmdb-django

# 2. 一键启动（自动创建虚拟环境、安装依赖、迁移、拉起 API + Streamlit）
./RUN.sh
```

启动后访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🖥️ **CMDB 前端** | http://localhost:8501 | Streamlit 管理界面 |
| 📖 **Swagger 文档** | http://localhost:8000/api/docs/ | API 交互式文档 |
| 🔐 **Django Admin** | http://localhost:8000/admin/ | 管理后台 |
| 🩺 **健康检查** | http://localhost:8000/health/ | 服务状态 |

### 方式二：Conda 手动启动

```bash
# 1. 进入后端目录
cd backend

# 2. 创建并激活 conda 环境
conda create -n cmdb-env python=3.11 -y
conda activate cmdb-env

# 3. 安装依赖
pip install -r requirements.txt

# 4. 数据库迁移
python manage.py migrate

# 5. 创建超级用户（可选，Admin 后台需要）
python manage.py createsuperuser

# 6. 生成演示数据（可选，推荐）
python seed_data.py

# 7. 启动 Django API
python manage.py runserver 127.0.0.1:8000

# 8. 另开终端，启动 Streamlit 前端
streamlit run streamlit_app.py --server.port 8501
```

### 🧪 快速验证

```bash
# 健康检查
curl http://localhost:8000/health/
# {"status": "ok"}

# 查看配置类列表（需登录态，或在 Swagger 中操作）
curl http://localhost:8000/api/cmdb/classes/
```

---

## 📁 项目结构

```
cmdb-django/
├── backend/                        # Django 后端
│   ├── manage.py                   # Django 管理入口
│   ├── settings.py                 # 项目配置（SQLite/PostgreSQL 切换、DRF、CORS）
│   ├── urls.py                     # 根路由
│   ├── requirements.txt            # 依赖清单
│   ├── seed_data.py                # 测试数据脚本
│   ├── streamlit_app.py            # Streamlit 前端
│   ├── start.sh / RUN.sh           # 一键启动脚本
│   ├── cmdb/                       # CMDB 主应用
│   │   ├── models.py               # 核心数据模型（9 个业务模型）
│   │   ├── views.py                # REST API ViewSet
│   │   ├── serializers.py          # 序列化器
│   │   ├── urls.py                 # API 路由（DRF Router）
│   │   ├── admin.py                # Admin 后台注册
│   │   ├── authentication.py       # Token / Session 认证
│   │   ├── middleware.py           # 审计日志、请求日志、错误处理中间件
│   │   ├── services/               # 业务服务层
│   │   │   ├── base_service.py     #   基础服务（统一响应、字段校验）
│   │   │   ├── card_service.py     #   卡片业务（创建/更新/删除/历史）
│   │   │   └── scheduler_service.py#   定时任务服务
│   │   └── migrations/             # 数据库迁移
│   ├── auth_app/                   # 认证应用（自定义 User、登录/登出、用户管理）
│   └── db.sqlite3                  # 开发数据库（默认，不入库）
├── frontend/                       # 预留的独立前端目录（待开发）
├── doc/                            # 界面截图（README 引用）
└── README.md
```

---

## 🗄️ 数据模型

核心采用 **Clazz → Attribute → Card** 三层元模型，任何 IT 资产类型都可以通过配置而非编码来扩展。

```
Clazz（配置类，如：服务器 / 数据库 / 交换机）
  ├── Attribute（属性定义，如：IP、CPU核数、内存、OS类型）
  │     └── options（下拉选项，JSON）
  └── Card（实例，如：web-server-01）
        └── CardLookup（属性值，EAV：attribute + value）
              └── 关联 Attribute

CardHistory（版本历史：每次变更生成快照，含修改人/确认人）
Lookup（数据字典：枚举/下拉项统一管理）
Permission / ClazzPermission（系统权限 + 类级权限）
AuditLog（审计日志：操作人/动作/资源/详情/IP）
```

| 模型 | 说明 |
|------|------|
| `auth_app.User` | 自定义用户模型（AbstractUser 扩展） |
| `Clazz` | 配置类（元模型：资产类型定义） |
| `Attribute` | 属性定义（数据类型/展示类型/必填/默认值/选项） |
| `Card` | 配置实例（具体资产条目） |
| `CardLookup` | 实例属性值（EAV 模型） |
| `CardHistory` | 实例历史版本（快照） |
| `Lookup` | 数据字典 |
| `Permission` | 系统权限 |
| `ClazzPermission` | 类级权限（view/create/edit/delete） |
| `AuditLog` | 审计日志 |

---

## 📡 API 端点

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| **认证** | POST | `/api/auth/auth/login/` | 用户登录 |
| | POST | `/api/auth/auth/logout/` | 用户登出 |
| | GET | `/api/auth/auth/me/` | 当前用户信息 |
| | CRUD | `/api/auth/users/` | 用户管理 |
| **配置类** | GET/POST | `/api/cmdb/classes/` | 列表 / 创建 |
| | GET/PUT/DELETE | `/api/cmdb/classes/{id}/` | 详情 / 更新 / 删除 |
| **属性** | GET/POST | `/api/cmdb/attributes/` | 列表 / 创建 |
| | GET/PUT/DELETE | `/api/cmdb/attributes/{id}/` | 详情 / 更新 / 删除 |
| **实例** | GET/POST | `/api/cmdb/cards/` | 列表 / 创建 |
| | GET/PUT/DELETE | `/api/cmdb/cards/{id}/` | 详情 / 更新 / 删除 |

> 完整交互式文档见启动后的 http://localhost:8000/api/docs/（Swagger UI）。

---

## 🧪 测试数据

```bash
cd backend
conda activate cmdb-env
python seed_data.py
```

生成内容：超级用户 `admin / admin123456`、3 个配置类（服务器/数据库/交换机）、13 个属性定义、4 个实例及完整属性值。

---

## 🗺️ 路线图

### ✅ Phase 1 - 基础框架（已完成）
- Django 项目脚手架 + 10 个数据模型
- REST API（Clazz / Attribute / Card）
- 认证系统（登录 / 登出 / 用户管理）
- Swagger API 文档 + Django Admin
- Streamlit 前端（仪表盘 / 实例管理 / 动态表单）
- 测试数据与一键启动脚本

### 🔄 Phase 2 - 认证与权限完善
- [ ] JWT Token 认证
- [ ] 权限装饰器 / 细粒度权限控制
- [ ] CAS 单点登录集成

### 📅 Phase 3 - 业务能力增强
- [ ] 类关系（关系图）与预定义查询
- [ ] 属性验证规则（正则、取值范围）
- [ ] 自动采集作业（对接 Kafka / 脚本采集）
- [ ] 全文检索（接入 Elasticsearch 或基于 PostgreSQL 的全文搜索）

### 🎨 Phase 4 - 独立前端
- [ ] Vue 3 + Element Plus 前端工程
- [ ] 对接 DRF API，打造更完善的交互界面

---

## 📄 License

本平台为自主开发项目，代码与设计版权归开发者所有，仅供学习与参考。

---

**技术栈**：Django 5 / DRF / Streamlit / Python 3.11
# cmdb-django
