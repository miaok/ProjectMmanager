import streamlit as st
import pandas as pd
import sqlite3
from components.db_utils import get_connection
import io
import base64
from datetime import datetime

def query_management():
    st.subheader("数据查询")
    
    # 创建查询选项卡
    query_tab1, query_tab2, query_tab3, query_tab4, query_tab5 = st.tabs([
        "按人员查询", "按项目查询", "按标准查询", "按专利查询", "按论文查询"
    ])
    
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
    
    # 按人员查询
    with query_tab1:
        st.write("根据人员信息查询关联数据")
        
        # 获取所有人员数据
        conn = get_connection()
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)
        
        if persons_df.empty:
            st.info("暂无人员数据")
        else:
            # 下拉选择人员
            selected_person = st.selectbox(
                "选择人员", 
                options=persons_df['id'].tolist(),
                format_func=lambda x: persons_df[persons_df['id'] == x]['name'].iloc[0]
            )
            
            # 多选查询类型
            query_types = st.multiselect(
                "选择要查询的关联信息",
                options=["基本信息", "关联项目", "关联标准", "关联专利", "关联论文"],
                default=["基本信息"]
            )
            
            if st.button("查询"):
                results = {}
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename_base = f"人员查询_{persons_df[persons_df['id'] == selected_person]['name'].iloc[0]}_{timestamp}"
                
                # 基本信息查询
                if "基本信息" in query_types:
                    person_info = pd.read_sql(f"SELECT * FROM person WHERE id = {selected_person}", conn)
                    if not person_info.empty:
                        # 转换为中文列名
                        display_person = person_info.copy()
                        display_person = display_person.rename(columns={
                            'id': '人员ID',
                            'name': '姓名',
                            'gender': '性别',
                            'birth_date': '出生日期',
                            'id_card': '身份证号',
                            'education': '学历',
                            'school': '毕业学校',
                            'graduation_date': '毕业日期',
                            'major': '专业',
                            'title': '职称',
                            'phone': '手机号码'
                        })
                        
                        st.subheader("基本信息")
                        st.dataframe(display_person)
                        results["基本信息"] = display_person
                
                # 关联项目查询
                if "关联项目" in query_types:
                    projects_query = f"""
                    SELECT p.* FROM project p
                    WHERE p.leader_id = {selected_person} OR p.members LIKE '%{selected_person}%'
                    """
                    projects = pd.read_sql(projects_query, conn)
                    
                    if not projects.empty:
                        # 格式化项目数据，将leader_id替换为姓名
                        persons_dict = dict(zip(persons_df['id'], persons_df['name']))
                        
                        # 处理负责人
                        def format_leader(leader_id):
                            if pd.isna(leader_id) or leader_id is None:
                                return "无"
                            return persons_dict.get(leader_id, f"ID:{leader_id}")
                        
                        # 处理成员列表
                        def format_members(members_str):
                            if not members_str:
                                return "无"
                            try:
                                member_ids = [int(id_str) for id_str in members_str.split(",")]
                                return ", ".join([persons_dict.get(m_id, f"ID:{m_id}") for m_id in member_ids])
                            except:
                                return members_str
                        
                        display_projects = projects.copy()
                        display_projects['项目负责人'] = display_projects['leader_id'].apply(format_leader)
                        display_projects['项目成员'] = display_projects['members'].apply(format_members)
                        
                        # 重命名列为中文并选择要显示的列
                        display_projects = display_projects.rename(columns={
                            'id': '项目ID', 
                            'name': '项目名称',
                            'start_date': '开始日期',
                            'end_date': '结束日期',
                            'outcome': '项目成果'
                        })
                        
                        # 选择要显示的列
                        display_columns = ['项目ID', '项目名称', '开始日期', '结束日期', '项目负责人', '项目成员', '项目成果']
                        
                        st.subheader("关联项目")
                        st.dataframe(display_projects[display_columns])
                        results["关联项目"] = display_projects[display_columns]
                    else:
                        st.info("该人员未参与任何项目")
                
                # 关联标准查询
                if "关联标准" in query_types:
                    standards_query = f"SELECT * FROM standard WHERE participant_id = {selected_person}"
                    standards = pd.read_sql(standards_query, conn)
                    
                    if not standards.empty:
                        # 格式化标准数据，将participant_id替换为姓名
                        persons_dict = dict(zip(persons_df['id'], persons_df['name']))
                        
                        def format_participant(participant_id):
                            if pd.isna(participant_id) or participant_id is None:
                                return "无"
                            return persons_dict.get(participant_id, f"ID:{participant_id}")
                        
                        display_standards = standards.copy()
                        display_standards['参与人员'] = display_standards['participant_id'].apply(format_participant)
                        
                        # 重命名列为中文并选择要显示的列
                        display_standards = display_standards.rename(columns={
                            'id': '标准ID',
                            'name': '标准名称',
                            'type': '标准类型',
                            'code': '标准号',
                            'release_date': '发布日期',
                            'implementation_date': '实施日期',
                            'company': '参与单位'
                        })
                        
                        # 选择要显示的列
                        display_columns = ['标准ID', '标准名称', '标准类型', '标准号', '发布日期', '实施日期', '参与单位', '参与人员']
                        
                        st.subheader("关联标准")
                        st.dataframe(display_standards[display_columns])
                        results["关联标准"] = display_standards[display_columns]
                    else:
                        st.info("该人员未参与任何标准")
                
                # 关联专利查询
                if "关联专利" in query_types:
                    patents_query = f"""
                    SELECT * FROM patent 
                    WHERE owner_id = {selected_person} OR participants LIKE '%{selected_person}%'
                    """
                    patents = pd.read_sql(patents_query, conn)
                    
                    if not patents.empty:
                        # 格式化专利数据，将owner_id和participants替换为姓名
                        persons_dict = dict(zip(persons_df['id'], persons_df['name']))
                        
                        def format_owner(owner_id):
                            if pd.isna(owner_id) or owner_id is None:
                                return "无"
                            return persons_dict.get(owner_id, f"ID:{owner_id}")
                        
                        def format_participants(participants_str):
                            if not participants_str:
                                return "无"
                            try:
                                participant_ids = [int(id_str) for id_str in participants_str.split(",")]
                                return ", ".join([persons_dict.get(p_id, f"ID:{p_id}") for p_id in participant_ids])
                            except:
                                return participants_str
                        
                        display_patents = patents.copy()
                        display_patents['专利所有人'] = display_patents['owner_id'].apply(format_owner)
                        display_patents['参与人员'] = display_patents['participants'].apply(format_participants)
                        
                        # 重命名列为中文并选择要显示的列
                        display_patents = display_patents.rename(columns={
                            'id': '专利ID',
                            'name': '专利名称',
                            'type': '专利类型',
                            'application_date': '申请日期',
                            'grant_date': '授权日期',
                            'company': '申请单位',
                            'patent_number': '专利号'
                        })
                        
                        # 选择要显示的列
                        display_columns = ['专利ID', '专利名称', '专利类型', '专利号', '申请日期', '授权日期', '申请单位', '专利所有人', '参与人员']
                        
                        st.subheader("关联专利")
                        st.dataframe(display_patents[display_columns])
                        results["关联专利"] = display_patents[display_columns]
                    else:
                        st.info("该人员未关联任何专利")
                
                # 关联论文查询
                if "关联论文" in query_types:
                    papers_query = f"""
                    SELECT * FROM paper 
                    WHERE first_author_id = {selected_person} OR co_authors LIKE '%{selected_person}%'
                    """
                    papers = pd.read_sql(papers_query, conn)
                    
                    if not papers.empty:
                        # 格式化论文数据，将first_author_id和co_authors替换为姓名
                        persons_dict = dict(zip(persons_df['id'], persons_df['name']))
                        
                        def format_first_author(author_id):
                            if pd.isna(author_id) or author_id is None:
                                return "无"
                            return persons_dict.get(author_id, f"ID:{author_id}")
                        
                        def format_co_authors(co_authors_str):
                            if not co_authors_str:
                                return "无"
                            try:
                                co_author_ids = [int(id_str) for id_str in co_authors_str.split(",")]
                                return ", ".join([persons_dict.get(a_id, f"ID:{a_id}") for a_id in co_author_ids])
                            except:
                                return co_authors_str
                        
                        display_papers = papers.copy()
                        display_papers['第一作者'] = display_papers['first_author_id'].apply(format_first_author)
                        display_papers['参与作者'] = display_papers['co_authors'].apply(format_co_authors)
                        
                        # 重命名列为中文并选择要显示的列
                        display_papers = display_papers.rename(columns={
                            'id': '论文ID',
                            'title': '论文标题',
                            'journal': '期刊名称',
                            'journal_type': '期刊类型',
                            'publish_date': '发表日期',
                            'organization': '作者单位'
                        })
                        
                        # 选择要显示的列
                        display_columns = ['论文ID', '论文标题', '期刊名称', '期刊类型', '发表日期', '作者单位', '第一作者', '参与作者']
                        
                        st.subheader("关联论文")
                        st.dataframe(display_papers[display_columns])
                        results["关联论文"] = display_papers[display_columns]
                    else:
                        st.info("该人员未关联任何论文")
                
                # 导出数据
                if results:
                    st.subheader("导出查询结果")
                    
                    # 为每个查询结果创建下载链接
                    for key, df in results.items():
                        filename = f"{filename_base}_{key}.xlsx"
                        download_link = get_excel_download_link(df, filename)
                        st.markdown(f"{key}: {download_link}", unsafe_allow_html=True)
                    
                    # 创建一个包含所有结果的Excel文件
                    if len(results) > 1:
                        # 创建Excel writer
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            for key, df in results.items():
                                df.to_excel(writer, sheet_name=key[:31], index=False)  # Excel限制工作表名不超过31个字符
                        
                        excel_data = output.getvalue()
                        b64 = base64.b64encode(excel_data).decode()
                        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename_base}_全部数据.xlsx">下载所有查询结果</a>'
                        st.markdown(href, unsafe_allow_html=True)
    
    # 按标准查询
    with query_tab3:
        st.write("根据标准信息查询关联数据")
        
        # 获取所有标准数据
        conn = get_connection()
        standards_df = pd.read_sql("SELECT id, name FROM standard", conn)
        
        if standards_df.empty:
            st.info("暂无标准数据")
        else:
            # 下拉选择标准
            selected_standard = st.selectbox(
                "选择标准", 
                options=standards_df['id'].tolist(),
                format_func=lambda x: standards_df[standards_df['id'] == x]['name'].iloc[0],
                key="standard_select"
            )
            
            # 多选查询类型
            query_types = st.multiselect(
                "选择要查询的关联信息",
                options=["标准详情", "参与人员"],
                default=["标准详情", "参与人员"],
                key="standard_query_types"
            )
            
            if st.button("查询", key="standard_query_button"):
                results = {}
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename_base = f"标准查询_{standards_df[standards_df['id'] == selected_standard]['name'].iloc[0]}_{timestamp}"
                
                # 标准详情查询
                if "标准详情" in query_types:
                    standard_info = pd.read_sql(f"SELECT * FROM standard WHERE id = {selected_standard}", conn)
                    if not standard_info.empty:
                        # 格式化标准数据，将participant_id替换为姓名
                        persons_dict = dict(zip(persons_df['id'], persons_df['name']))
                        
                        def format_participant(participant_id):
                            if pd.isna(participant_id) or participant_id is None:
                                return "无"
                            return persons_dict.get(participant_id, f"ID:{participant_id}")
                        
                        display_standard = standard_info.copy()
                        display_standard['参与人员'] = display_standard['participant_id'].apply(format_participant)
                        
                        # 重命名列为中文并选择要显示的列
                        display_standard = display_standard.rename(columns={
                            'id': '标准ID',
                            'name': '标准名称',
                            'type': '标准类型',
                            'code': '标准号',
                            'release_date': '发布日期',
                            'implementation_date': '实施日期',
                            'company': '参与单位'
                        })
                        
                        # 选择要显示的列
                        display_columns = ['标准ID', '标准名称', '标准类型', '标准号', '发布日期', '实施日期', '参与单位', '参与人员']
                        
                        st.subheader("标准详情")
                        st.dataframe(display_standard[display_columns])
                        results["标准详情"] = display_standard[display_columns]
                
                # 参与人员查询
                if "参与人员" in query_types:
                    standard_info = pd.read_sql(f"SELECT * FROM standard WHERE id = {selected_standard}", conn)
                    if not standard_info.empty:
                        participant_id = standard_info['participant_id'].iloc[0]
                        if participant_id:
                            participant_query = f"SELECT * FROM person WHERE id = {participant_id}"
                            participant = pd.read_sql(participant_query, conn)
                            
                            if not participant.empty:
                                # 重命名列为中文
                                display_participant = participant.copy()
                                display_participant = display_participant.rename(columns={
                                    'id': '人员ID',
                                    'name': '姓名',
                                    'gender': '性别',
                                    'birth_date': '出生日期',
                                    'id_card': '身份证号',
                                    'education': '学历',
                                    'school': '毕业学校',
                                    'graduation_date': '毕业日期',
                                    'major': '专业',
                                    'title': '职称',
                                    'phone': '手机号码'
                                })
                                
                                # 选择要显示的重要字段
                                display_columns = ['人员ID', '姓名', '性别', '学历', '专业', '职称', '手机号码']
                                
                                st.subheader("参与人员")
                                st.dataframe(display_participant[display_columns])
                                results["参与人员"] = display_participant[display_columns]
                        else:
                            st.info("该标准没有记录参与人员")
                
                # 导出数据
                if results:
                    st.subheader("导出查询结果")
                    
                    # 为每个查询结果创建下载链接
                    for key, df in results.items():
                        filename = f"{filename_base}_{key}.xlsx"
                        download_link = get_excel_download_link(df, filename)
                        st.markdown(f"{key}: {download_link}", unsafe_allow_html=True)
                    
                    # 创建一个包含所有结果的Excel文件
                    if len(results) > 1:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            for key, df in results.items():
                                df.to_excel(writer, sheet_name=key[:31], index=False)
                        
                        excel_data = output.getvalue()
                        b64 = base64.b64encode(excel_data).decode()
                        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename_base}_全部数据.xlsx">下载所有查询结果</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                # 导出数据
                if results:
                    st.subheader("导出查询结果")
                    
                    # 为每个查询结果创建下载链接
                    for key, df in results.items():
                        filename = f"{filename_base}_{key}.xlsx"
                        download_link = get_excel_download_link(df, filename)
                        st.markdown(f"{key}: {download_link}", unsafe_allow_html=True)
                    
                    # 创建一个包含所有结果的Excel文件
                    if len(results) > 1:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            for key, df in results.items():
                                df.to_excel(writer, sheet_name=key[:31], index=False)
                        
                        excel_data = output.getvalue()
                        b64 = base64.b64encode(excel_data).decode()
                        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename_base}_全部数据.xlsx">下载所有查询结果</a>'
                        st.markdown(href, unsafe_allow_html=True)
    
    # 按论文查询
    with query_tab5:
        st.write("根据论文信息查询关联数据")
        
        # 获取所有论文数据
        conn = get_connection()
        papers_df = pd.read_sql("SELECT id, title FROM paper", conn)
        
        if papers_df.empty:
            st.info("暂无论文数据")
        else:
            # 下拉选择论文
            selected_paper = st.selectbox(
                "选择论文", 
                options=papers_df['id'].tolist(),
                format_func=lambda x: papers_df[papers_df['id'] == x]['title'].iloc[0],
                key="paper_select"
            )
            
            # 多选查询类型
            query_types = st.multiselect(
                "选择要查询的关联信息",
                options=["论文详情", "第一作者", "参与作者"],
                default=["论文详情", "第一作者", "参与作者"],
                key="paper_query_types"
            )
            
            if st.button("查询", key="paper_query_button"):
                results = {}
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename_base = f"论文查询_{papers_df[papers_df['id'] == selected_paper]['title'].iloc[0][:20]}_{timestamp}"
                
                # 论文详情查询
                if "论文详情" in query_types:
                    paper_info = pd.read_sql(f"SELECT * FROM paper WHERE id = {selected_paper}", conn)
                    if not paper_info.empty:
                        # 格式化论文数据，将first_author_id和co_authors替换为姓名
                        persons_dict = dict(zip(persons_df['id'], persons_df['name']))
                        
                        def format_first_author(author_id):
                            if pd.isna(author_id) or author_id is None:
                                return "无"
                            return persons_dict.get(author_id, f"ID:{author_id}")
                        
                        def format_co_authors(co_authors_str):
                            if not co_authors_str:
                                return "无"
                            try:
                                co_author_ids = [int(id_str) for id_str in co_authors_str.split(",")]
                                return ", ".join([persons_dict.get(a_id, f"ID:{a_id}") for a_id in co_author_ids])
                            except:
                                return co_authors_str
                        
                        display_paper = paper_info.copy()
                        display_paper['第一作者'] = display_paper['first_author_id'].apply(format_first_author)
                        display_paper['参与作者'] = display_paper['co_authors'].apply(format_co_authors)
                        
                        # 重命名列为中文并选择要显示的列
                        display_paper = display_paper.rename(columns={
                            'id': '论文ID',
                            'title': '论文标题',
                            'journal': '期刊名称',
                            'journal_type': '期刊类型',
                            'publish_date': '发表日期',
                            'organization': '作者单位'
                        })
                        
                        # 选择要显示的列
                        display_columns = ['论文ID', '论文标题', '期刊名称', '期刊类型', '发表日期', '作者单位', '第一作者', '参与作者']
                        
                        st.subheader("论文详情")
                        st.dataframe(display_paper[display_columns])
                        results["论文详情"] = display_paper[display_columns]
                
                # 第一作者查询
                if "第一作者" in query_types:
                    paper_info = pd.read_sql(f"SELECT * FROM paper WHERE id = {selected_paper}", conn)
                    if not paper_info.empty:
                        first_author_id = paper_info['first_author_id'].iloc[0]
                        if first_author_id:
                            first_author_query = f"SELECT * FROM person WHERE id = {first_author_id}"
                            first_author = pd.read_sql(first_author_query, conn)
                            
                            if not first_author.empty:
                                # 重命名列为中文
                                display_first_author = first_author.copy()
                                display_first_author = display_first_author.rename(columns={
                                    'id': '人员ID',
                                    'name': '姓名',
                                    'gender': '性别',
                                    'birth_date': '出生日期',
                                    'id_card': '身份证号',
                                    'education': '学历',
                                    'school': '毕业学校',
                                    'graduation_date': '毕业日期',
                                    'major': '专业',
                                    'title': '职称',
                                    'phone': '手机号码'
                                })
                                
                                # 选择要显示的重要字段
                                display_columns = ['人员ID', '姓名', '性别', '学历', '专业', '职称', '手机号码']
                                
                                st.subheader("第一作者")
                                st.dataframe(display_first_author[display_columns])
                                results["第一作者"] = display_first_author[display_columns]
                        else:
                            st.info("该论文没有记录第一作者")
                
                # 参与作者查询
                if "参与作者" in query_types:
                    paper_info = pd.read_sql(f"SELECT * FROM paper WHERE id = {selected_paper}", conn)
                    if not paper_info.empty:
                        co_authors_str = paper_info['co_authors'].iloc[0]
                        if co_authors_str:
                            co_authors_list = co_authors_str.split(',')
                            if co_authors_list:
                                co_authors_query = f"""
                                SELECT * FROM person 
                                WHERE id IN ({','.join(co_authors_list)})
                                """
                                co_authors = pd.read_sql(co_authors_query, conn)
                                
                                if not co_authors.empty:
                                    # 重命名列为中文
                                    display_co_authors = co_authors.copy()
                                    display_co_authors = display_co_authors.rename(columns={
                                        'id': '人员ID',
                                        'name': '姓名',
                                        'gender': '性别',
                                        'birth_date': '出生日期',
                                        'id_card': '身份证号',
                                        'education': '学历',
                                        'school': '毕业学校',
                                        'graduation_date': '毕业日期',
                                        'major': '专业',
                                        'title': '职称',
                                        'phone': '手机号码'
                                    })
                                    
                                    # 选择要显示的重要字段
                                    display_columns = ['人员ID', '姓名', '性别', '学历', '专业', '职称', '手机号码']
                                    
                                    st.subheader("参与作者")
                                    st.dataframe(display_co_authors[display_columns])
                                    results["参与作者"] = display_co_authors[display_columns]
                        else:
                            st.info("该论文没有记录参与作者")
                
                # 导出数据
                if results:
                    st.subheader("导出查询结果")
                    
                    # 为每个查询结果创建下载链接
                    for key, df in results.items():
                        filename = f"{filename_base}_{key}.xlsx"
                        download_link = get_excel_download_link(df, filename)
                        st.markdown(f"{key}: {download_link}", unsafe_allow_html=True)
                    
                    # 创建一个包含所有结果的Excel文件
                    if len(results) > 1:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            for key, df in results.items():
                                df.to_excel(writer, sheet_name=key[:31], index=False)
                        
                        excel_data = output.getvalue()
                        b64 = base64.b64encode(excel_data).decode()
                        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename_base}_全部数据.xlsx">下载所有查询结果</a>'
                        st.markdown(href, unsafe_allow_html=True)
    
    # 关闭数据库连接
    conn.close() 