# routes/auth_routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.database import get_db
import hashlib

auth_bp = Blueprint('auth', __name__)


def hash_password(password):
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """登录页面"""
    if session.get('user_id'):
        return redirect(url_for('index'))
    return render_template('login.html')


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """登录接口"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'success': False, 'error': '请输入用户名和密码'}), 400

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, real_name, email, role, status, password
                FROM users
                WHERE username = ?
            ''', (username,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

            if user['status'] != '启用':
                return jsonify({'success': False, 'error': '账户已被禁用'}), 401

            # 验证密码 - 加密后比对
            encrypted_password = hash_password(password)
            if user['password'] != encrypted_password:
                return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

            # 更新最后登录时间
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user['id'],))
            conn.commit()

            # 保存会话
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['real_name'] = user['real_name']
            session['role'] = user['role']

            return jsonify({
                'success': True,
                'data': {
                    'id': user['id'],
                    'username': user['username'],
                    'real_name': user['real_name'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """退出登录"""
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})


@auth_bp.route('/api/auth/current_user', methods=['GET'])
def get_current_user():
    """获取当前登录用户"""
    if session.get('user_id'):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, real_name, email, role, status, last_login
                FROM users
                WHERE id = ?
            ''', (session['user_id'],))
            user = cursor.fetchone()
            if user:
                return jsonify({
                    'success': True,
                    'data': dict(user)
                })
    return jsonify({'success': False, 'error': '未登录'}), 401