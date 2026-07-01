# app.py
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from models.database import init_db
from routes.api_routes import api_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.reduction_routes import reduction_bp
from routes.transport_chain_routes import transport_chain_bp
from routes.carbon_finance_routes import carbon_finance_bp  # 新增碳金融蓝图

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# 初始化数据库
init_db()

# 注册蓝图
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(reduction_bp)
app.register_blueprint(transport_chain_bp)
app.register_blueprint(carbon_finance_bp)  # 注册碳金融蓝图


def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/emission_source')
@login_required
def emission_source():
    return render_template('emission_source.html')

@app.route('/emission_factor')
@login_required
def emission_factor():
    return render_template('emission_factor.html')

@app.route('/organization')
@login_required
def organization():
    return render_template('organization.html')

@app.route('/transport_chain')
@login_required
def transport_chain():
    return render_template('transport_chain.html')

@app.route('/product_footprint')
@login_required
def product_footprint():
    return render_template('product_footprint.html')

@app.route('/reduction_overview')
@login_required
def reduction_overview():
    return render_template('reduction_overview.html')

@app.route('/reduction_target')
@login_required
def reduction_target():
    return render_template('reduction_target.html')

@app.route('/reduction_forecast')
@login_required
def reduction_forecast():
    return render_template('reduction_forecast.html')

@app.route('/reduction_measure')
@login_required
def reduction_measure():
    return render_template('reduction_measure.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


if __name__ == '__main__':
    print("🚀 服务器启动: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)