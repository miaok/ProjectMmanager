import streamlit as st
from components.person import person_management

st.set_page_config(
    page_title="人员管理",
    page_icon="👤",
    layout="wide"
)

# 页面标题
st.title("人员管理")

# 调用人员管理组件
person_management() 