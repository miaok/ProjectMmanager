import streamlit as st
import pandas as pd
from components.db_utils import get_connection
import datetime

def project_management():
    #st.title("项目管理")

    # 上下布局替代左右分栏

    # 使用expander使添加/编辑表单默认隐藏
    with st.expander("添加/编辑项目信息", expanded=False):
        # 获取所有项目信息用于编辑
        conn = get_connection()
        projects_df = pd.read_sql("SELECT * FROM project", conn)

        # 获取所有人员信息用于选择
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)

        # 表单用于添加或编辑项目
        with st.form("project_form"):
            # 如果是编辑模式，需要选择项目
            edit_mode = st.checkbox("编辑已有项目")

            if edit_mode and not projects_df.empty:
                project_id = st.selectbox("选择要编辑的项目", projects_df['id'].tolist(),
                                        format_func=lambda x: projects_df[projects_df['id'] == x]['name'].iloc[0])
                project_data = projects_df[projects_df['id'] == project_id].iloc[0]

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

                        if edit_mode and project_id:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE project SET name=?, start_date=?, end_date=?, members=?,
                                leader_id=?, outcome=?, status=? WHERE id=?
                            ''', (name, start_date_str, end_date_str, members_str,
                                 leader_id, outcome, status, project_id))
                            st.success(f"已更新项目 {name} 的信息")
                        else:
                            # 新增记录
                            cursor.execute('''
                                INSERT INTO project (name, start_date, end_date, members, leader_id, outcome, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (name, start_date_str, end_date_str, members_str, leader_id, outcome, status))
                            st.success(f"已添加项目 {name} 的信息")

                        conn.commit()
                        conn.close()

                        # 刷新页面
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")

        conn.close()

    st.subheader("项目列表")

    # 查询功能
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        search_name = st.text_input("按项目名称搜索")
    with search_col2:
        search_status = st.selectbox("按项目状态筛选", ["全部", "进行中", "已完成"])

    # 获取项目信息
    conn = get_connection()

    # 构建查询条件
    conditions = []
    params = []

    if search_name:
        conditions.append("name LIKE ?")
        params.append(f"%{search_name}%")

    if search_status != "全部":
        conditions.append("status = ?")
        params.append(search_status)

    # 构建SQL查询
    query = "SELECT * FROM project"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    projects_df = pd.read_sql(query, conn, params=params)

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

        # 显示项目列表
        display_columns = ['id', 'name', 'start_date', 'end_date', 'leader', 'status', 'outcome']
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
                    st.success("已删除项目")
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
        st.dataframe(stats_df)

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