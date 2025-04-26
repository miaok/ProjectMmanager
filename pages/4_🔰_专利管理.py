import streamlit as st
from components.patent import patent_management

st.set_page_config(
    page_title="专利管理",
    page_icon="🔰",
    layout="wide"
)

# 页面标题
st.title("专利管理")

# 调用专利管理组件
patent_management() 