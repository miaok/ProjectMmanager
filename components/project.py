import streamlit as st
import pandas as pd
from components.db_utils import get_connection
import datetime

def project_management():
    #st.title("项目管理")

    # 上下布局替代左右分栏

    # 初始化会话状态
    if 'project_edit_mode' not in st.session_state:
        st.session_state.project_edit_mode = False

    if 'project_selected_id' not in st.session_state:
        st.session_state.project_selected_id = None

    # 初始化消息状态
    if 'project_success_message' not in st.session_state:
        st.session_state.project_success_message = None

    # 初始化expander展开状态
    if 'project_expander_expanded' not in st.session_state:
        st.session_state.project_expander_expanded = False

    # 显示持久化的成功消息
    if st.session_state.project_success_message:
        st.success(st.session_state.project_success_message)

    # 使用expander，根据会话状态决定是否展开
    with st.expander("添加/编辑项目信息", expanded=st.session_state.project_expander_expanded):
        # 获取所有项目信息用于编辑
        conn = get_connection()
        projects_df = pd.read_sql("SELECT * FROM project", conn)

        # 获取所有人员信息用于选择
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)

        # 编辑模式切换回调函数
        def set_add_mode():
            st.session_state.project_edit_mode = False
            st.session_state.project_selected_id = None
            # 清除成功消息
            st.session_state.project_success_message = None
            # 保持expander展开
            st.session_state.project_expander_expanded = True
            if 'project_selector' in st.session_state:
                del st.session_state.project_selector

        def set_edit_mode():
            st.session_state.project_edit_mode = True
            # 清除成功消息
            st.session_state.project_success_message = None
            # 保持expander展开
            st.session_state.project_expander_expanded = True

        # 项目选择回调函数
        def on_project_select():
            st.session_state.project_selected_id = st.session_state.project_selector
            # 清除成功消息
            st.session_state.project_success_message = None
            # 保持expander展开
            st.session_state.project_expander_expanded = True

        # 创建两个按钮用于切换模式，使用更紧凑的布局
        button_cols = st.columns([1, 1, 3])  # 两个按钮占用较小空间，右侧留白
        with button_cols[0]:
            st.button("新增信息", on_click=set_add_mode, type="primary" if not st.session_state.project_edit_mode else "secondary")
        with button_cols[1]:
            st.button("编辑已有信息", on_click=set_edit_mode, type="primary" if st.session_state.project_edit_mode else "secondary")

        # 获取当前模式
        edit_mode = st.session_state.project_edit_mode

        # 如果是编辑模式，显示项目选择器
        if edit_mode and not projects_df.empty:
            project_id = st.selectbox(
                "选择要编辑的项目",
                options=projects_df['id'].tolist(),
                format_func=lambda x: projects_df[projects_df['id'] == x]['name'].iloc[0],
                key="project_selector",
                on_change=on_project_select
            )

            # 获取选中的项目数据
            if st.session_state.project_selected_id:
                project_id = st.session_state.project_selected_id
                project_data = projects_df[projects_df['id'] == project_id].iloc[0]
            else:
                project_data = projects_df[projects_df['id'] == project_id].iloc[0]
                st.session_state.project_selected_id = project_id

            # 获取已有成员
            if project_data['members']:
                current_members = [int(m) for m in project_data['members'].split(',') if m]
            else:
                current_members = []
        else:
            project_id = None
            project_data = pd.Series({"name": "", "start_date": None, "end_date": None,
                                    "members": "", "leader_id": None, "outcome": "", "status": "进行中"})
            current_members = []
            st.session_state.project_selected_id = None

        # 表单用于添加或编辑项目
        with st.form("project_form"):

            # 表单字段
            col1, col2, col3 = st.columns(3)

            with col1:
                name = st.text_input("项目名称", value=project_data["name"])

                # 处理开始日期
                start_date_value = None
                if project_data["start_date"]:
                    try:
                        start_date_value = datetime.datetime.strptime(project_data["start_date"], "%Y-%m-%d").date()
                    except:
                        pass

                start_date = st.date_input("起始日期", value=start_date_value)

            with col2:
                # 处理结束日期
                end_date_value = None
                if project_data["end_date"]:
                    try:
                        end_date_value = datetime.datetime.strptime(project_data["end_date"], "%Y-%m-%d").date()
                    except:
                        pass

                end_date = st.date_input("截止日期", value=end_date_value)

            with col3:
                # 项目状态选择，默认为根据日期自动判断
                today = datetime.date.today()
                if edit_mode and 'status' in project_data:
                    default_status = project_data["status"]
                else:
                    if end_date_value and end_date_value < today:
                        default_status = "已完成"
                    else:
                        default_status = "进行中"

                status = st.selectbox("项目状态", ["进行中", "已完成"],
                                     index=0 if default_status == "进行中" else 1)

                auto_status = st.checkbox("根据日期自动判断状态", value=not edit_mode)

            # 成员选择放在下方，占据整行空间
            if not persons_df.empty:
                persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}
                members = st.multiselect("项目成员", options=persons_df['id'].tolist(),
                                        default=current_members,
                                        format_func=lambda x: persons_dict.get(x, f"ID:{x}"))

                # 负责人选择（从成员中选择）
                leader_options = [m for m in members]
                if project_data["leader_id"] in persons_dict and project_data["leader_id"] not in leader_options:
                    leader_options.append(project_data["leader_id"])

                if leader_options:
                    leader_id = st.selectbox("主负责人", options=leader_options,
                                           index=0 if project_data["leader_id"] is None else leader_options.index(project_data["leader_id"]) if project_data["leader_id"] in leader_options else 0,
                                           format_func=lambda x: persons_dict.get(x, f"ID:{x}"))
                else:
                    leader_id = None
                    st.warning("请先选择项目成员以指定负责人")
            else:
                members = []
                leader_id = None
                st.warning("暂无人员信息，请先添加人员")

            outcome = st.text_area("项目成果", value=project_data["outcome"])

            submit_button = st.form_submit_button("保存")

            if submit_button:
                # 表单验证
                if not name:
                    st.error("项目名称不能为空")
                elif start_date > end_date:
                    st.error("开始日期不能晚于结束日期")
                elif not members:
                    st.error("项目必须至少有一个成员")
                elif not leader_id:
                    st.error("必须指定一个主负责人")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()

                        # 格式化日期
                        start_date_str = start_date.strftime("%Y-%m-%d")
                        end_date_str = end_date.strftime("%Y-%m-%d")

                        # 如果选择自动判断状态
                        if auto_status:
                            today = datetime.date.today()
                            if end_date < today:
                                status = "已完成"
                            else:
                                status = "进行中"

                        # 处理成员列表
                        members_str = ",".join([str(m) for m in members])

                        if st.session_state.project_edit_mode and st.session_state.project_selected_id:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE project SET name=?, start_date=?, end_date=?, members=?,
                                leader_id=?, outcome=?, status=? WHERE id=?
                            ''', (name, start_date_str, end_date_str, members_str,
                                 leader_id, outcome, status, st.session_state.project_selected_id))
                            # 保存成功消息到会话状态
                            st.session_state.project_success_message = f"已更新项目 {name} 的信息"
                            # 保持expander展开
                            st.session_state.project_expander_expanded = True
                        else:
                            # 新增记录
                            cursor.execute('''
                                INSERT INTO project (name, start_date, end_date, members, leader_id, outcome, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (name, start_date_str, end_date_str, members_str, leader_id, outcome, status))
                            # 保存成功消息到会话状态
                            st.session_state.project_success_message = f"已添加项目 {name} 的信息"
                            # 保持expander展开
                            st.session_state.project_expander_expanded = True

                        conn.commit()
                        conn.close()

                        # 刷新页面
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")

        conn.close()

    st.subheader("项目列表")

    # 直接从数据库获取项目数据
    conn = get_connection()
    projects_df = pd.read_sql("SELECT * FROM project", conn)

    # 获取人员信息用于显示
    persons_df = pd.read_sql("SELECT id, name FROM person", conn)
    persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}

    if not projects_df.empty:
        # 格式化显示数据
        display_df = projects_df.copy()
        # 处理负责人，检查是否存在
        display_df['leader'] = display_df['leader_id'].apply(
            lambda x: persons_dict.get(x, "未找到 (可能已被删除)") if x and x in persons_dict else "无" if not x else "未找到 (可能已被删除)"
        )

        # 显示项目列表 (不显示ID)
        display_columns = ['name', 'start_date', 'end_date', 'leader', 'status', 'outcome']
        st.dataframe(display_df[display_columns])

        # 详细信息查看和删除选项
        col_view, col_del = st.columns(2)

        with col_view:
            view_id = st.selectbox("选择要查看详细信息的项目", projects_df['id'].tolist(),
                                 format_func=lambda x: projects_df[projects_df['id'] == x]['name'].iloc[0])

            if st.button("查看详细信息"):
                project_data = projects_df[projects_df['id'] == view_id].iloc[0]

                # 显示基本信息
                st.subheader(f"{project_data['name']}的详细信息")
                st.text(f"起始日期: {project_data['start_date']}")
                st.text(f"截止日期: {project_data['end_date']}")
                st.text(f"项目状态: {project_data['status']}")

                # 显示负责人
                leader_id = project_data['leader_id']
                if leader_id in persons_dict:
                    leader_name = persons_dict.get(leader_id)
                    st.text(f"主负责人: {leader_name}")
                else:
                    st.text("主负责人: 未找到 (可能已被删除)")

                # 显示项目成员
                if project_data['members']:
                    member_ids = [int(m) for m in project_data['members'].split(',') if m]
                    # 过滤掉不存在的成员ID
                    valid_member_ids = [m_id for m_id in member_ids if m_id in persons_dict]

                    if valid_member_ids:
                        st.subheader("项目成员")
                        for member_id in valid_member_ids:
                            member_name = persons_dict.get(member_id)
                            is_leader = member_id == project_data['leader_id']
                            role = "主负责人" if is_leader else "项目成员"
                            st.text(f"- {member_name} ({role})")
                    else:
                        st.info("该项目没有有效的成员")

                # 显示项目成果
                st.subheader("项目成果")
                st.text(project_data['outcome'])

        with col_del:
            del_id = st.selectbox("选择要删除的项目", projects_df['id'].tolist(),
                                format_func=lambda x: projects_df[projects_df['id'] == x]['name'].iloc[0])

            if st.button("删除项目"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM project WHERE id = ?", (del_id,))
                    conn.commit()
                    conn.close()
                    # 保存成功消息到会话状态
                    st.session_state.project_success_message = "已删除项目"
                    # 保持expander展开
                    st.session_state.project_expander_expanded = True
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {str(e)}")
    else:
        st.info("暂无项目信息")

    conn.close()

# 辅助函数 - 显示项目统计信息
def show_statistics():
    conn = get_connection()

    # 获取人员参与项目数量统计
    query = """
    SELECT p.id, p.name, COUNT(pr.id) as project_count
    FROM person p
    LEFT JOIN (
        SELECT id, members, leader_id
        FROM project
    ) pr ON (pr.members LIKE '%' || p.id || '%' OR pr.leader_id = p.id)
    GROUP BY p.id
    ORDER BY project_count DESC
    """

    stats_df = pd.read_sql(query, conn)

    if not stats_df.empty:
        st.subheader("人员参与项目统计")
        # 不显示ID列
        st.dataframe(stats_df[['name', 'project_count']])

        # 可视化
        st.bar_chart(stats_df.set_index('name')['project_count'])

    # 获取项目状态统计
    status_query = """
    SELECT status, COUNT(*) as count
    FROM project
    GROUP BY status
    """

    status_df = pd.read_sql(status_query, conn)

    if not status_df.empty:
        st.subheader("项目状态统计")
        st.dataframe(status_df)

        # 可视化项目状态分布
        st.bar_chart(status_df.set_index('status')['count'])

    conn.close()