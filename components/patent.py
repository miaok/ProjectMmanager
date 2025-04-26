import streamlit as st
import pandas as pd
from components.db_utils import get_connection
import datetime

def patent_management():
    #st.title("专利管理")

    # 上下布局替代左右分栏

    # 初始化会话状态
    if 'patent_edit_mode' not in st.session_state:
        st.session_state.patent_edit_mode = False

    if 'patent_selected_id' not in st.session_state:
        st.session_state.patent_selected_id = None

    # 初始化消息状态
    if 'patent_success_message' not in st.session_state:
        st.session_state.patent_success_message = None

    # 初始化expander展开状态
    if 'patent_expander_expanded' not in st.session_state:
        st.session_state.patent_expander_expanded = False

    # 显示持久化的成功消息
    if st.session_state.patent_success_message:
        st.success(st.session_state.patent_success_message)

    # 使用expander，根据会话状态决定是否展开
    with st.expander("添加/编辑专利信息", expanded=st.session_state.patent_expander_expanded):
        # 获取所有专利信息用于编辑
        conn = get_connection()
        patents_df = pd.read_sql("SELECT * FROM patent", conn)

        # 获取所有人员信息用于选择专利所有人和参与人员
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)

        # 编辑模式切换回调函数
        def set_add_mode():
            st.session_state.patent_edit_mode = False
            st.session_state.patent_selected_id = None
            # 清除成功消息
            st.session_state.patent_success_message = None
            # 保持expander展开
            st.session_state.patent_expander_expanded = True
            if 'patent_selector' in st.session_state:
                del st.session_state.patent_selector

        def set_edit_mode():
            st.session_state.patent_edit_mode = True
            # 清除成功消息
            st.session_state.patent_success_message = None
            # 保持expander展开
            st.session_state.patent_expander_expanded = True

        # 专利选择回调函数
        def on_patent_select():
            st.session_state.patent_selected_id = st.session_state.patent_selector
            # 清除成功消息
            st.session_state.patent_success_message = None
            # 保持expander展开
            st.session_state.patent_expander_expanded = True

        # 创建两个按钮用于切换模式，使用更紧凑的布局
        button_cols = st.columns([1, 1, 3])  # 两个按钮占用较小空间，右侧留白
        with button_cols[0]:
            add_button = st.button("新增信息", on_click=set_add_mode, type="primary" if not st.session_state.patent_edit_mode else "secondary")
        with button_cols[1]:
            edit_button = st.button("编辑已有信息", on_click=set_edit_mode, type="primary" if st.session_state.patent_edit_mode else "secondary")

        # 获取当前模式
        edit_mode = st.session_state.patent_edit_mode

        # 如果是编辑模式，显示专利选择器
        if edit_mode and not patents_df.empty:
            patent_id = st.selectbox(
                "选择要编辑的专利",
                options=patents_df['id'].tolist(),
                format_func=lambda x: patents_df[patents_df['id'] == x]['name'].iloc[0],
                key="patent_selector",
                on_change=on_patent_select
            )

            # 获取选中的专利数据
            if st.session_state.patent_selected_id:
                patent_id = st.session_state.patent_selected_id
                patent_data = patents_df[patents_df['id'] == patent_id].iloc[0]
            else:
                patent_data = patents_df[patents_df['id'] == patent_id].iloc[0]
                st.session_state.patent_selected_id = patent_id
        else:
            patent_id = None
            patent_data = pd.Series({"name": "", "type": "发明专利", "application_date": None,
                                    "grant_date": None, "owner_id": None, "participants": "",
                                    "company": "", "patent_number": "", "certificate": "无"})
            st.session_state.patent_selected_id = None

        # 表单用于添加或编辑专利
        with st.form("patent_form"):

            # 表单字段
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("专利名称", value=patent_data["name"])

                # 专利类型选择
                patent_types = ["发明专利", "实用新型专利", "外观设计专利"]
                type_index = patent_types.index(patent_data["type"]) if patent_data["type"] in patent_types else 0
                patent_type = st.selectbox("专利类型", patent_types, index=type_index)

                # 处理申请日期
                application_date_value = None
                if patent_data["application_date"]:
                    try:
                        application_date_value = datetime.datetime.strptime(patent_data["application_date"], "%Y-%m-%d").date()
                    except:
                        pass

                application_date = st.date_input("申请日期", value=application_date_value)

                # 处理授权日期
                grant_date_value = None
                if patent_data["grant_date"]:
                    try:
                        grant_date_value = datetime.datetime.strptime(patent_data["grant_date"], "%Y-%m-%d").date()
                    except:
                        pass

            with col2:
                grant_date = st.date_input("授权日期", value=grant_date_value)

                # 专利号
                patent_number = st.text_input("专利号", value=patent_data["patent_number"])

                # 申请单位
                company = st.text_input("申请单位", value=patent_data["company"])

                # 证书状态
                certificate_value = patent_data["certificate"] if "certificate" in patent_data else "无"
                certificate = st.selectbox("证书状态", ["有", "无"],
                                         index=0 if certificate_value == "有" else 1)

            # 专利所有人选择
            if not persons_df.empty:
                persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}
                # 添加一个"无"选项
                persons_dict[0] = "无"

                # 获取当前所有人
                current_owner = patent_data["owner_id"] if patent_data["owner_id"] else 0

                owner_id = st.selectbox("专利所有人",
                                      options=[0] + persons_df['id'].tolist(),
                                      index=([0] + persons_df['id'].tolist()).index(current_owner) if current_owner in persons_df['id'].tolist() else 0,
                                      format_func=lambda x: persons_dict.get(x, f"ID:{x}"))

                if owner_id == 0:
                    owner_id = None
            else:
                st.warning("暂无人员信息，请先添加人员")
                owner_id = None

            # 参与人员选择（多选）
            if not persons_df.empty:
                st.subheader("参与人员")

                # 获取当前参与人员
                current_participants = []
                if patent_data["participants"]:
                    try:
                        current_participants = [int(p_id) for p_id in patent_data["participants"].split(",")]
                    except:
                        current_participants = []

                # 过滤掉所有人（一个人不能同时是所有人和参与人）
                participant_options = [p_id for p_id in persons_df['id'].tolist() if p_id != owner_id]

                # 使用multiselect替代复选框
                all_participants = st.multiselect(
                    "选择参与人员",
                    options=participant_options,
                    default=current_participants,
                    format_func=lambda x: persons_dict.get(x, f"ID:{x}")
                )

                participants_str = ",".join(map(str, all_participants)) if all_participants else ""
            else:
                participants_str = ""

            submit_button = st.form_submit_button("保存")

            if submit_button:
                # 表单验证
                if not name:
                    st.error("专利名称不能为空")
                elif not patent_number:
                    st.error("专利号不能为空")
                elif grant_date < application_date:
                    st.error("授权日期不能早于申请日期")
                elif not owner_id and not participants_str:
                    st.error("专利所有人和参与人员至少需要填写一项")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()

                        # 格式化日期
                        application_date_str = application_date.strftime("%Y-%m-%d")
                        grant_date_str = grant_date.strftime("%Y-%m-%d")

                        if st.session_state.patent_edit_mode and st.session_state.patent_selected_id:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE patent SET name=?, type=?, application_date=?, grant_date=?,
                                owner_id=?, participants=?, company=?, patent_number=?, certificate=? WHERE id=?
                            ''', (name, patent_type, application_date_str, grant_date_str,
                                 owner_id, participants_str, company, patent_number, certificate, st.session_state.patent_selected_id))
                            # 保存成功消息到会话状态
                            st.session_state.patent_success_message = f"已更新专利 {name} 的信息"
                            # 保持expander展开
                            st.session_state.patent_expander_expanded = True
                        else:
                            # 新增记录
                            cursor.execute('''
                                INSERT INTO patent (name, type, application_date, grant_date,
                                owner_id, participants, company, patent_number, certificate)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (name, patent_type, application_date_str, grant_date_str,
                                 owner_id, participants_str, company, patent_number, certificate))
                            # 保存成功消息到会话状态
                            st.session_state.patent_success_message = f"已添加专利 {name} 的信息"
                            # 保持expander展开
                            st.session_state.patent_expander_expanded = True

                        conn.commit()
                        conn.close()

                        # 刷新页面
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")

        conn.close()

    st.subheader("专利列表")

    # 查询功能
    search_col1, search_col2, search_col3 = st.columns(3)
    with search_col1:
        search_name = st.text_input("按专利名称搜索")
    with search_col2:
        search_type = st.selectbox("按专利类型筛选", ["全部"] + ["发明专利", "实用新型专利", "外观设计专利"])
    with search_col3:
        search_certificate = st.selectbox("按证书状态筛选", ["全部", "有", "无"])

    # 获取专利信息
    conn = get_connection()

    # 构建查询条件
    conditions = []
    params = []

    if search_name:
        conditions.append("name LIKE ?")
        params.append(f"%{search_name}%")

    if search_type != "全部":
        conditions.append("type = ?")
        params.append(search_type)

    if search_certificate != "全部":
        conditions.append("certificate = ?")
        params.append(search_certificate)

    # 构建SQL查询
    query = "SELECT * FROM patent"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    patents_df = pd.read_sql(query, conn, params=params)

    # 获取人员信息用于显示
    persons_df = pd.read_sql("SELECT id, name FROM person", conn)

    if not patents_df.empty:
        # 格式化人员信息用于显示
        persons_dict = dict(zip(persons_df['id'], persons_df['name']))

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
        display_df = patents_df.copy()
        display_df['专利所有人'] = display_df['owner_id'].apply(format_owner)
        display_df['申请日期'] = display_df['application_date']
        display_df['授权日期'] = display_df['grant_date']
        display_df['证书状态'] = display_df['certificate']

        # 显示专利列表 (不显示ID)
        display_columns = ['name', 'type', '申请日期', '授权日期', '专利所有人', 'patent_number', '证书状态']
        st.dataframe(display_df[display_columns])

        # 详细信息查看和删除选项
        col_view, col_del = st.columns(2)

        with col_view:
            view_id = st.selectbox("选择要查看详细信息的专利", patents_df['id'].tolist(),
                                 format_func=lambda x: patents_df[patents_df['id'] == x]['name'].iloc[0])

            if st.button("查看详细信息"):
                patent_data = patents_df[patents_df['id'] == view_id].iloc[0]

                # 显示基本信息
                st.subheader(f"{patent_data['name']}的详细信息")
                st.markdown(f"**专利类型**: {patent_data['type']}")
                st.markdown(f"**申请日期**: {patent_data['application_date']}")
                st.markdown(f"**授权日期**: {patent_data['grant_date']}")
                st.markdown(f"**专利号**: {patent_data['patent_number']}")
                st.markdown(f"**证书状态**: {patent_data['certificate']}")
                st.markdown(f"**申请单位**: {patent_data['company']}")

                # 显示专利所有人
                owner_name = format_owner(patent_data['owner_id'])
                st.markdown(f"**专利所有人**: {owner_name}")

                # 显示参与人员
                participants = format_participants(patent_data['participants'])
                if participants:
                    st.markdown(f"**参与人员**: {participants}")

        with col_del:
            del_id = st.selectbox("选择要删除的专利", patents_df['id'].tolist(),
                                format_func=lambda x: patents_df[patents_df['id'] == x]['name'].iloc[0])

            if st.button("删除专利"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM patent WHERE id = ?", (del_id,))
                    conn.commit()
                    conn.close()
                    # 保存成功消息到会话状态
                    st.session_state.patent_success_message = "已删除专利"
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {str(e)}")
    else:
        st.info("暂无专利信息")

    conn.close()

# 辅助函数 - 显示专利统计信息
def show_patent_statistics():
    conn = get_connection()

    # 按专利类型统计
    type_stats = pd.read_sql("""
    SELECT type, COUNT(*) as count
    FROM patent
    GROUP BY type
    """, conn)

    if not type_stats.empty:
        st.subheader("专利类型统计")
        st.dataframe(type_stats)
        st.bar_chart(type_stats.set_index('type')['count'])

    # 按证书状态统计
    certificate_stats = pd.read_sql("""
    SELECT certificate, COUNT(*) as count
    FROM patent
    GROUP BY certificate
    """, conn)

    if not certificate_stats.empty:
        st.subheader("证书状态统计")
        st.dataframe(certificate_stats)
        st.bar_chart(certificate_stats.set_index('certificate')['count'])

    # 按年度统计专利申请量
    year_stats = pd.read_sql("""
    SELECT strftime('%Y', application_date) as year, COUNT(*) as count
    FROM patent
    GROUP BY year
    ORDER BY year
    """, conn)

    if not year_stats.empty and not year_stats['year'].iloc[0] is None:
        st.subheader("年度专利申请量")
        st.dataframe(year_stats)
        st.line_chart(year_stats.set_index('year')['count'])

    conn.close()