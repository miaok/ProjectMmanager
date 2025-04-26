import sqlite3
import random
import string
from datetime import datetime, timedelta

# 数据库文件路径
DB_FILE = 'project_manager.db'

# 获取数据库连接
def get_connection():
    return sqlite3.connect(DB_FILE)

# 生成随机身份证号
def generate_id_card():
    # 地区码（前6位）- 使用有效的地区码
    area_codes = [
        "110100", "110200", "120100", "130100", "130200", "130300", "130400", "130500",
        "130600", "130700", "130800", "130900", "131000", "131100", "140100", "140200",
        "140300", "140400", "140500", "140600", "140700", "140800", "140900", "141000",
        "141100", "150100", "150200", "150300", "150400", "150500", "150600", "150700",
        "150800", "150900", "152200", "152500", "152900", "210100", "210200", "210300",
        "210400", "210500", "210600", "210700", "210800", "210900", "211000", "211100",
        "211200", "211300", "211400", "220100", "220200", "220300", "220400", "220500",
        "220600", "220700", "220800", "222400", "230100", "230200", "230300", "230400",
        "230500", "230600", "230700", "230800", "230900", "231000", "231100", "231200",
        "232700", "310100", "310200", "320100", "320200", "320300", "320400", "320500",
        "320600", "320700", "320800", "320900", "321000", "321100", "321200", "321300",
        "330100", "330200", "330300", "330400", "330500", "330600", "330700", "330800",
        "330900", "331000", "331100", "340100", "340200", "340300", "340400", "340500",
        "340600", "340700", "340800", "341000", "341100", "341200", "341300", "341500",
        "341600", "341700", "341800", "350100", "350200", "350300", "350400", "350500",
        "350600", "350700", "350800", "350900", "360100", "360200", "360300", "360400",
        "360500", "360600", "360700", "360800", "360900", "361000", "361100", "370100",
        "370200", "370300", "370400", "370500", "370600", "370700", "370800", "370900",
        "371000", "371100", "371200", "371300", "371400", "371500", "371600", "371700",
        "410100", "410200", "410300", "410400", "410500", "410600", "410700", "410800",
        "410900", "411000", "411100", "411200", "411300", "411400", "411500", "411600",
        "411700", "420100", "420200", "420300", "420500", "420600", "420700", "420800",
        "420900", "421000", "421100", "421200", "421300", "422800", "429000", "430100",
        "430200", "430300", "430400", "430500", "430600", "430700", "430800", "430900",
        "431000", "431100", "431200", "431300", "433100", "440100", "440200", "440300",
        "440400", "440500", "440600", "440700", "440800", "440900", "441200", "441300",
        "441400", "441500", "441600", "441700", "441800", "441900", "442000", "445100",
        "445200", "445300", "450100", "450200", "450300", "450400", "450500", "450600",
        "450700", "450800", "450900", "451000", "451100", "451200", "451300", "451400",
        "460100", "460200", "460300", "460400", "469000", "500100", "500200", "510100",
        "510300", "510400", "510500", "510600", "510700", "510800", "510900", "511000",
        "511100", "511300", "511400", "511500", "511600", "511700", "511800", "511900",
        "512000", "513200", "513300", "513400", "520100", "520200", "520300", "520400",
        "520500", "520600", "522300", "522600", "522700", "530100", "530300", "530400",
        "530500", "530600", "530700", "530800", "530900", "532300", "532500", "532600",
        "532800", "532900", "533100", "533300", "533400", "540100", "542100", "542200",
        "542300", "542400", "542500", "542600", "610100", "610200", "610300", "610400",
        "610500", "610600", "610700", "610800", "610900", "611000", "620100", "620200",
        "620300", "620400", "620500", "620600", "620700", "620800", "620900", "621000",
        "621100", "621200", "622900", "623000", "630100", "632100", "632200", "632300",
        "632500", "632600", "632700", "632800", "640100", "640200", "640300", "640400",
        "640500", "650100", "650200", "652100", "652200", "652300", "652700", "652800",
        "652900", "653000", "653100", "653200", "654000", "654200", "654300", "659000"
    ]
    area_code = random.choice(area_codes)

    # 出生日期（中间8位）
    birth_year = random.randint(1960, 2000)
    birth_month = random.randint(1, 12)
    # 根据月份确定天数
    if birth_month in [4, 6, 9, 11]:
        max_day = 30
    elif birth_month == 2:
        # 处理闰年
        if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
            max_day = 29
        else:
            max_day = 28
    else:
        max_day = 31

    birth_day = random.randint(1, max_day)
    birth_code = f"{birth_year:04d}{birth_month:02d}{birth_day:02d}"

    # 顺序码（后3位）
    seq = random.randint(1, 999)

    # 构建前17位
    id_17 = f"{area_code}{birth_code}{seq:03d}"

    # 计算校验码
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    checksum_map = '10X98765432'

    # 计算校验和
    checksum = 0
    for i in range(17):
        checksum += int(id_17[i]) * factors[i]

    # 计算校验码
    verify_code = checksum_map[checksum % 11]

    return f"{id_17}{verify_code}"

