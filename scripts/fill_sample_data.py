"""
全面填充铁路碳资产管理系统示例数据
以北京局为核心，覆盖所有模块
"""
import sqlite3
import json
import random
import os

random.seed(42)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'carbon_asset.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_organizations(conn):
    """填充组织机构数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM organizations")
    if cursor.fetchone()[0] > 0:
        print("✅ 组织数据已存在，跳过")
        return

    # 组织数据：id, org_code, org_name, org_type, parent_id
    orgs = [
        # 一级：国铁集团
        (1, 'GL', '中国铁路总公司', '集团', None),
        # 二级分类
        (2, 'TJ', '铁路局集团公司', '分类', 1),
        (3, 'ZY', '专业运输公司', '分类', 1),
        (4, 'FYS', '非运输企业', '分类', 1),
        # 三级：铁路局
        (5, 'BJ', '中国铁路北京局集团有限公司', '铁路局', 2),
        (6, 'SH', '中国铁路上海局集团有限公司', '铁路局', 2),
        (7, 'GD', '中国铁路广州局集团有限公司', '铁路局', 2),
        (8, 'CD', '中国铁路成都局集团有限公司', '铁路局', 2),
        (9, 'WH', '中国铁路武汉局集团有限公司', '铁路局', 2),
        (10, 'XA', '中国铁路西安局集团有限公司', '铁路局', 2),
        (11, 'ZZ', '中国铁路郑州局集团有限公司', '铁路局', 2),
        (12, 'SY', '中国铁路沈阳局集团有限公司', '铁路局', 2),
        (13, 'LZ', '中国铁路兰州局集团有限公司', '铁路局', 2),
        (14, 'HL', '中国铁路哈尔滨局集团有限公司', '铁路局', 2),
        (15, 'UR', '中国铁路乌鲁木齐局集团有限公司', '铁路局', 2),
        (16, 'QZ', '中国铁路青藏集团有限公司', '铁路局', 2),
        (17, 'NMG', '中国铁路呼和浩特局集团有限公司', '铁路局', 2),
        (18, 'JN', '中国铁路济南局集团有限公司', '铁路局', 2),
        # 三级：专业运输公司
        (19, 'HY', '中铁货运有限责任公司', '专业公司', 3),
        (20, 'KC', '中铁集装箱有限责任公司', '专业公司', 3),
        (21, 'TE', '中铁特货运输有限责任公司', '专业公司', 3),
    ]

    for o in orgs:
        cursor.execute('''
            INSERT OR IGNORE INTO organizations (id, org_code, org_name, org_type, parent_id, status)
            VALUES (?, ?, ?, ?, ?, '启用')
        ''', (*o,))
    
    conn.commit()
    print(f"✅ 组织数据初始化完成（{len(orgs)}条）")


def init_emission_sources(conn):
    """确保排放源数据完整"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emission_sources")
    if cursor.fetchone()[0] > 0:
        print("✅ 排放源数据已存在，跳过")
        return

    sources = [
        # 范围1 - 固体燃料
        (1, '范围1', '固定燃烧', '固体燃料', '无烟煤', '吨', '锅炉', '实测'),
        (2, '范围1', '固定燃烧', '固体燃料', '烟煤', '吨', '锅炉', '实测'),
        (3, '范围1', '固定燃烧', '固体燃料', '煤制品', '吨', '锅炉', '实测'),
        (4, '范围1', '固定燃烧', '固体燃料', '焦炭', '吨', '锅炉', '实测'),
        (5, '范围1', '固定燃烧', '固体燃料', '褐煤', '吨', '锅炉', '实测'),
        (6, '范围1', '固定燃烧', '固体燃料', '洗精煤', '吨', '锅炉', '实测'),
        # 范围1 - 液体燃料
        (7, '范围1', '固定燃烧', '液体燃料', '燃料油（重油）', '吨', '锅炉', '实测'),
        (8, '范围1', '移动燃烧', '液体燃料', '柴油', '吨', '内燃机车', '实测'),
        (9, '范围1', '移动燃烧', '液体燃料', '汽油', '吨', '公路车辆', '实测'),
        (10, '范围1', '移动燃烧', '液体燃料', '煤油', '吨', '备用设备', '实测'),
        # 范围1 - 气体燃料
        (11, '范围1', '固定燃烧', '气体燃料', '焦炉煤气', '万Nm³', '锅炉', '实测'),
        (12, '范围1', '固定燃烧', '气体燃料', '油田天然气', '万Nm³', '锅炉', '实测'),
        (13, '范围1', '固定燃烧', '气体燃料', '气田天然气', '万Nm³', '锅炉', '实测'),
        (14, '范围1', '固定燃烧', '气体燃料', '液化石油气', '吨', '锅炉', '实测'),
        (15, '范围1', '固定燃烧', '气体燃料', '液化天然气', '吨', '锅炉', '实测'),
        # 范围1 - 非牵引排放
        (16, '范围1', '非牵引排放', '供暖', '办公室供暖', 'GJ', '供暖设备', '实测'),
        (17, '范围1', '非牵引排放', '发电', '发电机', 'kWh', '柴油发电机', '实测'),
        (18, '范围1', '非牵引排放', '其他燃烧', '其他固定燃烧', 'GJ', '其他设备', '实测'),
        (19, '范围1', '非牵引排放', '道路运输', '道路车辆及机械', '升', '公路车辆', '实测'),
        (20, '范围1', '非牵引排放', '装卸设备', '专业装卸设备', 'kWh', '装卸机械', '实测'),
        # 范围2
        (21, '范围2', '牵引排放', '电力', '电动列车用电', 'MWh', '电力机车', '电表计量'),
        (22, '范围2', '非牵引排放', '电力', '道路车辆用电', 'MWh', '电动车辆', '电表计量'),
        (23, '范围2', '非牵引排放', '电力', '装卸设备用电', 'MWh', '装卸机械', '电表计量'),
        (24, '范围2', '非牵引排放', '电力', '办公室及仓库用电', 'MWh', '建筑设施', '电表计量'),
        (25, '范围2', '非牵引排放', '热力', '外购热力', 'GJ', '供暖设备', '热力公司'),
        # 范围3 - 采购货物服务
        (26, '范围3', '采购货物服务', '维护服务', '铁路车辆维护承包商', '次', '外包服务', '估算'),
        (27, '范围3', '采购货物服务', '零部件', '铁路车辆部件', '件', '采购', '估算'),
        (28, '范围3', '采购货物服务', '油品', '油品润滑剂', '升', '采购', '估算'),
        (29, '范围3', '采购货物服务', '设备', '设备部件', '件', '采购', '估算'),
        (30, '范围3', '采购货物服务', '油品', '装卸设备油品', '升', '采购', '估算'),
        (31, '范围3', '采购货物服务', '服务', '清洁服务', '次', '外包', '估算'),
        (32, '范围3', '采购货物服务', '办公用品', '办公用品', '件', '采购', '估算'),
        (33, '范围3', '采购货物服务', 'IT服务', '数据中心服务', '月', '外包', '估算'),
        (34, '范围3', '采购货物服务', '通信', '电信服务', '月', '外包', '估算'),
        # 范围3 - 资本货物
        (35, '范围3', '资本货物', '机车车辆', '新机车车辆', '辆', '采购', '估算'),
        (36, '范围3', '资本货物', '装卸设备', '新装卸设备', '台', '采购', '估算'),
        (37, '范围3', '资本货物', '道路车辆', '新道路车辆', '辆', '采购', '估算'),
        (38, '范围3', '资本货物', '建筑', '新建筑物', '平方米', '建设', '估算'),
        # 范围3 - 燃料能源相关
        (39, '范围3', '燃料能源相关', '燃油', '燃油燃油税', '吨', '采购', '估算'),
        (40, '范围3', '燃料能源相关', '电力', '电力WTT', 'MWh', '上游', '估算'),
        (41, '范围3', '燃料能源相关', '电力', '输配电损耗', 'MWh', '电网', '估算'),
        # 范围3 - 商务差旅
        (42, '范围3', '商务差旅', '陆路', '商务旅行(陆路)', '公里', '出差', '报销'),
        (43, '范围3', '商务差旅', '航空', '商务旅行(航空)', '公里', '出差', '报销'),
        (44, '范围3', '商务差旅', '住宿', '酒店住宿', '晚', '出差', '报销'),
        # 范围3 - 员工通勤
        (45, '范围3', '员工通勤', '通勤', '员工通勤', '公里', '公共交通', '统计'),
        (46, '范围3', '员工通勤', '远程办公', '在家办公', '天', '远程', '统计'),
    ]

    for s in sources:
        cursor.execute('''
            INSERT OR IGNORE INTO emission_sources 
            (id, range_type, scenario_type, source_type, source_name, unit, equipment, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', s)

    conn.commit()
    print(f"✅ 排放源数据初始化完成（{len(sources)}条）")


def init_emission_factors(conn):
    """确保排放因子数据完整"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emission_factors")
    if cursor.fetchone()[0] > 0:
        print("✅ 排放因子数据已存在，跳过")
        return

    factors = [
        (1, '化石燃料', '固体燃料', '无烟煤', 'tCO2/吨', 2.32, None, None, None, None, None, None, 'IPCC', '2024-01-01', '启用'),
        (2, '化石燃料', '固体燃料', '烟煤', 'tCO2/吨', 2.07, None, None, None, None, None, None, 'IPCC', '2024-01-01', '启用'),
        (3, '化石燃料', '固体燃料', '焦炭', 'tCO2/吨', 2.85, None, None, None, None, None, None, 'IPCC', '2024-01-01', '启用'),
        (4, '化石燃料', '液体燃料', '柴油', 'tCO2/吨', 3.15, None, None, None, None, None, None, '国家发改委', '2024-01-01', '启用'),
        (5, '化石燃料', '液体燃料', '汽油', 'tCO2/吨', 3.04, None, None, None, None, None, None, '国家发改委', '2024-01-01', '启用'),
        (6, '化石燃料', '液体燃料', '燃料油', 'tCO2/吨', 3.05, None, None, None, None, None, None, '国家发改委', '2024-01-01', '启用'),
        (7, '化石燃料', '气体燃料', '天然气', 'tCO2/万Nm³', 19.74, None, None, None, None, None, None, 'IPCC', '2024-01-01', '启用'),
        (8, '电力', '外购电力', '华北电网', 'tCO2/MWh', 0.5366, None, None, None, None, None, None, '生态环境部', '2024-01-01', '启用'),
        (9, '电力', '外购电力', '华东电网', 'tCO2/MWh', 0.4823, None, None, None, None, None, None, '生态环境部', '2024-01-01', '启用'),
        (10, '热力', '外购热力', '集中供热', 'tCO2/GJ', 0.11, None, None, None, None, None, None, '地方标准', '2024-01-01', '启用'),
    ]

    for f in factors:
        cursor.execute('''
            INSERT OR IGNORE INTO emission_factors 
            (factor_type, category, subcategory, unit, factor_value, data_source, effective_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (f[1], f[2], f[3], f[4], f[5], f[9], f[10], f[11]))

    conn.commit()
    print(f"✅ 排放因子数据初始化完成（{len(factors)}条）")


def init_source_configs(conn):
    """为北京局配置排放源"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM source_configs WHERE org_id = 5")
    if cursor.fetchone()[0] > 0:
        print("✅ 北京局排放源配置已存在，跳过")
        return

    cursor.execute("SELECT id, source_name FROM emission_sources")
    sources = cursor.fetchall()
    for s in sources:
        cursor.execute('''
            INSERT INTO source_configs (org_id, org_name, source_id, source_name, is_selected)
            VALUES (5, '北京局', ?, ?, 1)
        ''', (s['id'], s['source_name']))

    conn.commit()
    print(f"✅ 北京局排放源配置完成（{len(sources)}个）")


def init_energy_data(conn):
    """为北京局填充月度能耗数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM energy_data WHERE org_id = 5")
    if cursor.fetchone()[0] > 0:
        print("✅ 北京局能耗数据已存在，跳过")
        return

    def seasonal_factor(month):
        if month in [12, 1, 2]: return 1.15
        elif month in [6, 7, 8]: return 1.10
        elif month in [3, 4, 5]: return 0.90
        elif month in [9, 10, 11]: return 0.95
        return 1.0

    def winter_heating_factor(month):
        if month in [12, 1, 2]: return 1.5
        elif month in [11, 3]: return 1.1
        return 0.3

    def summer_cooling_factor(month):
        if month in [6, 7, 8]: return 1.4
        elif month in [5, 9]: return 1.1
        return 0.8

    source_templates = [
        (1, '无烟煤', '范围1', '吨', 2.32, 300, seasonal_factor),
        (2, '烟煤', '范围1', '吨', 2.07, 150, seasonal_factor),
        (3, '煤制品', '范围1', '吨', 1.94, 50, seasonal_factor),
        (4, '焦炭', '范围1', '吨', 2.85, 30, seasonal_factor),
        (5, '褐煤', '范围1', '吨', 1.42, 20, seasonal_factor),
        (6, '洗精煤', '范围1', '吨', 2.28, 40, seasonal_factor),
        (7, '燃料油（重油）', '范围1', '吨', 3.05, 80, seasonal_factor),
        (8, '柴油', '范围1', '吨', 3.15, 650, seasonal_factor),
        (9, '汽油', '范围1', '吨', 3.04, 120, seasonal_factor),
        (10, '煤油', '范围1', '吨', 3.15, 30, seasonal_factor),
        (11, '焦炉煤气', '范围1', '万Nm³', 8.58, 15, seasonal_factor),
        (12, '油田天然气', '范围1', '万Nm³', 21.62, 20, seasonal_factor),
        (13, '气田天然气', '范围1', '万Nm³', 19.74, 60, seasonal_factor),
        (14, '液化石油气', '范围1', '吨', 2.95, 25, seasonal_factor),
        (15, '液化天然气', '范围1', '吨', 2.33, 40, seasonal_factor),
        (16, '办公室供暖', '范围1', 'GJ', 0.11, 200, winter_heating_factor),
        (17, '发电机', '范围1', 'kWh', 0.0005, 50000, seasonal_factor),
        (18, '其他固定燃烧', '范围1', 'GJ', 0.11, 80, winter_heating_factor),
        (19, '道路车辆及机械', '范围1', '升', 0.0027, 100000, seasonal_factor),
        (20, '专业装卸设备', '范围1', 'kWh', 0.0005, 30000, seasonal_factor),
        (21, '电动列车用电', '范围2', 'MWh', 0.5366, 65000, summer_cooling_factor),
        (22, '道路车辆用电', '范围2', 'MWh', 0.5366, 800, seasonal_factor),
        (23, '装卸设备用电', '范围2', 'MWh', 0.5366, 1500, seasonal_factor),
        (24, '办公室及仓库用电', '范围2', 'MWh', 0.5366, 3500, summer_cooling_factor),
        (25, '外购热力', '范围2', 'GJ', 0.11, 150, winter_heating_factor),
        (26, '铁路车辆维护承包商', '范围3', '次', 0.05, 500, seasonal_factor),
        (27, '铁路车辆部件', '范围3', '件', 0.05, 2000, seasonal_factor),
        (28, '油品润滑剂', '范围3', '升', 0.0027, 50000, seasonal_factor),
        (29, '设备部件', '范围3', '件', 0.05, 800, seasonal_factor),
        (30, '装卸设备油品', '范围3', '升', 0.0027, 30000, seasonal_factor),
        (31, '清洁服务', '范围3', '次', 0.02, 300, seasonal_factor),
        (32, '办公用品', '范围3', '件', 0.01, 5000, seasonal_factor),
        (33, '数据中心服务', '范围3', '月', 0.5, 12, seasonal_factor),
        (34, '电信服务', '范围3', '月', 0.3, 12, seasonal_factor),
        (35, '新机车车辆', '范围3', '辆', 50, 2, seasonal_factor),
        (36, '新装卸设备', '范围3', '台', 10, 1, seasonal_factor),
        (37, '新道路车辆', '范围3', '辆', 15, 3, seasonal_factor),
        (38, '新建筑物', '范围3', '平方米', 0.5, 5000, seasonal_factor),
        (39, '燃油燃油税', '范围3', '吨', 0.1, 100, seasonal_factor),
        (40, '电力WTT', '范围3', 'MWh', 0.05, 2000, seasonal_factor),
        (41, '输配电损耗', '范围3', 'MWh', 0.02, 1500, seasonal_factor),
        (42, '商务旅行(陆路)', '范围3', '公里', 0.00025, 60000, seasonal_factor),
        (43, '商务旅行(航空)', '范围3', '公里', 0.00015, 40000, seasonal_factor),
        (44, '酒店住宿', '范围3', '晚', 0.02, 1000, seasonal_factor),
        (45, '员工通勤', '范围3', '公里', 0.00015, 350000, seasonal_factor),
        (46, '在家办公', '范围3', '天', 0.01, 5000, seasonal_factor),
    ]

    year_factors = {2022: 1.08, 2023: 1.03, 2024: 1.00}
    insert_count = 0

    for year in [2022, 2023, 2024]:
        yf = year_factors[year]
        for month in range(1, 13):
            details = []
            total_emission = 0.0

            for (sid, sname, srange, sunit, sfactor, base_consump, sfn) in source_templates:
                sf = sfn(month)
                consumption = round(base_consump * sf * yf * random.uniform(0.92, 1.08), 2)
                emission = round(consumption * sfactor, 4)
                total_emission += emission
                details.append({
                    'source_name': sname, 'range': srange, 'unit': sunit,
                    'consumption': consumption, 'factor': sfactor,
                    'emission': emission, 'percentage': 0
                })

            for d in details:
                d['percentage'] = round(d['emission'] / total_emission * 100, 2) if total_emission > 0 else 0

            total_emission = round(total_emission, 2)
            cursor.execute('''
                INSERT INTO energy_data 
                (org_id, org_name, period_type, period_year, period_month, data_json, total_emission)
                VALUES (5, '北京局', '月度', ?, ?, ?, ?)
            ''', (year, month, json.dumps(details, ensure_ascii=False), total_emission))
            insert_count += 1

    conn.commit()
    print(f"✅ 北京局能耗数据初始化完成（{insert_count}条，2022-2024年）")


def init_transport_chains(conn):
    """填充运输链碳核算示例数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transport_chains")
    if cursor.fetchone()[0] > 0:
        print("✅ 运输链数据已存在，跳过")
        return

    chains = [
        (1, '货运', '北京→上海', 1318, '高速列车', '电力', '集装箱', 1, 28500.5, 12.5),
        (2, '货运', '北京→广州', 2294, '高速列车', '电力', '大宗货物', 1, 36515.9, 14.3),
        (3, '货运', '北京→成都', 1876, '非高速列车', '柴油', '散货', 1, 52340.2, 8.7),
        (4, '客运', '北京→上海', 1318, '高速列车', '电力', '二等', 2, 18250.3, 18.2),
        (5, '客运', '北京→广州', 2294, '高速列车', '电力', '一等', 2, 31280.7, 16.8),
        (6, '客运', '上海→西安', 1508, '高速列车', '电力', '二等', 2, 21500.1, 15.5),
        (7, '货运', '广州→成都', 2650, '非高速列车', '柴油', '集装箱', 1, 61250.8, 6.2),
        (8, '客运', '武汉→北京', 1152, '高速列车', '电力', '商务', 2, 16800.4, 20.1),
    ]

    for c in chains:
        cursor.execute('''
            INSERT INTO transport_chains 
            (type, route, distance, train_type, traction, cargo_class, carbon_emission, reduction_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (c[0], c[1], c[2], c[3], c[4], c[5], c[7], c[8]))

    conn.commit()
    print(f"✅ 运输链数据初始化完成（{len(chains)}条）")


def init_reduction_targets(conn):
    """填充碳减排目标数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reduction_targets")
    if cursor.fetchone()[0] > 0:
        print("✅ 碳减排目标数据已存在，跳过")
        return

    targets = [
        (1, '北京局2025年度碳减排目标', 5, '北京局', 2025, 480000, 420000, '1.5°C', '范围一+范围二', '进行中', 
         '通过优化能源结构、提升电气化率、推广节能技术，实现年度碳排放总量较基准年下降12.5%', 85),
        (2, '北京局2030年碳达峰目标', 5, '北京局', 2030, 480000, 380000, '2°C', '全部范围', '已规划',
         '确保2030年前碳排放达峰，峰值控制在38万吨以内', 30),
    ]

    for t in targets:
        cursor.execute('''
            INSERT INTO reduction_targets 
            (target_name, org_id, org_name, target_year, baseline_emission, target_emission, 
             temperature_goal, scope, status, description, progress)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10]))

    conn.commit()
    print(f"✅ 碳减排目标数据初始化完成（{len(targets)}条）")


def init_product_footprints(conn):
    """填充产品碳足迹数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM product_footprints")
    if cursor.fetchone()[0] > 0:
        print("✅ 产品碳足迹数据已存在，跳过")
        return

    footprints = [
        (1, 5, '北京局', '高速铁路客运服务', '吨CO2e/万人公里', 2024, '月度', 1, 8.56, 
         json.dumps([
            {'stage': '原材料获取', 'emission': 0.42, 'percentage': 4.9},
            {'stage': '生产制造', 'emission': 0.15, 'percentage': 1.8},
            {'stage': '运输交付', 'emission': 6.82, 'percentage': 79.7},
            {'stage': '使用阶段', 'emission': 0.95, 'percentage': 11.1},
            {'stage': '维护保养', 'emission': 0.12, 'percentage': 1.4},
            {'stage': '报废回收', 'emission': 0.10, 'percentage': 1.2},
         ], ensure_ascii=False)),
        (2, 5, '北京局', '高速铁路客运服务', '吨CO2e/万人公里', 2024, '月度', 2, 8.23,
         json.dumps([
            {'stage': '原材料获取', 'emission': 0.40, 'percentage': 4.9},
            {'stage': '生产制造', 'emission': 0.14, 'percentage': 1.7},
            {'stage': '运输交付', 'emission': 6.55, 'percentage': 79.6},
            {'stage': '使用阶段', 'emission': 0.92, 'percentage': 11.2},
            {'stage': '维护保养', 'emission': 0.12, 'percentage': 1.5},
            {'stage': '报废回收', 'emission': 0.10, 'percentage': 1.2},
         ], ensure_ascii=False)),
        (3, 5, '北京局', '高速铁路客运服务', '吨CO2e/万人公里', 2024, '月度', 3, 7.95,
         json.dumps([
            {'stage': '原材料获取', 'emission': 0.38, 'percentage': 4.8},
            {'stage': '生产制造', 'emission': 0.13, 'percentage': 1.6},
            {'stage': '运输交付', 'emission': 6.35, 'percentage': 79.9},
            {'stage': '使用阶段', 'emission': 0.88, 'percentage': 11.1},
            {'stage': '维护保养', 'emission': 0.11, 'percentage': 1.4},
            {'stage': '报废回收', 'emission': 0.10, 'percentage': 1.3},
         ], ensure_ascii=False)),
        (4, 5, '北京局', '普速铁路货运服务', '吨CO2e/万吨公里', 2024, '月度', 1, 25.6,
         json.dumps([
            {'stage': '原材料获取', 'emission': 1.28, 'percentage': 5.0},
            {'stage': '生产制造', 'emission': 0.51, 'percentage': 2.0},
            {'stage': '运输交付', 'emission': 20.22, 'percentage': 79.0},
            {'stage': '使用阶段', 'emission': 2.56, 'percentage': 10.0},
            {'stage': '维护保养', 'emission': 0.64, 'percentage': 2.5},
            {'stage': '报废回收', 'emission': 0.39, 'percentage': 1.5},
         ], ensure_ascii=False)),
    ]

    for f in footprints:
        cursor.execute('''
            INSERT INTO product_footprints 
            (org_id, org_name, product_name, unit, year, period_type, period_value, footprint_value, lifecycle_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]))

    conn.commit()
    print(f"✅ 产品碳足迹数据初始化完成（{len(footprints)}条）")


