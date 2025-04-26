import streamlit as st
import pandas as pd
from components.db_utils import get_connection

def advanced_search(entity_type):
    """
    高级搜索组件，支持多条件组合搜索、模糊搜索、关键词搜索和结果排序

    参数:
    - entity_type: 实体类型，可选值为 'person', 'project', 'standard', 'patent', 'paper'

    返回:
    - DataFrame: 搜索结果
    """
    # 定义各实体类型的字段映射
    field_mappings = {
        'person': {
            'name': '姓名',
            'gender': '性别',
            'birth_date': '出生日期',
            'id_card': '身份证号',
            'education': '学历',
            'school': '毕业学校',
            'graduation_date': '毕业日期',
            'major': '专业',
            'title': '职称',
            'phone': '手机号码',
            'department': '部门',
            'position': '职位',
            'skill_level': '技能等级'
        },
        'project': {
            'name': '项目名称',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'leader_id': '负责人',
            'members': '项目成员',
            'status': '状态',
            'outcome': '成果'
        },
        'standard': {
            'name': '标准名称',
            'type': '标准性质',
            'code': '标准号',
            'release_date': '发布日期',
            'implementation_date': '实施日期',
            'company': '参与单位',
            'participant_id': '参与人员'
        },
        'patent': {
            'name': '专利名称',
            'type': '专利类型',
            'application_date': '申请日期',
            'grant_date': '授权日期',
            'owner_id': '专利所有人',
            'participants': '参与人员',
            'company': '申请单位',
            'patent_number': '专利号',
            'certificate': '证书状态'
        },
        'paper': {
            'title': '论文标题',
            'journal': '期刊名称',
            'journal_type': '期刊类型',
            'publish_date': '发表日期',
            'first_author_id': '第一作者',
            'co_authors': '参与作者',
            'organization': '作者单位',
            'volume_info': '期次信息'
        }
    }

    # 定义各实体类型的可搜索字段
    searchable_fields = {
        'person': ['name', 'gender', 'education', 'title', 'department', 'position', 'skill_level', 'major', 'school', 'phone', 'id_card'],
        'project': ['name', 'status', 'outcome', 'members', 'leader_id'],
        'standard': ['name', 'type', 'code', 'company', 'participant_id'],
        'patent': ['name', 'type', 'company', 'patent_number', 'certificate', 'owner_id', 'participants'],
        'paper': ['title', 'journal', 'journal_type', 'organization', 'volume_info', 'first_author_id', 'co_authors']
    }

    # 定义各实体类型的日期字段
    date_fields = {
        'person': ['birth_date', 'graduation_date'],
        'project': ['start_date', 'end_date'],
        'standard': ['release_date', 'implementation_date'],
        'patent': ['application_date', 'grant_date'],
        'paper': ['publish_date']
    }

    # 定义各实体类型的下拉选择字段及选项
    dropdown_fields = {
        'person': {
            'gender': ['全部', '男', '女'],
            'education': ['全部', '高中', '专科', '本科', '硕士', '博士'],
            'skill_level': ['全部', '初级', '中级', '高级', '资深', '专家']
        },
        'project': {
            'status': ['全部', '进行中', '已完成']
        },
        'standard': {
            'type': ['全部', '国家标准', '行业标准', '地方标准', '团体标准', '企业标准']
        },
        'patent': {
            'type': ['全部', '发明专利', '实用新型专利', '外观设计专利'],
            'certificate': ['全部', '有', '无']
        },
        'paper': {
            'journal_type': ['全部', '核心期刊', '非核心期刊', 'EI收录', 'SCI收录']
        }
    }

    # 定义各实体类型的排序字段
    sortable_fields = {
        'person': ['name', 'birth_date', 'graduation_date'],
        'project': ['name', 'start_date', 'end_date'],
        'standard': ['name', 'release_date', 'implementation_date'],
        'patent': ['name', 'application_date', 'grant_date'],
        'paper': ['title', 'publish_date']
    }

    # 定义各实体类型的显示字段
    display_fields = {
        'person': ['name', 'gender', 'department', 'position', 'education', 'title', 'skill_level', 'phone'],
        'project': ['name', 'start_date', 'end_date', 'leader', 'status', 'outcome'],
        'standard': ['name', 'type', 'code', 'release_date', 'implementation_date', 'company', 'participant'],
        'patent': ['name', 'type', 'application_date', 'grant_date', 'owner', 'patent_number', 'certificate'],
        'paper': ['title', 'journal', 'journal_type', 'publish_date', 'volume_info', 'first_author', 'organization']
    }

    # 获取当前实体类型的字段映射
    current_fields = field_mappings.get(entity_type, {})
    current_searchable = searchable_fields.get(entity_type, [])
    current_date_fields = date_fields.get(entity_type, [])
    current_dropdowns = dropdown_fields.get(entity_type, {})
    current_sortable = sortable_fields.get(entity_type, [])
    current_display = display_fields.get(entity_type, [])

    # 创建高级搜索UI
    with st.expander("高级搜索", expanded=False):
        # 关键词搜索（在所有可搜索字段中查找）
        keyword = st.text_input("关键词搜索（在所有字段中查找）", key=f"keyword_{entity_type}")

        # 创建多列布局用于字段搜索
        cols = st.columns(3)

        # 文本字段搜索
        field_values = {}
        for i, field in enumerate(current_searchable):
            if field not in current_dropdowns:
                # 获取字段显示名称，如果不存在则使用字段名
                field_display = current_fields.get(field, field)
                with cols[i % 3]:
                    field_values[field] = st.text_input(
                        f"按{field_display}搜索",
                        key=f"text_{entity_type}_{field}"
                    )

        # 下拉选择字段搜索
        col_index = len(field_values) % 3  # 初始列索引
        for field, options in current_dropdowns.items():
            # 获取字段显示名称，如果不存在则使用字段名
            field_display = current_fields.get(field, field)
            with cols[col_index]:
                field_values[field] = st.selectbox(
                    f"按{field_display}筛选",
                    options,
                    key=f"select_{entity_type}_{field}"
                )
            col_index = (col_index + 1) % 3  # 更新列索引

        # 日期范围搜索
        date_ranges = {}
        for field in current_date_fields:
            # 获取字段显示名称，如果不存在则使用字段名
            field_display = current_fields.get(field, field)
            with st.container():
                st.write(f"按{field_display}范围筛选")
                date_cols = st.columns(2)
                with date_cols[0]:
                    start_date = st.date_input(
                        f"{field_display}起始",
                        value=None,
                        key=f"start_date_{entity_type}_{field}"
                    )
                with date_cols[1]:
                    end_date = st.date_input(
                        f"{field_display}截止",
                        value=None,
                        key=f"end_date_{entity_type}_{field}"
                    )
                date_ranges[field] = (start_date, end_date)

        # 排序选项
        sort_cols = st.columns(2)
        with sort_cols[0]:
            # 获取排序字段的显示名称，如果不存在则使用字段名
            sortable_display = ["无"]
            for f in current_sortable:
                field_display = current_fields.get(f, f)
                sortable_display.append(field_display)

            sort_field = st.selectbox(
                "排序字段",
                sortable_display,
                key=f"sort_field_{entity_type}"
            )
        with sort_cols[1]:
            sort_order = st.selectbox(
                "排序方式",
                ["升序", "降序"],
                key=f"sort_order_{entity_type}"
            )

        # 每页显示数量
        page_size = st.slider(
            "每页显示数量",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            key=f"page_size_{entity_type}"
        )

        # 搜索按钮
        search_button = st.button("搜索", key=f"advanced_search_{entity_type}")

    # 如果点击了搜索按钮，执行搜索
    if search_button or keyword or any(v for v in field_values.values() if v and v != "全部") or any(r[0] or r[1] for r in date_ranges.values()):
        # 构建查询条件
        conditions = []
        params = []

        # 处理关键词搜索
        if keyword:
            keyword_conditions = []

            # 定义可以进行文本搜索的字段类型
            text_searchable_fields = [
                'name', 'title', 'outcome', 'company', 'organization', 'volume_info',
                'department', 'position', 'major', 'school', 'phone', 'id_card',
                'code', 'patent_number', 'journal', 'participants', 'co_authors'
            ]

            # 对所有可搜索字段进行搜索
            for field in current_searchable:
                # 文本字段使用LIKE进行模糊匹配
                if field in text_searchable_fields:
                    keyword_conditions.append(f"{field} LIKE ?")
                    params.append(f"%{keyword}%")
                # 对于枚举类型字段，如果关键词完全匹配则添加条件
                elif field in current_dropdowns:
                    options = current_dropdowns[field]
                    for option in options:
                        if option != "全部" and keyword.lower() in option.lower():
                            keyword_conditions.append(f"{field} = ?")
                            params.append(option)

            # 特殊处理：如果关键词是人名，尝试在相关ID字段中查找
            try:
                # 尝试在人员表中查找匹配的人员
                conn = get_connection()
                person_query = "SELECT id, name FROM person WHERE name LIKE ?"
                person_df = pd.read_sql(person_query, conn, params=[f"%{keyword}%"])
                conn.close()

                if not person_df.empty:
                    # 找到了匹配的人员，根据实体类型添加相应的搜索条件
                    for _, person in person_df.iterrows():
                        person_id = person['id']

                        if entity_type == 'project':
                            # 搜索项目的负责人和成员
                            keyword_conditions.append(f"leader_id = ?")
                            params.append(person_id)
                            keyword_conditions.append(f"members LIKE ?")
                            params.append(f"%{person_id}%")

                        elif entity_type == 'standard':
                            # 搜索标准的参与人员
                            keyword_conditions.append(f"participant_id = ?")
                            params.append(person_id)

                        elif entity_type == 'patent':
                            # 搜索专利的所有人和参与人员
                            keyword_conditions.append(f"owner_id = ?")
                            params.append(person_id)
                            keyword_conditions.append(f"participants LIKE ?")
                            params.append(f"%{person_id}%")

                        elif entity_type == 'paper':
                            # 搜索论文的第一作者和参与作者
                            keyword_conditions.append(f"first_author_id = ?")
                            params.append(person_id)
                            keyword_conditions.append(f"co_authors LIKE ?")
                            params.append(f"%{person_id}%")
            except Exception as e:
                # 如果查询失败，忽略这部分搜索条件
                pass

            # 如果是paper实体，特殊处理title字段
            if entity_type == 'paper' and 'title' in current_searchable:
                keyword_conditions.append(f"title LIKE ?")
                params.append(f"%{keyword}%")

            if keyword_conditions:
                conditions.append(f"({' OR '.join(keyword_conditions)})")

        # 处理字段搜索
        for field, value in field_values.items():
            if value and value != "全部":
                # 定义可以进行文本搜索的字段类型
                text_searchable_fields = [
                    'name', 'title', 'outcome', 'company', 'organization', 'volume_info',
                    'department', 'position', 'major', 'school', 'phone', 'id_card',
                    'code', 'patent_number', 'journal', 'participants', 'co_authors'
                ]

                if field in text_searchable_fields:
                    # 文本字段使用LIKE进行模糊匹配
                    conditions.append(f"{field} LIKE ?")
                    params.append(f"%{value}%")
                else:
                    # 其他字段使用精确匹配
                    conditions.append(f"{field} = ?")
                    params.append(value)

        # 处理日期范围搜索
        for field, (start, end) in date_ranges.items():
            if start:
                conditions.append(f"{field} >= ?")
                params.append(start.strftime("%Y-%m-%d"))
            if end:
                conditions.append(f"{field} <= ?")
                params.append(end.strftime("%Y-%m-%d"))

        # 构建SQL查询
        table_name = 'paper' if entity_type == 'paper' else entity_type
        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # 添加排序
        if sort_field != "无":
            # 将显示名称转换回字段名
            sort_field_name = next((f for f, v in current_fields.items() if v == sort_field), None)
            if sort_field_name:
                query += f" ORDER BY {sort_field_name} {'DESC' if sort_order == '降序' else 'ASC'}"

        # 执行查询
        conn = get_connection()

        # 获取总记录数
        count_query = f"SELECT COUNT(*) FROM ({query})"
        count_df = pd.read_sql(count_query, conn, params=params)
        total_records = count_df.iloc[0, 0]

        # 分页查询
        current_page = st.session_state.get(f'page_{entity_type}', 1)
        total_pages = (total_records + page_size - 1) // page_size

        # 确保当前页在有效范围内
        if current_page < 1:
            current_page = 1
        if current_page > total_pages and total_pages > 0:
            current_page = total_pages

        # 更新分页状态
        st.session_state[f'page_{entity_type}'] = current_page

        # 添加分页限制
        offset = (current_page - 1) * page_size
        query += f" LIMIT {page_size} OFFSET {offset}"

        # 执行最终查询
        df = pd.read_sql(query, conn, params=params)

        # 处理特殊字段（如外键关联）
        if entity_type in ['project', 'standard', 'patent', 'paper']:
            # 获取人员信息用于显示
            persons_df = pd.read_sql("SELECT id, name FROM person", conn)
            persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

            if entity_type == 'project':
                # 处理负责人
                df['leader'] = df['leader_id'].apply(
                    lambda x: persons_dict.get(x, "未找到") if x and x in persons_dict else "无"
                )

            elif entity_type == 'standard':
                # 处理参与人员
                df['participant'] = df['participant_id'].apply(
                    lambda x: persons_dict.get(x, "无") if x else "无"
                )

            elif entity_type == 'patent':
                # 处理专利所有人
                df['owner'] = df['owner_id'].apply(
                    lambda x: persons_dict.get(x, "无") if x else "无"
                )

            elif entity_type == 'paper':
                # 处理第一作者
                df['first_author'] = df['first_author_id'].apply(
                    lambda x: persons_dict.get(x, "无") if x else "无"
                )

        conn.close()

        # 显示搜索结果
        if df.empty:
            st.info("未找到符合条件的记录")
            return pd.DataFrame()
        else:
            # 显示分页信息
            st.write(f"共找到 {total_records} 条记录，当前显示第 {current_page}/{total_pages if total_pages > 0 else 1} 页")

            # 分页控制
            page_cols = st.columns([1, 1, 3, 1, 1])
            with page_cols[0]:
                if st.button("首页", key=f"first_page_{entity_type}_{current_page}") and current_page > 1:
                    st.session_state[f'page_{entity_type}'] = 1
                    st.rerun()

            with page_cols[1]:
                if st.button("上一页", key=f"prev_page_{entity_type}_{current_page}") and current_page > 1:
                    st.session_state[f'page_{entity_type}'] = current_page - 1
                    st.rerun()

            with page_cols[3]:
                if st.button("下一页", key=f"next_page_{entity_type}_{current_page}") and current_page < total_pages:
                    st.session_state[f'page_{entity_type}'] = current_page + 1
                    st.rerun()

            with page_cols[4]:
                if st.button("末页", key=f"last_page_{entity_type}_{current_page}") and current_page < total_pages:
                    st.session_state[f'page_{entity_type}'] = total_pages
                    st.rerun()

            # 显示结果表格
            display_df = df.copy()

            # 选择要显示的列
            if entity_type in display_fields:
                display_columns = [col for col in current_display if col in display_df.columns]
                st.dataframe(display_df[display_columns])
            else:
                st.dataframe(display_df)

            return df

    return pd.DataFrame()  # 如果没有执行搜索，返回空DataFrame
