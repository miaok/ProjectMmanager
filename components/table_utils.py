import streamlit as st
import pandas as pd

# 定义所有可能的列名及其中文翻译
COLUMN_TRANSLATIONS = {
    # 人员表
    'name': '姓名',  # 人员表中的name是姓名
    'gender': '性别',
    'birth_date': '出生日期',
    'id_card': '身份证号',
    'education': '学历',
    'school': '毕业学校',
    'graduation_date': '毕业日期',
    'major': '专业',
    'title': '职称',
    'phone': '电话',
    'department': '部门',
    'position': '职位',
    'skill_level': '技能等级',

    # 项目表
    'project_name': '项目名称',  # 项目表中的name是项目名称
    'start_date': '开始日期',
    'end_date': '结束日期',
    'leader': '负责人',
    'leader_id': '负责人ID',
    'members': '成员',
    'status': '状态',
    'outcome': '成果',

    # 标准表
    'standard_name': '标准名称',  # 标准表中的name是标准名称
    'type': '类型',
    'code': '标准号',
    'release_date': '发布日期',
    'implementation_date': '实施日期',
    'company': '单位',
    'participant': '参与人员',
    'participant_id': '参与人员ID',

    # 专利表
    'patent_name': '专利名称',  # 专利表中的name是专利名称
    'application_date': '申请日期',
    'grant_date': '授权日期',
    'owner': '专利所有人',
    'owner_id': '专利所有人ID',
    'participants': '参与人员',
    'patent_number': '专利号',
    'certificate': '证书状态',

    # 论文表
    'title': '标题',
    'journal': '期刊',
    'journal_type': '期刊类型',
    'publish_date': '发表日期',
    'volume_info': '卷期信息',
    'first_author': '第一作者',
    'first_author_id': '第一作者ID',
    'co_authors': '参与作者',
    'organization': '组织/单位',

    # 其他通用字段
    'id': 'ID',
    'count': '数量',
    '负责人': '负责人',
    '成员': '成员',
    '第一作者': '第一作者',
    '参与作者': '参与作者',
    '参与人员': '参与人员',
    '专利所有人': '专利所有人',
    '数据类型': '数据类型'
}

# 原默认显示列定义
# DEFAULT_DISPLAY_COLUMNS = {
#     'person': ['姓名', '性别', '部门', '职位', '学历', '职称', '技能等级', '电话'],
#     'project': ['项目名称', '开始日期', '结束日期', '负责人', '状态', '成果'],
#     'standard': ['标准名称', '类型', '标准号', '发布日期', '实施日期', '单位', '参与人员'],
#     'patent': ['专利名称', '类型', '申请日期', '授权日期', '专利所有人', '专利号', '证书状态'],
#     'paper': ['标题', '期刊', '期刊类型', '发表日期', '卷期信息', '第一作者', '组织/单位']
# }

# 原所有可选列定义
# ALL_AVAILABLE_COLUMNS = {
#     'person': ['姓名', '性别', '出生日期', '部门', '职位', '学历', '毕业学校', '毕业日期', '专业', '职称', '技能等级', '电话'],
#     'project': ['项目名称', '开始日期', '结束日期', '负责人', '成员', '状态', '成果'],
#     'standard': ['标准名称', '类型', '标准号', '发布日期', '实施日期', '单位', '参与人员'],
#     'patent': ['专利名称', '类型', '申请日期', '授权日期', '专利所有人', '参与人员', '专利号', '证书状态', '单位'],
#     'paper': ['标题', '期刊', '期刊类型', '发表日期', '卷期信息', '第一作者', '参与作者', '组织/单位']
# }

def translate_columns(df, entity_type=None):
    """
    将DataFrame的列名翻译为中文

    参数:
    - df: 要处理的DataFrame
    - entity_type: 实体类型，用于处理特殊列

    返回:
    - 处理后的DataFrame副本，确保列名唯一
    """
    # 创建DataFrame的副本
    display_df = df.copy()

    # 翻译列名
    rename_dict = {}
    for col in display_df.columns:
        if col in COLUMN_TRANSLATIONS:
            # 特殊处理人员表中的title字段
            if entity_type == 'person' and col == 'title':
                rename_dict[col] = '职称'
            else:
                rename_dict[col] = COLUMN_TRANSLATIONS[col]

    # 应用翻译
    if rename_dict:
        display_df = display_df.rename(columns=rename_dict)

    # 处理可能的重复列名
    # 获取所有列名
    columns = list(display_df.columns)

    # 检查是否有重复列名
    if len(columns) != len(set(columns)):
        # 创建一个新的列名列表，确保唯一性
        new_columns = []
        seen = set()

        for i, col in enumerate(columns):
            if col in seen:
                # 如果列名已经存在，添加一个后缀
                count = 1
                new_col = f"{col}_{count}"
                while new_col in seen:
                    count += 1
                    new_col = f"{col}_{count}"
                new_columns.append(new_col)
                seen.add(new_col)
            else:
                new_columns.append(col)
                seen.add(col)

        # 重命名列
        display_df.columns = new_columns

    return display_df