def print_summary(conn):
    """打印数据填充汇总"""
    cursor = conn.cursor()
    tables = {
        'organizations': '组织机构',
        'emission_sources': '排放源',
        'emission_factors': '排放因子',
        'source_configs': '排放源配置(北京局)',
        'energy_data': '能耗数据(北京局)',
        'calculation_methods': '核算方法',
        'transport_chains': '运输链',
        'reduction_targets': '碳减排目标',
        'product_footprints': '产品碳足迹',
        'users': '用户',
    }

    print("\n" + "=" * 50)
    print("  数据库填充汇总")
    print("=" * 50)
    for table, name in tables.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {name}: {count} 条")

    # 北京局能耗数据详情
    print("\n  北京局月度能耗数据示例（2024年）：")
    cursor.execute('''
        SELECT period_year, period_month, total_emission 
        FROM energy_data WHERE org_id=5 AND period_year=2024 
        ORDER BY period_month
    ''')
    for r in cursor.fetchall():
        bar = '█' * int(r['total_emission'] / 2000)
        print(f"    {r['period_year']}-{r['period_month']:02d}: {r['total_emission']:>10.1f} tCO2e  {bar}")

    # 范围分布
    print("\n  2024年排放范围分布（1月示例）：")
    cursor.execute("SELECT data_json FROM energy_data WHERE org_id=5 AND period_year=2024 AND period_month=1")
    row = cursor.fetchone()
    if row:
        details = json.loads(row['data_json'])
        range_totals = {}
        for d in details:
            r = d['range']
            range_totals[r] = range_totals.get(r, 0) + d['emission']
        for r, total in sorted(range_totals.items()):
            print(f"    {r}: {total:.1f} tCO2e")

    print("=" * 50)


