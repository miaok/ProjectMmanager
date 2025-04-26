import streamlit as st
import os
from components.db_utils import init_db, get_connection

# 页面配置
st.set_page_config(
    page_title="项目与人员管理系统",
    page_icon="📊",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
footer {
    visibility: hidden;
}
.warning-box {
    background-color: #ffe0b2;
    border-left: 4px solid #ff9800;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}
.error-box {
    background-color: #ffcdd2;
    border-left: 4px solid #f44336;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}
.info-box {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# 检查数据库文件是否存在
db_exists = os.path.exists('project_manager.db')

# 如果数据库不存在，显示错误信息
if not db_exists:
    st.markdown("""
    <div class="error-box">
        <h3>数据库文件不存在</h3>
        <p>请运行以下命令生成示例数据库：</p>
        <pre>python generate_data.py</pre>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示数据生成说明
    st.markdown("""
    ### 数据生成说明
    
    1. 在命令行运行 `python generate_data.py` 生成示例数据
    2. 该脚本将创建 `project_manager.db` 文件并填充模拟数据
    3. 生成完成后，刷新本页面继续使用系统
    
    如果您需要修改模拟数据，可以编辑 `generate_data.py` 文件调整参数。
    """)
    
    st.stop()  # 停止应用程序继续执行

# 初始化数据库
init_db()

# 检查数据是否存在
conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM person")
person_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM project")
project_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM standard")
standard_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM patent")
patent_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM paper")
paper_count = cursor.fetchone()[0]

conn.close()

# 如果数据不完整，显示警告信息
if person_count == 0 or project_count == 0 or standard_count == 0 or patent_count == 0 or paper_count == 0:
    st.markdown(f"""
    <div class="warning-box">
        <h3>数据不完整</h3>
        <p>检测到数据库中的数据不完整：</p>
        <ul>
            <li>人员数据：{person_count} 条</li>
            <li>项目数据：{project_count} 条</li>
            <li>标准数据：{standard_count} 条</li>
            <li>专利数据：{patent_count} 条</li>
            <li>论文数据：{paper_count} 条</li>
        </ul>
        <p>建议运行 <code>python generate_data.py</code> 重新生成完整数据</p>
    </div>
    """, unsafe_allow_html=True)

# 主页内容
st.title("项目与人员管理系统")

# 主页简介
st.markdown("""
## 欢迎使用项目与人员管理系统

这是一个基于Streamlit和SQLite开发的简单项目与人员管理系统。系统可用于管理：

- **人员信息**：添加、编辑、删除人员信息
- **项目管理**：管理项目信息、项目成员和负责人
- **标准管理**：管理标准信息和参与人员
- **专利管理**：管理专利信息、专利所有人和参与人员
- **论文管理**：管理论文信息、第一作者和参与作者
- **数据查询**：查询各类数据之间的关联关系并导出Excel
- **统计分析**：对各类数据进行统计和可视化分析

### 使用指南

请通过左侧导航菜单选择要使用的功能：

1. 👤 **人员管理**：管理系统中的人员信息
2. 📋 **项目管理**：管理项目信息和团队成员
3. 📑 **标准管理**：管理标准信息和参与人员
4. 🔰 **专利管理**：管理专利信息、所有人和参与人员
5. 📚 **论文管理**：管理论文信息、第一作者和参与作者
6. 🔍 **数据查询**：查询系统中各类数据的关联关系并导出
7. 📈 **统计分析**：查看各类统计数据和图表
""")

# 显示系统信息
#st.sidebar.caption("项目与人员管理系统 v1.0") 