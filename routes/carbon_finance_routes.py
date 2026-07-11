# routes/carbon_finance_routes.py
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models.carbon_finance_model import CarbonFinanceDAO

carbon_finance_bp = Blueprint('carbon_finance', __name__, url_prefix='/carbon_finance')


# ========== 页面路由 ==========
@carbon_finance_bp.route('/asset_development')
def asset_development():
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    return render_template('carbon_finance_asset.html')


# ========== 项目管理 API ==========
@carbon_finance_bp.route('/api/projects', methods=['GET'])
def get_projects():
    projects = CarbonFinanceDAO.get_projects()
    return jsonify(projects)


@carbon_finance_bp.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = CarbonFinanceDAO.get_project(project_id)
    if project:
        return jsonify(project)
    return jsonify({'error': '项目不存在'}), 404


@carbon_finance_bp.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    try:
        project_id = CarbonFinanceDAO.create_project(data)
        return jsonify({'id': project_id, 'message': '项目创建成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    try:
        success = CarbonFinanceDAO.update_project(project_id, data)
        if success:
            return jsonify({'message': '项目更新成功'})
        return jsonify({'error': '项目不存在或更新失败'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        success = CarbonFinanceDAO.delete_project(project_id)
        if success:
            return jsonify({'message': '项目删除成功'})
        return jsonify({'error': '项目不存在或删除失败'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/projects/submit/<int:project_id>', methods=['POST'])
def submit_project(project_id):
    """提交核证 - 自动创建审核记录"""
    data = request.get_json()
    try:
        success = CarbonFinanceDAO.submit_project(project_id, data.get('comment', ''))
        if success:
            return jsonify({'message': '提交核证成功，已进入审核流程'})
        return jsonify({'error': '提交失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ========== 审核管理 API ==========
@carbon_finance_bp.route('/api/audits', methods=['GET'])
def get_audits():
    audits = CarbonFinanceDAO.get_audits()
    return jsonify(audits)


@carbon_finance_bp.route('/api/audits/<int:audit_id>', methods=['GET'])
def get_audit(audit_id):
    audit = CarbonFinanceDAO.get_audit(audit_id)
    if audit:
        return jsonify(audit)
    return jsonify({'error': '审核记录不存在'}), 404


@carbon_finance_bp.route('/api/audits', methods=['POST'])
def create_audit():
    data = request.get_json()
    try:
        audit_id = CarbonFinanceDAO.create_audit(data)
        return jsonify({'id': audit_id, 'message': '审核记录创建成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/audits/<int:audit_id>', methods=['PUT'])
def update_audit(audit_id):
    data = request.get_json()
    try:
        success = CarbonFinanceDAO.update_audit(audit_id, data)
        if success:
            return jsonify({'message': '审核记录更新成功'})
        return jsonify({'error': '审核记录不存在或更新失败'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/audits/<int:audit_id>', methods=['DELETE'])
def delete_audit(audit_id):
    try:
        success = CarbonFinanceDAO.delete_audit(audit_id)
        if success:
            return jsonify({'message': '审核记录删除成功'})
        return jsonify({'error': '审核记录不存在或删除失败'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/audits/approve/<int:audit_id>', methods=['POST'])
def approve_audit(audit_id):
    """审核通过 - 报告传送"""
    data = request.get_json()
    try:
        success = CarbonFinanceDAO.approve_audit(audit_id, data.get('comment', ''))
        if success:
            return jsonify({'message': '报告传送成功'})
        return jsonify({'error': '操作失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/audits/reject/<int:audit_id>', methods=['POST'])
def reject_audit(audit_id):
    """驳回审核"""
    data = request.get_json()
    try:
        success = CarbonFinanceDAO.reject_audit(audit_id, data.get('comment', ''))
        if success:
            return jsonify({'message': '驳回成功'})
        return jsonify({'error': '操作失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/audits/upload_report/<int:audit_id>', methods=['POST'])
def upload_audit_report(audit_id):
    """上传审核报告"""
    data = request.get_json()
    try:
        success = CarbonFinanceDAO.upload_audit_report(audit_id, data.get('report_file', ''))
        if success:
            return jsonify({'message': '报告上传成功'})
        return jsonify({'error': '上传失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@carbon_finance_bp.route('/api/audits/transmit/<int:audit_id>', methods=['POST'])
def transmit_report(audit_id):
    """报告传送"""
    data = request.get_json()
    try:
        success = CarbonFinanceDAO.transmit_report(audit_id, data.get('comment', ''))
        if success:
            return jsonify({'message': '报告传送成功'})
        return jsonify({'error': '传送失败'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400