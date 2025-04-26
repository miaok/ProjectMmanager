import streamlit as st
import pandas as pd
from components.db_utils import get_connection
import datetime

def standard_management():
    #st.title("标准管理")
    
    # 上下布局替代左右分栏
    
    # 使用expander使添加/编辑表单默认隐藏
    with st.expander("添加/编辑标准信息", expanded=False):
        # 获取所有标准信息用于编辑
        conn = get_connection()
        standards_df = pd.read_sql("SELECT * FROM standard", conn)
        
        # 获取所有人员信息用于选择参与人员
        persons_df = pd.read_sql("SELECT id, name FROM person", conn)
        
        # 表单用于添加或编辑标准
        with st.form("standard_form"):
            # 如果是编辑模式，需要选择标准
            edit_mode = st.checkbox("编辑已有标准")
            
            if edit_mode and not standards_df.empty:
                standard_id = st.selectbox("选择要编辑的标准", standards_df['id'].tolist(), 
                                         format_func=lambda x: standards_df[standards_df['id'] == x]['name'].iloc[0])
                standard_data = standards_df[standards_df['id'] == standard_id].iloc[0]
            else:
                standard_id = None
                standard_data = pd.Series({"name": "", "type": "国家标准", "code": "", 
                                          "release_date": None, "implementation_date": None, 
                                          "company": "", "participant_id": None})
            
            # 表单字段分为两列
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("标准名称", value=standard_data["name"])
                
                # 标准性质选择
                standard_types = ["国家标准", "行业标准", "地方标准", "团体标准", "企业标准"]
                type_index = standard_types.index(standard_data["type"]) if standard_data["type"] in standard_types else 0
                standard_type = st.selectbox("标准性质", standard_types, index=type_index)
                
                code = st.text_input("标准号", value=standard_data["code"])
                
                # 处理发布日期
                release_date_value = None
                if standard_data["release_date"]:
                    try:
                        release_date_value = datetime.datetime.strptime(standard_data["release_date"], "%Y-%m-%d").date()
                    except:
                        pass
                
                release_date = st.date_input("发布日期", value=release_date_value)
            
            with col2:
                # 处理实施日期
                impl_date_value = None
                if standard_data["implementation_date"]:
                    try:
                        impl_date_value = datetime.datetime.strptime(standard_data["implementation_date"], "%Y-%m-%d").date()
                    except:
                        pass
                
                implementation_date = st.date_input("实施日期", value=impl_date_value)
                
                # 参与单位
                company = st.text_input("参与单位", value=standard_data["company"])
                
                # 参与人员选择
                if not persons_df.empty:
                    persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}
                    # 添加一个"无"选项
                    persons_dict[0] = "无"
                    
                    # 获取当前参与人员
                    current_participant = standard_data["participant_id"] if standard_data["participant_id"] else 0
                    
                    participant_id = st.selectbox("参与人员", 
                                                options=[0] + persons_df['id'].tolist(),
                                                index=[0] + persons_df['id'].tolist().index(current_participant) if current_participant in persons_df['id'].tolist() else 0,
                                                format_func=lambda x: persons_dict.get(x, f"ID:{x}"))
                    
                    if participant_id == 0:
                        participant_id = None
                else:
                    st.warning("暂无人员信息，请先添加人员")
                    participant_id = None
            
            submit_button = st.form_submit_button("保存")
            
            if submit_button:
                # 表单验证
                if not name:
                    st.error("标准名称不能为空")
                elif not code:
                    st.error("标准号不能为空")
                elif implementation_date < release_date:
                    st.error("实施日期不能早于发布日期")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        # 格式化日期
                        release_date_str = release_date.strftime("%Y-%m-%d")
                        implementation_date_str = implementation_date.strftime("%Y-%m-%d")
                        
                        if edit_mode and standard_id:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE standard SET name=?, type=?, code=?, release_date=?, 
                                implementation_date=?, company=?, participant_id=? WHERE id=?
                            ''', (name, standard_type, code, release_date_str, 
                                 implementation_date_str, company, participant_id, standard_id))
                            st.success(f"已更新标准 {name} 的信息")
                        else:
                            # 新增记录
                            cursor.execute('''
                                INSERT INTO standard (name, type, code, release_date, 
                                implementation_date, company, participant_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (name, standard_type, code, release_date_str, 
                                 implementation_date_str, company, participant_id))
                            st.success(f"已添加标准 {name} 的信息")
                        
                        conn.commit()
                        conn.close()
                        
                        # 刷新页面
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {str(e)}")
        
        conn.close()
    
    st.subheader("标准列表")
    
    # 查询功能
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        search_name = st.text_input("按标准名称搜索")
    with search_col2:
        search_type = st.selectbox("按标准性质筛选", ["全部"] + ["国家标准", "行业标准", "地方标准", "团体标准", "企业标准"])
    
    # 获取标准信息
    conn = get_connection()
    
    # 构建查询条件
    conditions = []
    params = []
    
    if search_name:
        conditions.append("name LIKE ?")
        params.append(f"%{search_name}%")
    
    if search_type != "全部":
        conditions.append("type = ?")
        params.append(search_type)
    
    # 构建SQL查询
    query = "SELECT * FROM standard"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    standards_df = pd.read_sql(query, conn, params=params)
    
    # 获取人员信息用于显示
    persons_df = pd.read_sql("SELECT id, name FROM person", conn)
    persons_dict = {row['id']: row['name'] for _, row in persons_df.iterrows()}
    
    if not standards_df.empty:
        # 格式化显示数据
        display_df = standards_df.copy()
        display_df['participant'] = display_df['participant_id'].apply(
            lambda x: persons_dict.get(x, "无") if x else "无")
        
        # 显示标准列表
        display_columns = ['id', 'name', 'type', 'code', 'release_date', 'implementation_date', 'company', 'participant']
        st.dataframe(display_df[display_columns])
        
        # 详细信息查看和删除选项
        col_view, col_del = st.columns(2)
        
        with col_view:
            view_id = st.selectbox("选择要查看详细信息的标准", standards_df['id'].tolist(), 
                                 format_func=lambda x: standards_df[standards_df['id'] == x]['name'].iloc[0])
            
            if st.button("查看详细信息"):
                standard_data = standards_df[standards_df['id'] == view_id].iloc[0]
                
                # 显示基本信息
                st.subheader(f"{standard_data['name']}的详细信息")
                st.text(f"标准性质: {standard_data['type']}")
                st.text(f"标准号: {standard_data['code']}")
                st.text(f"发布日期: {standard_data['release_date']}")
                st.text(f"实施日期: {standard_data['implementation_date']}")
                st.text(f"参与单位: {standard_data['company']}")
                
                # 显示参与人员信息
                if standard_data['participant_id']:
                    participant_query = "SELECT * FROM person WHERE id = ?"
                    participant_df = pd.read_sql(participant_query, conn, params=[standard_data['participant_id']])
                    
                    if not participant_df.empty:
                        participant = participant_df.iloc[0]
                        st.subheader("参与人员信息")
                        st.text(f"姓名: {participant['name']}")
                        st.text(f"性别: {participant['gender']}")
                        st.text(f"职称: {participant['title']}")
                        st.text(f"联系电话: {participant['phone']}")
                else:
                    st.text("参与人员: 无")
        
        with col_del:
            del_id = st.selectbox("选择要删除的标准", standards_df['id'].tolist(), 
                                format_func=lambda x: standards_df[standards_df['id'] == x]['name'].iloc[0])
            
            if st.button("删除标准"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM standard WHERE id = ?", (del_id,))
                    conn.commit()
                    conn.close()
                    st.success("已删除标准")
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {str(e)}")
    else:
        st.info("未找到符合条件的标准信息")
    
    conn.close()

# 辅助函数 - 显示标准统计信息
def show_standard_statistics():
    conn = get_connection()
    
    # 按标准性质统计
    type_query = """
    SELECT type, COUNT(*) as count
    FROM standard
    GROUP BY type
    ORDER BY count DESC
    """
    type_df = pd.read_sql(type_query, conn)
    
    if not type_df.empty:
        st.subheader("标准性质分布")
        st.dataframe(type_df)
        
        # 可视化
        st.bar_chart(type_df.set_index('type')['count'])
    
    # 按发布年份统计
    year_query = """
    SELECT substr(release_date, 1, 4) as year, COUNT(*) as count
    FROM standard
    GROUP BY year
    ORDER BY year
    """
    year_df = pd.read_sql(year_query, conn)
    
    if not year_df.empty:
        st.subheader("标准发布年份分布")
        st.dataframe(year_df)
        
        # 可视化
        st.line_chart(year_df.set_index('year')['count'])
    
    # 按参与人员统计
    participant_query = """
    SELECT p.name, COUNT(s.id) as standard_count
    FROM person p
    LEFT JOIN standard s ON p.id = s.participant_id
    GROUP BY p.id
    HAVING standard_count > 0
    ORDER BY standard_count DESC
    LIMIT 10
    """
    
    participant_df = pd.read_sql(participant_query, conn)
    
    if not participant_df.empty:
        st.subheader("参与标准最多的人员")
        st.dataframe(participant_df)
        
        # 可视化
        st.bar_chart(participant_df.set_index('name')['standard_count'])
    
    conn.close() 