import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.db_utils import get_connection
from components.project import show_statistics
from components.standard import show_standard_statistics
from components.patent import show_patent_statistics
from components.paper import show_paper_statistics

st.set_page_config(
    page_title="统计分析",
    page_icon="📈",
    layout="wide"
)

# 页面标题
st.title("统计分析")

# 创建切换标签页，增加人员统计标签页和自定义图表标签页
stats_tab1, stats_tab2, stats_tab3, stats_tab4, stats_tab5, stats_tab_custom = st.tabs(
    ["人员统计", "项目统计", "标准统计", "专利统计", "论文统计", "自定义图表"]
)

# 新增人员统计标签页
with stats_tab1:
    st.subheader("人员基本统计")

    conn = get_connection()

    # 统计人员性别分布
    gender_query = """
    SELECT gender, COUNT(*) as count
    FROM person
    GROUP BY gender
    """
    gender_df = pd.read_sql(gender_query, conn)

    if not gender_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("性别分布")
            st.dataframe(gender_df)

        with col2:
            fig = px.pie(gender_df, values='count', names='gender', title='性别分布',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig)

    # 统计人员学历分布
    edu_query = """
    SELECT education, COUNT(*) as count
    FROM person
    GROUP BY education
    ORDER BY
    CASE
        WHEN education = '高中' THEN 1
        WHEN education = '专科' THEN 2
        WHEN education = '本科' THEN 3
        WHEN education = '硕士' THEN 4
        WHEN education = '博士' THEN 5
        ELSE 6
    END
    """
    edu_df = pd.read_sql(edu_query, conn)

    if not edu_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("学历分布")
            st.dataframe(edu_df)

        with col2:
            fig = px.pie(edu_df, values='count', names='education', title='学历分布',
                         color_discrete_sequence=px.colors.sequential.Viridis)
            st.plotly_chart(fig)

    # 职称分布
    title_query = """
    SELECT title, COUNT(*) as count
    FROM person
    WHERE title <> ''
    GROUP BY title
    ORDER BY count DESC
    """
    title_df = pd.read_sql(title_query, conn)

    if not title_df.empty and len(title_df) > 0:
        st.subheader("职称分布")
        fig = px.bar(title_df, x='title', y='count', title='职称分布')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

    # 年龄分布（基于出生日期）
    age_query = """
    SELECT
        CASE
            WHEN (strftime('%Y', 'now') - strftime('%Y', birth_date)) < 30 THEN '30岁以下'
            WHEN (strftime('%Y', 'now') - strftime('%Y', birth_date)) BETWEEN 30 AND 40 THEN '30-40岁'
            WHEN (strftime('%Y', 'now') - strftime('%Y', birth_date)) BETWEEN 41 AND 50 THEN '41-50岁'
            ELSE '50岁以上'
        END as age_group,
        COUNT(*) as count
    FROM person
    GROUP BY age_group
    ORDER BY
    CASE
        WHEN age_group = '30岁以下' THEN 1
        WHEN age_group = '30-40岁' THEN 2
        WHEN age_group = '41-50岁' THEN 3
        WHEN age_group = '50岁以上' THEN 4
    END
    """
    age_df = pd.read_sql(age_query, conn)

    if not age_df.empty:
        st.subheader("年龄分布")
        fig = px.bar(age_df, x='age_group', y='count', title='年龄分布',
                     color='count', color_continuous_scale='Viridis')
        st.plotly_chart(fig)

    # 人员贡献度统计
    contribution_query = """
    SELECT
        p.name,
        COUNT(DISTINCT pr.id) as project_count,
        COUNT(DISTINCT s.id) as standard_count,
        COUNT(DISTINCT CASE WHEN pt.owner_id = p.id THEN pt.id END) as patent_owner_count,
        COUNT(DISTINCT CASE WHEN pt.participants LIKE '%' || p.id || '%' THEN pt.id END) as patent_participant_count,
        COUNT(DISTINCT CASE WHEN pa.first_author_id = p.id THEN pa.id END) as paper_first_author_count,
        COUNT(DISTINCT CASE WHEN pa.co_authors LIKE '%' || p.id || '%' THEN pa.id END) as paper_co_author_count
    FROM
        person p
    LEFT JOIN
        (SELECT id, members, leader_id FROM project) pr
        ON (pr.members LIKE '%' || p.id || '%' OR pr.leader_id = p.id)
    LEFT JOIN
        standard s ON p.id = s.participant_id
    LEFT JOIN
        patent pt ON (pt.owner_id = p.id OR pt.participants LIKE '%' || p.id || '%')
    LEFT JOIN
        paper pa ON (pa.first_author_id = p.id OR pa.co_authors LIKE '%' || p.id || '%')
    GROUP BY
        p.id
    HAVING
        project_count > 0 OR standard_count > 0 OR patent_owner_count > 0 OR patent_participant_count > 0 OR paper_first_author_count > 0 OR paper_co_author_count > 0
    ORDER BY
        (project_count + standard_count + patent_owner_count + patent_participant_count + paper_first_author_count + paper_co_author_count) DESC
    LIMIT 10
    """

    contribution_df = pd.read_sql(contribution_query, conn)

    if not contribution_df.empty:
        st.subheader("人员综合贡献度排名（Top 10）")

        # 添加总贡献列
        contribution_df['total_contribution'] = (
            contribution_df['project_count'] +
            contribution_df['standard_count'] +
            contribution_df['patent_owner_count'] * 1.5 +
            contribution_df['patent_participant_count'] * 0.5 +
            contribution_df['paper_first_author_count'] * 1.5 +
            contribution_df['paper_co_author_count'] * 0.5
        )

        st.dataframe(contribution_df.sort_values(by='total_contribution', ascending=False))

        # 可视化 - 堆叠柱状图
        fig = px.bar(
            contribution_df,
            x='name',
            y=['project_count', 'standard_count', 'patent_owner_count', 'patent_participant_count', 'paper_first_author_count', 'paper_co_author_count'],
            title='人员综合贡献度',
            labels={
                'value': '数量',
                'name': '人员',
                'variable': '贡献类型'
            },
            color_discrete_map={
                'project_count': '#1f77b4',
                'standard_count': '#ff7f0e',
                'patent_owner_count': '#2ca02c',
                'patent_participant_count': '#d62728',
                'paper_first_author_count': '#9467bd',
                'paper_co_author_count': '#8c564b'
            },
            hover_data=['total_contribution']
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            legend_title="贡献类型",
            legend={
                'yanchor': "top",
                'y': 0.99,
                'xanchor': "right",
                'x': 0.99
            }
        )

        # 重命名图例
        newnames = {
            'project_count': '项目数',
            'standard_count': '标准数',
            'patent_owner_count': '专利所有',
            'patent_participant_count': '专利参与',
            'paper_first_author_count': '论文第一作者',
            'paper_co_author_count': '论文参与作者'
        }
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))

        st.plotly_chart(fig)

        # 添加雷达图 - 选择前5名人员的贡献度雷达图
        st.subheader("人员贡献度雷达图（Top 5）")

        # 选择前5名人员
        top5_df = contribution_df.sort_values(by='total_contribution', ascending=False).head(5)

        # 准备雷达图数据
        categories = ['项目', '标准', '专利(所有)', '专利(参与)', '论文(第一作者)', '论文(参与作者)']

        fig = go.Figure()

        for i, row in top5_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[
                    row['project_count'],
                    row['standard_count'],
                    row['patent_owner_count'],
                    row['patent_participant_count'],
                    row['paper_first_author_count'],
                    row['paper_co_author_count']
                ],
                theta=categories,
                fill='toself',
                name=row['name']
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, top5_df[['project_count', 'standard_count', 'patent_owner_count',
                                      'patent_participant_count', 'paper_first_author_count',
                                      'paper_co_author_count']].max().max() * 1.1]
                )),
            showlegend=True,
            title="人员贡献度雷达图对比"
        )

        st.plotly_chart(fig)

    # 部门人员分布 - 添加饼图和树状图
    st.subheader("部门人员分布")
    dept_query = """
    SELECT department, COUNT(*) as count
    FROM person
    WHERE department IS NOT NULL AND department != ''
    GROUP BY department
    ORDER BY count DESC
    """
    dept_df = pd.read_sql(dept_query, conn)

    if not dept_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(dept_df)

            # 饼图
            fig = px.pie(
                dept_df,
                values='count',
                names='department',
                title='部门人员分布',
                hole=0.4,  # 设置为环形图
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig)

        with col2:
            # 树状图
            fig = px.treemap(
                dept_df,
                path=['department'],
                values='count',
                title='部门人员分布树状图',
                color='count',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig)

    conn.close()

