from flask import Flask
from flask_cors import CORS
from utils.Logging import hijack_std_output
from api.app import app_orders
from api.FileApi import file_view
from api.ScriptApi import script_view
from api.TaskChainApi import task_chain_view
from api.PackageApi import package_view
import os

app = Flask(__name__)
CORS(app)
# 配置
app.config['SECRET_KEY'] = 'your_secret_key'  # 你可以保留这个密钥用于其他用途
app.config['WTF_CSRF_ENABLED'] = False  # 禁用 CSRF 保护

app.register_blueprint(app_orders)
app.register_blueprint(file_view, url_prefix='/file')
# 注册蓝图
app.register_blueprint(script_view, url_prefix='/script')
app.register_blueprint(task_chain_view, url_prefix='/task_chain')
app.register_blueprint(package_view, url_prefix='/package')
hijack_std_output("test")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
