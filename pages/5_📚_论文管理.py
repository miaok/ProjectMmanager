import streamlit as st
from components.paper import paper_management

st.set_page_config(
    page_title="论文管理",
    page_icon="📚",
    layout="wide"
)

# 页面标题
st.title("论文管理")

# 调用论文管理组件
paper_management() 