# 项目统计标签页（原来的第一个标签页）
with stats_tab2:
    show_statistics()

    # 添加项目相关统计分析
    conn = get_connection()

    # 项目时间跨度统计
    st.subheader("项目时间跨度统计")
    duration_query = """
    SELECT name,
           start_date,
           end_date,
           julianday(end_date) - julianday(start_date) as duration_days
    FROM project
    ORDER BY duration_days DESC
    """
    duration_df = pd.read_sql(duration_query, conn)

    if not duration_df.empty:
        duration_df['duration_months'] = (duration_df['duration_days'] / 30).round(1)
        st.dataframe(duration_df[['name', 'start_date', 'end_date', 'duration_months']])

        # 可视化
        st.bar_chart(duration_df.set_index('name')['duration_months'])

    # 学历分布统计
    st.subheader("人员学历分布")
    edu_query = """
    SELECT education, COUNT(*) as count
    FROM person
    GROUP BY education
    ORDER BY count DESC
    """
    edu_df = pd.read_sql(edu_query, conn)

    if not edu_df.empty:
        st.dataframe(edu_df)

        # 使用 plotly 绘制饼图
        fig = px.pie(edu_df, values='count', names='education', title='学历分布')
        st.plotly_chart(fig)

    # 项目时间趋势分析
    st.subheader("项目时间趋势分析")
    trend_query = """
    SELECT
        strftime('%Y', start_date) as year,
        COUNT(*) as project_count,
        SUM(CASE WHEN status = '已完成' THEN 1 ELSE 0 END) as completed_count,
        SUM(CASE WHEN status = '进行中' THEN 1 ELSE 0 END) as ongoing_count,
        SUM(CASE WHEN status = '未开始' THEN 1 ELSE 0 END) as not_started_count
    FROM
        project
    WHERE
        start_date IS NOT NULL
    GROUP BY
        year
    ORDER BY
        year
    """
    trend_df = pd.read_sql(trend_query, conn)

    if not trend_df.empty and not trend_df['year'].iloc[0] is None:
        st.dataframe(trend_df)

        # 使用 plotly 绘制折线图
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=trend_df['year'],
            y=trend_df['project_count'],
            mode='lines+markers',
            name='项目总数',
            line=dict(color='royalblue', width=4)
        ))

        fig.add_trace(go.Scatter(
            x=trend_df['year'],
            y=trend_df['completed_count'],
            mode='lines+markers',
            name='已完成',
            line=dict(color='green', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=trend_df['year'],
            y=trend_df['ongoing_count'],
            mode='lines+markers',
            name='进行中',
            line=dict(color='orange', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=trend_df['year'],
            y=trend_df['not_started_count'],
            mode='lines+markers',
            name='未开始',
            line=dict(color='red', width=2)
        ))

        fig.update_layout(
            title='项目数量年度趋势',
            xaxis_title='年份',
            yaxis_title='项目数量',
            legend_title='项目状态',
            hovermode='x unified'
        )

        st.plotly_chart(fig)

        # 添加堆叠面积图
        fig = px.area(
            trend_df,
            x='year',
            y=['completed_count', 'ongoing_count', 'not_started_count'],
            title='项目状态分布趋势',
            labels={'value': '项目数量', 'year': '年份', 'variable': '项目状态'},
            color_discrete_map={
                'completed_count': 'green',
                'ongoing_count': 'orange',
                'not_started_count': 'red'
            }
        )

        # 重命名图例
        newnames = {
            'completed_count': '已完成',
            'ongoing_count': '进行中',
            'not_started_count': '未开始'
        }
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))

        st.plotly_chart(fig)

    conn.close()

