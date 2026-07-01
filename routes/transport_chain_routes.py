# routes/transport_chain_routes.py
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models.transport_chain_model import TransportChainDAO
from models.database import get_db
import json

transport_chain_bp = Blueprint('transport_chain', __name__, url_prefix='/transport_chain')


@transport_chain_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    return render_template('transport_chain.html')


@transport_chain_bp.route('/api/calculate', methods=['POST'])
def calculate_emission():
    """计算碳排放并保存"""
    data = request.get_json()

    # 提取数据
    chain_type = data.get('chain_type', '客运')
    start = data.get('start_location', '上海')
    end = data.get('end_location', '西安')
    distance = data.get('distance', 0)
    weight = data.get('weight', 500)
    turnover = data.get('turnover', 0)
    train_type = data.get('train_type', '')
    seat_type = data.get('seat_type', '')
    energy_type = data.get('energy_type', '')
    transport_mode = data.get('transport_mode', '')

    rail_emission = data.get('rail_emission', 0)
    rail_intensity = data.get('rail_intensity', 0)
    rail_energy_intensity = data.get('rail_energy_intensity', 0)
    road_emission = data.get('road_emission', 0)
    road_intensity = data.get('road_intensity', 0)
    road_energy_intensity = data.get('road_energy_intensity', 0)
    reduction_amount = data.get('reduction_amount', 0)
    reduction_rate = data.get('reduction_rate', 0)
    chain_transport = data.get('chain_transport', 0)
    chain_handling = data.get('chain_handling', 0)
    chain_storage = data.get('chain_storage', 0)
    chain_other = data.get('chain_other', 0)
    route_data = data.get('route_data', [])

    record_data = {
        'chain_type': chain_type,
        'start_location': start,
        'end_location': end,
        'train_type': train_type,
        'seat_type': seat_type,
        'energy_type': energy_type,
        'transport_mode': transport_mode,
        'distance': distance,
        'weight': weight,
        'turnover': turnover,
        'rail_emission': rail_emission,
        'rail_intensity': rail_intensity,
        'rail_energy_intensity': rail_energy_intensity,
        'road_emission': road_emission,
        'road_intensity': road_intensity,
        'road_energy_intensity': road_energy_intensity,
        'reduction_amount': reduction_amount,
        'reduction_rate': reduction_rate,
        'chain_transport': chain_transport,
        'chain_handling': chain_handling,
        'chain_storage': chain_storage,
        'chain_other': chain_other,
        'route_data': route_data
    }

    record_id = TransportChainDAO.create(record_data)

    return jsonify({
        'success': True,
        'id': record_id,
        'message': '计算完成并已保存'
    })


@transport_chain_bp.route('/api/records', methods=['GET'])
def get_records():
    """获取所有记录"""
    records = TransportChainDAO.get_all()
    return jsonify(records)


@transport_chain_bp.route('/api/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    """获取单条记录"""
    record = TransportChainDAO.get_by_id(record_id)
    if record:
        return jsonify(record)
    return jsonify({'error': '记录不存在'}), 404


@transport_chain_bp.route('/api/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    """更新记录"""
    data = request.get_json()
    success = TransportChainDAO.update(record_id, data)
    if success:
        return jsonify({'success': True, 'message': '更新成功'})
    return jsonify({'error': '更新失败'}), 400


@transport_chain_bp.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除记录"""
    success = TransportChainDAO.delete(record_id)
    if success:
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'error': '删除失败'}), 400


@transport_chain_bp.route('/api/records/batch_delete', methods=['POST'])
def batch_delete_records():
    """批量删除"""
    data = request.get_json()
    ids = data.get('ids', [])
    count = TransportChainDAO.delete_batch(ids)
    return jsonify({'success': True, 'count': count, 'message': f'成功删除 {count} 条记录'})


@transport_chain_bp.route('/api/station_data')
def get_station_data():
    """获取站点和路线数据"""
    # 主要铁路干线数据
    railway_lines = [
        {'name': '京沪线', 'stations': ['北京', '天津', '济南', '徐州', '南京', '上海']},
        {'name': '京广线', 'stations': ['北京', '石家庄', '郑州', '武汉', '长沙', '广州']},
        {'name': '陇海线', 'stations': ['连云港', '徐州', '郑州', '西安', '兰州', '乌鲁木齐']},
        {'name': '京九线', 'stations': ['北京', '衡水', '商丘', '阜阳', '九江', '南昌', '深圳']},
        {'name': '沪昆线', 'stations': ['上海', '杭州', '南昌', '长沙', '贵阳', '昆明']},
        {'name': '京哈线', 'stations': ['北京', '沈阳', '长春', '哈尔滨']},
        {'name': '兰新线', 'stations': ['兰州', '嘉峪关', '乌鲁木齐', '阿拉山口']},
        {'name': '青藏线', 'stations': ['西宁', '格尔木', '拉萨']}
    ]

    return jsonify(railway_lines)