import streamlit as st
import pandas as pd
from components.db_utils import get_connection
from components.advanced_search import advanced_search
import io
import base64

st.set_page_config(
    page_title="高级搜索",
    page_icon="🔎",
    layout="wide"
)

# 页面标题
st.title("高级搜索")

# 说明
st.markdown("""
本页面提供强大的高级搜索功能，支持多条件组合搜索、模糊搜索、关键词搜索和结果排序。

您可以通过以下方式搜索数据：
- **全局搜索**：在所有数据表中查找匹配的关键词，返回所有相关结果
- **关键词搜索**：在所有相关字段中查找匹配的关键词
- **多条件组合**：同时使用多个条件进行精确筛选
- **日期范围筛选**：按日期范围进行筛选
- **排序功能**：按指定字段升序或降序排列结果
- **分页显示**：大量结果分页显示，便于浏览

搜索结果可以导出为Excel文件。
""")

# 创建选项卡
search_tab_global, search_tab1, search_tab2, search_tab3, search_tab4, search_tab5 = st.tabs([
    "全局搜索", "人员搜索", "项目搜索", "标准搜索", "专利搜索", "论文搜索"
])

# 全局搜索函数
def global_search(keyword):
    """
    在所有表中搜索关键词，返回所有匹配的结果

    参数:
    - keyword: 搜索关键词

    返回:
    - dict: 包含各表搜索结果的字典
    """
    if not keyword:
        return {}

    conn = get_connection()
    results = {}

    # 定义各表的可搜索文本字段
    searchable_fields = {
        'person': ['name', 'department', 'position', 'major', 'school', 'phone', 'id_card'],
        'project': ['name', 'outcome'],
        'standard': ['name', 'code', 'company'],
        'patent': ['name', 'company', 'patent_number'],
        'paper': ['title', 'journal', 'organization', 'volume_info']
    }

    # 定义各表的显示名称
    table_display_names = {
        'person': '人员',
        'project': '项目',
        'standard': '标准',
        'patent': '专利',
        'paper': '论文'
    }

    # 在每个表中搜索
    for table, fields in searchable_fields.items():
        # 构建查询条件
        conditions = []
        params = []

        # 对所有可搜索字段进行搜索
        for field in fields:
            conditions.append(f"{field} LIKE ?")
            params.append(f"%{keyword}%")

        # 特殊处理：如果关键词是人名，尝试在相关ID字段中查找
        if table != 'person':
            try:
                # 尝试在人员表中查找匹配的人员
                person_query = "SELECT id, name FROM person WHERE name LIKE ?"
                person_df = pd.read_sql(person_query, conn, params=[f"%{keyword}%"])

                if not person_df.empty:
                    # 找到了匹配的人员，根据表类型添加相应的搜索条件
                    for _, person in person_df.iterrows():
                        person_id = person['id']

                        if table == 'project':
                            # 搜索项目的负责人和成员
                            conditions.append(f"leader_id = ?")
                            params.append(person_id)
                            conditions.append(f"members LIKE ?")
                            params.append(f"%{person_id}%")

                        elif table == 'standard':
                            # 搜索标准的参与人员
                            conditions.append(f"participant_id = ?")
                            params.append(person_id)

                        elif table == 'patent':
                            # 搜索专利的所有人和参与人员
                            conditions.append(f"owner_id = ?")
                            params.append(person_id)
                            conditions.append(f"participants LIKE ?")
                            params.append(f"%{person_id}%")

                        elif table == 'paper':
                            # 搜索论文的第一作者和参与作者
                            conditions.append(f"first_author_id = ?")
                            params.append(person_id)
                            conditions.append(f"co_authors LIKE ?")
                            params.append(f"%{person_id}%")
            except Exception as e:
                # 如果查询失败，忽略这部分搜索条件
                pass

        # 构建SQL查询
        query = f"SELECT * FROM {table}"
        if conditions:
            query += " WHERE " + " OR ".join(conditions)

        # 执行查询
        try:
            df = pd.read_sql(query, conn, params=params)

            # 如果有结果，添加表名列
            if not df.empty:
                df['数据类型'] = table_display_names.get(table, table)

                # 处理特殊字段（如外键关联）
                if table in ['project', 'standard', 'patent', 'paper']:
                    # 获取人员信息用于显示
                    persons_df = pd.read_sql("SELECT id, name FROM person", conn)
                    persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

                    if table == 'project':
                        # 处理负责人
                        df['负责人'] = df['leader_id'].apply(
                            lambda x: persons_dict.get(x, "未找到") if x and x in persons_dict else "无"
                        )

                        # 处理成员
                        def format_members(members_str):
                            if not members_str:
                                return ""
                            try:
                                member_ids = [int(m_id) for m_id in members_str.split(",")]
                                return ", ".join([persons_dict.get(m_id, f"ID:{m_id}") for m_id in member_ids])
                            except:
                                return members_str

                        df['成员'] = df['members'].apply(format_members)

                    elif table == 'standard':
                        # 处理参与人员
                        df['参与人员'] = df['participant_id'].apply(
                            lambda x: persons_dict.get(x, "无") if x else "无"
                        )

                    elif table == 'patent':
                        # 处理专利所有人
                        df['专利所有人'] = df['owner_id'].apply(
                            lambda x: persons_dict.get(x, "无") if x else "无"
                        )

                        # 处理参与人员
                        def format_participants(participants_str):
                            if not participants_str:
                                return ""
                            try:
                                participant_ids = [int(p_id) for p_id in participants_str.split(",")]
                                return ", ".join([persons_dict.get(p_id, f"ID:{p_id}") for p_id in participant_ids])
                            except:
                                return participants_str

                        df['参与人员'] = df['participants'].apply(format_participants)

                    elif table == 'paper':
                        # 处理第一作者
                        df['第一作者'] = df['first_author_id'].apply(
                            lambda x: persons_dict.get(x, "无") if x else "无"
                        )

                        # 处理参与作者
                        def format_co_authors(co_authors_str):
                            if not co_authors_str:
                                return ""
                            try:
                                co_author_ids = [int(a_id) for a_id in co_authors_str.split(",")]
                                return ", ".join([persons_dict.get(a_id, f"ID:{a_id}") for a_id in co_author_ids])
                            except:
                                return co_authors_str

                        df['参与作者'] = df['co_authors'].apply(format_co_authors)

                # 添加到结果字典
                results[table] = df
        except Exception as e:
            st.error(f"搜索{table_display_names.get(table, table)}表时出错: {str(e)}")

    conn.close()
    return results