# 标准统计标签页（原来的第二个标签页）
with stats_tab3:
    show_standard_statistics()

    # 添加标准与人员关联的统计
    conn = get_connection()

    # 每个人参与标准和项目的对比
    st.subheader("人员参与项目与标准的对比")
    comparison_query = """
    SELECT p.name,
           COUNT(DISTINCT pr.id) as project_count,
           COUNT(DISTINCT s.id) as standard_count
    FROM person p
    LEFT JOIN (
        SELECT id, members, leader_id
        FROM project
    ) pr ON (pr.members LIKE '%' || p.id || '%' OR pr.leader_id = p.id)
    LEFT JOIN standard s ON p.id = s.participant_id
    GROUP BY p.id
    HAVING project_count > 0 OR standard_count > 0
    ORDER BY (project_count + standard_count) DESC
    LIMIT 10
    """
    comparison_df = pd.read_sql(comparison_query, conn)

    if not comparison_df.empty:
        st.dataframe(comparison_df)

        # 使用plotly创建堆叠柱状图
        fig = px.bar(comparison_df, x='name', y=['project_count', 'standard_count'],
                    title='人员参与项目与标准数量对比',
                    labels={'value': '数量', 'name': '人员', 'variable': '类型'},
                    barmode='group')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

    conn.close()

