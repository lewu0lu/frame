from flask import Flask, jsonify, redirect
from flask_cors import CORS
from utils.Logging import hijack_std_output
from api.app import app_orders
from api.FileApi import file_view
from api.ScriptApi import script_view
from api.TaskChainApi import task_chain_view
from api.PackageApi import package_view
from api.UserApi import user_view
import os
from config.ConfigLoader import config

app = Flask(__name__)
# 配置CORS，允许所有来源的请求，并支持凭证
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}}, 
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# 配置
app.config['SECRET_KEY'] = config.get('app', 'secret_key', fallback='your_secret_key')
app.config['WTF_CSRF_ENABLED'] = False  # 禁用 CSRF 保护

# 添加根路由处理
@app.route('/')
def index():
    # 返回API信息而不是重定向
    return jsonify({
        'success': True,
        'message': '任务管理系统API服务',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'user': '/user',
            'file': '/file',
            'script': '/script',
            'task_chain': '/task_chain',
            'package': '/package'
        }
    })

app.register_blueprint(app_orders)
app.register_blueprint(file_view, url_prefix='/file')
# 注册蓝图
app.register_blueprint(script_view, url_prefix='/script')
app.register_blueprint(task_chain_view, url_prefix='/task_chain')
app.register_blueprint(package_view, url_prefix='/package')
app.register_blueprint(user_view, url_prefix='/user')
#hijack_std_output("test")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
