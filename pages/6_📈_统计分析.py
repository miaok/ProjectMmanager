import streamlit as st
import pandas as pd
import plotly.express as px
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

# 创建切换标签页，增加人员统计标签页
stats_tab1, stats_tab2, stats_tab3, stats_tab4, stats_tab5 = st.tabs(["人员统计", "项目统计", "标准统计", "专利统计", "论文统计"])

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