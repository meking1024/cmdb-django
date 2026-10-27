"""CMDB Streamlit UI. Run with: streamlit run streamlit_app.py"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

import streamlit as st
import pandas as pd
from django.db import transaction
from django.db.models import Q
from cmdb.models import (
    Attribute, AutoCollectParseRule, Card, CardHistory, CardLookup, Clazz,
)

st.set_page_config(page_title='CMDB 管理平台', page_icon='🖥️', layout='wide')
st.title('🖥️ CMDB 管理平台')

with st.sidebar:
    st.header('CMDB 管理')
    section = st.radio('导航', ['概览', 'CI 管理', '模型设计', '自动采集', '系统设置'])
    if section == '自动采集':
        page = st.radio('自动采集', ['解析规则', '采集目标', '采集作业'], label_visibility='collapsed')
    elif section == 'CI 管理':
        page = st.radio('CI 管理', ['实例列表', '新增实例'], label_visibility='collapsed')
    elif section == '模型设计':
        page = '配置类'
    else:
        page = section


def parse_rule_form(rule=None, key_prefix='rule'):
    """Create or edit one parser rule, including the fields shown in the reference UI."""
    with st.form(f'{key_prefix}-form'):
        name = st.text_input('解析规则名称 *', value=rule.name if rule else '', max_chars=100)
        script_types = ['javascript', 'python', 'bash']
        old_type = rule.script_type if rule else 'javascript'
        script_type = st.selectbox('脚本类型', script_types,
                                   index=script_types.index(old_type) if old_type in script_types else 0)
        rule_types = ['json', 'regex', 'csv', 'xml', 'custom']
        old_rule_type = rule.rule_type if rule else 'custom'
        rule_type = st.selectbox('解析方式', rule_types,
                                 index=rule_types.index(old_rule_type) if old_rule_type in rule_types else 0)
        parameters = st.text_area('脚本参数（形参）', value=rule.script_parameters if rule else '', height=80)
        script = st.text_area('脚本内容 *', value=rule.script_content if rule else '', height=220,
                              placeholder='输入解析脚本内容')
        arguments = st.text_area('脚本参数（实参）', value=rule.script_arguments if rule else '', height=80)
        data_format = st.text_input('解析数据格式', value=rule.parse_data_format if rule else 'json')
        original_format = st.text_input('原始数据格式', value=rule.original_data_format if rule else 'text')
        active = st.checkbox('启用', value=rule.is_active if rule else True)
        saved = st.form_submit_button('保存', type='primary', width='stretch')
    if not saved:
        return
    if not name.strip() or not script.strip():
        st.error('解析规则名称和脚本内容为必填项。')
        return
    values = {
        'name': name.strip(), 'script_type': script_type, 'rule_type': rule_type,
        'script_parameters': parameters, 'script_content': script,
        'script_arguments': arguments, 'parse_data_format': data_format.strip() or 'json',
        'original_data_format': original_format.strip() or 'text', 'is_active': active,
    }
    if rule:
        for field, value in values.items():
            setattr(rule, field, value)
        rule.save()
        st.success('解析规则已更新。')
    else:
        AutoCollectParseRule.objects.create(**values)
        st.success('解析规则已创建。')
    st.rerun()


if page == '解析规则':
    st.subheader('自动采集 / 解析规则')
    toolbar_left, toolbar_mid, toolbar_right = st.columns([1, 1, 3])
    if toolbar_left.button('🔄 刷新'):
        st.rerun()
    create_mode = toolbar_mid.button('＋ 创建')
    search = toolbar_right.text_input('搜索解析规则', placeholder='输入规则名称', label_visibility='collapsed')
    if create_mode:
        st.markdown('#### 创建解析规则')
        parse_rule_form(key_prefix='create-rule')
        st.divider()

    rules = AutoCollectParseRule.objects.all().order_by('name')
    if search.strip():
        rules = rules.filter(Q(name__icontains=search.strip()))
    total = rules.count()
    page_size = st.selectbox('每页条数', [10, 20, 50], index=0, key='rules-page-size')
    pages = max(1, (total + page_size - 1) // page_size)
    current_page = st.number_input('页码', min_value=1, max_value=pages, value=1, step=1,
                                   label_visibility='collapsed', key='rules-page')
    current_rules = list(rules[(current_page - 1) * page_size:current_page * page_size])
    st.caption(f'共 {total} 条 · 第 {current_page}/{pages} 页')
    rule_rows = [{'解析规则名称': r.name, '脚本类型': r.get_script_type_display(),
                  '规则类型': r.get_rule_type_display(), '状态': '启用' if r.is_active else '停用',
                  '更新时间': r.updated_at.strftime('%Y-%m-%d %H:%M')}
                 for r in current_rules]
    st.dataframe(pd.DataFrame(rule_rows, columns=['解析规则名称', '脚本类型', '规则类型', '状态', '更新时间']),
                 width='stretch', hide_index=True)

    if current_rules:
        selected_id = st.selectbox('选择规则以编辑或删除', [r.id for r in current_rules],
                                   format_func=lambda rid: next(r.name for r in current_rules if r.id == rid))
        selected_rule = next(r for r in current_rules if r.id == selected_id)
        edit_col, delete_col = st.columns([1, 1])
        with edit_col:
            with st.expander('✏️ 编辑所选规则'):
                parse_rule_form(selected_rule, key_prefix=f'edit-rule-{selected_id}')
        with delete_col:
            with st.form(f'delete-rule-{selected_id}'):
                confirmed = st.checkbox(f'确认删除「{selected_rule.name}」')
                delete = st.form_submit_button('🗑 删除', type='secondary')
            if delete:
                if confirmed:
                    selected_rule.delete()
                    st.success('解析规则已删除。')
                    st.rerun()
                st.error('请先勾选确认框。')

elif page == '概览':
    st.subheader('CMDB 概览')
    a, b, c, d = st.columns(4)
    a.metric('配置类', Clazz.objects.count())
    b.metric('属性定义', Attribute.objects.count())
    c.metric('配置实例', Card.objects.count())
    d.metric('解析规则', AutoCollectParseRule.objects.count())
    st.subheader('最近创建的配置实例')
    st.dataframe([{'编码': c.code, '配置类': c.clazz.name, '状态': '启用' if c.is_active else '停用',
                   '创建时间': c.created_at.strftime('%Y-%m-%d %H:%M')}
                  for c in Card.objects.select_related('clazz').order_by('-created_at')[:10]],
                 width='stretch', hide_index=True)

elif page == '配置类':
    st.subheader('模型设计 / 配置类')
    with st.form('create-class'):
        name = st.text_input('配置类名称')
        description = st.text_area('描述')
        create = st.form_submit_button('创建配置类', type='primary')
    if create:
        if not name.strip():
            st.error('配置类名称不能为空。')
        else:
            Clazz.objects.create(name=name.strip(), description=description)
            st.success('配置类已创建。')
            st.rerun()
    for clazz in Clazz.objects.prefetch_related('attributes').order_by('name'):
        with st.expander(f'{clazz.name} — {clazz.description}'):
            st.dataframe([{'属性': a.name, '显示名': a.display_name, '类型': a.data_type,
                           '必填': '是' if a.is_required else '否'}
                          for a in clazz.attributes.all().order_by('order')],
                         width='stretch', hide_index=True)

elif page in ('实例列表', '新增实例'):
    if page == '实例列表':
        st.subheader('CI 管理 / 配置实例')
        clazzes = list(Clazz.objects.order_by('name'))
        clazz_name = st.selectbox('配置类', ['全部'] + [c.name for c in clazzes])
        term = st.text_input('搜索实例编码')
        cards = Card.objects.select_related('clazz').prefetch_related('lookups__attribute').order_by('-created_at')
        if clazz_name != '全部':
            cards = cards.filter(clazz__name=clazz_name)
        if term.strip():
            cards = cards.filter(code__icontains=term.strip())
        st.caption(f'共 {cards.count()} 个实例')
        st.dataframe([{'编码': card.code, '配置类': card.clazz.name,
                       '属性': ' | '.join(f'{x.attribute.display_name}: {x.value}' for x in card.lookups.all()),
                       '状态': '启用' if card.is_active else '停用'} for card in cards[:200]],
                     width='stretch', hide_index=True)
    else:
        st.subheader('CI 管理 / 新增实例')
        clazzes = list(Clazz.objects.order_by('name'))
        if not clazzes:
            st.info('请先在“模型设计”中创建配置类。')
        else:
            clazz = st.selectbox('选择配置类', clazzes, format_func=lambda c: c.name)
            attributes = list(clazz.attributes.order_by('order'))
            with st.form('create-card'):
                code = st.text_input('实例编码 *')
                values = {}
                for attr in attributes:
                    label = f'{attr.display_name}{" *" if attr.is_required else ""}'
                    if attr.display_type in ('select', 'radio') and attr.options:
                        values[attr] = st.selectbox(label, [''] + list(attr.options))
                    elif attr.display_type == 'textarea' or attr.data_type == 'text':
                        values[attr] = st.text_area(label, value=attr.default_value)
                    else:
                        values[attr] = st.text_input(label, value=attr.default_value)
                save = st.form_submit_button('创建实例', type='primary')
            if save:
                missing = [attr.display_name for attr, value in values.items() if attr.is_required and not str(value).strip()]
                if not code.strip() or missing:
                    st.error('请填写实例编码和必填属性' + (f'：{", ".join(missing)}' if missing else '。'))
                else:
                    try:
                        with transaction.atomic():
                            card = Card.objects.create(clazz=clazz, code=code.strip())
                            entries = {attr.name: value for attr, value in values.items() if str(value).strip()}
                            CardLookup.objects.bulk_create([
                                CardLookup(card=card, attribute=attr, value=str(value))
                                for attr, value in values.items() if str(value).strip()
                            ])
                            CardHistory.objects.create(card=card, version=1,
                                                       content={'code': card.code, 'attribute_values': entries})
                        st.success(f'实例 {card.code} 创建成功。')
                        st.rerun()
                    except Exception as exc:
                        st.error(f'创建失败：{exc}')

elif page in ('采集目标', '采集作业'):
    st.subheader(f'自动采集 / {page}')
    st.info('该页面的数据库模型已定义；当前迭代先提供解析规则完整管理，采集连接与作业执行流程尚未接入。')

else:
    st.subheader('系统设置')
    st.write('数据库：PostgreSQL')
    st.write('前端：Streamlit')
    st.write(f'解析规则：{AutoCollectParseRule.objects.count()} 条')