# 生成Excel下载链接的函数
def get_excel_download_link(df, filename):
    # 使用BytesIO对象保存Excel文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    # 获取二进制数据并转换为base64
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()

    # 生成下载链接
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">下载Excel文件</a>'
    return href

# 全局搜索
with search_tab_global:
    st.subheader("全局搜索")

    # 创建搜索输入框
    global_keyword = st.text_input("请输入搜索关键词", key="global_search_keyword")

    # 搜索按钮
    search_button = st.button("搜索", key="global_search_button")

    # 如果点击了搜索按钮或输入了关键词，执行搜索
    if search_button or global_keyword:
        if not global_keyword:
            st.warning("请输入搜索关键词")
        else:
            # 执行全局搜索
            results = global_search(global_keyword)

            if not results:
                st.info("未找到符合条件的记录")
            else:
                # 显示搜索结果
                total_count = sum(len(df) for df in results.values())
                st.success(f"共找到 {total_count} 条相关记录")

                # 定义各表的显示字段
                display_fields = {
                    'person': ['数据类型', 'name', 'gender', 'department', 'position', 'education', 'title', 'skill_level', 'phone'],
                    'project': ['数据类型', 'name', 'start_date', 'end_date', '负责人', '成员', 'status', 'outcome'],
                    'standard': ['数据类型', 'name', 'type', 'code', 'release_date', 'implementation_date', 'company', '参与人员'],
                    'patent': ['数据类型', 'name', 'type', 'application_date', 'grant_date', '专利所有人', '参与人员', 'patent_number', 'certificate'],
                    'paper': ['数据类型', 'title', 'journal', 'journal_type', 'publish_date', '第一作者', '参与作者', 'organization']
                }

                # 显示各表的搜索结果
                for table, df in results.items():
                    if not df.empty:
                        # 获取表的中文名称
                        table_name = {'person': '人员', 'project': '项目', 'standard': '标准', 'patent': '专利', 'paper': '论文'}.get(table, table)

                        # 显示表名和结果数量
                        st.markdown(f"### {table_name}（{len(df)}条结果）")

                        # 选择要显示的列
                        if table in display_fields:
                            display_columns = [col for col in display_fields[table] if col in df.columns]
                            # 重命名列
                            rename_dict = {
                                'name': '姓名/名称',
                                'title': '标题/职称',
                                'gender': '性别',
                                'department': '部门',
                                'position': '职位',
                                'education': '学历',
                                'skill_level': '技能等级',
                                'phone': '电话',
                                'start_date': '开始日期',
                                'end_date': '结束日期',
                                'status': '状态',
                                'outcome': '成果',
                                'type': '类型',
                                'code': '标准号',
                                'release_date': '发布日期',
                                'implementation_date': '实施日期',
                                'company': '单位',
                                'application_date': '申请日期',
                                'grant_date': '授权日期',
                                'patent_number': '专利号',
                                'certificate': '证书状态',
                                'journal': '期刊',
                                'journal_type': '期刊类型',
                                'publish_date': '发表日期',
                                'organization': '组织/单位',
                            }
                            display_df = df[display_columns].copy()
                            display_df = display_df.rename(columns=rename_dict)
                            st.dataframe(display_df)
                        else:
                            st.dataframe(df)

                # 合并所有结果用于导出
                all_results = []
                for table, df in results.items():
                    if not df.empty:
                        # 添加到合并结果
                        all_results.append(df)

                if all_results:
                    # 合并所有结果
                    combined_df = pd.concat(all_results, ignore_index=True)

                    # 提供导出功能
                    st.markdown("### 导出所有搜索结果")
                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"全局搜索结果_{timestamp}.xlsx"
                    st.markdown(get_excel_download_link(combined_df, filename), unsafe_allow_html=True)

