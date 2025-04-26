import streamlit as st
from components.query import query_management

st.set_page_config(
    page_title="数据查询",
    page_icon="🔍",
    layout="wide"
)

# 页面标题
st.title("数据查询")

# 说明
st.markdown("""
本页面提供多种方式查询系统中的相关数据，并支持查询结果导出为Excel。

您可以通过以下方式查询数据：
- 按人员查询：查看指定人员的基本信息、参与的项目、标准、专利和论文
- 按项目查询：查看项目详情、项目成员和负责人
- 按标准查询：查看标准详情和参与人员
- 按专利查询：查看专利详情、专利所有人和参与人员
- 按论文查询：查看论文详情、第一作者和参与作者

查询结果可以单项或整体导出为Excel文件。
""")

# 调用查询组件
query_management() 