# models/database.py
import sqlite3
import os
import json
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'carbon_asset.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


@contextmanager
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """初始化数据库表"""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. 排放源表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emission_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_type TEXT, range_type TEXT, scenario_type TEXT,
                source_type TEXT, activity_category TEXT, subcategory TEXT,
                source_name TEXT, unit TEXT, equipment TEXT, data_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 排放因子表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emission_factors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factor_type TEXT, category TEXT, subcategory TEXT, unit TEXT,
                factor_value REAL, calorific_value REAL, carbon_content TEXT,
                oxidation_rate TEXT, region TEXT, coverage TEXT, product_type TEXT,
                data_source TEXT, effective_date TEXT, status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 3. 运营组织表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_code TEXT UNIQUE, org_name TEXT, org_type TEXT,
                parent_id INTEGER, contact_person TEXT, contact_phone TEXT,
                contact_email TEXT, address TEXT, status TEXT DEFAULT '启用',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 4. 运输链表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transport_chains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_code TEXT UNIQUE, chain_name TEXT, chain_type TEXT,
                start_location TEXT, end_location TEXT, distance REAL,
                transport_mode TEXT, org_id INTEGER, status TEXT DEFAULT '启用',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 5. 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                real_name TEXT,
                email TEXT,
                phone TEXT,
                role TEXT DEFAULT 'user',
                status TEXT DEFAULT '启用',
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 6. 系统配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE, config_value TEXT, description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 7. 排放源配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS source_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id INTEGER, org_name TEXT, source_id INTEGER,
                source_name TEXT, is_selected INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 8. 能耗数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id INTEGER, org_name TEXT, period_type TEXT,
                period_year INTEGER, period_month INTEGER, period_quarter TEXT,
                period_start TEXT, period_end TEXT, data_json TEXT,
                total_emission REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 9. 核算方法表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculation_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method_name TEXT, emission_type TEXT, data_type TEXT,
                unit TEXT, param_config TEXT, formula TEXT,
                is_referenced INTEGER DEFAULT 0, is_enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 10. 产品分类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE, icon TEXT, sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 11. 产品表（扩展字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                product_name TEXT,
                product_code TEXT,
                product_model TEXT,
                specification TEXT,
                functional_unit TEXT,
                declared_unit TEXT,
                design_life TEXT,
                reference_standard TEXT,
                unit TEXT,
                description TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES product_categories(id)
            )
        ''')

        # 12. 产品配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER, stage TEXT, config_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id),
                UNIQUE(product_id, stage)
            )
        ''')

        # 13. 产品碳足迹历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_footprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER, product_name TEXT, category_name TEXT,
                quantity INTEGER DEFAULT 1, total_emission REAL,
                stages_json TEXT, details_json TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        # 14. 碳减排目标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reduction_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_name TEXT,
                target_scope TEXT,
                base_year INTEGER,
                target_year INTEGER,
                reduction_percentage REAL,
                current_emission REAL,
                target_emission REAL,
                status TEXT DEFAULT '进行中',
                progress REAL DEFAULT 0,
                sbt_level TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 15. 碳排放预测表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emission_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_year INTEGER,
                forecast_emission REAL,
                target_emission REAL,
                scenario TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 16. 碳减排措施表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reduction_measures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measure_name TEXT,
                measure_type TEXT,
                category TEXT,
                estimated_reduction REAL,
                estimated_cost REAL,
                estimated_benefit REAL,
                feasibility TEXT,
                status TEXT DEFAULT '规划中',
                implementation_date TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 17. CCER项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ccer_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                project_type TEXT,
                status TEXT,
                reduction_amount REAL,
                start_date TEXT,
                end_date TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ============================================================
        # 18. 碳金融 - 项目发起表
        # ============================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                initiator TEXT,
                method_name TEXT,
                method_file TEXT,
                other_files TEXT,
                status TEXT DEFAULT '草稿',
                review_status TEXT DEFAULT '未提交',
                review_comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ============================================================
        # 19. 碳金融 - 开发材料审核表
        # ============================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                project_name TEXT,
                initiator TEXT,
                method_name TEXT,
                audit_report TEXT,
                audit_status TEXT DEFAULT '待审核',
                audit_comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES carbon_projects(id)
            )
        ''')

        conn.commit()

        # 检查是否需要初始化示例数据
        cursor.execute("SELECT COUNT(*) FROM emission_sources")
        emission_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM product_categories")
        product_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM carbon_projects")
        carbon_count = cursor.fetchone()[0]

        if emission_count == 0 or product_count == 0 or carbon_count == 0:
            init_sample_data(conn)
            print("✅ 数据库初始化完成（包含所有示例数据）")
        else:
            print("✅ 数据库已存在，跳过初始化")

        # ============================================================
        # 初始化北京局(org_id=5)的示例数据
        # ============================================================
        _init_beijing_bureau_sample_data(conn)


def init_sample_data(conn):
    """初始化示例数据"""
    cursor = conn.cursor()

    # ============================================================
    # 1. 排放源示例数据
    # ============================================================
    sample_sources = [
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "固体燃料", "", "", "无烟煤", "吨", "锅炉、炉窑等", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "固体燃料", "", "", "烟煤", "吨", "锅炉、炉窑等", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "固体燃料", "", "", "煤制品", "吨", "锅炉、炉窑等", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "固体燃料", "", "", "焦炭", "吨", "锅炉、炉窑等", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "固体燃料", "", "", "褐煤", "吨", "锅炉、茶炉等", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "固体燃料", "", "", "洗精煤", "吨", "锅炉、茶炉等", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "液体燃料", "", "", "燃料油", "吨", "燃油锅炉、炉窑等",
         "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "液体燃料", "", "", "柴油", "吨", "机车、空调发电车等",
         "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "液体燃料", "", "", "汽油", "吨", "装卸设备、汽车等",
         "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "液体燃料", "", "", "煤油", "吨", "其他设备", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "气体燃料", "", "", "焦炉煤气", "立方米", "锅炉、炉窑等",
         "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "气体燃料", "", "", "油田天然气", "立方米", "锅炉、炉窑等",
         "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "气体燃料", "", "", "气田天然气", "立方米", "", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "气体燃料", "", "", "液化石油气", "吨", "茶炉等", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "牵引排放", "气体燃料", "", "", "液化天然气", "吨", "锅炉、炉窑等",
         "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "非牵引排放", "固定源燃烧", "建筑物", "", "办公室供暖", "GJ", "", "账单"),
        ("货运物流类别", "直接排放（范围1）", "非牵引排放", "固定源燃烧", "建筑物", "", "发电机", "kWh", "", "自动采集"),
        ("货运物流类别", "直接排放（范围1）", "非牵引排放", "固定源燃烧", "建筑物", "", "其他固定燃烧", "GJ", "", "估算"),
        ("货运物流类别", "直接排放（范围1）", "非牵引排放", "移动源燃烧", "道路车辆", "", "道路车辆及机械", "升", "",
         "日志记录"),
        ("货运物流类别", "直接排放（范围1）", "非牵引排放", "装卸设备", "装卸设备", "", "专业装卸设备", "kWh", "",
         "自动采集"),
        ("货运物流类别", "间接排放（范围2）", "牵引排放", "购电", "铁路车辆", "", "电动列车用电", "kWh", "", "EC4T计费"),
        ("货运物流类别", "间接排放（范围2）", "非牵引排放", "外购电力", "道路车辆", "", "道路车辆用电", "kWh", "",
         "账单"),
        ("货运物流类别", "间接排放（范围2）", "非牵引排放", "外购电力", "装卸设备", "", "装卸设备用电", "kWh", "",
         "自动采集"),
        ("货运物流类别", "间接排放（范围2）", "非牵引排放", "外购电力", "建筑物", "", "办公室及仓库用电", "kWh", "",
         "账单"),
        ("货运物流类别", "间接排放（范围2）", "非牵引排放", "外购热力", "建筑物", "", "外购热力", "GJ", "", "账单"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "铁路车辆", "铁路车辆", "", "车辆维护承包商", "次",
         "", "收据"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "铁路车辆", "铁路车辆", "", "车辆部件", "件", "",
         "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "铁路车辆", "铁路车辆", "", "油品润滑剂", "升", "",
         "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "装卸设备", "装卸设备", "", "设备部件", "件", "",
         "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "装卸设备", "装卸设备", "", "装卸设备油品", "升",
         "", "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "建筑物", "建筑物", "", "清洁服务", "次", "",
         "收据"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "建筑物", "建筑物", "", "办公用品", "件", "",
         "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "IT和电信", "IT和电信", "", "数据中心服务", "月",
         "", "账单"),
        ("货运物流类别", "其他间接排放（范围3）", "采购的货物和服务", "IT和电信", "IT和电信", "", "电信服务", "月", "",
         "账单"),
        ("货运物流类别", "其他间接排放（范围3）", "资本货物", "铁路车辆", "铁路车辆", "", "新机车车辆", "辆", "",
         "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "资本货物", "装卸设备", "装卸设备", "", "新装卸设备", "台", "",
         "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "资本货物", "道路车辆", "道路车辆", "", "新道路车辆", "辆", "",
         "采购记录"),
        ("货运物流类别", "其他间接排放（范围3）", "资本货物", "建筑物", "建筑物", "", "新建筑物", "平方米", "", "估算"),
        ("货运物流类别", "其他间接排放（范围3）", "燃料和能源相关活动", "第三方", "", "", "燃油燃油税", "吨", "", "估算"),
        ("货运物流类别", "其他间接排放（范围3）", "燃料和能源相关活动", "第三方", "", "", "电力WTT", "kWh", "", "估算"),
        ("货运物流类别", "其他间接排放（范围3）", "燃料和能源相关活动", "第三方", "", "", "输配电损耗", "kWh", "",
         "估算"),
        ("货运物流类别", "其他间接排放（范围3）", "商务差旅", "商务差旅", "", "", "商务旅行(陆路)", "公里", "", "记录"),
        ("货运物流类别", "其他间接排放（范围3）", "商务差旅", "商务差旅", "", "", "商务旅行(航空)", "公里", "", "记录"),
        ("货运物流类别", "其他间接排放（范围3）", "商务差旅", "商务差旅", "", "", "酒店住宿", "晚", "", "收据"),
        ("货运物流类别", "其他间接排放（范围3）", "员工通勤", "员工通勤", "", "", "员工通勤", "公里", "", "估算"),
        ("货运物流类别", "其他间接排放（范围3）", "员工通勤", "员工通勤", "", "", "在家办公", "天", "", "估算"),
    ]
    for s in sample_sources:
        cursor.execute('''
            INSERT INTO emission_sources 
            (category_type, range_type, scenario_type, source_type, activity_category, 
             subcategory, source_name, unit, equipment, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', s)

    # ============================================================
    # 2. 排放因子示例数据
    # ============================================================
    sample_factors = [
        ("化石燃料排放因子", "固体燃料", "无烟煤", "t", 2.32, 24.52, "27.49×10^-3", "94%", None, None, None,
         "中国温室气体清单研究", "2024-01-01", "启用"),
        ("化石燃料排放因子", "固体燃料", "烟煤", "t", 2.07, 23.20, "26.18×10^-3", "93%", None, None, None,
         "中国温室气体清单研究", "2024-01-01", "启用"),
        ("化石燃料排放因子", "固体燃料", "褐煤", "t", 1.42, 14.45, "28.00×10^-3", "96%", None, None, None,
         "中国温室气体清单研究", "2024-01-01", "启用"),
        ("化石燃料排放因子", "液体燃料", "柴油", "t", 3.15, 43.33, "20.20×10^-3", "98%", None, None, None,
         "中国温室气体清单研究", "2024-01-01", "启用"),
        ("化石燃料排放因子", "液体燃料", "汽油", "t", 3.04, 44.80, "18.90×10^-3", "98%", None, None, None,
         "中国温室气体清单研究", "2024-01-01", "启用"),
        ("电网区域排放因子", "全国电力", "全国平均", "tCO2/MWh", 0.5366, None, None, None, "全国", None, None,
         "生态环境部公告", "2022-01-01", "启用"),
        ("电网区域排放因子", "区域电力", "华北区域", "kgCO2/kWh", 0.7120, None, None, None, "华北", "北京、天津等", None,
         "2022年区域电力排放因子", "2022-01-01", "启用"),
        ("电网区域排放因子", "区域电力", "华东区域", "kgCO2/kWh", 0.5992, None, None, None, "华东", "上海、江苏等", None,
         "2022年区域电力排放因子", "2022-01-01", "启用"),
        ("产品碳排放因子", "运输服务", "铁路货运", "kgCO2/吨公里", 0.028, None, None, None, None, None, "铁路运输",
         "全生命周期系数库", "2024-01-01", "启用"),
        ("其他排放因子", "热力供应", "外购热力", "tCO2/GJ", 0.11, None, None, None, None, None, None, "推荐值",
         "2024-01-01", "启用"),
    ]
    for f in sample_factors:
        cursor.execute('''
            INSERT INTO emission_factors 
            (factor_type, category, subcategory, unit, factor_value, calorific_value, 
             carbon_content, oxidation_rate, region, coverage, product_type, 
             data_source, effective_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', f)

    # ============================================================
    # 3. 用户
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        import hashlib
        hashed_pw = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password, real_name, email, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', hashed_pw, '管理员', 'admin@railway.com', 'admin', '启用'))

    # ============================================================
    # 4. 系统配置
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM system_configs WHERE config_key = 'system_name'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO system_configs (config_key, config_value, description) VALUES (?, ?, ?)',
                       ('system_name', '铁路碳资产管理系统', '系统名称'))

    # ============================================================
    # 5. 核算方法
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM calculation_methods")
    if cursor.fetchone()[0] == 0:
        methods = [
            ('高速铁路客运碳排放量', '能源消耗', '系统默认', 'kgCO2', '运输距离、能耗强度',
             '碳排放量=运输距离×能耗强度×碳排放因子', 0, 1),
            ('普速铁路货运碳排放量', '能源消耗', '系统默认', 'kgCO2', '运输距离、货物重量',
             '碳排放量=运输距离×货物重量×碳排放因子', 0, 1),
        ]
        for m in methods:
            cursor.execute('''
                INSERT INTO calculation_methods 
                (method_name, emission_type, data_type, unit, param_config, formula, is_referenced, is_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', m)

    # ============================================================
    # 6. 产品分类和产品数据
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM product_categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('工务', '🛤️', 1), ('供电', '⚡', 2), ('通信', '📡', 3),
            ('信号', '🚦', 4), ('运输', '🚂', 5), ('机车', '🚆', 6),
            ('客车', '🚃', 7), ('动车组', '🚄', 8), ('货车', '🚊', 9),
            ('通用产品', '🔧', 10),
        ]
        for c in categories:
            cursor.execute('INSERT INTO product_categories (category_name, icon, sort_order) VALUES (?, ?, ?)', c)

        # 产品数据
        products = [
            # 工务
            (1, '道岔', '组', '铁路道岔设备', 'PRD-001', 'SC330', '60kg/m', '1组道岔', '1组道岔', '30年',
             'TB/T 412-2014', 1),
            (1, '扣件', '套', '钢轨扣件系统', 'PRD-002', 'WJ-8', '通用60kg/m钢轨', '1套扣件', '1套扣件', '50年',
             'TB/T 3225-2010', 2),
            (1, '声屏障', '米', '铁路声屏障', 'PRD-003', 'SPZ-01', '2.5m高', '1米声屏障', '1米声屏障', '25年',
             'TB/T 3122-2019', 3),
            # 供电
            (2, '接触线', '米', '接触网导线', 'PRD-004', 'CT-120', '120mm²', '1米接触线', '1米接触线', '20年',
             'TB/T 2075-2010', 1),
            (2, '变配电设备', '台', '牵引变电设备', 'PRD-005', 'TZD-01', '10kV', '1台设备', '1台设备', '30年',
             'GB/T 14549-2016', 2),
            # 通信
            (3, '通信电源', '套', '铁路通信电源系统', 'PRD-006', 'TXD-48', '48V/200A', '1套电源', '1套电源', '15年',
             'TB/T 3021-2015', 1),
            (3, '调度系统', '套', '列车调度通信系统', 'PRD-007', 'DDS-01', '数字调度', '1套系统', '1套系统', '20年',
             'TB/T 3035-2016', 2),
            # 信号
            (4, '信号电缆', '米', '铁路信号电缆', 'PRD-008', 'XHD-01', '24芯', '1米电缆', '1米电缆', '25年',
             'TB/T 2476-2017', 1),
            (4, '变压器', '台', '信号变压器', 'PRD-009', 'BQ-01', '220V/24V', '1台变压器', '1台变压器', '20年',
             'TB/T 3219-2018', 2),
            # 运输
            (5, '安全防护装置', '套', '列车安全防护设备', 'PRD-010', 'FHZ-01', '通用型', '1套防护装置', '1套防护装置',
             '15年', 'TB/T 3315-2013', 1),
            # 机车
            (6, '受电弓', '套', '电力机车受电弓', 'PRD-011', 'SGD-01', 'DSA200型', '1套受电弓', '1套受电弓', '20年',
             'TB/T 1457-2015', 1),
            (6, '转向架', '台', '机车转向架', 'PRD-012', 'ZXJ-01', 'B型转向架', '1台转向架', '1台转向架', '30年',
             'TB/T 3316-2014', 2),
            (6, '制动系统', '套', '空气制动系统', 'PRD-013', 'ZD-01', 'JZ-7型', '1套制动系统', '1套制动系统', '25年',
             'TB/T 2958-2012', 3),
            # 客车
            (7, '转向架', '台', '客车转向架', 'PRD-014', 'ZXJ-02', 'K型转向架', '1台转向架', '1台转向架', '30年',
             'TB/T 3316-2014', 1),
            (7, '制动系统', '套', '客车制动系统', 'PRD-015', 'ZD-02', '104型', '1套制动系统', '1套制动系统', '25年',
             'TB/T 2958-2012', 2),
            (7, '钩缓系统', '套', '客车车钩缓冲', 'PRD-016', 'GH-01', '通用型', '1套钩缓系统', '1套钩缓系统', '20年',
             'TB/T 2949-2015', 3),
            # 动车组
            (8, '受电弓', '套', '动车组受电弓', 'PRD-017', 'SGD-02', 'DSA250型', '1套受电弓', '1套受电弓', '20年',
             'TB/T 1457-2015', 1),
            (8, '转向架', '台', '动车组转向架', 'PRD-018', 'ZXJ-03', 'H型转向架', '1台转向架', '1台转向架', '30年',
             'TB/T 3316-2014', 2),
            # 货车
            (9, 'X70型集装箱专用平车', '辆', 'X70型集装箱专用平车', 'PRD-019', 'X70', '集装箱专用平车', '1辆平车',
             '1辆平车', '25年', 'ISO14067:2018', 1),
            (9, '转向架', '台', '货车转向架', 'PRD-020', 'ZXJ-04', 'C型转向架', '1台转向架', '1台转向架', '25年',
             'TB/T 3316-2014', 2),
            (9, '制动系统', '套', '货车制动系统', 'PRD-021', 'ZD-03', '120型', '1套制动系统', '1套制动系统', '20年',
             'TB/T 2958-2012', 3),
            (9, '钩缓系统', '套', '货车车钩缓冲', 'PRD-022', 'GH-02', '通用型', '1套钩缓系统', '1套钩缓系统', '20年',
             'TB/T 2949-2015', 4),
            # 通用产品
            (10, '电器设备', '台', '铁路通用电器设备', 'PRD-023', 'DQ-01', '通用型', '1台设备', '1台设备', '15年',
             'GB/T 14048-2016', 1),
            (10, '电子设备', '台', '铁路通用电子设备', 'PRD-024', 'DZ-01', '通用型', '1台设备', '1台设备', '12年',
             'GB/T 2423-2015', 2),
            (10, '机械设备', '台', '铁路通用机械设备', 'PRD-025', 'JX-01', '通用型', '1台设备', '1台设备', '18年',
             'GB/T 16754-2014', 3),
        ]
        for p in products:
            cursor.execute('''
                INSERT INTO products 
                (category_id, product_name, unit, description, product_code, 
                 product_model, specification, functional_unit, declared_unit,
                 design_life, reference_standard, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', p)

    # ============================================================
    # 7. 产品配置示例数据
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM product_configs")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id, product_name FROM products")
        all_products = cursor.fetchall()

        # X70型集装箱专用平车配置
        x70_configs = {
            "原材料获取": [
                {"field_id": "steel_weathering", "name": "耐候钢", "type": "number", "unit": "kg", "default": "11732",
                 "factor": "steel", "source": "案例数据", "year": 2024, "region": "全国", "step": 100,
                 "category": "金属材料"},
                {"field_id": "cast_steel", "name": "铸钢", "type": "number", "unit": "kg", "default": "8792",
                 "factor": "cast_iron", "source": "案例数据", "year": 2024, "region": "全国", "step": 100,
                 "category": "金属材料"},
                {"field_id": "alloy_steel", "name": "合金钢", "type": "number", "unit": "kg", "default": "1136",
                 "factor": "steel", "source": "案例数据", "year": 2024, "region": "全国", "step": 50,
                 "category": "金属材料"},
                {"field_id": "carbon_steel", "name": "碳素钢", "type": "number", "unit": "kg", "default": "802",
                 "factor": "steel", "source": "案例数据", "year": 2024, "region": "全国", "step": 50,
                 "category": "金属材料"},
                {"field_id": "rubber", "name": "橡胶", "type": "number", "unit": "kg", "default": "14",
                 "factor": "rubber", "source": "案例数据", "year": 2024, "region": "全国", "step": 1,
                 "category": "非金属材料"},
                {"field_id": "nylon", "name": "尼龙", "type": "number", "unit": "kg", "default": "34",
                 "factor": "plastic", "source": "案例数据", "year": 2024, "region": "全国", "step": 1,
                 "category": "非金属材料"},
                {"field_id": "epoxy_resin", "name": "环氧树脂", "type": "number", "unit": "kg", "default": "141",
                 "factor": "plastic", "source": "案例数据", "year": 2024, "region": "全国", "step": 10,
                 "category": "非金属材料"},
            ],
            "生产制造": [
                {"field_id": "weld_wire", "name": "焊丝", "type": "number", "unit": "kg", "default": "190.68",
                 "factor": "steel", "source": "案例数据", "year": 2024, "region": "全国", "step": 10,
                 "category": "辅料消耗"},
                {"field_id": "water_based_paint", "name": "水性漆", "type": "number", "unit": "kg", "default": "80.00",
                 "factor": "plastic", "source": "案例数据", "year": 2024, "region": "全国", "step": 5,
                 "category": "辅料消耗"},
                {"field_id": "oxygen", "name": "氧气", "type": "number", "unit": "kg", "default": "151.61",
                 "source": "案例数据", "year": 2024, "region": "全国", "step": 10, "category": "辅料消耗"},
                {"field_id": "auxiliary_materials", "name": "辅料消耗", "type": "number", "unit": "kg",
                 "default": "18.40", "source": "案例数据", "year": 2024, "region": "全国", "step": 1,
                 "category": "辅料消耗"},
                {"field_id": "electricity_manufacturing", "name": "电力", "type": "number", "unit": "kWh",
                 "default": "28.00", "factor": "electricity_national", "source": "案例数据", "year": 2024,
                 "region": "全国", "step": 5, "category": "电力消耗"},
                {"field_id": "natural_gas_manufacturing", "name": "天然气", "type": "number", "unit": "m³",
                 "default": "321.40", "factor": "natural_gas", "source": "案例数据", "year": 2024, "region": "全国",
                 "step": 10, "category": "燃料消耗"},
                {"field_id": "diesel_manufacturing", "name": "柴油", "type": "number", "unit": "kg", "default": "3.00",
                 "factor": "diesel", "source": "案例数据", "year": 2024, "region": "全国", "step": 1,
                 "category": "燃料消耗"},
                {"field_id": "co2_emission", "name": "二氧化碳", "type": "number", "unit": "kg", "default": "14.70",
                 "source": "案例数据", "year": 2024, "region": "全国", "step": 1, "category": "大气排放"},
                {"field_id": "ch4_emission", "name": "甲烷", "type": "number", "unit": "kg", "default": "8.84",
                 "source": "案例数据", "year": 2024, "region": "全国", "step": 1, "category": "大气排放"},
                {"field_id": "n2o_emission", "name": "氧化亚氮", "type": "number", "unit": "kg", "default": "0.02",
                 "source": "案例数据", "year": 2024, "region": "全国", "step": 0.01, "category": "大气排放"},
            ],
            "使用阶段": [
                {"field_id": "steel_use", "name": "耐候钢(维护)", "type": "number", "unit": "kg", "default": "204.00",
                 "factor": "steel", "source": "案例数据", "year": 2024, "region": "全国", "step": 10,
                 "category": "主材消耗"},
                {"field_id": "paint_use", "name": "水性漆(维护)", "type": "number", "unit": "kg", "default": "156.86",
                 "factor": "plastic", "source": "案例数据", "year": 2024, "region": "全国", "step": 10,
                 "category": "辅料消耗"},
                {"field_id": "steel_shot", "name": "钢丸", "type": "number", "unit": "kg", "default": "40.00",
                 "factor": "steel", "source": "案例数据", "year": 2024, "region": "全国", "step": 5,
                 "category": "辅料消耗"},
                {"field_id": "clean_water", "name": "洁净水", "type": "number", "unit": "kg", "default": "630.40",
                 "factor": "water", "source": "案例数据", "year": 2024, "region": "全国", "step": 50,
                 "category": "资源消耗"},
                {"field_id": "electricity_use", "name": "电力(使用)", "type": "number", "unit": "kWh",
                 "default": "1174.32", "factor": "electricity_national", "source": "案例数据", "year": 2024,
                 "region": "全国", "step": 50, "category": "电力消耗"},
                {"field_id": "natural_gas_use", "name": "天然气(使用)", "type": "number", "unit": "m³",
                 "default": "24.77", "factor": "natural_gas", "source": "案例数据", "year": 2024, "region": "全国",
                 "step": 1, "category": "燃料消耗"},
                {"field_id": "diesel_use", "name": "柴油(使用)", "type": "number", "unit": "kg", "default": "11.28",
                 "factor": "diesel", "source": "案例数据", "year": 2024, "region": "全国", "step": 1,
                 "category": "燃料消耗"},
                {"field_id": "co2_use", "name": "二氧化碳(排放)", "type": "number", "unit": "kg", "default": "82.56",
                 "source": "案例数据", "year": 2024, "region": "全国", "step": 5, "category": "大气排放"},
                {"field_id": "ch4_use", "name": "甲烷(排放)", "type": "number", "unit": "kg", "default": "0.003",
                 "source": "案例数据", "year": 2024, "region": "全国", "step": 0.001, "category": "大气排放"},
                {"field_id": "n2o_use", "name": "氧化亚氮(排放)", "type": "number", "unit": "kg", "default": "0.004",
                 "source": "案例数据", "year": 2024, "region": "全国", "step": 0.001, "category": "大气排放"},
            ],
            "报废回收": [
                {"field_id": "recycling_benefit", "name": "回收碳补偿", "type": "number", "unit": "kgCO₂e",
                 "default": "-13970.17", "source": "案例数据", "year": 2024, "region": "全国", "step": 100,
                 "category": "碳补偿"},
            ]
        }

        stages = ["原材料获取", "生产制造", "使用阶段", "报废回收"]
        config_count = 0

        for product in all_products:
            product_id = product['id']
            product_name = product['product_name']

            if product_name == 'X70型集装箱专用平车':
                for stage, config in x70_configs.items():
                    cursor.execute('''
                        INSERT INTO product_configs (product_id, stage, config_json)
                        VALUES (?, ?, ?)
                        ON CONFLICT(product_id, stage) DO UPDATE SET
                            config_json = excluded.config_json,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (product_id, stage, json.dumps(config)))
                    config_count += 1
                print("✅ X70型集装箱专用平车配置数据初始化完成")

            elif product_name in ['道岔', '接触线', '受电弓', '转向架', '信号电缆', '通信电源']:
                default_configs_simple = {
                    "原材料获取": [
                        {"field_id": "steel", "name": "钢材", "type": "number", "unit": "kg", "default": "30000",
                         "factor": "steel", "source": "初级数据", "year": 2024, "region": "华北", "step": 1000,
                         "category": "金属材料"},
                        {"field_id": "aluminum", "name": "铝材", "type": "number", "unit": "kg", "default": "5000",
                         "factor": "aluminum", "source": "初级数据", "year": 2024, "region": "华东", "step": 500,
                         "category": "金属材料"},
                    ],
                    "生产制造": [
                        {"field_id": "processing_power", "name": "零部件加工耗电", "type": "number", "unit": "kWh",
                         "default": "80000", "factor": "electricity_north", "source": "初级数据", "year": 2024,
                         "region": "华北", "step": 5000, "category": "电力消耗"},
                        {"field_id": "assembly_power", "name": "装配耗电", "type": "number", "unit": "kWh",
                         "default": "50000", "factor": "electricity_north", "source": "初级数据", "year": 2024,
                         "region": "华北", "step": 5000, "category": "电力消耗"},
                    ],
                    "使用阶段": [
                        {"field_id": "product_life", "name": "产品寿命", "type": "number", "unit": "年",
                         "default": "25", "source": "次级数据", "year": 2023, "region": "全国", "step": 5,
                         "category": "寿命参数"},
                        {"field_id": "annual_power", "name": "年耗电量", "type": "number", "unit": "kWh/年",
                         "default": "500000", "factor": "electricity_east", "source": "次级数据", "year": 2023,
                         "region": "华东", "step": 10000, "category": "电力消耗"},
                    ],
                    "报废回收": [
                        {"field_id": "disposal_weight", "name": "报废重量", "type": "number", "unit": "kg",
                         "default": "38000", "source": "初级数据", "year": 2024, "region": "华北", "step": 1000,
                         "category": "报废参数"},
                        {"field_id": "steel_recycle_rate", "name": "钢材可回收率", "type": "number", "unit": "",
                         "default": "0.90", "source": "次级数据", "year": 2023, "region": "全国", "step": 0.05,
                         "category": "回收率"},
                    ],
                }
                for stage, config in default_configs_simple.items():
                    stage_config = []
                    for field in config:
                        field_copy = field.copy()
                        field_copy['field_id'] = f"{product_name}_{field['field_id']}"
                        stage_config.append(field_copy)
                    cursor.execute('''
                        INSERT INTO product_configs (product_id, stage, config_json)
                        VALUES (?, ?, ?)
                        ON CONFLICT(product_id, stage) DO UPDATE SET
                            config_json = excluded.config_json,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (product_id, stage, json.dumps(stage_config)))
                    config_count += 1

        print(f"✅ 产品配置数据初始化完成（{config_count} 个配置）")

    # ============================================================
    # 8. 碳减排示例数据
    # ============================================================

    # 减排目标
    cursor.execute("SELECT COUNT(*) FROM reduction_targets")
    if cursor.fetchone()[0] == 0:
        targets = [
            ('XXX工厂的减排目标', '范围一+范围二', 2025, 2035, 46.2, 5000, 2688, '进行中', 46.2, '1.5°C',
             'SBT 1.5°C 目标'),
            ('XXX工厂的减排目标(二期)', '范围三', 2025, 2060, 90, 10000, 1000, '进行中', 30, '优于2°C',
             'SBT 优于2°C 目标'),
        ]
        for t in targets:
            cursor.execute('''
                INSERT INTO reduction_targets 
                (target_name, target_scope, base_year, target_year, reduction_percentage,
                 current_emission, target_emission, status, progress, sbt_level, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', t)

    # 碳排放预测
    cursor.execute("SELECT COUNT(*) FROM emission_forecasts")
    if cursor.fetchone()[0] == 0:
        forecasts = [
            (2024, 5200, 5000, '基准情景'),
            (2025, 5000, 4800, '基准情景'),
            (2026, 4800, 4500, '基准情景'),
            (2027, 4500, 4200, '基准情景'),
            (2028, 4200, 4000, '基准情景'),
        ]
        for f in forecasts:
            cursor.execute('''
                INSERT INTO emission_forecasts (forecast_year, forecast_emission, target_emission, scenario)
                VALUES (?, ?, ?, ?)
            ''', f)

    # 碳减排措施
    cursor.execute("SELECT COUNT(*) FROM reduction_measures")
    if cursor.fetchone()[0] == 0:
        measures = [
            ('节能灯更换', '能效提升', '非牵引', 136.96, 4, 4, '高', '已实施', '2025-01-15',
             '更换节能灯具，降低照明能耗'),
            ('屋顶光伏', '可再生能源', '非牵引', 1720, 350, 350, '中', '进行中', '2025-06-01', '建设屋顶光伏发电系统'),
            ('制冷剂替换', '能源替代', '非牵引', 234.83, 50, 30, '中', '规划中', '2025-12-01', '替换高GWP制冷剂'),
            ('牵引电机升级', '能效提升', '牵引', 450.00, 120, 80, '高', '进行中', '2025-03-01', '升级高效牵引电机'),
        ]
        for m in measures:
            cursor.execute('''
                INSERT INTO reduction_measures 
                (measure_name, measure_type, category, estimated_reduction,
                 estimated_cost, estimated_benefit, feasibility, status,
                 implementation_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', m)

    # CCER项目
    cursor.execute("SELECT COUNT(*) FROM ccer_projects")
    if cursor.fetchone()[0] == 0:
        ccers = [
            ('某地林业碳汇项目', '林业碳汇', '已发起', 5000, '2024-01-01', '2024-12-31', ''),
            ('某地风电项目', '可再生能源', '已发起', 8000, '2024-03-01', '2025-02-28', ''),
            ('某地光伏项目', '可再生能源', '已审定', 6000, '2024-06-01', '2025-05-31', ''),
            ('某地沼气项目', '甲烷回收', '已签发', 3000, '2023-01-01', '2024-12-31', ''),
        ]
        for c in ccers:
            cursor.execute('''
                INSERT INTO ccer_projects 
                (project_name, project_type, status, reduction_amount, start_date, end_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', c)

    # ============================================================
    # 9. 碳金融 - 示例数据
    # ============================================================

    # 检查碳金融表是否有数据
    cursor.execute("SELECT COUNT(*) FROM carbon_projects")
    if cursor.fetchone()[0] == 0:
        # 示例项目
        projects = [
            ('风力发电项目', '企业用户', '《某地风力发电项目降碳产品方法学》',
             '方法学报告.pdf', '资料1.pdf,资料2.pdf', '已核证', '已通过', ''),
            ('集中式光伏项目', '企业用户', '《某地集中式光伏项目降碳产品方法学》',
             '方法学报告.pdf', '资料1.pdf', '已提交', '待审核', ''),
            ('分布式光伏项目', '某市园区', '《某市新区分布式光伏项目降碳产品方法学》',
             '方法学报告.pdf', '资料1.pdf,资料2.pdf', '驳回', '未通过', '材料不完整，请补充'),
            ('被动式超低能耗建筑', '某市园区', '《某省被动式超低能耗办公建筑降碳产品方法学》',
             '方法学报告.pdf', '资料1.pdf', '重新提交', '待审核', ''),
            ('风电项目', '企业用户', '《某市新区分布式光伏项目降碳产品方法学》',
             '方法学报告.pdf', '资料1.pdf', '已核证', '已通过', ''),
            ('分布式光伏项目二期', '某科技公司', '《某地集中式光伏项目降碳产品方法学》',
             '方法学报告_v2.pdf', '资料1.pdf,资料2.pdf,资料3.pdf', '已递交', '待审核', ''),
        ]

        for p in projects:
            cursor.execute('''
                INSERT INTO carbon_projects 
                (project_name, initiator, method_name, method_file, other_files, 
                 status, review_status, review_comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', p)

        # 示例审核记录
        audits = [
            (1, '风力发电项目', '企业用户', '《某地风力发电项目降碳产品方法学》',
             '审核报告.pdf', '已通过', '审核通过，符合要求'),
            (2, '集中式光伏项目', '企业用户', '《某地集中式光伏项目降碳产品方法学》',
             '', '待审核', ''),
            (4, '被动式超低能耗建筑', '某市园区', '《某省被动式超低能耗办公建筑降碳产品方法学》',
             '', '待审核', ''),
            (6, '分布式光伏项目二期', '某科技公司', '《某地集中式光伏项目降碳产品方法学》',
             '', '待审核', ''),
        ]

        for a in audits:
            cursor.execute('''
                INSERT INTO carbon_audits 
                (project_id, project_name, initiator, method_name, 
                 audit_report, audit_status, audit_comment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', a)

        print("✅ 碳金融示例数据初始化完成")

    print("✅ 所有示例数据初始化完成")

    conn.commit()
    print("✅ 数据库初始化完成")


def _init_beijing_bureau_sample_data(conn):
    """初始化北京局(org_id=5)的示例数据：排放源配置和月度能耗数据"""
    import random
    random.seed(42)

    cursor = conn.cursor()
    org_id = 5
    org_name = '北京局'

    # 检查是否已有北京局的能耗数据
    cursor.execute("SELECT COUNT(*) FROM energy_data WHERE org_id = ?", (org_id,))
    if cursor.fetchone()[0] > 0:
        print("✅ 北京局能耗数据已存在，跳过初始化")
        return

    # ============================================================
    # 1. 为北京局配置排放源（全部46个排放源）
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM source_configs WHERE org_id = ?", (org_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id, source_name FROM emission_sources")
        sources = cursor.fetchall()
        for s in sources:
            cursor.execute('''
                INSERT INTO source_configs (org_id, org_name, source_id, source_name, is_selected)
                VALUES (?, ?, ?, ?, 1)
            ''', (org_id, org_name, s['id'], s['source_name']))
        print("✅ 北京局排放源配置完成（46个排放源全部选中）")

    # ============================================================
    # 2. 生成月度能耗数据
    # ============================================================
    # 排放源定义：id, name, range, unit, factor
    # 季节性系数：冬季(12,1,2)供暖高，夏季(6,7,8)用电高
    def seasonal_factor(month):
        """返回季节性系数"""
        if month in [12, 1, 2]:
            return 1.15  # 冬季供暖排放高
        elif month in [6, 7, 8]:
            return 1.10  # 夏季用电高
        elif month in [3, 4, 5]:
            return 0.90  # 春季过渡
        elif month in [9, 10, 11]:
            return 0.95  # 秋季过渡
        return 1.0

    def winter_heating_factor(month):
        """冬季供暖额外系数"""
        if month in [12, 1, 2]:
            return 1.5
        elif month in [11, 3]:
            return 1.1
        return 0.3

    def summer_cooling_factor(month):
        """夏季制冷额外系数"""
        if month in [6, 7, 8]:
            return 1.4
        elif month in [5, 9]:
            return 1.1
        return 0.8

    # 定义每个排放源的月度消耗量生成函数
    # 返回 (source_id, source_name, range, unit, factor, base_consumption, seasonal_fn)
    source_templates = [
        # 范围1 - 牵引排放（固体燃料）
        (1, '无烟煤', '范围1', '吨', 2.32, 300, seasonal_factor),
        (2, '烟煤', '范围1', '吨', 2.07, 150, seasonal_factor),
        (3, '煤制品', '范围1', '吨', 1.94, 50, seasonal_factor),
        (4, '焦炭', '范围1', '吨', 2.85, 30, seasonal_factor),
        (5, '褐煤', '范围1', '吨', 1.42, 20, seasonal_factor),
        (6, '洗精煤', '范围1', '吨', 2.28, 40, seasonal_factor),
        # 范围1 - 牵引排放（液体燃料）
        (7, '燃料油（重油）', '范围1', '吨', 3.05, 80, seasonal_factor),
        (8, '柴油', '范围1', '吨', 3.15, 650, seasonal_factor),
        (9, '汽油', '范围1', '吨', 3.04, 120, seasonal_factor),
        (10, '煤油', '范围1', '吨', 3.15, 30, seasonal_factor),
        # 范围1 - 牵引排放（气体燃料）
        (11, '焦炉煤气', '范围1', '万Nm³', 8.58, 15, seasonal_factor),
        (12, '油田天然气', '范围1', '万Nm³', 21.62, 20, seasonal_factor),
        (13, '气田天然气', '范围1', '万Nm³', 19.74, 60, seasonal_factor),
        (14, '液化石油气', '范围1', '吨', 2.95, 25, seasonal_factor),
        (15, '液化天然气', '范围1', '吨', 2.33, 40, seasonal_factor),
        # 范围1 - 非牵引排放
        (16, '办公室供暖', '范围1', 'GJ', 0.11, 200, winter_heating_factor),
        (17, '发电机', '范围1', 'kWh', 0.0005, 50000, seasonal_factor),
        (18, '其他固定燃烧', '范围1', 'GJ', 0.11, 80, winter_heating_factor),
        (19, '道路车辆及机械', '范围1', '升', 0.0027, 100000, seasonal_factor),
        (20, '专业装卸设备', '范围1', 'kWh', 0.0005, 30000, seasonal_factor),
        # 范围2 - 牵引排放
        (21, '电动列车用电', '范围2', 'MWh', 0.5366, 65000, summer_cooling_factor),
        # 范围2 - 非牵引排放
        (22, '道路车辆用电', '范围2', 'MWh', 0.5366, 800, seasonal_factor),
        (23, '装卸设备用电', '范围2', 'MWh', 0.5366, 1500, seasonal_factor),
        (24, '办公室及仓库用电', '范围2', 'MWh', 0.5366, 3500, summer_cooling_factor),
        (25, '外购热力', '范围2', 'GJ', 0.11, 150, winter_heating_factor),
        # 范围3 - 采购的货物和服务
        (26, '铁路车辆维护承包商', '范围3', '次', 0.05, 500, seasonal_factor),
        (27, '铁路车辆部件', '范围3', '件', 0.05, 2000, seasonal_factor),
        (28, '油品润滑剂', '范围3', '升', 0.0027, 50000, seasonal_factor),
        (29, '设备部件', '范围3', '件', 0.05, 800, seasonal_factor),
        (30, '装卸设备油品', '范围3', '升', 0.0027, 30000, seasonal_factor),
        (31, '清洁服务', '范围3', '次', 0.02, 300, seasonal_factor),
        (32, '办公用品', '范围3', '件', 0.01, 5000, seasonal_factor),
        (33, '数据中心服务', '范围3', '月', 0.5, 12, seasonal_factor),
        (34, '电信服务', '范围3', '月', 0.3, 12, seasonal_factor),
        # 范围3 - 资本货物
        (35, '新机车车辆', '范围3', '辆', 50, 2, seasonal_factor),
        (36, '新装卸设备', '范围3', '台', 10, 1, seasonal_factor),
        (37, '新道路车辆', '范围3', '辆', 15, 3, seasonal_factor),
        (38, '新建筑物', '范围3', '平方米', 0.5, 5000, seasonal_factor),
        # 范围3 - 燃料和能源相关活动
        (39, '燃油燃油税', '范围3', '吨', 0.1, 100, seasonal_factor),
        (40, '电力WTT', '范围3', 'MWh', 0.05, 2000, seasonal_factor),
        (41, '输配电损耗', '范围3', 'MWh', 0.02, 1500, seasonal_factor),
        # 范围3 - 商务差旅
        (42, '商务旅行(陆路)', '范围3', '公里', 0.00025, 60000, seasonal_factor),
        (43, '商务旅行(航空)', '范围3', '公里', 0.00015, 40000, seasonal_factor),
        (44, '酒店住宿', '范围3', '晚', 0.02, 1000, seasonal_factor),
        # 范围3 - 员工通勤
        (45, '员工通勤', '范围3', '公里', 0.00015, 350000, seasonal_factor),
        (46, '在家办公', '范围3', '天', 0.01, 5000, seasonal_factor),
    ]

    # 年度系数：2022年最高，2023年略低，2024年最低（逐年减排趋势）
    year_factors = {
        2022: 1.08,
        2023: 1.03,
        2024: 1.00
    }

    insert_count = 0
    for year in [2022, 2023, 2024]:
        yf = year_factors[year]
        for month in range(1, 13):
            details = []
            total_emission = 0.0

            for (sid, sname, srange, sunit, sfactor, base_consump, sfn) in source_templates:
                # 计算消耗量：基础值 * 季节系数 * 年度系数 + 随机波动
                sf = sfn(month)
                consumption = base_consump * sf * yf * random.uniform(0.92, 1.08)
                consumption = round(consumption, 2)
                emission = round(consumption * sfactor, 4)
                total_emission += emission

                details.append({
                    'source_name': sname,
                    'range': srange,
                    'unit': sunit,
                    'consumption': consumption,
                    'factor': sfactor,
                    'emission': emission,
                    'percentage': 0  # 后面统一计算
                })

            # 计算百分比
            for d in details:
                d['percentage'] = round(d['emission'] / total_emission * 100, 2) if total_emission > 0 else 0

            total_emission = round(total_emission, 2)

            cursor.execute('''
                INSERT INTO energy_data 
                (org_id, org_name, period_type, period_year, period_month, 
                 data_json, total_emission)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (org_id, org_name, '月度', year, month,
                  json.dumps(details, ensure_ascii=False), total_emission))
            insert_count += 1

    conn.commit()
    print(f"✅ 北京局示例数据初始化完成（{insert_count} 条月度能耗数据，2022-2024年）")