# 专利统计标签页（原来的第三个标签页）
with stats_tab4:
    show_patent_statistics()

    # 添加专利与其他数据的关联统计
    conn = get_connection()

    # 人员专利统计 - 包括所有人和参与者
    st.subheader("人员专利总数统计")
    patents_query = """
    SELECT
        p.name,
        COUNT(DISTINCT CASE WHEN pt.owner_id = p.id THEN pt.id END) as owner_count,
        COUNT(DISTINCT CASE WHEN pt.participants LIKE '%' || p.id || '%' THEN pt.id END) as participant_count,
        COUNT(DISTINCT CASE WHEN pt.owner_id = p.id OR pt.participants LIKE '%' || p.id || '%' THEN pt.id END) as total_count
    FROM
        person p
    LEFT JOIN
        patent pt ON (pt.owner_id = p.id OR pt.participants LIKE '%' || p.id || '%')
    GROUP BY
        p.id
    HAVING
        total_count > 0
    ORDER BY
        total_count DESC
    LIMIT 10
    """

    patents_person_df = pd.read_sql(patents_query, conn)

    if not patents_person_df.empty:
        st.dataframe(patents_person_df)

        # 可视化 - 显示作为所有人和参与者的专利数量
        fig = px.bar(patents_person_df, x='name', y=['owner_count', 'participant_count'],
                     title='人员拥有和参与的专利数量',
                     labels={'value': '专利数量', 'name': '人员姓名', 'variable': '参与类型'},
                     barmode='stack')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

    # 专利与申请单位分布
    st.subheader("专利与申请单位分布")
    company_query = """
    SELECT
        company,
        COUNT(*) as patent_count,
        COUNT(DISTINCT type) as type_count
    FROM
        patent
    GROUP BY
        company
    ORDER BY
        patent_count DESC
    """

    company_df = pd.read_sql(company_query, conn)

    if not company_df.empty:
        st.dataframe(company_df)

        # 可视化
        if len(company_df) > 10:
            company_df = company_df.head(10)  # 限制显示前10个

        fig = px.bar(company_df, x='company', y='patent_count',
                     title='各单位专利数量分布',
                     labels={'patent_count': '专利数量', 'company': '申请单位'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

    conn.close()

# 添加论文统计标签页
with stats_tab5:
    show_paper_statistics()

# 自定义图表标签页
with stats_tab_custom:
    st.subheader("自定义图表")

    st.markdown("""
    在此页面，您可以创建自定义图表，选择数据源、图表类型和可视化参数。
    """)

    # 选择数据源
    data_source = st.selectbox(
        "选择数据源",
        ["人员数据", "项目数据", "标准数据", "专利数据", "论文数据", "综合数据"]
    )

    # 根据数据源获取数据
    conn = get_connection()

    if data_source == "人员数据":
        # 获取人员数据
        query = """
        SELECT * FROM person
        """
        df = pd.read_sql(query, conn)

        # 可选的分析维度
        dimensions = [
            "按性别统计", "按学历统计", "按部门统计", "按职称统计",
            "按技能等级统计", "按年龄段统计"
        ]

        dimension = st.selectbox("选择分析维度", dimensions)

        if dimension == "按性别统计":
            analysis_df = df.groupby('gender').size().reset_index(name='count')
            x_col = 'gender'
            y_col = 'count'
            title = '人员性别分布'
        elif dimension == "按学历统计":
            analysis_df = df.groupby('education').size().reset_index(name='count')
            x_col = 'education'
            y_col = 'count'
            title = '人员学历分布'
        elif dimension == "按部门统计":
            analysis_df = df.groupby('department').size().reset_index(name='count')
            x_col = 'department'
            y_col = 'count'
            title = '人员部门分布'
        elif dimension == "按职称统计":
            analysis_df = df[df['title'].notna() & (df['title'] != '')].groupby('title').size().reset_index(name='count')
            x_col = 'title'
            y_col = 'count'
            title = '人员职称分布'
        elif dimension == "按技能等级统计":
            analysis_df = df[df['skill_level'].notna() & (df['skill_level'] != '')].groupby('skill_level').size().reset_index(name='count')
            x_col = 'skill_level'
            y_col = 'count'
            title = '人员技能等级分布'
        elif dimension == "按年龄段统计":
            # 计算年龄段
            def get_age_group(birth_date):
                if pd.isna(birth_date) or birth_date == '':
                    return '未知'
                try:
                    year = int(birth_date.split('-')[0])
                    current_year = pd.Timestamp.now().year
                    age = current_year - year
                    if age < 30:
                        return '30岁以下'
                    elif age < 40:
                        return '30-40岁'
                    elif age < 50:
                        return '41-50岁'
                    else:
                        return '50岁以上'
                except:
                    return '未知'

            df['age_group'] = df['birth_date'].apply(get_age_group)
            analysis_df = df.groupby('age_group').size().reset_index(name='count')
            x_col = 'age_group'
            y_col = 'count'
            title = '人员年龄分布'

    elif data_source == "项目数据":
        # 获取项目数据
        query = """
        SELECT * FROM project
        """
        df = pd.read_sql(query, conn)

        # 可选的分析维度
        dimensions = [
            "按状态统计", "按年份统计", "按时长统计"
        ]

        dimension = st.selectbox("选择分析维度", dimensions)

        if dimension == "按状态统计":
            analysis_df = df.groupby('status').size().reset_index(name='count')
            x_col = 'status'
            y_col = 'count'
            title = '项目状态分布'
        elif dimension == "按年份统计":
            df['year'] = df['start_date'].apply(lambda x: x.split('-')[0] if isinstance(x, str) else '未知')
            analysis_df = df.groupby('year').size().reset_index(name='count')
            x_col = 'year'
            y_col = 'count'
            title = '项目年份分布'
        elif dimension == "按时长统计":
            # 计算项目时长（月）
            def calculate_duration(row):
                if pd.isna(row['start_date']) or pd.isna(row['end_date']):
                    return '未知'
                try:
                    start = pd.Timestamp(row['start_date'])
                    end = pd.Timestamp(row['end_date'])
                    months = (end.year - start.year) * 12 + end.month - start.month
                    if months <= 6:
                        return '6个月以内'
                    elif months <= 12:
                        return '6-12个月'
                    elif months <= 24:
                        return '1-2年'
                    else:
                        return '2年以上'
                except:
                    return '未知'

            df['duration'] = df.apply(calculate_duration, axis=1)
            analysis_df = df.groupby('duration').size().reset_index(name='count')
            x_col = 'duration'
            y_col = 'count'
            title = '项目时长分布'

    elif data_source == "标准数据":
        # 获取标准数据
        query = """
        SELECT * FROM standard
        """
        df = pd.read_sql(query, conn)

        # 可选的分析维度
        dimensions = [
            "按类型统计", "按发布年份统计", "按单位统计"
        ]

        dimension = st.selectbox("选择分析维度", dimensions)

        if dimension == "按类型统计":
            analysis_df = df.groupby('type').size().reset_index(name='count')
            x_col = 'type'
            y_col = 'count'
            title = '标准类型分布'
        elif dimension == "按发布年份统计":
            df['year'] = df['release_date'].apply(lambda x: x.split('-')[0] if isinstance(x, str) else '未知')
            analysis_df = df.groupby('year').size().reset_index(name='count')
            x_col = 'year'
            y_col = 'count'
            title = '标准发布年份分布'
        elif dimension == "按单位统计":
            analysis_df = df.groupby('company').size().reset_index(name='count')
            x_col = 'company'
            y_col = 'count'
            title = '标准单位分布'

    elif data_source == "专利数据":
        # 获取专利数据
        query = """
        SELECT * FROM patent
        """
        df = pd.read_sql(query, conn)

        # 可选的分析维度
        dimensions = [
            "按类型统计", "按申请年份统计", "按单位统计", "按证书状态统计"
        ]

        dimension = st.selectbox("选择分析维度", dimensions)

        if dimension == "按类型统计":
            analysis_df = df.groupby('type').size().reset_index(name='count')
            x_col = 'type'
            y_col = 'count'
            title = '专利类型分布'
        elif dimension == "按申请年份统计":
            df['year'] = df['application_date'].apply(lambda x: x.split('-')[0] if isinstance(x, str) else '未知')
            analysis_df = df.groupby('year').size().reset_index(name='count')
            x_col = 'year'
            y_col = 'count'
            title = '专利申请年份分布'
        elif dimension == "按单位统计":
            analysis_df = df.groupby('company').size().reset_index(name='count')
            x_col = 'company'
            y_col = 'count'
            title = '专利单位分布'
        elif dimension == "按证书状态统计":
            analysis_df = df.groupby('certificate').size().reset_index(name='count')
            x_col = 'certificate'
            y_col = 'count'
            title = '专利证书状态分布'

    elif data_source == "论文数据":
        # 获取论文数据
        query = """
        SELECT * FROM paper
        """
        df = pd.read_sql(query, conn)

        # 可选的分析维度
        dimensions = [
            "按期刊类型统计", "按发表年份统计", "按期刊统计"
        ]

        dimension = st.selectbox("选择分析维度", dimensions)

        if dimension == "按期刊类型统计":
            analysis_df = df.groupby('journal_type').size().reset_index(name='count')
            x_col = 'journal_type'
            y_col = 'count'
            title = '论文期刊类型分布'
        elif dimension == "按发表年份统计":
            df['year'] = df['publish_date'].apply(lambda x: x.split('-')[0] if isinstance(x, str) else '未知')
            analysis_df = df.groupby('year').size().reset_index(name='count')
            x_col = 'year'
            y_col = 'count'
            title = '论文发表年份分布'
        elif dimension == "按期刊统计":
            analysis_df = df.groupby('journal').size().reset_index(name='count')
            x_col = 'journal'
            y_col = 'count'
            title = '论文期刊分布'

    elif data_source == "综合数据":
        # 获取综合统计数据
        query_person = "SELECT COUNT(*) as count FROM person"
        query_project = "SELECT COUNT(*) as count FROM project"
        query_standard = "SELECT COUNT(*) as count FROM standard"
        query_patent = "SELECT COUNT(*) as count FROM patent"
        query_paper = "SELECT COUNT(*) as count FROM paper"

        person_count = pd.read_sql(query_person, conn).iloc[0]['count']
        project_count = pd.read_sql(query_project, conn).iloc[0]['count']
        standard_count = pd.read_sql(query_standard, conn).iloc[0]['count']
        patent_count = pd.read_sql(query_patent, conn).iloc[0]['count']
        paper_count = pd.read_sql(query_paper, conn).iloc[0]['count']

        analysis_df = pd.DataFrame({
            'category': ['人员', '项目', '标准', '专利', '论文'],
            'count': [person_count, project_count, standard_count, patent_count, paper_count]
        })

        x_col = 'category'
        y_col = 'count'
        title = '数据总量统计'

    # 选择图表类型
    chart_types = ["柱状图", "饼图", "折线图", "雷达图", "树状图", "热力图"]
    chart_type = st.selectbox("选择图表类型", chart_types)

    # 图表颜色主题
    color_themes = [
        "默认", "Viridis", "Plasma", "Inferno", "Magma", "Cividis",
        "Warm", "Cool", "Blues", "Greens", "Reds", "Purples", "Oranges"
    ]
    color_theme = st.selectbox("选择颜色主题", color_themes)

    # 获取颜色主题
    if color_theme == "默认":
        color_sequence = None
    else:
        color_sequence = getattr(px.colors.sequential, color_theme, None)

    # 图表标题
    custom_title = st.text_input("自定义图表标题", title)

    # 生成图表
    if st.button("生成图表"):
        if 'analysis_df' in locals() and not analysis_df.empty:
            st.subheader("数据预览")
            st.dataframe(analysis_df)

            st.subheader("图表预览")

            if chart_type == "柱状图":
                fig = px.bar(
                    analysis_df,
                    x=x_col,
                    y=y_col,
                    title=custom_title,
                    color=y_col if len(analysis_df) > 1 else None,
                    color_continuous_scale=color_sequence
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)

            elif chart_type == "饼图":
                fig = px.pie(
                    analysis_df,
                    values=y_col,
                    names=x_col,
                    title=custom_title,
                    color_discrete_sequence=color_sequence
                )
                st.plotly_chart(fig)

            elif chart_type == "折线图":
                fig = px.line(
                    analysis_df,
                    x=x_col,
                    y=y_col,
                    title=custom_title,
                    markers=True,
                    color_discrete_sequence=color_sequence
                )
                st.plotly_chart(fig)

            elif chart_type == "雷达图":
                # 雷达图需要特殊处理
                fig = go.Figure()

                fig.add_trace(go.Scatterpolar(
                    r=analysis_df[y_col],
                    theta=analysis_df[x_col],
                    fill='toself',
                    name=custom_title
                ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, analysis_df[y_col].max() * 1.1]
                        )
                    ),
                    showlegend=False,
                    title=custom_title
                )

                st.plotly_chart(fig)

            elif chart_type == "树状图":
                fig = px.treemap(
                    analysis_df,
                    path=[x_col],
                    values=y_col,
                    title=custom_title,
                    color=y_col,
                    color_continuous_scale=color_sequence
                )
                st.plotly_chart(fig)

            elif chart_type == "热力图":
                # 热力图需要特殊处理，这里简化为一维热力图
                fig = px.imshow(
                    analysis_df[y_col].values.reshape(1, -1),
                    labels=dict(x=x_col, y="", color=y_col),
                    x=analysis_df[x_col],
                    title=custom_title,
                    color_continuous_scale=color_sequence
                )
                st.plotly_chart(fig)
        else:
            st.error("无法生成图表，请检查数据源和分析维度。")

    conn.close()