# 生成随机手机号
def generate_phone():
    # 中国手机号码前三位运营商号段
    mobile_prefixes = [
        # 中国移动
        '134', '135', '136', '137', '138', '139', '147', '148', '150', '151', '152', '157', '158', '159',
        '165', '172', '178', '182', '183', '184', '187', '188', '195', '197', '198',
        # 中国联通
        '130', '131', '132', '145', '146', '155', '156', '166', '167', '171', '175', '176', '185', '186', '196',
        # 中国电信
        '133', '149', '153', '173', '174', '177', '180', '181', '189', '190', '191', '193', '199',
        # 虚拟运营商
        '162', '165', '167', '170', '171'
    ]

    # 随机选择前三位
    prefix = random.choice(mobile_prefixes)

    # 生成后8位数字
    suffix = ''.join(random.choice(string.digits) for _ in range(8))

    return f"{prefix}{suffix}"

# 创建数据库表结构
def create_tables():
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
        certificate TEXT DEFAULT "无",  -- 证书状态
        FOREIGN KEY (owner_id) REFERENCES person (id)
    )
    ''')

    # 创建论文表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paper (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,          -- 论文标题
        journal TEXT NOT NULL,        -- 期刊名称
        journal_type TEXT NOT NULL,   -- 期刊类型（核心、非核心、EI、SCI）
        publish_date TEXT,            -- 发表日期
        first_author_id INTEGER,      -- 第一作者ID
        co_authors TEXT,              -- 参与作者（以逗号分隔的ID）
        organization TEXT,            -- 作者单位
        volume_info TEXT,             -- 期次信息
        FOREIGN KEY (first_author_id) REFERENCES person (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("数据库表结构创建完成")

# 生成人员数据
def generate_person_data(count=15):
    conn = get_connection()
    cursor = conn.cursor()

    # 清空现有数据
    cursor.execute("DELETE FROM person")

    names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
             "郑十一", "王十二", "刘十三", "陈十四", "杨十五", "黄十六", "赵十七",
             "朱十八", "冯十九", "程二十", "褚二十一", "魏二十二"]

    if count > len(names):
        # 如果需要生成更多数据，复制名字列表
        names = names * (count // len(names) + 1)

    names = names[:count]  # 截取需要的数量

    genders = ["男", "女"]
    educations = ["高中", "专科", "本科", "硕士", "博士"]
    schools = ["四川大学", "江南大学", "中国农业大学", "华中农业大学", "天津科技大学",
               "北京工商大学", "西北农林科技大学", "安徽农业大学", "贵州大学", "山东大学"]
    majors = ["微生物学", "生物工程", "食品科学与工程", "酿酒工程", "发酵工程",
              "生物化学", "食品安全", "有机化学", "分析化学", "酒体设计学", "感官科学"]
    titles = ["初级品酒师", "高级品酒师", "酿酒工程师", "高级工程师", "研发主管", "技术专家", "无"]

    # 新增字段的数据选项
    departments = ["研发部", "生产部", "质检部", "实验室", "工艺部", "品控部", "技术中心"]
    positions = ["研究员", "工程师", "技术员", "部门经理", "主管", "专员", "组长", "技术总监"]
    skill_levels = ["初级", "中级", "高级", "资深", "专家"]

    person_ids = []  # 存储生成的人员ID

    for name in names:
        gender = random.choice(genders)
        birth_year = random.randint(1960, 2000)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

        id_card = generate_id_card()
        education = random.choice(educations)
        school = random.choice(schools)

        grad_year = birth_year + random.randint(20, 30)
        grad_month = random.randint(1, 12)
        grad_day = random.randint(1, 28)
        graduation_date = f"{grad_year}-{grad_month:02d}-{grad_day:02d}"

        major = random.choice(majors)
        title = random.choice(titles)
        phone = generate_phone()

        # 新增字段的随机值
        department = random.choice(departments)
        position = random.choice(positions)
        skill_level = random.choice(skill_levels)

        cursor.execute('''
            INSERT INTO person (name, gender, birth_date, id_card, education, school,
                               graduation_date, major, title, phone, department, position, skill_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, gender, birth_date, id_card, education, school,
              graduation_date, major, title, phone, department, position, skill_level))

        # 获取插入的ID
        person_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()
    print(f"已生成 {len(person_ids)} 条人员数据")
    return person_ids

