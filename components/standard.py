import streamlit as st
import pandas as pd
from components.db_utils import get_connection
import datetime
from components.table_utils import translate_columns, display_dataframe

def standard_management():
    #st.title("标准管理")

    # 上下布局替代左右分栏

    # 初始化会话状态
    if 'standard_edit_mode' not in st.session_state:
        st.session_state.standard_edit_mode = False

    if 'standard_selected_id' not in st.session_state:
        st.session_state.standard_selected_id = None

    # 初始化消息状态
    if 'standard_success_message' not in st.session_state:
        st.session_state.standard_success_message = None

    # 初始化expander展开状态
    if 'standard_expander_expanded' not in st.session_state:
        st.session_state.standard_expander_expanded = False

    # 显示持久化的成功消息
    if st.session_state.standard_success_message:
        st.success(st.session_state.standard_success_message)

    # 使用expander，根据会话状态决定是否展开
    with st.expander("添加/编辑标准信息", expanded=st.session_state.standard_expander_expanded):
        # 获取所有标准信息用于编辑
        conn = get_connection()
        standards_df = pd.read_sql("SELECT * FROM standard", conn)

        # 获取所有人员信息用于选择参与人员
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)

        # 编辑模式切换回调函数
        def set_add_mode():
            st.session_state.standard_edit_mode = False
            st.session_state.standard_selected_id = None
            # 清除成功消息
            st.session_state.standard_success_message = None
            # 保持expander展开
            st.session_state.standard_expander_expanded = True
            if 'standard_selector' in st.session_state:
                del st.session_state.standard_selector

        def set_edit_mode():
            st.session_state.standard_edit_mode = True
            # 清除成功消息
            st.session_state.standard_success_message = None
            # 保持expander展开
            st.session_state.standard_expander_expanded = True

        # 标准选择回调函数
        def on_standard_select():
            st.session_state.standard_selected_id = st.session_state.standard_selector
            # 清除成功消息
            st.session_state.standard_success_message = None
            # 保持expander展开
            st.session_state.standard_expander_expanded = True

        # 创建两个按钮用于切换模式，使用更紧凑的布局
        button_cols = st.columns([1, 1, 3])  # 两个按钮占用较小空间，右侧留白
        with button_cols[0]:
            st.button("新增信息", on_click=set_add_mode, type="primary" if not st.session_state.standard_edit_mode else "secondary")
        with button_cols[1]:
            st.button("编辑已有信息", on_click=set_edit_mode, type="primary" if st.session_state.standard_edit_mode else "secondary")

        # 获取当前模式
        edit_mode = st.session_state.standard_edit_mode

        # 如果是编辑模式，显示标准选择器
        if edit_mode and not standards_df.empty:
            standard_id = st.selectbox(
                "选择要编辑的标准",
                options=standards_df['id'].tolist(),
                format_func=lambda x: standards_df[standards_df['id'] == x]['name'].iloc[0],
                key="standard_selector",
                on_change=on_standard_select
            )

            # 获取选中的标准数据
            if st.session_state.standard_selected_id:
                standard_id = st.session_state.standard_selected_id
                standard_data = standards_df[standards_df['id'] == standard_id].iloc[0]
            else:
                standard_data = standards_df[standards_df['id'] == standard_id].iloc[0]
                st.session_state.standard_selected_id = standard_id
        else:
            standard_id = None
            standard_data = pd.Series({"name": "", "type": "国家标准", "code": "",
                                      "release_date": None, "implementation_date": None,
                                      "company": "", "participant_id": None})
            st.session_state.standard_selected_id = None

        # 表单用于添加或编辑标准
        with st.form("standard_form"):

            # 表单字段分为两列
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("标准名称", value=standard_data["name"])

                # 标准性质选择
                standard_types = ["国家标准", "行业标准", "地方标准", "团体标准", "企业标准"]
                type_index = standard_types.index(standard_data["type"]) if standard_data["type"] in standard_types else 0
                standard_type = st.selectbox("标准性质", standard_types, index=type_index)

                code = st.text_input("标准号", value=standard_data["code"])

                # 处理发布日期
                release_date_value = None
                if standard_data["release_date"]:
                    try:
                        release_date_value = datetime.datetime.strptime(standard_data["release_date"], "%Y-%m-%d").date()
                    except:
                        pass

                release_date = st.date_input("发布日期", value=release_date_value)

            with col2:
                # 处理实施日期
                impl_date_value = None
                if standard_data["implementation_date"]:
                    try:
                        impl_date_value = datetime.datetime.strptime(standard_data["implementation_date"], "%Y-%m-%d").date()
                    except:
                        pass

                implementation_date = st.date_input("实施日期", value=impl_date_value)

                # 参与单位
                company = st.text_input("参与单位", value=standard_data["company"])

                # 参与人员选择
                if not persons_df.empty:
                    persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}
                    # 添加一个"无"选项
                    persons_dict[0] = "无"

                    # 获取当前参与人员
                    current_participant = standard_data["participant_id"] if standard_data["participant_id"] else 0

                    # 创建选项列表
                    options = [0] + persons_df['id'].tolist()

                    # 计算索引
                    if current_participant in persons_df['id'].tolist():
                        # 找到当前参与人员在选项列表中的索引
                        index = options.index(current_participant)
                    else:
                        # 默认选择"无"选项
                        index = 0

                    participant_id = st.selectbox("参与人员",
                                                options=options,
                                                index=index,
                                                format_func=lambda x: persons_dict.get(x, f"ID:{x}"))

                    if participant_id == 0:
                        participant_id = None
                else:
                    st.warning("暂无人员信息，请先添加人员")
                    participant_id = None

            submit_button = st.form_submit_button("保存")

            if submit_button:
                # 表单验证
                if not name:
                    st.error("标准名称不能为空")
                elif not code:
                    st.error("标准号不能为空")
                elif implementation_date < release_date:
                    st.error("实施日期不能早于发布日期")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()

                        # 格式化日期
                        release_date_str = release_date.strftime("%Y-%m-%d")
                        implementation_date_str = implementation_date.strftime("%Y-%m-%d")

                        if edit_mode and standard_id:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE standard SET name=?, type=?, code=?, release_date=?,
                                implementation_date=?, company=?, participant_id=? WHERE id=?
                            ''', (name, standard_type, code, release_date_str,
                                 implementation_date_str, company, participant_id, standard_id))
                            # 保存成功消息到会话状态
                            st.session_state.standard_success_message = f"已更新标准 {name} 的信息"
                            # 保持expander展开
                            st.session_state.standard_expander_expanded = True
                        else:
                            # 新增记录
                            cursor.execute('''
                                INSERT INTO standard (name, type, code, release_date,
                                implementation_date, company, participant_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (name, standard_type, code, release_date_str,
                                 implementation_date_str, company, participant_id))
                            # 保存成功消息到会话状态
                            st.session_state.standard_success_message = f"已添加标准 {name} 的信息"
                            # 保持expander展开
                            st.session_state.standard_expander_expanded = True

                        conn.commit()
                        conn.close()

                        # 刷新页面
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")

        conn.close()

    st.subheader("标准列表")

    # 直接从数据库获取标准数据
    conn = get_connection()
    standards_df = pd.read_sql("SELECT * FROM standard", conn)

    # 获取人员信息用于显示
    persons_df = pd.read_sql("SELECT id, name FROM person", conn)
    persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

    if not standards_df.empty:
        # 格式化显示数据
        display_df = standards_df.copy()

        # 创建一个新的DataFrame，只包含我们需要的列，避免重复列名问题
        formatted_df = pd.DataFrame()

        # 复制原始列
        formatted_df['id'] = display_df['id']
        formatted_df['standard_name'] = display_df['name']  # 使用standard_name作为列名，以便正确翻译为"标准名称"
        formatted_df['type'] = display_df['type']
        formatted_df['code'] = display_df['code']
        formatted_df['release_date'] = display_df['release_date']
        formatted_df['implementation_date'] = display_df['implementation_date']

        # 添加格式化的字段
        formatted_df['参与人员'] = display_df['participant_id'].apply(
            lambda x: persons_dict.get(x, "无") if x else "无")
        formatted_df['单位'] = display_df['company']

        # 使用自定义表格显示工具
        display_dataframe(formatted_df, 'standard')

        # 详细信息查看和删除选项
        col_view, col_del = st.columns(2)

        with col_view:
            view_id = st.selectbox("选择要查看详细信息的标准", standards_df['id'].tolist(),
                                 format_func=lambda x: standards_df[standards_df['id'] == x]['name'].iloc[0])

            if st.button("查看详细信息"):
                standard_data = standards_df[standards_df['id'] == view_id].iloc[0]

                # 显示基本信息
                st.subheader(f"{standard_data['name']}的详细信息")
                st.text(f"标准性质: {standard_data['type']}")
                st.text(f"标准号: {standard_data['code']}")
                st.text(f"发布日期: {standard_data['release_date']}")
                st.text(f"实施日期: {standard_data['implementation_date']}")
                st.text(f"参与单位: {standard_data['company']}")

                # 显示参与人员信息
                if standard_data['participant_id']:
                    participant_query = "SELECT * FROM person WHERE id = ?"
                    participant_df = pd.read_sql(participant_query, conn, params=[standard_data['participant_id']])

                    if not participant_df.empty:
                        participant = participant_df.iloc[0]
                        st.subheader("参与人员信息")
                        st.text(f"姓名: {participant['name']}")
                        st.text(f"性别: {participant['gender']}")
                        st.text(f"职称: {participant['title']}")
                        st.text(f"联系电话: {participant['phone']}")
                else:
                    st.text("参与人员: 无")

        with col_del:
            del_id = st.selectbox("选择要删除的标准", standards_df['id'].tolist(),
                                format_func=lambda x: standards_df[standards_df['id'] == x]['name'].iloc[0])

            if st.button("删除标准"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM standard WHERE id = ?", (del_id,))
                    conn.commit()
                    conn.close()
                    # 保存成功消息到会话状态
                    st.session_state.standard_success_message = "已删除标准"
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {str(e)}")
    else:
        st.info("未找到符合条件的标准信息")

    conn.close()

# 辅助函数 - 显示标准统计信息
def show_standard_statistics():
    conn = get_connection()

    # 按标准性质统计
    type_query = """
    SELECT type, COUNT(*) as count
    FROM standard
    GROUP BY type
    ORDER BY count DESC
    """
    type_df = pd.read_sql(type_query, conn)

    if not type_df.empty:
        st.subheader("标准性质分布")
        # 翻译列名
        display_df = translate_columns(type_df)
        st.dataframe(display_df)

        # 可视化
        st.bar_chart(type_df.set_index('type')['count'])

    # 按发布年份统计
    year_query = """
    SELECT substr(release_date, 1, 4) as year, COUNT(*) as count
    FROM standard
    GROUP BY year
    ORDER BY year
    """
    year_df = pd.read_sql(year_query, conn)

    if not year_df.empty:
        st.subheader("标准发布年份分布")
        # 翻译列名
        display_df = translate_columns(year_df)
        st.dataframe(display_df)

        # 可视化
        st.line_chart(year_df.set_index('year')['count'])

    # 按参与人员统计
    participant_query = """
    SELECT p.name, COUNT(s.id) as standard_count
    FROM person p
    LEFT JOIN standard s ON p.id = s.participant_id
    GROUP BY p.id
    HAVING standard_count > 0
    ORDER BY standard_count DESC
    LIMIT 10
    """

    participant_df = pd.read_sql(participant_query, conn)

    if not participant_df.empty:
        st.subheader("参与标准最多的人员")
        # 翻译列名
        display_df = translate_columns(participant_df)
        st.dataframe(display_df)

        # 可视化
        st.bar_chart(participant_df.set_index('name')['standard_count'])

    conn.close()