def display_dataframe(df, entity_type, key_suffix=None):
    """
    使用dashboard风格显示DataFrame，支持内置的列选择和排序功能
    默认不显示ID列和index列

    参数:
    - df: 要显示的DataFrame
    - entity_type: 实体类型
    - key_suffix: 会话状态键的后缀（保留参数以兼容现有代码，但不再使用）
    """
    # 忽略key_suffix参数，保留它只是为了兼容现有代码
    if df.empty:
        st.info(f"暂无{entity_type}数据")
        return

    # 翻译列名
    display_df = translate_columns(df, entity_type)

    # 移除ID列（包括'id'和任何以'ID'结尾的列）
    id_columns = [col for col in display_df.columns if col.lower() == 'id' or col.endswith('ID') or col == 'ID']
    if id_columns:
        display_df = display_df.drop(columns=id_columns)

    # 创建列配置
    column_config = {}

    # 根据不同实体类型配置列
    if entity_type == 'person':
        # 人员表列配置
        column_config = {
            "姓名": st.column_config.TextColumn("姓名"),
            "性别": st.column_config.TextColumn("性别"),
            "出生日期": st.column_config.DateColumn("出生日期", format="YYYY-MM-DD"),
            "部门": st.column_config.TextColumn("部门"),
            "职位": st.column_config.TextColumn("职位"),
            "学历": st.column_config.TextColumn("学历"),
            "职称": st.column_config.TextColumn("职称"),
            "技能等级": st.column_config.TextColumn("技能等级"),
            "电话": st.column_config.TextColumn("电话")
        }
    elif entity_type == 'project':
        # 项目表列配置
        column_config = {
            "项目名称": st.column_config.TextColumn("项目名称"),
            "开始日期": st.column_config.DateColumn("开始日期", format="YYYY-MM-DD"),
            "结束日期": st.column_config.DateColumn("结束日期", format="YYYY-MM-DD"),
            "负责人": st.column_config.TextColumn("负责人"),
            "成员": st.column_config.TextColumn("成员"),
            "状态": st.column_config.TextColumn("状态"),
            "成果": st.column_config.TextColumn("成果")
        }
    elif entity_type == 'standard':
        # 标准表列配置
        column_config = {
            "标准名称": st.column_config.TextColumn("标准名称"),
            "类型": st.column_config.TextColumn("类型"),
            "标准号": st.column_config.TextColumn("标准号"),
            "发布日期": st.column_config.DateColumn("发布日期", format="YYYY-MM-DD"),
            "实施日期": st.column_config.DateColumn("实施日期", format="YYYY-MM-DD"),
            "单位": st.column_config.TextColumn("单位"),
            "参与人员": st.column_config.TextColumn("参与人员")
        }
    elif entity_type == 'patent':
        # 专利表列配置
        column_config = {
            "专利名称": st.column_config.TextColumn("专利名称"),
            "类型": st.column_config.TextColumn("类型"),
            "申请日期": st.column_config.DateColumn("申请日期", format="YYYY-MM-DD"),
            "授权日期": st.column_config.DateColumn("授权日期", format="YYYY-MM-DD"),
            "专利所有人": st.column_config.TextColumn("专利所有人"),
            "参与人员": st.column_config.TextColumn("参与人员"),
            "专利号": st.column_config.TextColumn("专利号"),
            "证书状态": st.column_config.TextColumn("证书状态"),
            "单位": st.column_config.TextColumn("单位")
        }
    elif entity_type == 'paper':
        # 论文表列配置
        column_config = {
            "标题": st.column_config.TextColumn("标题"),
            "期刊": st.column_config.TextColumn("期刊"),
            "期刊类型": st.column_config.TextColumn("期刊类型"),
            "发表日期": st.column_config.DateColumn("发表日期", format="YYYY-MM-DD"),
            "卷期信息": st.column_config.TextColumn("卷期信息"),
            "第一作者": st.column_config.TextColumn("第一作者"),
            "参与作者": st.column_config.TextColumn("参与作者"),
            "组织/单位": st.column_config.TextColumn("组织/单位")
        }

    # 重置索引，使其从1开始计数
    display_df = display_df.reset_index(drop=True)
    display_df.index = display_df.index + 1  # 索引从1开始

    # 显示DataFrame，使用dashboard风格，显示索引列
    st.dataframe(
        display_df,
        column_config=column_config,
        hide_index=False,  # 显示索引列
        use_container_width=True
    )