# 生成项目数据
def generate_project_data(person_ids, count=10):
    if not person_ids:
        print("无法生成项目数据：没有人员数据")
        return []

    conn = get_connection()
    cursor = conn.cursor()

    # 清空现有数据
    cursor.execute("DELETE FROM project")

    project_names = [
        "白酒酿造微生物菌种优化研究", "白酒香味成分分析系统开发", "酒曲制作工艺改良",
        "白酒陈酿加速技术研究", "发酵温度对白酒品质影响分析",
        "白酒酿造过程智能监控系统", "酿酒微生物多样性研究",
        "白酒感官评价标准体系构建", "酒体设计数字模型开发",
        "酿酒废弃物资源化利用技术", "酒体中有机酸含量调控研究",
        "白酒中微量元素分析方法开发", "基于代谢组学的白酒品质控制",
        "白酒酿造智能温控系统", "新型酒曲微生物筛选与应用研究"
    ]

    if count > len(project_names):
        # 构造更多项目名称
        for i in range(len(project_names), count):
            project_names.append(f"白酒研究项目{i+1}")

    project_names = project_names[:count]  # 截取需要的数量

    project_ids = []  # 存储生成的项目ID

    # 项目成果选项
    outcomes = [
        "发酵效率提高15%",
        "建立完整的白酒品评体系",
        "申请3项发酵工艺专利",
        "白酒产量提升20%",
        "降低生产成本30%",
        "微生物种群优化方案",
        "获得省级科技进步奖",
        "开发新型酿酒微生物菌剂",
        "完成酿酒智能监控系统开发",
        "白酒陈酿期缩短40%"
    ]

    # 项目状态选项
    statuses = ["进行中", "已完成"]

    for project_name in project_names:
        # 随机起止日期
        start_year = random.randint(2018, 2023)
        start_month = random.randint(1, 12)
        start_day = random.randint(1, 28)
        start_date = f"{start_year}-{start_month:02d}-{start_day:02d}"

        # 确保结束日期在开始日期之后
        end_date_obj = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(90, 730))
        end_date = end_date_obj.strftime("%Y-%m-%d")

        # 根据当前日期和结束日期自动判断项目状态
        current_date = datetime.now()
        if end_date_obj < current_date:
            status = "已完成"
        else:
            # 如果结束日期还未到，大部分是进行中，但也有可能提前完成
            status = random.choices(statuses, weights=[0.8, 0.2], k=1)[0]

        # 随机选择项目成员和负责人
        team_size = random.randint(3, min(6, len(person_ids)))
        team_members = random.sample(person_ids, team_size)
        leader = random.choice(team_members)

        # 构建项目成员字符串
        member_ids = [str(member_id) for member_id in team_members]
        members_str = ",".join(member_ids)

        # 随机项目成果
        outcome = random.choice(outcomes)

        cursor.execute('''
            INSERT INTO project (name, start_date, end_date, members, leader_id, outcome, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_name, start_date, end_date, members_str, leader, outcome, status))

        # 获取插入的ID
        project_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()
    print(f"已生成 {len(project_ids)} 条项目数据")
    return project_ids

# 生成标准数据
def generate_standard_data(person_ids, count=12):
    if not person_ids:
        print("无法生成标准数据：没有人员数据")
        return []

    conn = get_connection()
    cursor = conn.cursor()

    # 清空现有数据
    cursor.execute("DELETE FROM standard")

    standard_names = [
        "白酒感官评价方法",
        "白酒酿造微生物检测技术规范",
        "白酒中微量成分检测方法",
        "酒曲制作工艺规范",
        "白酒贮存条件要求",
        "酿酒原料质量控制规范",
        "白酒中乙酸乙酯测定方法",
        "白酒生产环境要求",
        "酿酒用水质量标准",
        "白酒中赤霉素成分检测方法",
        "白酒微生物安全控制规范",
        "白酒风味物质分析方法",
        "酱香型白酒工艺规范",
        "浓香型白酒工艺规范",
        "清香型白酒工艺规范"
    ]

    if count > len(standard_names):
        # 构造更多标准名称
        for i in range(len(standard_names), count):
            standard_names.append(f"白酒技术规范{i+1}")

    standard_names = standard_names[:count]  # 截取需要的数量

    standard_types = ["国家标准", "行业标准", "地方标准", "团体标准", "企业标准"]

    companies = [
        "五粮液集团有限公司",
        "贵州茅台酒厂(集团)有限责任公司",
        "四川省食品发酵工业研究设计院",
        "江苏洋河酒厂股份有限公司",
        "中国食品发酵工业研究院",
        "四川省酿酒工业协会",
        "中国白酒工业协会",
        "泸州老窖股份有限公司",
        "山西杏花村汾酒集团有限责任公司"
    ]

    standard_ids = []  # 存储生成的标准ID

    for standard_name in standard_names:
        # 生成标准号
        standard_type = random.choice(standard_types)
        if standard_type == "国家标准":
            prefix = "GB/T"
        elif standard_type == "行业标准":
            prefix = random.choice(["QB/T", "SB/T", "LS/T"])
        elif standard_type == "地方标准":
            prefix = random.choice(["DB51/T", "DB52/T", "DB44/T"])
        elif standard_type == "团体标准":
            prefix = random.choice(["T/CADA", "T/CBWA", "T/CFII"])
        else:  # 企业标准
            prefix = "Q/" + ''.join(random.choices(string.ascii_uppercase, k=4))

        number_part = f"{random.randint(10000, 99999)}-{random.randint(2018, 2023)}"
        standard_code = f"{prefix} {number_part}"

        # 随机日期
        release_year = random.randint(2018, 2023)
        release_month = random.randint(1, 12)
        release_day = random.randint(1, 28)
        release_date = f"{release_year}-{release_month:02d}-{release_day:02d}"

        # 实施日期在发布日期之后
        release_date_obj = datetime.strptime(release_date, "%Y-%m-%d")
        impl_date_obj = release_date_obj + timedelta(days=random.randint(30, 180))
        impl_date = impl_date_obj.strftime("%Y-%m-%d")

        # 随机选择参与单位
        company = random.choice(companies)

        # 随机选择参与人员（通常只有一个）
        participant_id = random.choice(person_ids)

        cursor.execute('''
            INSERT INTO standard (name, type, code, release_date, implementation_date,
                               company, participant_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (standard_name, standard_type, standard_code, release_date, impl_date,
              company, participant_id))

        # 获取插入的ID
        standard_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()
    print(f"已生成 {len(standard_ids)} 条标准数据")
    return standard_ids

# 生成专利数据
def generate_patent_data(person_ids, count=30):
    if not person_ids:
        print("无法生成专利数据：没有人员数据")
        return []

    conn = get_connection()
    cursor = conn.cursor()

    # 清空现有数据
    cursor.execute("DELETE FROM patent")

    # 专利名称列表
    patent_names = [
        "一种基于微生物发酵的白酒酿造方法",
        "一种酒曲培养装置及培养方法",
        "一种白酒陈酿加速装置",
        "一种白酒品质快速检测传感器",
        "一种酿酒温度智能控制系统",
        "一种酿酒微生物菌种保存方法",
        "一种白酒中赤霉素的检测方法",
        "一种改善白酒香气的微生物菌剂",
        "一种白酒酿造发酵罐结构",
        "一种白酒中酯类物质提取装置",
        "一种白酒酸度调节方法",
        "一种酿酒微生物菌种活化装置",
        "一种白酒糟醅固液分离设备",
        "一种白酒香味物质浓缩方法",
        "一种白酒感官评价辅助系统",
        "一种白酒窖藏环境控制装置",
        "一种白酒中有机酸快速检测装置",
        "一种混合微生物发酵剂及其制备方法",
        "一种白酒品评用标准杯",
        "一种强化酒曲发酵的方法",
    ]

    # if count > len(patent_names):
    #     # 构造更多专利名称
    #     for i in range(len(patent_names), count):
    #         patent_names.append(f"一种白酒酿造改良技术{i+1}")

    patent_names = patent_names[:count]  # 截取需要的数量

    # 专利类型
    patent_types = ["发明专利", "实用新型专利", "外观设计专利"]

    # 专利类型权重 - 发明专利相对较多
    patent_type_weights = [0.6, 0.3, 0.1]

    # 申请单位
    companies = [
        "五粮液集团有限公司",
        "贵州茅台酒厂(集团)有限责任公司",
        "四川省食品发酵工业研究设计院",
        "江苏洋河酒厂股份有限公司",
        "中国食品发酵工业研究院",
        "泸州老窖股份有限公司",
        "山西杏花村汾酒集团有限责任公司",
        "郎酒集团有限公司",
        "剑南春集团有限责任公司",
    ]

    # 证书状态选项
    certificate_statuses = ["有", "无"]

    patent_ids = []  # 存储生成的专利ID

    for patent_name in patent_names:
        # 随机专利类型 (基于权重)
        patent_type = random.choices(patent_types, weights=patent_type_weights, k=1)[0]

        # 随机申请日期（2015-2023年间）
        app_year = random.randint(2015, 2023)
        app_month = random.randint(1, 12)
        app_day = random.randint(1, 28)
        application_date = f"{app_year}-{app_month:02d}-{app_day:02d}"

        # 授权日期在申请日期之后1-3年
        app_date_obj = datetime.strptime(application_date, "%Y-%m-%d")
        # 外观设计专利审查周期较短
        if patent_type == "外观设计专利":
            delay_days = random.randint(180, 365)
        elif patent_type == "实用新型专利":
            delay_days = random.randint(270, 730)
        else:  # 发明专利
            delay_days = random.randint(365, 1095)

        grant_date_obj = app_date_obj + timedelta(days=delay_days)
        grant_date = grant_date_obj.strftime("%Y-%m-%d")

        # 随机选择申请单位
        company = random.choice(companies)

        # 随机选择专利所有人（通常是一个人）
        owner_id = random.choice(person_ids)

        # 随机选择参与人员（根据专利类型调整人数）
        available_participants = [p_id for p_id in person_ids if p_id != owner_id]

        if patent_type == "发明专利":
            participant_count = min(random.randint(2, 5), len(available_participants))
        elif patent_type == "实用新型专利":
            participant_count = min(random.randint(1, 3), len(available_participants))
        else:  # 外观设计专利
            participant_count = min(random.randint(1, 2), len(available_participants))

        participants = random.sample(available_participants, participant_count)
        participants_str = ",".join(map(str, participants))

        # 生成专利号
        if patent_type == "发明专利":
            prefix = "CN"
        elif patent_type == "实用新型专利":
            prefix = "ZL"
        else:  # 外观设计专利
            prefix = "ZD"

        year_part = str(app_year)[2:]  # 年份后两位
        number_part = random.randint(100000, 999999)
        suffix = random.choice(['A', 'B', 'C'])

        patent_number = f"{prefix}{year_part}{number_part}{suffix}"

        # 随机证书状态，授权日期越早，拥有证书的几率越高
        years_since_grant = (datetime.now() - grant_date_obj).days / 365
        if years_since_grant > 2:
            certificate_probabilities = [0.8, 0.2]  # 80%有证书
        elif years_since_grant > 1:
            certificate_probabilities = [0.6, 0.4]  # 60%有证书
        else:
            certificate_probabilities = [0.3, 0.7]  # 30%有证书

        certificate = random.choices(certificate_statuses, weights=certificate_probabilities, k=1)[0]

        cursor.execute('''
            INSERT INTO patent (name, type, application_date, grant_date,
                             owner_id, participants, company, patent_number, certificate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patent_name, patent_type, application_date, grant_date,
             owner_id, participants_str, company, patent_number, certificate))

        # 获取插入的ID
        patent_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()
    print(f"已生成 {len(patent_ids)} 条专利数据")
    return patent_ids

# 生成论文数据
def generate_paper_data(person_ids, count=25):
    if not person_ids:
        print("无法生成论文数据：没有人员数据")
        return []

    conn = get_connection()
    cursor = conn.cursor()

    # 清空现有数据
    cursor.execute("DELETE FROM paper")

    # 论文标题列表
    paper_titles = [
        "白酒酿造过程中呈香物质代谢机制研究",
        "基于气相色谱-质谱联用技术的白酒香气成分分析",
        "微生物区系多样性对白酒品质的影响",
        "酒曲中功能微生物的筛选及其发酵特性研究",
        "不同原料白酒发酵工艺比较与优化",
        "白酒陈酿过程中风味物质变化规律",
        "酿酒酵母耐高温特性的研究",
        "酒曲制作工艺对微生物菌群结构的影响",
        "白酒中酯类化合物的形成机理",
        "白酒中有机酸组成与感官品质相关性研究",
        "乳酸菌在白酒酿造中的应用研究",
        "不同发酵温度对白酒品质的影响研究",
        "固态发酵过程中微生物动态变化研究",
        "白酒中呈味物质的鉴定与分析",
        "白酒陈酿工艺优化及其对品质的影响",
        "基于代谢组学的白酒风味特征解析",
        "白酒酿造过程中微生物互作关系研究",
        "白酒勾调工艺优化及其对感官品质的影响",
        "白酒窖池微生物生态系统研究",
        "传统酿造工艺与现代技术相结合的应用研究"
    ]

    # if count > len(paper_titles):
    #     # 构造更多论文标题
    #     for i in range(len(paper_titles), count):
    #         paper_titles.append(f"白酒酿造工艺优化研究({i+1})")

    paper_titles = paper_titles[:count]  # 截取需要的数量

    # 期刊名称列表
    journals = [
        "食品科学",
        "食品与发酵工业",
        "中国酒业",
        "酿酒科技",
        "食品与机械",
        "中国农业科学",
        "食品安全质量检测学报",
        "中国酿造",
        "食品工业科技",
        "Journal of Food Science",
        "Food Chemistry",
        "Journal of Agricultural and Food Chemistry",
        "Biotechnology and Bioengineering",
        "Journal of Microbiology and Biotechnology",
        "Applied Microbiology and Biotechnology",
        "FEMS Microbiology Letters"
    ]

    # 期刊类型
    journal_types = ["核心期刊", "非核心期刊", "EI收录", "SCI收录"]

    # 期刊类型权重 - 调整不同类型期刊的比例
    journal_type_weights = [0.4, 0.3, 0.2, 0.1]

    # 作者单位
    organizations = [
        "四川大学",
        "江南大学",
        "中国农业大学",
        "华中农业大学",
        "天津科技大学",
        "北京工商大学",
        "西北农林科技大学",
        "五粮液集团有限公司",
        "贵州茅台酒厂(集团)有限责任公司",
        "四川省食品发酵工业研究设计院",
        "江苏洋河酒厂股份有限公司",
        "中国食品发酵工业研究院",
        "泸州老窖股份有限公司技术中心"
    ]

    paper_ids = []  # 存储生成的论文ID

    for paper_title in paper_titles:
        # 随机选择期刊
        journal = random.choice(journals)

        # 随机期刊类型(基于权重)
        journal_type = random.choices(journal_types, weights=journal_type_weights, k=1)[0]

        # 随机发表日期（2015-2023年间）
        pub_year = random.randint(2015, 2023)
        pub_month = random.randint(1, 12)
        pub_day = random.randint(1, 28)
        publish_date = f"{pub_year}-{pub_month:02d}-{pub_day:02d}"

        # 随机选择作者单位
        organization = random.choice(organizations)

        # 随机选择第一作者（通常是一个人）
        first_author_id = random.choice(person_ids)

        # 随机选择参与作者（2-4人）
        available_co_authors = [p_id for p_id in person_ids if p_id != first_author_id]

        co_author_count = min(random.randint(2, 4), len(available_co_authors))
        co_authors = random.sample(available_co_authors, co_author_count)
        co_authors_str = ",".join(map(str, co_authors))

        # 生成随机期次信息
        volume = random.randint(1, 40)
        issue = random.randint(1, 12)
        volume_info = f"第{volume}卷第{issue}期"

        cursor.execute('''
            INSERT INTO paper (title, journal, journal_type, publish_date,
                            first_author_id, co_authors, organization, volume_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (paper_title, journal, journal_type, publish_date,
              first_author_id, co_authors_str, organization, volume_info))

        # 获取插入的ID
        paper_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()
    print(f"已生成 {len(paper_ids)} 条论文数据")
    return paper_ids

# 生成全部模拟数据
def generate_all_data():
    print("开始生成模拟数据...")

    # 创建表结构
    create_tables()

    # 生成人员数据
    person_ids = generate_person_data(20)

    # 生成项目数据
    project_ids = generate_project_data(person_ids, 15)

    # 生成标准数据
    standard_ids = generate_standard_data(person_ids, 15)

    # 生成专利数据
    patent_ids = generate_patent_data(person_ids, 30)

    # 生成论文数据
    paper_ids = generate_paper_data(person_ids, 25)

    print("所有模拟数据生成完成！")
    print(f"生成了 {len(person_ids)} 条人员数据")
    print(f"生成了 {len(project_ids)} 条项目数据")
    print(f"生成了 {len(standard_ids)} 条标准数据")
    print(f"生成了 {len(patent_ids)} 条专利数据")
    print(f"生成了 {len(paper_ids)} 条论文数据")

# 主函数
if __name__ == "__main__":
    generate_all_data()