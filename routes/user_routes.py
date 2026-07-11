# routes/user_routes.py
from flask import Blueprint, request, jsonify
from models.database import get_db
import hashlib

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@user_bp.route('', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, real_name, email, phone, role, status, last_login, created_at
                FROM users
                ORDER BY created_at DESC
            ''')
            users = [dict(row) for row in cursor.fetchall()]
            return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, real_name, email, phone, role, status, last_login, created_at
                FROM users
                WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({'success': True, 'data': dict(user)})
            return jsonify({'success': False, 'error': '用户不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('', methods=['POST'])
def create_user():
    """创建用户"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        real_name = data.get('real_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        role = data.get('role', 'user')

        if not username:
            return jsonify({'success': False, 'error': '用户名不能为空'}), 400
        if len(username) < 3:
            return jsonify({'success': False, 'error': '用户名至少3个字符'}), 400
        if not password:
            return jsonify({'success': False, 'error': '密码不能为空'}), 400
        if len(password) < 6:
            return jsonify({'success': False, 'error': '密码至少6个字符'}), 400

        with get_db() as conn:
            cursor = conn.cursor()

            # 检查用户名是否已存在
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return jsonify({'success': False, 'error': '用户名已存在'}), 400

            cursor.execute('''
                INSERT INTO users (username, password, real_name, email, phone, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, hash_password(password), real_name, email, phone, role, '启用'))

            conn.commit()
            return jsonify({'success': True, 'message': '用户创建成功', 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    try:
        data = request.json
        real_name = data.get('real_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        role = data.get('role', 'user')
        status = data.get('status', '启用')
        password = data.get('password', '').strip()

        with get_db() as conn:
            cursor = conn.cursor()

            # 构建更新语句
            updates = []
            params = []

            if real_name:
                updates.append('real_name = ?')
                params.append(real_name)
            if email:
                updates.append('email = ?')
                params.append(email)
            if phone:
                updates.append('phone = ?')
                params.append(phone)
            if role:
                updates.append('role = ?')
                params.append(role)
            if status:
                updates.append('status = ?')
                params.append(status)
            if password:
                updates.append('password = ?')
                params.append(hash_password(password))

            if not updates:
                return jsonify({'success': False, 'error': '没有要更新的字段'}), 400

            params.append(user_id)
            cursor.execute(f'''
                UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', params)

            conn.commit()
            return jsonify({'success': True, 'message': '用户更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    try:
        # 不允许删除管理员
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'success': False, 'error': '用户不存在'}), 404
            if user['role'] == 'admin':
                return jsonify({'success': False, 'error': '不能删除管理员账户'}), 400

            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return jsonify({'success': True, 'message': '用户删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/<int:user_id>/reset_password', methods=['POST'])
def reset_password(user_id):
    """重置用户密码"""
    try:
        data = request.json
        new_password = data.get('password', '').strip()

        if not new_password or len(new_password) < 6:
            return jsonify({'success': False, 'error': '密码至少6个字符'}), 400

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (hash_password(new_password), user_id))
            conn.commit()
            return jsonify({'success': True, 'message': '密码重置成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500