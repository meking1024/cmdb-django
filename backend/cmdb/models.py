"""
CMDB Core Models
配置管理数据库核心数据模型

元模型设计：
- Clazz（配置类）→ 定义一种配置对象（如：服务器、数据库、中间件）
- Attribute（属性）→ 每个类有哪些字段（如：CPU、内存、IP）
- Card（卡片/实例）→ 具体的配置实例（如：web-server-01）
- CardLookup（卡片属性值）→ Card 与 Attribute 的多对多值表
- CardHistory（历史版本）→ 每次变更的快照
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """抽象基类：自动加创建/更新时间"""
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        abstract = True


class Clazz(TimeStampedModel):
    """
    配置类 / 模型定义
    例：服务器、数据库、交换机、应用系统
    """
    name = models.CharField(_('类名'), max_length=100, unique=True)
    description = models.TextField(_('描述'), blank=True, default='')
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_classes',
        verbose_name=_('创建人')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_classes',
        verbose_name=_('更新人')
    )

    class Meta:
        db_table = 'cmdb_clazz'
        verbose_name = _('配置类')
        verbose_name_plural = _('配置类')
        ordering = ['name']

    def __str__(self):
        return self.name


class Attribute(TimeStampedModel):
    """
    属性定义
    每个 Clazz 下挂多个 Attribute，定义该类有哪些字段
    """
    DATA_TYPE_CHOICES = [
        ('string', '字符串'),
        ('int', '整数'),
        ('float', '小数'),
        ('boolean', '布尔'),
        ('date', '日期'),
        ('datetime', '日期时间'),
        ('text', '长文本'),
        ('json', 'JSON'),
    ]
    DISPLAY_TYPE_CHOICES = [
        ('text', '单行文本'),
        ('textarea', '多行文本'),
        ('select', '下拉选择'),
        ('radio', '单选框'),
        ('checkbox', '多选框'),
        ('date', '日期选择'),
        ('datetime', '日期时间选择'),
    ]

    clazz = models.ForeignKey(
        Clazz,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name=_('所属类')
    )
    name = models.CharField(_('属性名'), max_length=100)
    display_name = models.CharField(_('显示名'), max_length=100)
    data_type = models.CharField(
        _('数据类型'),
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='string'
    )
    display_type = models.CharField(
        _('展示类型'),
        max_length=20,
        choices=DISPLAY_TYPE_CHOICES,
        default='text'
    )
    is_required = models.BooleanField(_('是否必填'), default=False)
    is_visible = models.BooleanField(_('是否可见'), default=True)
    default_value = models.CharField(_('默认值'), max_length=255, blank=True, default='')
    options = models.JSONField(_('选项'), default=list, blank=True)
    order = models.IntegerField(_('排序'), default=0)

    class Meta:
        db_table = 'cmdb_attribute'
        verbose_name = _('属性')
        verbose_name_plural = _('属性')
        unique_together = [['clazz', 'name']]
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.clazz.name}.{self.name}'


class Card(TimeStampedModel):
    """
    配置实例 / 卡片
    某个 Clazz 下的具体一条数据，如：web-server-01
    """
    clazz = models.ForeignKey(
        Clazz,
        on_delete=models.PROTECT,
        related_name='cards',
        verbose_name=_('所属类')
    )
    code = models.CharField(_('实例编码'), max_length=255)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_cards',
        verbose_name=_('创建人')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_cards',
        verbose_name=_('更新人')
    )

    class Meta:
        db_table = 'cmdb_card'
        verbose_name = _('配置实例')
        verbose_name_plural = _('配置实例')
        unique_together = [['clazz', 'code']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.clazz.name}:{self.code}'


class CardLookup(models.Model):
    """
    卡片属性值
    Card 与 Attribute 的关联表，存储每个实例的具体属性值
    （即 Card 的 EAV 模型：Entity-Attribute-Value）
    """
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='lookups',
        verbose_name=_('卡片')
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.PROTECT,
        related_name='card_values',
        verbose_name=_('属性')
    )
    value = models.TextField(_('属性值'), blank=True, default='')

    class Meta:
        db_table = 'cmdb_card_lookup'
        verbose_name = _('卡片属性值')
        verbose_name_plural = _('卡片属性值')
        unique_together = [['card', 'attribute']]

    def __str__(self):
        return f'{self.card.code}.{self.attribute.name}={self.value}'


class CardHistory(models.Model):
    """
    卡片历史版本
    每次修改 Card 时生成一条快照，用于审计和回滚
    """
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='histories',
        verbose_name=_('卡片')
    )
    version = models.IntegerField(_('版本号'), default=1)
    begin_date = models.DateTimeField(_('生效时间'), auto_now_add=True)
    content = models.JSONField(_('快照内容'), default=dict)
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_histories',
        verbose_name=_('修改人')
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_histories',
        verbose_name=_('确认人')
    )
    comment = models.TextField(_('备注'), blank=True, default='')

    class Meta:
        db_table = 'cmdb_card_history'
        verbose_name = _('卡片历史')
        verbose_name_plural = _('卡片历史')
        ordering = ['-version']

    def __str__(self):
        return f'{self.card.code} v{self.version}'


class Lookup(models.Model):
    """
    通用数据字典 / 查找表
    用于存放下拉选项、枚举值等
    """
    TYPE_CHOICES = [
        ('priority', '优先级'),
        ('status', '状态'),
        ('env', '环境'),
        ('vendor', '厂商'),
        ('custom', '自定义'),
    ]

    type = models.CharField(_('类型'), max_length=50, choices=TYPE_CHOICES, default='custom')
    name = models.CharField(_('名称'), max_length=100)
    value = models.CharField(_('值'), max_length=100)
    order = models.IntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否启用'), default=True)

    class Meta:
        db_table = 'cmdb_lookup'
        verbose_name = _('数据字典')
        verbose_name_plural = _('数据字典')
        unique_together = [['type', 'value']]
        ordering = ['type', 'order']

    def __str__(self):
        return f'{self.type}:{self.name}'


class Permission(models.Model):
    """
    系统权限定义
    """
    name = models.CharField(_('权限名称'), max_length=100)
    codename = models.CharField(_('权限标识'), max_length=100, unique=True)
    description = models.TextField(_('描述'), blank=True, default='')

    class Meta:
        db_table = 'cmdb_permission'
        verbose_name = _('权限')
        verbose_name_plural = _('权限')

    def __str__(self):
        return self.codename


class ClazzPermission(models.Model):
    """
    类级权限
    控制哪些用户/角色可以对某个 Clazz 做什么操作
    """
    PERMISSION_CHOICES = [
        ('view', '查看'),
        ('create', '创建'),
        ('edit', '编辑'),
        ('delete', '删除'),
    ]

    clazz = models.ForeignKey(
        Clazz,
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name=_('配置类')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clazz_permissions',
        verbose_name=_('用户')
    )
    permission = models.CharField(
        _('权限类型'),
        max_length=20,
        choices=PERMISSION_CHOICES
    )

    class Meta:
        db_table = 'cmdb_clazz_permission'
        verbose_name = _('类权限')
        verbose_name_plural = _('类权限')
        unique_together = [['clazz', 'user', 'permission']]

    def __str__(self):
        return f'{self.user}@{self.clazz}:{self.permission}'


class AuditLog(models.Model):
    """
    审计日志
    记录所有对 CMDB 数据的增删改操作
    """
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('view', '查看'),
        ('login', '登录'),
        ('logout', '登出'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('操作用户')
    )
    action = models.CharField(_('操作类型'), max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(_('资源类型'), max_length=100)
    resource_id = models.CharField(_('资源ID'), max_length=100, blank=True, default='')
    details = models.JSONField(_('详情'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP地址'), null=True, blank=True)
    created_at = models.DateTimeField(_('操作时间'), auto_now_add=True)

    class Meta:
        db_table = 'cmdb_audit_log'
        verbose_name = _('审计日志')
        verbose_name_plural = _('审计日志')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} {self.action} {self.resource_type}#{self.resource_id}'


# ============================================
# 拓扑图/关系配置模型
# ============================================

class TopoLayer(TimeStampedModel):
    """
    拓扑分层配置
    定义拓扑图的层级结构
    """
    name = models.CharField(_('分层名称'), max_length=100, unique=True)
    description = models.TextField(_('描述'), blank=True, default='')
    is_default = models.BooleanField(_('是否默认分层'), default=False)
    clazzes = models.ManyToManyField(
        Clazz,
        related_name='topo_layers',
        blank=True,
        verbose_name=_('关联配置类')
    )
    order = models.IntegerField(_('排序'), default=0)

    class Meta:
        db_table = 'cmdb_topo_layer'
        verbose_name = _('拓扑分层')
        verbose_name_plural = _('拓扑分层')
        ordering = ['order']

    def __str__(self):
        return f'{self.name}'


class TopoRelation(TimeStampedModel):
    """
    拓扑关系配置
    定义配置类之间的拓扑关系
    """
    SOURCE_CHOICES = [
        ('upstream', '上游'),
        ('downstream', '下游'),
        ('related', '相关'),
    ]

    name = models.CharField(_('关系名称'), max_length=100)
    source_clazz = models.ForeignKey(
        Clazz,
        on_delete=models.CASCADE,
        related_name='source_relations',
        verbose_name=_('源配置类')
    )
    target_clazz = models.ForeignKey(
        Clazz,
        on_delete=models.CASCADE,
        related_name='target_relations',
        verbose_name=_('目标配置类')
    )
    relation_type = models.CharField(
        _('关系类型'),
        max_length=20,
        choices=SOURCE_CHOICES,
        default='upstream'
    )
    condition_expression = models.TextField(_('条件表达式'), blank=True, default='')
    description = models.TextField(_('描述'), blank=True, default='')

    class Meta:
        db_table = 'cmdb_topo_relation'
        verbose_name = _('拓扑关系')
        verbose_name_plural = _('拓扑关系')
        unique_together = [['source_clazz', 'target_clazz', 'relation_type']]

    def __str__(self):
        return f'{self.source_clazz.name} -> {self.target_clazz.name} ({self.relation_type})'


# ============================================
# 数据采集模型
# ============================================

class AutoCollectCertificate(TimeStampedModel):
    """
    自动采集凭证
    存储采集服务器/设备的连接信息（密码、密钥等）
    """
    PROTOCOL_CHOICES = [
        ('ssh', 'SSH'),
        ('telnet', 'Telnet'),
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
        ('jdbc', 'JDBC'),
        ('mysql', 'MySQL'),
        ('postgresql', 'PostgreSQL'),
        ('redis', 'Redis'),
        ('mongodb', 'MongoDB'),
        ('snmp', 'SNMP'),
    ]

    PLATFORM_CHOICES = [
        ('Linux', 'Linux'),
        ('Windows', 'Windows'),
        ('Unix', 'Unix'),
        ('Network', '网络设备'),
        ('Database', '数据库'),
    ]

    name = models.CharField(_('凭证名称'), max_length=100)
    protocol = models.CharField(_('协议'), max_length=20, choices=PROTOCOL_CHOICES)
    platform = models.CharField(_('平台类型'), max_length=50, choices=PLATFORM_CHOICES)
    username = models.CharField(_('用户名'), max_length=100)
    password = models.CharField(_('密码'), blank=True, default='')
    private_key = models.TextField(_('私钥'), blank=True, default='')
    private_key_password = models.CharField(_('私钥密码'), max_length=100, blank=True, default='')
    port = models.IntegerField(_('端口'), default=22)
    enable_https = models.BooleanField(_('启用HTTPS'), default=False)
    terminal_type = models.CharField(_('终端类型'), max_length=50, blank=True, default='')
    charset_name = models.CharField(_('字符集'), max_length=50, blank=True, default='UTF-8')
    database_name = models.CharField(_('数据库名'), max_length=100, blank=True, default='')
    enable_encryption = models.BooleanField(_('启用加密'), default=False)
    last_test_time = models.DateTimeField(_('最后测试时间'), null=True, blank=True)
    is_active = models.BooleanField(_('是否启用'), default=True)

    class Meta:
        db_table = 'cmdb_autocollect_certificate'
        verbose_name = _('采集凭证')
        verbose_name_plural = _('采集凭证')

    def __str__(self):
        return f'{self.name} ({self.protocol})'


class AutoCollectTarget(TimeStampedModel):
    """
    自动采集目标
    定义采集的目标对象（IP、设备ID等）
    """
    name = models.CharField(_('目标名称'), max_length=100)
    description = models.TextField(_('描述'), blank=True, default='')
    target_type = models.CharField(_('目标类型'), max_length=50, choices=[
        ('server', '服务器'),
        ('network', '网络设备'),
        ('database', '数据库'),
        ('application', '应用系统'),
        ('custom', '自定义'),
    ])
    ip_address = models.GenericIPAddressField(_('IP地址'))
    card_class = models.ForeignKey(
        Clazz,
        on_delete=models.PROTECT,
        related_name='collect_targets',
        verbose_name=_('关联配置类')
    )
    filter_expression = models.TextField(_('过滤表达式'), blank=True, default='')
    certificate = models.ForeignKey(
        AutoCollectCertificate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targets',
        verbose_name=_('采集凭证')
    )
    collect_script = models.TextField(_('采集脚本'), blank=True, default='')
    parse_rule = models.ForeignKey(
        'AutoCollectParseRule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targets',
        verbose_name=_('解析规则')
    )
    is_active = models.BooleanField(_('是否启用'), default=True)

    class Meta:
        db_table = 'cmdb_autocollect_target'
        verbose_name = _('采集目标')
        verbose_name_plural = _('采集目标')

    def __str__(self):
        return f'{self.name} ({self.ip_address})'


class AutoCollectParseRule(TimeStampedModel):
    """
    解析规则
    定义采集数据的解析规则
    """
    NAME_CHOICES = [
        ('json', 'JSON解析'),
        ('regex', '正则解析'),
        ('csv', 'CSV解析'),
        ('xml', 'XML解析'),
        ('custom', '自定义脚本'),
    ]

    name = models.CharField(_('解析规则名称'), max_length=100)
    rule_type = models.CharField(_('规则类型'), max_length=20, choices=NAME_CHOICES)
    script_type = models.CharField(_('脚本类型'), max_length=20, choices=[
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('bash', 'Bash'),
    ], default='python')
    script_parameters = models.TextField(_('脚本参数（形参）'), blank=True, default='')

    # 解析配置
    script_content = models.TextField(_('脚本内容'))
    script_arguments = models.TextField(_('脚本参数（实参）'), blank=True, default='')
    parse_data_format = models.CharField(_('解析数据格式'), max_length=50, default='json')
    original_data_format = models.CharField(_('原始数据格式'), max_length=50, default='text')

    is_active = models.BooleanField(_('是否启用'), default=True)

    class Meta:
        db_table = 'cmdb_autocollect_parse_rule'
        verbose_name = _('解析规则')
        verbose_name_plural = _('解析规则')

    def __str__(self):
        return f'{self.name} ({self.rule_type})'


class AutoCollectTask(TimeStampedModel):
    """
    自动采集作业
    定义采集任务的基本信息
    """
    NAME_CHOICES = [
        ('snmp', 'SNMP采集'),
        ('http', 'HTTP采集'),
        ('ssh', 'SSH采集'),
        ('jdbc', 'JDBC采集'),
        ('custom', '自定义采集'),
    ]

    TASK_STATUS_CHOICES = [
        ('stopped', '已停止'),
        ('running', '运行中'),
        ('paused', '已暂停'),
        ('error', '错误'),
    ]

    name = models.CharField(_('作业名称'), max_length=100)
    task_type = models.CharField(_('任务类型'), max_length=50, choices=NAME_CHOICES)
    description = models.TextField(_('描述'), blank=True, default='')
    cron_expression = models.CharField(_('Cron表达式'), max_length=100, blank=True, default='')
    interval_seconds = models.IntegerField(_('间隔秒数'), default=3600)
    run_servers = models.TextField(_('运行服务器列表'), blank=True, default='[]')
    targets = models.ManyToManyField(
        AutoCollectTarget,
        related_name='tasks',
        blank=True,
        verbose_name=_('采集目标')
    )
    parse_rule = models.ForeignKey(
        AutoCollectParseRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('解析规则')
    )
    result_map = models.JSONField(_('结果映射'), default=dict)
    is_active = models.BooleanField(_('是否启用'), default=True)
    status = models.CharField(_('状态'), max_length=20, choices=TASK_STATUS_CHOICES, default='stopped')
    last_run_time = models.DateTimeField(_('最后运行时间'), null=True, blank=True)
    next_run_time = models.DateTimeField(_('下次运行时间'), null=True, blank=True)
    run_count = models.IntegerField(_('运行次数'), default=0)
    error_message = models.TextField(_('错误信息'), blank=True, default='')

    class Meta:
        db_table = 'cmdb_autocollect_task'
        verbose_name = _('采集作业')
        verbose_name_plural = _('采集作业')

    def __str__(self):
        return f'{self.name} ({self.task_type})'


class AutoCollectTaskInstance(TimeStampedModel):
    """
    采集任务实例
    记录每次采集任务的具体执行情况
    """
    TASK_STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '执行中'),
        ('success', '成功'),
        ('failed', '失败'),
    ]

    task = models.ForeignKey(
        AutoCollectTask,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name=_('采集任务')
    )
    target = models.ForeignKey(
        AutoCollectTarget,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name=_('采集目标')
    )
    status = models.CharField(_('状态'), max_length=20, choices=TASK_STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField(_('开始时间'), null=True, blank=True)
    end_time = models.DateTimeField(_('结束时间'), null=True, blank=True)
    duration = models.IntegerField(_('耗时（秒）'), null=True, blank=True)
    log_content = models.TextField(_('日志内容'), blank=True, default='')
    error_message = models.TextField(_('错误信息'), blank=True, default='')

    class Meta:
        db_table = 'cmdb_autocollect_task_instance'
        verbose_name = _('采集任务实例')
        verbose_name_plural = _('采集任务实例')
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.task.name} - {self.target.name} ({self.status})'


# ============================================
# 定时任务模型
# ============================================

class ScheduledJob(TimeStampedModel):
    """
    定时任务
    独立于采集任务的定时任务
    """
    TASK_TYPE_CHOICES = [
        ('email', '邮件发送'),
        ('report', '报表生成'),
        ('backup', '数据备份'),
        ('cleanup', '数据清理'),
        ('sync', '数据同步'),
        ('custom', '自定义'),
    ]

    JOB_STATUS_CHOICES = [
        ('stopped', '已停止'),
        ('running', '运行中'),
        ('paused', '已暂停'),
        ('error', '错误'),
    ]

    name = models.CharField(_('任务名称'), max_length=100)
    task_type = models.CharField(_('任务类型'), max_length=50, choices=TASK_TYPE_CHOICES)
    description = models.TextField(_('描述'), blank=True, default='')
    cron_expression = models.CharField(_('Cron表达式'), max_length=100, blank=True, default='')
    is_active = models.BooleanField(_('是否启用'), default=True)
    status = models.CharField(_('状态'), max_length=20, choices=JOB_STATUS_CHOICES, default='stopped')
    last_run_time = models.DateTimeField(_('最后运行时间'), null=True, blank=True)
    next_run_time = models.DateTimeField(_('下次运行时间'), null=True, blank=True)
    run_count = models.IntegerField(_('运行次数'), default=0)
    error_message = models.TextField(_('错误信息'), blank=True, default='')
    log_content = models.TextField(_('日志内容'), blank=True, default='')

    class Meta:
        db_table = 'cmdb_scheduled_job'
        verbose_name = _('定时任务')
        verbose_name_plural = _('定时任务')

    def __str__(self):
        return f'{self.name} ({self.task_type})'
