import streamlit as st
import pandas as pd
from components.db_utils import get_connection
import datetime

def paper_management():
    #st.title("论文管理")

    # 上下布局替代左右分栏

    # 初始化会话状态
    if 'paper_edit_mode' not in st.session_state:
        st.session_state.paper_edit_mode = False

    if 'paper_selected_id' not in st.session_state:
        st.session_state.paper_selected_id = None

    # 初始化消息状态
    if 'paper_success_message' not in st.session_state:
        st.session_state.paper_success_message = None

    # 初始化expander展开状态
    if 'paper_expander_expanded' not in st.session_state:
        st.session_state.paper_expander_expanded = False

    # 显示持久化的成功消息
    if st.session_state.paper_success_message:
        st.success(st.session_state.paper_success_message)

    # 使用expander，根据会话状态决定是否展开
    with st.expander("添加/编辑论文信息", expanded=st.session_state.paper_expander_expanded):
        # 获取所有论文信息用于编辑
        conn = get_connection()
        papers_df = pd.read_sql("SELECT * FROM paper", conn)

        # 获取所有人员信息用于选择论文作者
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)

        # 编辑模式切换回调函数
        def set_add_mode():
            st.session_state.paper_edit_mode = False
            st.session_state.paper_selected_id = None
            # 清除成功消息
            st.session_state.paper_success_message = None
            # 保持expander展开
            st.session_state.paper_expander_expanded = True
            if 'paper_selector' in st.session_state:
                del st.session_state.paper_selector

        def set_edit_mode():
            st.session_state.paper_edit_mode = True
            # 清除成功消息
            st.session_state.paper_success_message = None
            # 保持expander展开
            st.session_state.paper_expander_expanded = True

        # 论文选择回调函数
        def on_paper_select():
            st.session_state.paper_selected_id = st.session_state.paper_selector
            # 清除成功消息
            st.session_state.paper_success_message = None
            # 保持expander展开
            st.session_state.paper_expander_expanded = True

        # 创建两个按钮用于切换模式，使用更紧凑的布局
        button_cols = st.columns([1, 1, 3])  # 两个按钮占用较小空间，右侧留白
        with button_cols[0]:
            st.button("新增信息", on_click=set_add_mode, type="primary" if not st.session_state.paper_edit_mode else "secondary")
        with button_cols[1]:
            st.button("编辑已有信息", on_click=set_edit_mode, type="primary" if st.session_state.paper_edit_mode else "secondary")

        # 获取当前模式
        edit_mode = st.session_state.paper_edit_mode

        # 如果是编辑模式，显示论文选择器
        if edit_mode and not papers_df.empty:
            paper_id = st.selectbox(
                "选择要编辑的论文",
                options=papers_df['id'].tolist(),
                format_func=lambda x: papers_df[papers_df['id'] == x]['title'].iloc[0],
                key="paper_selector",
                on_change=on_paper_select
            )

            # 获取选中的论文数据
            if st.session_state.paper_selected_id:
                paper_id = st.session_state.paper_selected_id
                paper_data = papers_df[papers_df['id'] == paper_id].iloc[0]
            else:
                paper_data = papers_df[papers_df['id'] == paper_id].iloc[0]
                st.session_state.paper_selected_id = paper_id
        else:
            paper_id = None
            paper_data = pd.Series({"title": "", "journal": "", "journal_type": "核心期刊",
                                  "publish_date": None, "first_author_id": None,
                                  "co_authors": "", "organization": "", "volume_info": ""})
            st.session_state.paper_selected_id = None

        # 表单用于添加或编辑论文
        with st.form("paper_form"):

            # 表单字段
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("论文标题", value=paper_data["title"])

                journal = st.text_input("期刊名称", value=paper_data["journal"])

                # 期刊类型选择
                journal_types = ["核心期刊", "非核心期刊", "EI收录", "SCI收录"]
                type_index = journal_types.index(paper_data["journal_type"]) if paper_data["journal_type"] in journal_types else 0
                journal_type = st.selectbox("期刊类型", journal_types, index=type_index)

                # 处理发表日期
                publish_date_value = None
                if paper_data["publish_date"]:
                    try:
                        publish_date_value = datetime.datetime.strptime(paper_data["publish_date"], "%Y-%m-%d").date()
                    except:
                        pass

                publish_date = st.date_input("发表日期", value=publish_date_value)

            with col2:
                # 作者单位
                organization = st.text_input("作者单位", value=paper_data["organization"])

                # 期刊期次信息
                volume_info = st.text_input("期刊期次信息(如: 第13卷第5期)", value=paper_data["volume_info"] if "volume_info" in paper_data else "")

                # 第一作者选择
                if not persons_df.empty:
                    persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}
                    # 添加一个"无"选项
                    persons_dict[0] = "无"

                    # 获取当前第一作者
                    current_first_author = paper_data["first_author_id"] if paper_data["first_author_id"] else 0

                    first_author_id = st.selectbox("第一作者",
                                              options=[0] + persons_df['id'].tolist(),
                                              index=([0] + persons_df['id'].tolist()).index(current_first_author) if current_first_author in [0] + persons_df['id'].tolist() else 0,
                                              format_func=lambda x: persons_dict.get(x, f"ID:{x}"))

                    if first_author_id == 0:
                        first_author_id = None
                else:
                    st.warning("暂无人员信息，请先添加人员")
                    first_author_id = None

            # 参与作者选择（多选）
            if not persons_df.empty:
                st.subheader("参与作者")

                # 获取当前参与作者
                current_co_authors = []
                if paper_data["co_authors"]:
                    try:
                        current_co_authors = [int(p_id) for p_id in paper_data["co_authors"].split(",")]
                    except:
                        current_co_authors = []

                # 过滤掉第一作者（一个人不能同时是第一作者和参与作者）
                co_author_options = [p_id for p_id in persons_df['id'].tolist() if p_id != first_author_id]

                # 使用multiselect替代复选框
                all_co_authors = st.multiselect(
                    "选择参与作者",
                    options=co_author_options,
                    default=current_co_authors,
                    format_func=lambda x: persons_dict.get(x, f"ID:{x}")
                )

                co_authors_str = ",".join(map(str, all_co_authors)) if all_co_authors else ""
            else:
                co_authors_str = ""

            submit_button = st.form_submit_button("保存")

            if submit_button:
                # 表单验证
                if not title:
                    st.error("论文标题不能为空")
                elif not journal:
                    st.error("期刊名称不能为空")
                elif not first_author_id and not co_authors_str:
                    st.error("第一作者和参与作者至少需要填写一项")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()

                        # 格式化日期
                        publish_date_str = publish_date.strftime("%Y-%m-%d")

                        if edit_mode and paper_id:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE paper SET title=?, journal=?, journal_type=?, publish_date=?,
                                first_author_id=?, co_authors=?, organization=?, volume_info=? WHERE id=?
                            ''', (title, journal, journal_type, publish_date_str,
                                 first_author_id, co_authors_str, organization, volume_info, paper_id))
                            # 保存成功消息到会话状态
                            st.session_state.paper_success_message = f"已更新论文 {title} 的信息"
                            # 保持expander展开
                            st.session_state.paper_expander_expanded = True
                        else:
                            # 新增记录
                            cursor.execute('''
                                INSERT INTO paper (title, journal, journal_type, publish_date,
                                first_author_id, co_authors, organization, volume_info)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (title, journal, journal_type, publish_date_str,
                                 first_author_id, co_authors_str, organization, volume_info))
                            # 保存成功消息到会话状态
                            st.session_state.paper_success_message = f"已添加论文 {title} 的信息"
                            # 保持expander展开
                            st.session_state.paper_expander_expanded = True

                        conn.commit()
                        conn.close()

                        # 刷新页面
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")

        conn.close()

    st.subheader("论文列表")

    # 直接从数据库获取论文数据
    conn = get_connection()
    papers_df = pd.read_sql("SELECT * FROM paper", conn)

    # 获取人员信息用于显示
    persons_df = pd.read_sql("SELECT id, name FROM person", conn)

    if papers_df.empty:
        st.info("暂无论文信息")
    else:
        # 格式化作者信息
        persons_dict = dict(zip(persons_df['id'], persons_df['name']))

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
        display_df = papers_df.copy()
        display_df['第一作者'] = display_df['first_author_id'].apply(format_first_author)
        display_df['参与作者'] = display_df['co_authors'].apply(format_co_authors)

        # 显示论文列表 (不显示ID)
        display_columns = ['title', 'journal', 'journal_type', 'publish_date', 'volume_info', '第一作者', 'organization']
        st.dataframe(display_df[display_columns])

        # 详细信息查看和删除选项
        col_view, col_del = st.columns(2)

        with col_view:
            view_id = st.selectbox("选择要查看详细信息的论文", papers_df['id'].tolist(),
                                 format_func=lambda x: papers_df[papers_df['id'] == x]['title'].iloc[0])

            if st.button("查看详细信息"):
                paper_data = papers_df[papers_df['id'] == view_id].iloc[0]

                # 显示基本信息
                st.subheader(f"{paper_data['title']}的详细信息")
                st.markdown(f"**期刊名称**: {paper_data['journal']}")
                st.markdown(f"**期刊类型**: {paper_data['journal_type']}")
                st.markdown(f"**发表日期**: {paper_data['publish_date']}")

                # 显示期次信息
                if 'volume_info' in paper_data and paper_data['volume_info']:
                    st.markdown(f"**期次信息**: {paper_data['volume_info']}")

                st.markdown(f"**作者单位**: {paper_data['organization']}")

                # 显示第一作者
                first_author = format_first_author(paper_data['first_author_id'])
                st.markdown(f"**第一作者**: {first_author}")

                # 显示参与作者
                co_authors = format_co_authors(paper_data['co_authors'])
                if co_authors:
                    st.markdown(f"**参与作者**: {co_authors}")

        with col_del:
            del_id = st.selectbox("选择要删除的论文", papers_df['id'].tolist(),
                                format_func=lambda x: papers_df[papers_df['id'] == x]['title'].iloc[0])

            if st.button("删除论文"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM paper WHERE id = ?", (del_id,))
                    conn.commit()
                    conn.close()
                    # 保存成功消息到会话状态
                    st.session_state.paper_success_message = "已删除论文"
                    # 保持expander展开
                    st.session_state.paper_expander_expanded = True
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {str(e)}")

    conn.close()

# 辅助函数 - 显示论文统计信息
def show_paper_statistics():
    conn = get_connection()

    # 按期刊类型统计
    type_stats = pd.read_sql("""
    SELECT journal_type, COUNT(*) as count
    FROM paper
    GROUP BY journal_type
    """, conn)

    if not type_stats.empty:
        st.subheader("期刊类型统计")
        st.dataframe(type_stats)
        st.bar_chart(type_stats.set_index('journal_type')['count'])

    # 按年度统计论文发表量
    year_stats = pd.read_sql("""
    SELECT strftime('%Y', publish_date) as year, COUNT(*) as count
    FROM paper
    GROUP BY year
    ORDER BY year
    """, conn)

    if not year_stats.empty and not year_stats['year'].iloc[0] is None:
        st.subheader("年度论文发表量")
        st.dataframe(year_stats)
        st.line_chart(year_stats.set_index('year')['count'])

    # 按期刊统计论文数量
    journal_stats = pd.read_sql("""
    SELECT journal, COUNT(*) as count
    FROM paper
    GROUP BY journal
    ORDER BY count DESC
    LIMIT 10
    """, conn)

    if not journal_stats.empty:
        st.subheader("期刊发表统计(Top 10)")
        st.dataframe(journal_stats)
        st.bar_chart(journal_stats.set_index('journal')['count'])

    conn.close()