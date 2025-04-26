import streamlit as st
from components.standard import standard_management

st.set_page_config(
    page_title="标准管理",
    page_icon="📑",
    layout="wide"
)

# 页面标题
st.title("标准管理")

# 调用标准管理组件
standard_management() 