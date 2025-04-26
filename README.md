# 项目与人员管理系统

基于Streamlit和SQLite3的简单数据存储与查询项目。

## 功能特点

1. **人员管理**：
   - 添加、编辑、删除人员信息
   - 查询人员信息
   - 查看人员参与的项目

2. **项目管理**：
   - 添加、编辑、删除项目信息
   - 查询项目信息
   - 管理项目成员和负责人

3. **标准管理**：
   - 添加、编辑、删除标准信息
   - 查询标准信息
   - 跟踪标准的参与单位和参与人员

4. **专利管理**：
   - 添加、编辑、删除专利信息
   - 查询专利信息
   - 管理专利所有人和参与人员
   - 记录专利申请和授权时间

5. **数据关联**：
   - 人员可以关联到多个项目、标准和专利
   - 项目可以包含多个人员
   - 标准可以关联到参与人员
   - 专利可以关联到所有人和多位参与人员
   - 支持查询某人参与的项目、标准和专利

## 系统结构

- 使用SQLite3数据库存储数据
- 使用Streamlit构建用户界面
- 左右分栏布局，左侧为编辑区，右侧为显示区
- 模块化设计，便于扩展

## 安装与运行

1. 安装依赖：
```
pip install -r requirements.txt
```

2. 生成示例数据：
```
python generate_data.py
```

3. 运行应用：
```
streamlit run app.py
```

## 数据生成

本系统使用独立的数据生成脚本(`generate_data.py`)来创建示例数据，这样做的好处是：

1. 可以方便地修改生成脚本以自定义数据
2. 可以随时重新生成干净的数据库
3. 分离数据生成和应用逻辑，使代码更清晰

如果需要自定义生成的数据，可以修改`generate_data.py`文件中的以下参数：

- 生成的人员数量: `generate_person_data(20)`
- 生成的项目数量: `generate_project_data(person_ids, 15)`
- 生成的标准数量: `generate_standard_data(person_ids, 15)`
- 生成的专利数量: `generate_patent_data(person_ids, 30)`

## 数据结构

1. 人员信息表 (person)：
   - id：主键
   - name：姓名
   - gender：性别
   - birth_date：出生日期
   - id_card：身份证号
   - education：学历
   - school：毕业学校
   - graduation_date：毕业日期
   - major：专业
   - title：职称
   - phone：手机号码

2. 项目信息表 (project)：
   - id：主键
   - name：项目名称
   - start_date：起始日期
   - end_date：截止日期
   - members：项目成员（以逗号分隔的ID）
   - leader_id：主负责人ID
   - outcome：项目成果

3. 标准信息表 (standard)：
   - id：主键
   - name：标准名称
   - type：标准性质（国标、行标等）
   - code：标准号
   - release_date：发布日期
   - implementation_date：实施日期
   - company：参与单位
   - participant_id：参与人员ID

4. 专利信息表 (patent)：
   - id：主键
   - name：专利名称
   - type：专利类型（发明专利、实用新型专利、外观设计专利）
   - application_date：申请日期
   - grant_date：授权日期
   - owner_id：专利所有人ID
   - participants：其他参与人员（以逗号分隔的ID）
   - company：申请单位
   - patent_number：专利号

## 注意事项

- 首次运行前需要先执行`generate_data.py`生成示例数据
- 人员信息被项目、标准或专利引用时，无法直接删除
- 项目成员必须包含主负责人
- 专利需要至少有所有人或参与人员之一
- 系统会自动检测数据完整性，如果数据不完整会提示重新生成数据 