import sqlite3
import os

# 数据库连接
def get_connection():
    return sqlite3.connect('project_manager.db')

# 更新数据库结构
def update_db_structure():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 检查项目表是否已有status字段
        cursor.execute("PRAGMA table_info(project)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # 项目表添加status字段
        if 'status' not in column_names:
            cursor.execute('ALTER TABLE project ADD COLUMN status TEXT DEFAULT "进行中"')
            print("项目表已添加status字段")
        
        # 专利表添加certificate字段
        cursor.execute("PRAGMA table_info(patent)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'certificate' not in column_names:
            cursor.execute('ALTER TABLE patent ADD COLUMN certificate TEXT DEFAULT "无"')
            print("专利表已添加certificate字段")
        
        # 论文表添加volume_info字段
        cursor.execute("PRAGMA table_info(paper)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'volume_info' not in column_names:
            cursor.execute('ALTER TABLE paper ADD COLUMN volume_info TEXT')
            print("论文表已添加volume_info字段")
        
        # 人员表添加department、position和skill_level字段
        cursor.execute("PRAGMA table_info(person)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'department' not in column_names:
            cursor.execute('ALTER TABLE person ADD COLUMN department TEXT')
            print("人员表已添加department字段")
            
        if 'position' not in column_names:
            cursor.execute('ALTER TABLE person ADD COLUMN position TEXT')
            print("人员表已添加position字段")
            
        if 'skill_level' not in column_names:
            cursor.execute('ALTER TABLE person ADD COLUMN skill_level TEXT')
            print("人员表已添加skill_level字段")
            
        conn.commit()
        print("数据库结构更新完成")
    except Exception as e:
        print(f"更新数据库结构失败: {str(e)}")
    finally:
        conn.close()

# 检查数据库是否存在并初始化
def init_db():
    # 检查数据库文件是否存在
    if not os.path.exists('project_manager.db'):
        print("数据库文件不存在，请先运行 generate_data.py 生成数据")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 创建人员表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS person (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            birth_date TEXT,
            id_card TEXT UNIQUE,
            education TEXT,
            school TEXT,
            graduation_date TEXT,
            major TEXT,
            title TEXT,
            phone TEXT,
            department TEXT,
            position TEXT,
            skill_level TEXT
        )
        ''')
        
        # 创建项目表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            members TEXT,  -- 存储人员id，以逗号分隔
            leader_id INTEGER,
            outcome TEXT,
            status TEXT DEFAULT "进行中",
            FOREIGN KEY (leader_id) REFERENCES person (id)
        )
        ''')
        
        # 创建标准表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS standard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,          -- 标准名称
            type TEXT NOT NULL,          -- 标准性质（国标、行标等）
            code TEXT NOT NULL,          -- 标准号
            release_date TEXT,           -- 发布日期
            implementation_date TEXT,    -- 实施日期
            company TEXT,                -- 参与单位
            participant_id INTEGER,      -- 参与人员ID
            FOREIGN KEY (participant_id) REFERENCES person (id)
        )
        ''')
        
        # 创建专利表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,          -- 专利名称
            type TEXT NOT NULL,          -- 专利类型（发明、实用新型、外观设计）
            application_date TEXT,       -- 申请日期
            grant_date TEXT,             -- 授权日期
            owner_id INTEGER,            -- 专利所有人（人员ID）
            participants TEXT,           -- 其他参与人员（以逗号分隔的ID）
            company TEXT,                -- 申请单位
            patent_number TEXT,          -- 专利号
            certificate TEXT DEFAULT "无", -- 证书状态
            FOREIGN KEY (owner_id) REFERENCES person (id)
        )
        ''')
        
        # 创建论文表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS paper (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,          -- 论文标题
            journal TEXT NOT NULL,        -- 期刊名称
            journal_type TEXT NOT NULL,   -- 期刊类型（核心期刊、SCI等）
            publish_date TEXT,            -- 发表日期
            first_author_id INTEGER,      -- 第一作者ID
            co_authors TEXT,              -- 合作作者ID（以逗号分隔）
            organization TEXT,            -- 作者单位
            volume_info TEXT,             -- 期次信息
            FOREIGN KEY (first_author_id) REFERENCES person (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    else:
        # 如果数据库存在，更新其结构
        update_db_structure()
    
    # 验证表是否存在
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查各表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='person'")
    person_table_exists = cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project'")
    project_table_exists = cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='standard'")
    standard_table_exists = cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patent'")
    patent_table_exists = cursor.fetchone() is not None
    
    # 检查数据是否存在
    if person_table_exists:
        cursor.execute("SELECT COUNT(*) FROM person")
        person_count = cursor.fetchone()[0]
    else:
        person_count = 0
    
    if project_table_exists:
        cursor.execute("SELECT COUNT(*) FROM project")
        project_count = cursor.fetchone()[0]
    else:
        project_count = 0
    
    if standard_table_exists:
        cursor.execute("SELECT COUNT(*) FROM standard")
        standard_count = cursor.fetchone()[0]
    else:
        standard_count = 0
    
    if patent_table_exists:
        cursor.execute("SELECT COUNT(*) FROM patent")
        patent_count = cursor.fetchone()[0]
    else:
        patent_count = 0
    
    conn.close()
    
    # 如果数据为空，建议运行生成脚本
    if person_count == 0 or project_count == 0 or standard_count == 0 or patent_count == 0:
        print(f"数据不完整：人员({person_count})、项目({project_count})、标准({standard_count})、专利({patent_count})")
        print("请运行 generate_data.py 生成完整数据") 