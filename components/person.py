import streamlit as st
import pandas as pd
from components.db_utils import get_connection
import datetime
from components.validation import validate_id_card, validate_phone
from components.table_utils import translate_columns, display_dataframe

def person_management():
    #st.title("人员管理")

    # 上下布局替代左右分栏

    # 初始化会话状态
    if 'person_edit_mode' not in st.session_state:
        st.session_state.person_edit_mode = False

    if 'person_selected_id' not in st.session_state:
        st.session_state.person_selected_id = None

    # 初始化消息状态
    if 'person_success_message' not in st.session_state:
        st.session_state.person_success_message = None

    # 初始化expander展开状态
    if 'person_expander_expanded' not in st.session_state:
        st.session_state.person_expander_expanded = False

    # 显示持久化的成功消息
    if st.session_state.person_success_message:
        st.success(st.session_state.person_success_message)

    # 使用expander，根据会话状态决定是否展开
    with st.expander("添加/编辑人员信息", expanded=st.session_state.person_expander_expanded):
        # 获取所有人员信息用于编辑
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM person", conn)
        conn.close()

        # 编辑模式切换回调函数
        def set_add_mode():
            st.session_state.person_edit_mode = False
            st.session_state.person_selected_id = None
            # 清除成功消息
            st.session_state.person_success_message = None
            # 保持expander展开
            st.session_state.person_expander_expanded = True
            if 'person_selector' in st.session_state:
                del st.session_state.person_selector

        def set_edit_mode():
            st.session_state.person_edit_mode = True
            # 清除成功消息
            st.session_state.person_success_message = None
            # 保持expander展开
            st.session_state.person_expander_expanded = True

        # 人员选择回调函数
        def on_person_select():
            st.session_state.person_selected_id = st.session_state.person_selector
            # 清除成功消息
            st.session_state.person_success_message = None
            # 保持expander展开
            st.session_state.person_expander_expanded = True

        # 创建两个按钮用于切换模式，使用更紧凑的布局
        button_cols = st.columns([1, 1, 3])  # 两个按钮占用较小空间，右侧留白
        with button_cols[0]:
            st.button("新增信息", on_click=set_add_mode, type="primary" if not st.session_state.person_edit_mode else "secondary")
        with button_cols[1]:
            st.button("编辑已有信息", on_click=set_edit_mode, type="primary" if st.session_state.person_edit_mode else "secondary")

        # 获取当前模式
        edit_mode = st.session_state.person_edit_mode

        # 如果是编辑模式，显示人员选择器
        if edit_mode and not df.empty:
            person_id = st.selectbox(
                "选择要编辑的人员",
                options=df['id'].tolist(),
                format_func=lambda x: df[df['id'] == x]['name'].iloc[0],
                key="person_selector",
                on_change=on_person_select
            )

            # 获取选中的人员数据
            if st.session_state.person_selected_id:
                person_id = st.session_state.person_selected_id
                person_data = df[df['id'] == person_id].iloc[0]
            else:
                person_data = df[df['id'] == person_id].iloc[0]
                st.session_state.person_selected_id = person_id
        else:
            person_id = None
            person_data = pd.Series({"name": "", "gender": "男", "birth_date": None, "id_card": "",
                                     "education": "本科", "school": "", "graduation_date": None,
                                     "major": "", "title": "", "phone": "", "department": "",
                                     "position": "", "skill_level": ""})
            st.session_state.person_selected_id = None

        # 表单用于添加或编辑人员
        with st.form("person_form"):

            # 将表单字段分为两列
            col1, col2, col3 = st.columns(3)

            with col1:
                name = st.text_input("姓名", value=person_data["name"])
                gender = st.selectbox("性别", ["男", "女"], index=0 if person_data["gender"] == "男" else 1)

                # 处理日期
                birth_date_value = None
                if person_data["birth_date"]:
                    try:
                        birth_date_value = datetime.datetime.strptime(person_data["birth_date"], "%Y-%m-%d").date()
                    except:
                        pass

                birth_date = st.date_input("出生日期", value=birth_date_value)

                id_card = st.text_input("身份证号", value=person_data["id_card"])

                # 部门信息
                department = st.text_input("所属部门", value=person_data["department"] if "department" in person_data else "")

            with col2:
                education = st.selectbox("学历", ["高中", "专科", "本科", "硕士", "博士"],
                                        index=["高中", "专科", "本科", "硕士", "博士"].index(person_data["education"]) if person_data["education"] in ["高中", "专科", "本科", "硕士", "博士"] else 2)

                school = st.text_input("毕业学校", value=person_data["school"])

                # 处理毕业日期
                grad_date_value = None
                if person_data["graduation_date"]:
                    try:
                        grad_date_value = datetime.datetime.strptime(person_data["graduation_date"], "%Y-%m-%d").date()
                    except:
                        pass

                graduation_date = st.date_input("毕业日期", value=grad_date_value)

                major = st.text_input("专业", value=person_data["major"])

                # 职位信息
                position = st.text_input("职位", value=person_data["position"] if "position" in person_data else "")

            with col3:
                title = st.text_input("职称", value=person_data["title"])
                phone = st.text_input("手机号码", value=person_data["phone"])

                # 技能等级
                skill_levels = ["初级", "中级", "高级", "资深", "专家"]
                current_skill = person_data["skill_level"] if "skill_level" in person_data and person_data["skill_level"] in skill_levels else ""
                skill_level = st.selectbox("技能等级", [""] + skill_levels,
                                          index=0 if not current_skill else skill_levels.index(current_skill) + 1)

            submit_button = st.form_submit_button("保存")

            if submit_button:
                # 表单验证
                if not name:
                    st.error("姓名不能为空")
                else:
                    # 验证身份证号
                    id_card_valid, id_card_error = validate_id_card(id_card)
                    if not id_card_valid:
                        st.error(id_card_error)
                        return

                    # 验证手机号
                    phone_valid, phone_error = validate_phone(phone)
                    if not phone_valid:
                        st.error(phone_error)
                        return

                    try:
                        conn = get_connection()
                        cursor = conn.cursor()

                        # 格式化日期
                        birth_date_str = birth_date.strftime("%Y-%m-%d")
                        graduation_date_str = graduation_date.strftime("%Y-%m-%d")

                        if st.session_state.person_edit_mode and st.session_state.person_selected_id:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE person SET name=?, gender=?, birth_date=?, id_card=?,
                                education=?, school=?, graduation_date=?, major=?, title=?, phone=?,
                                department=?, position=?, skill_level=?
                                WHERE id=?
                            ''', (name, gender, birth_date_str, id_card, education, school,
                                 graduation_date_str, major, title, phone, department, position,
                                 skill_level, st.session_state.person_selected_id))
                            # 保存成功消息到会话状态
                            st.session_state.person_success_message = f"已更新 {name} 的信息"
                            # 保持expander展开
                            st.session_state.person_expander_expanded = True
                        else:
                            # 新增记录
                            cursor.execute('''
                                INSERT INTO person (name, gender, birth_date, id_card, education,
                                                  school, graduation_date, major, title, phone,
                                                  department, position, skill_level)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (name, gender, birth_date_str, id_card, education, school,
                                 graduation_date_str, major, title, phone, department, position,
                                 skill_level))
                            # 保存成功消息到会话状态
                            st.session_state.person_success_message = f"已添加 {name} 的信息"
                            # 保持expander展开
                            st.session_state.person_expander_expanded = True

                        conn.commit()
                        conn.close()

                        # 刷新页面
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")
                        if "UNIQUE constraint failed" in str(e):
                            st.error("身份证号已存在，请检查输入")

    st.subheader("人员列表")

    # 直接从数据库获取人员数据
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM person", conn)

    if not df.empty:
        # 创建一个新的DataFrame，只包含我们需要的列，确保正确的列名翻译
        formatted_df = pd.DataFrame()

        # 复制原始列，确保title字段被正确翻译为职称
        formatted_df['id'] = df['id']
        formatted_df['name'] = df['name']  # 将被翻译为姓名
        formatted_df['gender'] = df['gender']
        formatted_df['birth_date'] = df['birth_date']
        formatted_df['id_card'] = df['id_card']
        formatted_df['education'] = df['education']
        formatted_df['school'] = df['school']
        formatted_df['graduation_date'] = df['graduation_date']
        formatted_df['major'] = df['major']
        formatted_df['title'] = df['title']  # 将被翻译为职称
        formatted_df['phone'] = df['phone']
        formatted_df['department'] = df['department']
        formatted_df['position'] = df['position']
        formatted_df['skill_level'] = df['skill_level']

        # 使用自定义表格显示工具
        display_dataframe(formatted_df, 'person')

        # 详细信息查看和删除选项
        col_view, col_del = st.columns(2)

        with col_view:
            view_id = st.selectbox("选择要查看详细信息的人员", df['id'].tolist(),
                                 format_func=lambda x: df[df['id'] == x]['name'].iloc[0])
            if st.button("查看详细信息"):
                person_data = df[df['id'] == view_id].iloc[0]

                # 显示详细信息
                st.subheader(f"{person_data['name']}的详细信息")

                # 基本信息
                st.markdown("##### 基本信息")
                st.markdown(f"**性别**: {person_data['gender']}")
                st.markdown(f"**出生日期**: {person_data['birth_date']}")
                st.markdown(f"**身份证号**: {person_data['id_card']}")
                st.markdown(f"**联系电话**: {person_data['phone']}")

                # 部门与职位信息
                st.markdown("##### 部门与职位信息")
                if person_data['department']:
                    st.markdown(f"**所属部门**: {person_data['department']}")
                if person_data['position']:
                    st.markdown(f"**职位**: {person_data['position']}")
                if person_data['title']:
                    st.markdown(f"**职称**: {person_data['title']}")
                if person_data['skill_level']:
                    st.markdown(f"**技能等级**: {person_data['skill_level']}")

                # 教育背景
                st.markdown("##### 教育背景")
                st.markdown(f"**学历**: {person_data['education']}")
                st.markdown(f"**毕业学校**: {person_data['school']}")
                st.markdown(f"**毕业日期**: {person_data['graduation_date']}")
                st.markdown(f"**专业**: {person_data['major']}")

                # 获取此人参与的项目
                projects_query = "SELECT * FROM project WHERE members LIKE ? OR leader_id = ?"
                projects_df = pd.read_sql(projects_query, conn, params=[f'%{view_id}%', view_id])

                if not projects_df.empty:
                    st.markdown("##### 参与的项目")
                    for _, project in projects_df.iterrows():
                        is_leader = project['leader_id'] == view_id
                        role = "主负责人" if is_leader else "项目成员"
                        status = project['status'] if 'status' in project else "进行中"
                        st.markdown(f"- **{project['name']}** ({project['start_date']} 至 {project['end_date']}) - {role} - 状态: {status}")
                else:
                    st.info("该人员未参与任何项目")

                # 获取此人关联的专利信息（作为所有人或参与者）
                patents_owner_query = "SELECT * FROM patent WHERE owner_id = ?"
                patents_owner_df = pd.read_sql(patents_owner_query, conn, params=[view_id])

                patents_participant_query = "SELECT * FROM patent WHERE participants LIKE ?"
                patents_participant_df = pd.read_sql(patents_participant_query, conn, params=[f'%{view_id}%'])

                if not patents_owner_df.empty or not patents_participant_df.empty:
                    st.markdown("##### 关联的专利")

                    # 显示作为专利所有人的专利
                    if not patents_owner_df.empty:
                        st.markdown("**作为专利所有人**")
                        for _, patent in patents_owner_df.iterrows():
                            cert_status = patent['certificate'] if 'certificate' in patent else "无"
                            st.markdown(f"- **{patent['name']}** ({patent['type']}) - 专利号: {patent['patent_number']} - 证书状态: {cert_status}")

                    # 显示作为专利参与人的专利
                    if not patents_participant_df.empty:
                        st.markdown("**作为专利参与人**")
                        for _, patent in patents_participant_df.iterrows():
                            cert_status = patent['certificate'] if 'certificate' in patent else "无"
                            st.markdown(f"- **{patent['name']}** ({patent['type']}) - 专利号: {patent['patent_number']} - 证书状态: {cert_status}")
                else:
                    st.info("该人员未关联任何专利")

                # 获取此人参与的标准
                standards_query = "SELECT * FROM standard WHERE participant_id = ?"
                standards_df = pd.read_sql(standards_query, conn, params=[view_id])

                if not standards_df.empty:
                    st.markdown("##### 参与的标准")
                    for _, standard in standards_df.iterrows():
                        st.markdown(f"- **{standard['name']}** ({standard['type']}) - 标准号: {standard['code']} - 发布日期: {standard['release_date']}")
                else:
                    st.info("该人员未参与任何标准")

                # 获取此人关联的论文信息（作为第一作者或参与作者）
                papers_first_author_query = "SELECT * FROM paper WHERE first_author_id = ?"
                papers_first_author_df = pd.read_sql(papers_first_author_query, conn, params=[view_id])

                papers_co_author_query = "SELECT * FROM paper WHERE co_authors LIKE ?"
                papers_co_author_df = pd.read_sql(papers_co_author_query, conn, params=[f'%{view_id}%'])

                if not papers_first_author_df.empty or not papers_co_author_df.empty:
                    st.markdown("##### 关联的论文")

                    # 显示作为第一作者的论文
                    if not papers_first_author_df.empty:
                        st.markdown("**作为第一作者**")
                        for _, paper in papers_first_author_df.iterrows():
                            volume = f" - {paper['volume_info']}" if 'volume_info' in paper and paper['volume_info'] else ""
                            st.markdown(f"- **{paper['title']}** - {paper['journal']} ({paper['journal_type']}){volume} - 发表日期: {paper['publish_date']}")

                    # 显示作为参与作者的论文
                    if not papers_co_author_df.empty:
                        st.markdown("**作为参与作者**")
                        for _, paper in papers_co_author_df.iterrows():
                            volume = f" - {paper['volume_info']}" if 'volume_info' in paper and paper['volume_info'] else ""
                            st.markdown(f"- **{paper['title']}** - {paper['journal']} ({paper['journal_type']}){volume} - 发表日期: {paper['publish_date']}")
                else:
                    st.info("该人员未关联任何论文")

        with col_del:
            del_id = st.selectbox("选择要删除的人员", df['id'].tolist(),
                                format_func=lambda x: df[df['id'] == x]['name'].iloc[0])

            if st.button("删除人员"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()

                    # 先检查此人是否是项目负责人
                    cursor.execute("SELECT id, name FROM project WHERE leader_id = ?", (del_id,))
                    leader_projects = cursor.fetchall()

                    if leader_projects:
                        project_names = ", ".join([p[1] for p in leader_projects])
                        st.error(f"无法删除：该人员是以下项目的负责人: {project_names}")
                        st.info("请先修改这些项目的负责人后再尝试删除")
                    else:
                        # 更新所有包含此人的项目成员列表
                        cursor.execute("SELECT id, members FROM project WHERE members LIKE ?", (f'%{del_id}%',))
                        affected_projects = cursor.fetchall()

                        for project in affected_projects:
                            project_id, members_str = project
                            # 从成员列表中移除此人
                            member_ids = [int(m) for m in members_str.split(',') if m and int(m) != del_id]
                            new_members_str = ",".join([str(m) for m in member_ids])

                            # 更新项目成员
                            cursor.execute("UPDATE project SET members = ? WHERE id = ?",
                                          (new_members_str, project_id))

                        # 删除人员
                        cursor.execute("DELETE FROM person WHERE id = ?", (del_id,))
                        conn.commit()
                        # 保存成功消息到会话状态
                        st.session_state.person_success_message = f"已删除人员，并从 {len(affected_projects)} 个项目的成员列表中移除"
                        # 保持expander展开
                        st.session_state.person_expander_expanded = True
                        st.rerun()

                    conn.close()
                except Exception as e:
                    st.error(f"删除失败: {str(e)}")
    else:
        st.info("暂无人员信息")

    conn.close()

# 辅助函数 - 显示人员统计信息
def show_person_statistics():
    conn = get_connection()

    # 按部门统计人数
    department_stats = pd.read_sql("""
    SELECT department, COUNT(*) as count
    FROM person
    WHERE department IS NOT NULL AND department != ''
    GROUP BY department
    ORDER BY count DESC
    """, conn)

    if not department_stats.empty:
        st.subheader("部门人员分布")
        # 翻译列名
        display_df = translate_columns(department_stats)
        st.dataframe(display_df)
        st.bar_chart(department_stats.set_index('department')['count'])

    # 按技能等级统计
    skill_stats = pd.read_sql("""
    SELECT skill_level, COUNT(*) as count
    FROM person
    WHERE skill_level IS NOT NULL AND skill_level != ''
    GROUP BY skill_level
    ORDER BY CASE
             WHEN skill_level = '初级' THEN 1
             WHEN skill_level = '中级' THEN 2
             WHEN skill_level = '高级' THEN 3
             WHEN skill_level = '资深' THEN 4
             WHEN skill_level = '专家' THEN 5
             ELSE 6 END
    """, conn)

    if not skill_stats.empty:
        st.subheader("技能等级分布")
        # 翻译列名
        display_df = translate_columns(skill_stats)
        st.dataframe(display_df)
        st.bar_chart(skill_stats.set_index('skill_level')['count'])

    # 按学历统计
    education_stats = pd.read_sql("""
    SELECT education, COUNT(*) as count
    FROM person
    GROUP BY education
    ORDER BY CASE
             WHEN education = '高中' THEN 1
             WHEN education = '专科' THEN 2
             WHEN education = '本科' THEN 3
             WHEN education = '硕士' THEN 4
             WHEN education = '博士' THEN 5
             ELSE 6 END
    """, conn)

    if not education_stats.empty:
        st.subheader("学历分布")
        # 翻译列名
        display_df = translate_columns(education_stats)
        st.dataframe(display_df)
        st.bar_chart(education_stats.set_index('education')['count'])

    conn.close()