# 人员搜索
with search_tab1:
    st.subheader("人员高级搜索")

    # 使用高级搜索组件
    person_df = advanced_search('person')

    # 如果有搜索结果，提供导出功能
    if not person_df.empty:
        st.markdown("### 导出搜索结果")
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"人员搜索结果_{timestamp}.xlsx"
        st.markdown(get_excel_download_link(person_df, filename), unsafe_allow_html=True)

# 项目搜索
with search_tab2:
    st.subheader("项目高级搜索")

    # 使用高级搜索组件
    project_df = advanced_search('project')

    # 如果有搜索结果，提供导出功能
    if not project_df.empty:
        # 获取人员信息用于显示
        conn = get_connection()
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)
        persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

        # 处理负责人
        project_df['leader'] = project_df['leader_id'].apply(
            lambda x: persons_dict.get(x, "未找到") if x and x in persons_dict else "无"
        )

        # 处理成员
        def format_members(members_str):
            if not members_str:
                return ""
            try:
                member_ids = [int(m_id) for m_id in members_str.split(",")]
                return ", ".join([persons_dict.get(m_id, f"ID:{m_id}") for m_id in member_ids])
            except:
                return members_str

        project_df['members_display'] = project_df['members'].apply(format_members)

        # 准备导出数据
        export_df = project_df.copy()
        export_df['负责人'] = export_df['leader']
        export_df['成员'] = export_df['members_display']

        st.markdown("### 导出搜索结果")
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"项目搜索结果_{timestamp}.xlsx"
        st.markdown(get_excel_download_link(export_df, filename), unsafe_allow_html=True)

        conn.close()

# 标准搜索
with search_tab3:
    st.subheader("标准高级搜索")

    # 使用高级搜索组件
    standard_df = advanced_search('standard')

    # 如果有搜索结果，提供导出功能
    if not standard_df.empty:
        # 获取人员信息用于显示
        conn = get_connection()
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)
        persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

        # 处理参与人员
        standard_df['participant'] = standard_df['participant_id'].apply(
            lambda x: persons_dict.get(x, "无") if x else "无"
        )

        # 准备导出数据
        export_df = standard_df.copy()
        export_df['参与人员'] = export_df['participant']

        st.markdown("### 导出搜索结果")
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"标准搜索结果_{timestamp}.xlsx"
        st.markdown(get_excel_download_link(export_df, filename), unsafe_allow_html=True)

        conn.close()

# 专利搜索
with search_tab4:
    st.subheader("专利高级搜索")

    # 使用高级搜索组件
    patent_df = advanced_search('patent')

    # 如果有搜索结果，提供导出功能
    if not patent_df.empty:
        # 获取人员信息用于显示
        conn = get_connection()
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)
        persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

        # 定义格式化函数
        def format_owner(owner_id):
            if pd.isna(owner_id) or owner_id is None:
                return "无"
            return persons_dict.get(owner_id, f"ID:{owner_id}")

        def format_participants(participants_str):
            if not participants_str:
                return ""
            try:
                participant_ids = [int(p_id) for p_id in participants_str.split(",")]
                return ", ".join([persons_dict.get(p_id, f"ID:{p_id}") for p_id in participant_ids])
            except:
                return participants_str

        # 格式化显示数据
        patent_df['专利所有人'] = patent_df['owner_id'].apply(format_owner)
        patent_df['参与人员'] = patent_df['participants'].apply(format_participants)

        # 准备导出数据
        export_df = patent_df.copy()

        st.markdown("### 导出搜索结果")
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"专利搜索结果_{timestamp}.xlsx"
        st.markdown(get_excel_download_link(export_df, filename), unsafe_allow_html=True)

        conn.close()

# 论文搜索
with search_tab5:
    st.subheader("论文高级搜索")

    # 使用高级搜索组件
    paper_df = advanced_search('paper')

    # 如果有搜索结果，提供导出功能
    if not paper_df.empty:
        # 获取人员信息用于显示
        conn = get_connection()
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)
        persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

        # 定义格式化函数
        def format_first_author(author_id):
            if pd.isna(author_id) or author_id is None:
                return "无"
            return persons_dict.get(author_id, f"ID:{author_id}")

        def format_co_authors(co_authors_str):
            if not co_authors_str:
                return ""
            try:
                co_author_ids = [int(a_id) for a_id in co_authors_str.split(",")]
                return ", ".join([persons_dict.get(a_id, f"ID:{a_id}") for a_id in co_author_ids])
            except:
                return co_authors_str

        # 格式化显示数据
        paper_df['第一作者'] = paper_df['first_author_id'].apply(format_first_author)
        paper_df['参与作者'] = paper_df['co_authors'].apply(format_co_authors)

        # 准备导出数据
        export_df = paper_df.copy()

        st.markdown("### 导出搜索结果")
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"论文搜索结果_{timestamp}.xlsx"
        st.markdown(get_excel_download_link(export_df, filename), unsafe_allow_html=True)

        conn.close()
