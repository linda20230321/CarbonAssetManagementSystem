# routes/api_routes.py
from flask import Blueprint, jsonify, request, send_file
from models import (
    EmissionSourceDAO,
    EmissionFactorDAO,
    SourceConfigDAO,
    EnergyDataDAO,
    CalculationMethodDAO
)
from models.database import get_db, init_sample_data
import pandas as pd
from io import BytesIO
from datetime import datetime

# ==================== 创建蓝图（必须有） ====================
api_bp = Blueprint('api', __name__)


# ==================== 排放源 API ====================
@api_bp.route('/emission_sources', methods=['GET'])
def get_emission_sources():
    try:
        return jsonify(EmissionSourceDAO.get_all())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_sources/<int:source_id>', methods=['GET'])
def get_emission_source(source_id):
    try:
        data = EmissionSourceDAO.get_by_id(source_id)
        if data:
            return jsonify(data)
        return jsonify({'error': '未找到该排放源'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_sources', methods=['POST'])
def create_emission_source():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        source_id = EmissionSourceDAO.create(data)
        if source_id:
            new_data = EmissionSourceDAO.get_by_id(source_id)
            return jsonify(new_data), 201
        return jsonify({'error': '创建失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_sources/<int:source_id>', methods=['PUT'])
def update_emission_source(source_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        if EmissionSourceDAO.update(source_id, data):
            updated = EmissionSourceDAO.get_by_id(source_id)
            return jsonify(updated)
        return jsonify({'error': '未找到该排放源'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_sources/<int:source_id>', methods=['DELETE'])
def delete_emission_source(source_id):
    try:
        if EmissionSourceDAO.delete(source_id):
            return jsonify({'message': '删除成功'})
        return jsonify({'error': '未找到该排放源'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_sources/batch_delete', methods=['POST'])
def batch_delete_emission_sources():
    try:
        data = request.json
        ids = data.get('ids', [])
        if not ids:
            return jsonify({'error': '请提供要删除的ID列表'}), 400
        count = EmissionSourceDAO.delete_batch(ids)
        return jsonify({'message': f'成功删除 {count} 条记录'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_sources/export', methods=['GET'])
def export_emission_sources():
    try:
        data = EmissionSourceDAO.get_all()
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        filename = f"排放源数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_sources/reset', methods=['POST'])
def reset_emission_sources():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM emission_sources')
            conn.commit()
        with get_db() as conn:
            init_sample_data(conn)
        return jsonify({'success': True, 'message': '排放源数据已重置'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 排放因子 API ====================
@api_bp.route('/emission_factors', methods=['GET'])
def get_emission_factors():
    try:
        return jsonify(EmissionFactorDAO.get_all())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_factors/<int:factor_id>', methods=['GET'])
def get_emission_factor(factor_id):
    try:
        data = EmissionFactorDAO.get_by_id(factor_id)
        if data:
            return jsonify(data)
        return jsonify({'error': '未找到该排放因子'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_factors', methods=['POST'])
def create_emission_factor():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        factor_id = EmissionFactorDAO.create(data)
        if factor_id:
            new_data = EmissionFactorDAO.get_by_id(factor_id)
            return jsonify(new_data), 201
        return jsonify({'error': '创建失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_factors/<int:factor_id>', methods=['PUT'])
def update_emission_factor(factor_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        if EmissionFactorDAO.update(factor_id, data):
            updated = EmissionFactorDAO.get_by_id(factor_id)
            return jsonify(updated)
        return jsonify({'error': '未找到该排放因子'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_factors/<int:factor_id>', methods=['DELETE'])
def delete_emission_factor(factor_id):
    try:
        if EmissionFactorDAO.delete(factor_id):
            return jsonify({'message': '删除成功'})
        return jsonify({'error': '未找到该排放因子'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_factors/batch_delete', methods=['POST'])
def batch_delete_factors():
    try:
        data = request.json
        ids = data.get('ids', [])
        if not ids:
            return jsonify({'error': '请提供要删除的ID列表'}), 400
        count = EmissionFactorDAO.delete_batch(ids)
        return jsonify({'message': f'成功删除 {count} 条记录'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_factors/export', methods=['GET'])
def export_emission_factors():
    try:
        data = EmissionFactorDAO.get_all()
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        filename = f"排放因子数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/emission_factors/import', methods=['POST'])
def import_emission_factors():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '请选择要导入的文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '请选择要导入的文件'}), 400
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        required_columns = ['factor_type', 'category', 'subcategory', 'unit', 'factor_value']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': '文件格式不正确，缺少必要列'}), 400

        imported_data = df.to_dict('records')
        count = 0
        for record in imported_data:
            record['status'] = record.get('status', '启用')
            record['effective_date'] = record.get('effective_date', datetime.now().strftime('%Y-%m-%d'))
            EmissionFactorDAO.create(record)
            count += 1
        return jsonify({'message': f'成功导入 {count} 条记录'})
    except Exception as e:
        return jsonify({'error': f'导入失败: {str(e)}'}), 500


@api_bp.route('/emission_factors/reset', methods=['POST'])
def reset_emission_factors():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM emission_factors')
            conn.commit()
        with get_db() as conn:
            init_sample_data(conn)
        return jsonify({'success': True, 'message': '排放因子数据已重置'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 排放源配置 API ====================
@api_bp.route('/source_configs', methods=['POST'])
def save_source_config():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        org_id = data.get('org_id')
        org_name = data.get('org_name')
        selections = data.get('selections', {})
        if not org_id:
            return jsonify({'error': '组织ID不能为空'}), 400
        count = SourceConfigDAO.save(org_id, org_name, selections)
        return jsonify({'success': True, 'message': f'成功保存 {count} 个排放源配置'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/source_configs/<int:org_id>', methods=['GET'])
def get_source_configs(org_id):
    try:
        return jsonify(SourceConfigDAO.get_by_org(org_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 能耗数据 API ====================
@api_bp.route('/energy_data', methods=['POST'])
def save_energy_data():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        EnergyDataDAO.save(data)
        return jsonify({'success': True, 'message': '能耗数据保存成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/energy_data/<int:org_id>', methods=['GET'])
def get_energy_data(org_id):
    try:
        return jsonify(EnergyDataDAO.get_by_org(org_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/energy_data/<int:org_id>/query', methods=['GET'])
def query_energy_data(org_id):
    """按条件查询能耗数据"""
    try:
        period_type = request.args.get('period_type', '月度')
        period_year = request.args.get('period_year', type=int, default=2024)
        period_month = request.args.get('period_month', type=int)
        period_quarter = request.args.get('period_quarter')
        print(f'[DEBUG query] org_id={org_id}, period_type={period_type}, year={period_year}, month={period_month}, quarter={period_quarter}')
        data = EnergyDataDAO.get_by_org_and_period(
            org_id, period_type, period_year, period_month, period_quarter
        )
        print(f'[DEBUG query] result count={len(data)}')
        return jsonify(data)
    except Exception as e:
        print(f'[DEBUG query] ERROR: {e}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/energy_data/<int:record_id>', methods=['DELETE'])
def delete_energy_data(record_id):
    """删除单条能耗数据"""
    try:
        if EnergyDataDAO.delete(record_id):
            return jsonify({'success': True, 'message': '能耗数据删除成功'})
        return jsonify({'error': '未找到该能耗数据记录'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/energy_data/<int:record_id>', methods=['PUT'])
def update_energy_data(record_id):
    """更新单条能耗数据"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        if EnergyDataDAO.update(record_id, data):
            return jsonify({'success': True, 'message': '能耗数据更新成功'})
        return jsonify({'error': '未找到该能耗数据记录'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 核算方法 API ====================
@api_bp.route('/calculation_methods', methods=['GET'])
def get_calculation_methods():
    try:
        return jsonify(CalculationMethodDAO.get_all())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/calculation_methods/<int:method_id>', methods=['GET'])
def get_calculation_method(method_id):
    try:
        data = CalculationMethodDAO.get_by_id(method_id)
        if data:
            return jsonify(data)
        return jsonify({'error': '未找到该核算方法'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/calculation_methods', methods=['POST'])
def create_calculation_method():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        method_id = CalculationMethodDAO.create(data)
        if method_id:
            new_data = CalculationMethodDAO.get_by_id(method_id)
            return jsonify(new_data), 201
        return jsonify({'error': '创建失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/calculation_methods/<int:method_id>', methods=['PUT'])
def update_calculation_method(method_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效数据'}), 400
        if CalculationMethodDAO.update(method_id, data):
            updated = CalculationMethodDAO.get_by_id(method_id)
            return jsonify(updated)
        return jsonify({'error': '未找到该核算方法'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/calculation_methods/<int:method_id>', methods=['DELETE'])
def delete_calculation_method(method_id):
    try:
        if CalculationMethodDAO.delete(method_id):
            return jsonify({'message': '删除成功'})
        return jsonify({'error': '未找到该核算方法'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/calculation_methods/batch_delete', methods=['POST'])
def batch_delete_calculation_methods():
    try:
        data = request.json
        ids = data.get('ids', [])
        if not ids:
            return jsonify({'error': '请提供要删除的ID列表'}), 400
        count = CalculationMethodDAO.delete_batch(ids)
        return jsonify({'message': f'成功删除 {count} 条记录'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# routes/api_routes.py - 在文件末尾添加以下API

# ==================== 产品碳足迹 API ====================
@api_bp.route('/product_categories', methods=['GET'])
def get_product_categories():
    try:
        from models import ProductCategoryDAO
        return jsonify(ProductCategoryDAO.get_all())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/all_products', methods=['GET'])
def get_all_products():
    try:
        from models import ProductDAO
        return jsonify(ProductDAO.get_all())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        from models import ProductDAO
        data = ProductDAO.get_by_id(product_id)
        return jsonify(data) if data else jsonify({'error': '未找到'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/product_configs/<int:product_id>', methods=['GET'])
def get_product_configs(product_id):
    try:
        from models import ProductConfigDAO
        return jsonify(ProductConfigDAO.get_by_product(product_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/product_config', methods=['POST'])
def save_product_config():
    try:
        from models import ProductConfigDAO
        data = request.json
        ProductConfigDAO.save(data.get('product_id'), data.get('stage'), data.get('config'))
        return jsonify({'success': True, 'message': '配置保存成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# routes/api_routes.py - 在 product_config 相关API后添加

@api_bp.route('/product_config', methods=['PUT'])
def update_product_config():
    """更新产品配置（支持单个字段编辑）"""
    try:
        from models import ProductConfigDAO
        data = request.json
        product_id = data.get('product_id')
        stage = data.get('stage')
        config = data.get('config')

        if not product_id or not stage:
            return jsonify({'error': '缺少必要参数'}), 400

        ProductConfigDAO.save(product_id, stage, config)
        return jsonify({'success': True, 'message': '配置更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/product_footprints/<int:product_id>', methods=['GET'])
def get_product_footprints(product_id):
    try:
        from models import ProductFootprintDAO
        return jsonify(ProductFootprintDAO.get_by_product(product_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/calculate_footprint', methods=['POST'])
def calculate_footprint():
    try:
        from models import ProductFootprintDAO, EmissionFactorDAO
        data = request.json
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        category_name = data.get('category_name')
        quantity = data.get('quantity', 1)
        activities = data.get('activities', [])

        # 获取排放因子
        factors = {}
        for f in EmissionFactorDAO.get_all():
            factor_key = f.get('factor_key')
            if factor_key:
                factors[factor_key] = f

        # GWP值
        GWP = {'CO2': 1, 'CH4': 28, 'N2O': 265}

        # 计算
        stage_results = {}
        details = []
        total = 0.0

        for activity in activities:
            stage = activity.get('stage', '')
            name = activity.get('name', '')
            quantity_val = activity.get('quantity', 0)
            factor_key = activity.get('factor_key', '')
            unit = activity.get('unit', '')

            emission = 0
            if factor_key in factors:
                factor = factors[factor_key]
                emission = (
                    quantity_val * factor.get('co2_factor', 0) * GWP['CO2'] +
                    quantity_val * factor.get('ch4_factor', 0) * GWP['CH4'] +
                    quantity_val * factor.get('n2o_factor', 0) * GWP['N2O']
                )
            else:
                # 如果没有匹配的因子，使用默认计算（兼容桌面版）
                emission = quantity_val * 0.5

            if stage not in stage_results:
                stage_results[stage] = 0
            stage_results[stage] += emission
            total += emission

            details.append({
                'stage': stage,
                'name': name,
                'quantity': quantity_val,
                'unit': unit,
                'emission': emission
            })

        # 计算占比
        stages = {}
        for stage, value in stage_results.items():
            stages[stage] = {
                'value': value,
                'percentage': (value / total * 100) if total > 0 else 0
            }

        result = {
            'total': total,
            'stages': stages,
            'details': details
        }

        # 保存核算结果
        ProductFootprintDAO.save({
            'product_id': product_id,
            'product_name': product_name,
            'category_name': category_name,
            'quantity': quantity,
            'total_emission': total,
            'stages': stages,
            'details': details
        })

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/product_footprints/<int:footprint_id>', methods=['DELETE'])
def delete_product_footprint(footprint_id):
    try:
        from models import ProductFootprintDAO
        if ProductFootprintDAO.delete(footprint_id):
            return jsonify({'message': '删除成功'})
        return jsonify({'error': '未找到'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# routes/api_routes.py - 在末尾添加

# ==================== 产品管理 API ====================
@api_bp.route('/products', methods=['POST'])
def create_product():
    """新增产品"""
    try:
        from models import ProductDAO
        data = request.json
        if not data.get('product_name'):
            return jsonify({'error': '产品名称不能为空'}), 400
        if not data.get('category_id'):
            return jsonify({'error': '请选择产品分类'}), 400

        product_id = ProductDAO.create(data)
        if product_id:
            new_product = ProductDAO.get_by_id(product_id)
            return jsonify({'success': True, 'data': new_product, 'message': '产品创建成功'}), 201
        return jsonify({'error': '创建失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新产品"""
    try:
        from models import ProductDAO
        data = request.json
        if ProductDAO.update(product_id, data):
            updated = ProductDAO.get_by_id(product_id)
            return jsonify({'success': True, 'data': updated, 'message': '更新成功'})
        return jsonify({'error': '更新失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """删除产品"""
    try:
        from models import ProductDAO
        if ProductDAO.delete(product_id):
            return jsonify({'success': True, 'message': '删除成功'})
        return jsonify({'error': '删除失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/product_categories', methods=['POST'])
def create_product_category():
    """新增产品分类"""
    try:
        from models import ProductCategoryDAO
        data = request.json
        if not data.get('category_name'):
            return jsonify({'error': '分类名称不能为空'}), 400
        category_id = ProductCategoryDAO.create(data)
        return jsonify({'success': True, 'id': category_id, 'message': '分类创建成功'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/product_categories/<int:category_id>', methods=['DELETE'])
def delete_product_category(category_id):
    """删除产品分类"""
    try:
        from models import ProductCategoryDAO
        if ProductCategoryDAO.delete(category_id):
            return jsonify({'success': True, 'message': '删除成功'})
        return jsonify({'error': '删除失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/product_overview', methods=['GET'])
def get_product_overview():
    """获取产品碳足迹概览数据"""
    try:
        from models import ProductFootprintDAO
        import json

        product_id = request.args.get('product_id', type=int)
        period = request.args.get('period', '月度')
        year = request.args.get('year', type=int, default=2024)
        month = request.args.get('month', type=int)
        quarter = request.args.get('quarter')

        if not product_id:
            return jsonify({'error': '产品ID不能为空'}), 400

        # 获取该产品的所有核算结果
        footprints = ProductFootprintDAO.get_by_product(product_id, limit=50)

        print(f"📊 产品 {product_id} 的核算结果数量: {len(footprints)}")
        if footprints:
            print(f"📊 第一条记录: {footprints[0]}")

        # 根据周期筛选
        filtered = []
        for fp in footprints:
            calc_at = fp.get('calculated_at', '')
            if calc_at:
                try:
                    # 解析日期
                    date_str = calc_at.split(' ')[0]
                    parts = date_str.split('-')
                    if len(parts) >= 2:
                        fp_year = int(parts[0])
                        fp_month = int(parts[1])
                        fp_quarter = f"Q{(fp_month - 1) // 3 + 1}"

                        if fp_year == year:
                            if period == '月度' and month and fp_month == month:
                                filtered.append(fp)
                            elif period == '季度' and quarter and fp_quarter == quarter:
                                filtered.append(fp)
                            elif period == '年度':
                                filtered.append(fp)
                except Exception as e:
                    print(f"解析日期失败: {calc_at}, {e}")
                    # 解析失败也保留
                    filtered.append(fp)
            else:
                filtered.append(fp)

        # 如果筛选后没有数据，但原始数据有，则使用最新的
        if len(filtered) == 0 and len(footprints) > 0:
            filtered = [footprints[0]]
            print(f"⚠️ 筛选后无数据，使用最新记录")

        result = {
            'product_id': product_id,
            'stages': {},
            'total': 0,
            'has_data': False
        }

        if filtered and len(filtered) > 0:
            latest = filtered[0]
            stages_json = latest.get('stages_json', {})
            if isinstance(stages_json, str):
                try:
                    stages_json = json.loads(stages_json)
                except:
                    stages_json = {}

            result['stages'] = stages_json
            result['total'] = latest.get('total_emission', 0)
            result['has_data'] = True
            result['calculated_at'] = latest.get('calculated_at', '')
            result['quantity'] = latest.get('quantity', 1)
            print(f"✅ 返回概览数据: total={result['total']}, stages={len(result['stages'])}")
        else:
            print(f"⚠️ 没有找到核算结果")

        return jsonify(result)
    except Exception as e:
        print(f"❌ 获取概览数据失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500