def main():
    # 先删除旧数据库，重新初始化
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️  已清除旧数据库")

    conn = get_db()

    # 先创建所有表（从database.py的init_db逻辑）
    create_tables(conn)

    # 填充数据
    init_organizations(conn)
    init_emission_sources(conn)
    init_emission_factors(conn)
    init_source_configs(conn)
    init_energy_data(conn)
    init_transport_chains(conn)
    init_reduction_targets(conn)
    init_product_footprints(conn)

    # 打印汇总
    print_summary(conn)

    conn.close()
    print("\n✅ 所有数据填充完成！")


def create_tables(conn):
    """创建所有数据库表"""
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, org_code TEXT UNIQUE, org_name TEXT,
        org_type TEXT, parent_id INTEGER, contact_person TEXT, contact_phone TEXT,
        contact_email TEXT, address TEXT, status TEXT DEFAULT '启用',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS emission_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT, category_type TEXT, range_type TEXT, scenario_type TEXT,
        source_type TEXT, activity_category TEXT, subcategory TEXT, source_name TEXT, unit TEXT,
        equipment TEXT, data_source TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS emission_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, factor_type TEXT, category TEXT, subcategory TEXT,
        unit TEXT, factor_value REAL, calorific_value REAL, carbon_content TEXT, oxidation_rate TEXT,
        region TEXT, coverage TEXT, product_type TEXT, data_source TEXT, effective_date TEXT, status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS source_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, org_id INTEGER, org_name TEXT, source_id INTEGER,
        source_name TEXT, is_selected INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS energy_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT, org_id INTEGER, org_name TEXT, period_type TEXT,
        period_year INTEGER, period_month INTEGER, period_quarter TEXT, period_start TEXT,
        period_end TEXT, data_json TEXT, total_emission REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS calculation_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT, method_name TEXT, emission_type TEXT, data_type TEXT,
        unit TEXT, param_config TEXT, formula TEXT, is_referenced INTEGER DEFAULT 0,
        is_enabled INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS transport_chains (
        id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, route TEXT, distance REAL,
        train_type TEXT, traction TEXT, cargo_class TEXT, org_id INTEGER,
        carbon_emission REAL, reduction_rate REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS reduction_targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, target_name TEXT, org_id INTEGER, org_name TEXT,
        target_year INTEGER, baseline_emission REAL, target_emission REAL, temperature_goal TEXT,
        scope TEXT, status TEXT, description TEXT, progress REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS product_footprints (
        id INTEGER PRIMARY KEY AUTOINCREMENT, org_id INTEGER, org_name TEXT, product_name TEXT,
        unit TEXT, year INTEGER, period_type TEXT, period_value INTEGER, footprint_value REAL,
        lifecycle_data TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 插入默认管理员用户
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')''')

    conn.commit()
    print("✅ 数据库表创建完成")


if __name__ == '__main__':
    main()
