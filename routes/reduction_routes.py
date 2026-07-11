# routes/reduction_routes.py
from flask import Blueprint, jsonify, request
from models.database import get_db
import json
from datetime import datetime

reduction_bp = Blueprint('reduction', __name__, url_prefix='/api/reduction')


# ============================================================
# 碳减排概览 API
# ============================================================
@reduction_bp.route('/overview', methods=['GET'])
def get_overview():
    """获取碳减排概览数据"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # 获取总排放量
            cursor.execute('SELECT SUM(total_emission) as total FROM energy_data')
            total_row = cursor.fetchone()
            total_emission = total_row['total'] if total_row and total_row['total'] else 0

            # 获取减排目标
            cursor.execute('SELECT SUM(target_emission) as target FROM reduction_targets WHERE status = "进行中"')
            target_row = cursor.fetchone()
            target_emission = target_row['target'] if target_row and target_row['target'] else 0

            # 获取已实施措施数量
            cursor.execute('SELECT COUNT(*) as count FROM reduction_measures WHERE status = "已实施"')
            measure_row = cursor.fetchone()
            measure_count = measure_row['count'] if measure_row else 0

            # 获取CCER项目数量和详情
            cursor.execute('SELECT COUNT(*) as count FROM ccer_projects')
            ccer_row = cursor.fetchone()
            ccer_count = ccer_row['count'] if ccer_row else 0
            
            cursor.execute('SELECT COUNT(*) as count FROM ccer_projects WHERE status = "已备案"')
            ccer_initiated = cursor.fetchone()['count'] or 0
            cursor.execute('SELECT COUNT(*) as count FROM ccer_projects WHERE status = "已签发"')
            ccer_verified = cursor.fetchone()['count'] or 0
            cursor.execute('SELECT SUM(reduction_amount) as total FROM ccer_projects')
            ccer_total = cursor.fetchone()['total'] or 0

            # 获取年度趋势数据（按 period_year 分组）
            cursor.execute('''
                SELECT period_year as year, SUM(total_emission) as emission
                FROM energy_data
                GROUP BY period_year
                ORDER BY year DESC
                LIMIT 5
            ''')
            trend_data = [dict(row) for row in cursor.fetchall()]

            return jsonify({
                'success': True,
                'data': {
                    'total_emission': total_emission,
                    'target_emission': target_emission,
                    'measure_count': measure_count,
                    'ccer_count': ccer_count,
                    'ccer_initiated': ccer_initiated,
                    'ccer_verified': ccer_verified,
                    'ccer_total': ccer_total,
                    'trend_data': trend_data
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# 碳减排目标 API
# ============================================================
@reduction_bp.route('/targets', methods=['GET'])
def get_targets():
    """获取所有碳减排目标"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, target_name, target_scope, base_year, target_year,
                       reduction_percentage, current_emission, target_emission,
                       status, progress, sbt_level, created_at
                FROM reduction_targets
                ORDER BY target_year
            ''')
            targets = [dict(row) for row in cursor.fetchall()]
            return jsonify({'success': True, 'data': targets})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reduction_bp.route('/targets', methods=['POST'])
def create_target():
    """创建碳减排目标"""
    try:
        data = request.json
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reduction_targets 
                (target_name, target_scope, base_year, target_year, reduction_percentage,
                 current_emission, target_emission, status, progress, sbt_level, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('target_name'),
                data.get('target_scope', '范围一+范围二'),
                data.get('base_year'),
                data.get('target_year'),
                data.get('reduction_percentage', 0),
                data.get('current_emission', 0),
                data.get('target_emission', 0),
                data.get('status', '进行中'),
                data.get('progress', 0),
                data.get('sbt_level', '1.5°C'),
                data.get('description', '')
            ))
            conn.commit()
            return jsonify({'success': True, 'message': '目标创建成功', 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reduction_bp.route('/targets/<int:target_id>', methods=['PUT'])
def update_target(target_id):
    """更新碳减排目标"""
    try:
        data = request.json
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reduction_targets 
                SET target_name=?, target_scope=?, base_year=?, target_year=?,
                    reduction_percentage=?, current_emission=?, target_emission=?,
                    status=?, progress=?, sbt_level=?, description=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                data.get('target_name'),
                data.get('target_scope', '范围一+范围二'),
                data.get('base_year'),
                data.get('target_year'),
                data.get('reduction_percentage', 0),
                data.get('current_emission', 0),
                data.get('target_emission', 0),
                data.get('status', '进行中'),
                data.get('progress', 0),
                data.get('sbt_level', '1.5°C'),
                data.get('description', ''),
                target_id
            ))
            conn.commit()
            return jsonify({'success': True, 'message': '目标更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reduction_bp.route('/targets/<int:target_id>', methods=['DELETE'])
def delete_target(target_id):
    """删除碳减排目标"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM reduction_targets WHERE id = ?', (target_id,))
            conn.commit()
            return jsonify({'success': True, 'message': '目标删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# 碳排放预测 API
# ============================================================
@reduction_bp.route('/forecast', methods=['GET'])
def get_forecast():
    """获取碳排放预测数据"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # 获取历史数据（按 period_year 和 period_month 分组）
            cursor.execute('''
                SELECT period_year || '-' || CASE WHEN period_month < 10 THEN '0' || period_month ELSE period_month END as month,
                       SUM(total_emission) as emission
                FROM energy_data
                GROUP BY period_year, period_month
                ORDER BY period_year, period_month
            ''')
            history = [dict(row) for row in cursor.fetchall()]

            # 获取预测数据（默认基准情景）
            scenario = request.args.get('scenario', '基准情景')
            cursor.execute('''
                SELECT forecast_year, forecast_emission, target_emission
                FROM emission_forecasts
                WHERE scenario = ?
                ORDER BY forecast_year
            ''', (scenario,))
            forecasts = [dict(row) for row in cursor.fetchall()]

            return jsonify({
                'success': True,
                'data': {
                    'history': history,
                    'forecasts': forecasts
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reduction_bp.route('/forecast', methods=['POST'])
def create_forecast():
    """创建碳排放预测"""
    try:
        data = request.json
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emission_forecasts 
                (forecast_year, forecast_emission, target_emission, scenario)
                VALUES (?, ?, ?, ?)
            ''', (
                data.get('forecast_year'),
                data.get('forecast_emission', 0),
                data.get('target_emission', 0),
                data.get('scenario', '基准情景')
            ))
            conn.commit()
            return jsonify({'success': True, 'message': '预测数据创建成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# 碳减排措施 API
# ============================================================
@reduction_bp.route('/measures', methods=['GET'])
def get_measures():
    """获取所有碳减排措施"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, measure_name, measure_type, category, 
                       estimated_reduction, estimated_cost, estimated_benefit,
                       feasibility, status, implementation_date, description
                FROM reduction_measures
                ORDER BY id
            ''')
            measures = [dict(row) for row in cursor.fetchall()]
            return jsonify({'success': True, 'data': measures})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reduction_bp.route('/measures', methods=['POST'])
def create_measure():
    """创建碳减排措施"""
    try:
        data = request.json
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reduction_measures 
                (measure_name, measure_type, category, estimated_reduction,
                 estimated_cost, estimated_benefit, feasibility, status,
                 implementation_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('measure_name'),
                data.get('measure_type', '能效提升'),
                data.get('category', ''),
                data.get('estimated_reduction', 0),
                data.get('estimated_cost', 0),
                data.get('estimated_benefit', 0),
                data.get('feasibility', '中'),
                data.get('status', '规划中'),
                data.get('implementation_date'),
                data.get('description', '')
            ))
            conn.commit()
            return jsonify({'success': True, 'message': '措施创建成功', 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reduction_bp.route('/measures/<int:measure_id>', methods=['PUT'])
def update_measure(measure_id):
    """更新碳减排措施"""
    try:
        data = request.json
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reduction_measures 
                SET measure_name=?, measure_type=?, category=?,
                    estimated_reduction=?, estimated_cost=?, estimated_benefit=?,
                    feasibility=?, status=?, implementation_date=?, description=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                data.get('measure_name'),
                data.get('measure_type', '能效提升'),
                data.get('category', ''),
                data.get('estimated_reduction', 0),
                data.get('estimated_cost', 0),
                data.get('estimated_benefit', 0),
                data.get('feasibility', '中'),
                data.get('status', '规划中'),
                data.get('implementation_date'),
                data.get('description', ''),
                measure_id
            ))
            conn.commit()
            return jsonify({'success': True, 'message': '措施更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reduction_bp.route('/measures/<int:measure_id>', methods=['DELETE'])
def delete_measure(measure_id):
    """删除碳减排措施"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM reduction_measures WHERE id = ?', (measure_id,))
            conn.commit()
            return jsonify({'success': True, 'message': '措施删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500