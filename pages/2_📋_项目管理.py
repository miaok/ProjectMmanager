import streamlit as st
from components.project import project_management

st.set_page_config(
    page_title="项目管理",
    page_icon="📋",
    layout="wide"
)

# 页面标题
st.title("项目管理")

# 调用项目管理组件
project_management() 