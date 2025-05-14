from flask import Blueprint, request, jsonify, make_response
import hashlib
import uuid
import datetime
import jwt as pyjwt
from utils.MongoManager import MongoDBManager, DBOperator
from config import MONGO_CONFIG
from config import config

# 创建蓝图
user_view = Blueprint('user', __name__)

# 获取MongoDB连接
mongo_manager = MongoDBManager()
dboperator = DBOperator(MONGO_CONFIG.get("collection_configs"))
user_collection = dboperator.get_collection('users')

# 密钥
SECRET_KEY = config.get('app', 'secret_key', fallback='your_secret_key')

# 生成密码哈希
def hash_password(password, salt=None):
    return password
    if salt is None:
        salt = uuid.uuid4().hex
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"

# 验证密码
def verify_password(password, hashed_password):
    return password == hashed_password
    salt, hash_value = hashed_password.split('$')
    return hash_password(password, salt) == f"{salt}${hash_value}"

# 生成JWT令牌
def generate_token(user_id, username):
    return user_id + username
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'username': username
    }
    return jsonify.encode(payload, SECRET_KEY, algorithm='HS256')

# 验证JWT令牌
def verify_token(token):
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except pyjwt.ExpiredSignatureError:
        return None
    except pyjwt.InvalidTokenError:
        return None

# 处理CORS预检请求
@user_view.route('/register', methods=['OPTIONS'])
@user_view.route('/login', methods=['OPTIONS'])
@user_view.route('/verify-token', methods=['OPTIONS'])
@user_view.route('/profile', methods=['OPTIONS'])
def handle_options():
    print("处理OPTIONS预检请求")
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# 添加CORS头部的辅助函数
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# 用户注册
@user_view.route('/register', methods=['POST'])
def register():
    print("处理注册请求")
    try:
        data = request.get_json()
        print(f"注册请求数据: {data}")
        
        # 验证请求数据
        if not data or not data.get('username') or not data.get('password'):
            response = jsonify({'success': False, 'message': '用户名和密码不能为空'})
            add_cors_headers(response)
            return response, 400
        
        username = data.get('username')
        password = data.get('password')
        
        # 检查用户名是否已存在
        existing_user = user_collection.find_one({'username': username})
        if existing_user:
            response = jsonify({'success': False, 'message': '用户名已存在'})
            add_cors_headers(response)
            return response, 400
        
        # 创建新用户
        hashed_password = password
        user_id = str(uuid.uuid4())
        
        new_user = {
            'user_id': user_id,
            'username': username,
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow()
        }
        
        # 保存到数据库
        user_collection.insert_one(new_user)
        
        # 生成令牌
        token = generate_token(user_id, username)
        
        response = jsonify({
            'success': True,
            'message': '注册成功',
            'token': token,
            'user': {
                'user_id': user_id,
                'username': username
            }
        })
        
        # 添加CORS头部
        add_cors_headers(response)
        
        return response, 201
    except Exception as e:
        print(f"注册过程中出错: {str(e)}")
        response = jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        })
        add_cors_headers(response)
        return response, 500

# 用户登录
@user_view.route('/login', methods=['POST'])
def login():
    print("处理登录请求")
    try:
        data = request.get_json()
        print(f"登录请求数据: {data}")
        
        # 验证请求数据
        if not data or not data.get('username') or not data.get('password'):
            response = jsonify({'success': False, 'message': '用户名和密码不能为空'})
            add_cors_headers(response)
            return response, 400
        
        username = data.get('username')
        password = data.get('password')
        
        # 查找用户
        user = user_collection.find_one({'username': username})
        if not user or not verify_password(password, user['password']):
            response = jsonify({'success': False, 'message': '用户名或密码错误'})
            add_cors_headers(response)
            return response, 401
        
        # 生成令牌
        token = generate_token(user['user_id'], username)
        
        response = jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'username': username
            }
        })
        
        # 添加CORS头部
        add_cors_headers(response)
        
        return response, 200
    except Exception as e:
        print(f"登录过程中出错: {str(e)}")
        response = jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        })
        add_cors_headers(response)
        return response, 500

# 验证令牌
@user_view.route('/verify-token', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        print(f"验证令牌请求数据: {data}")
        
        if not data or not data.get('token'):
            response = jsonify({'success': False, 'message': '令牌不能为空'})
            add_cors_headers(response)
            return response, 400
        
        token = data.get('token')
        payload = verify_token(token)
        
        if not payload:
            response = jsonify({'success': False, 'message': '令牌无效或已过期'})
            add_cors_headers(response)
            return response, 401
        
        # 查找用户
        user = user_collection.find_one({'user_id': payload['sub']})
        if not user:
            response = jsonify({'success': False, 'message': '用户不存在'})
            add_cors_headers(response)
            return response, 404
        
        response = jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'username': user['username']
            }
        })
        
        add_cors_headers(response)
        return response, 200
    except Exception as e:
        print(f"验证令牌过程中出错: {str(e)}")
        response = jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        })
        add_cors_headers(response)
        return response, 500

# 获取用户信息
@user_view.route('/profile', methods=['GET'])
def profile():
    try:
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization')
        print(f"获取用户信息请求头: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            response = jsonify({'success': False, 'message': '未提供令牌'})
            add_cors_headers(response)
            return response, 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            response = jsonify({'success': False, 'message': '令牌无效或已过期'})
            add_cors_headers(response)
            return response, 401
        
        # 查找用户
        user = user_collection.find_one({'user_id': payload['sub']})
        if not user:
            response = jsonify({'success': False, 'message': '用户不存在'})
            add_cors_headers(response)
            return response, 404
        
        response = jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'created_at': user['created_at']
            }
        })
        
        add_cors_headers(response)
        return response, 200
    except Exception as e:
        print(f"获取用户信息过程中出错: {str(e)}")
        response = jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        })
        add_cors_headers(response)
        return response, 500
