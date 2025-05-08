import subprocess
import os
import sys
import time

from flask import Blueprint, request, jsonify

package_view = Blueprint('package_view', __name__)


@package_view.route('/package_list', methods=['GET'])
def get_package_list():
    """获取已安装的包的列表"""
    try:
        file_name = str(time.time()) + 'packages.txt'
        with open(file_name, 'w') as f:
            subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=freeze'], stdout=f)
        with open(file_name, 'r') as f:
            packages = f.readlines()  # 逐行读取文件内容
        os.remove(file_name)

        package_list = []
        for package in packages:
            if '==' in package:
                name, version = package.strip().split('==')
                package_list.append({"package_name": name, "version": version})

        return jsonify({'status': True, 'message': '获取列表成功', 'package_list': package_list})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@package_view.route('/install', methods=['POST'])
def install_package():
    """安装包 更新包"""
    data = request.get_json()
    package_name = data.get('package_name', None)
    package_version = data.get('package_version', None)
    output_message = ""
    try:
        if package_version is None or package_version == '':
            command = f"{sys.executable} -m pip install {package_name}"
        else:
            command = f"{sys.executable} -m pip install {package_name}=={package_version}"

        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            output_message += f"Error: {result.stderr}\n"
            return jsonify({'status': False, 'message': '安装包失败', 'output_message': output_message})
        else:
            return jsonify({'status': True, 'message': '安装包成功'})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@package_view.route('/uninstall', methods=['POST'])
def uninstall_package():
    """卸载包"""
    data = request.get_json()
    package_name = data.get('package_name', None)
    output_message = ""
    try:
        command = f"{sys.executable} -m pip uninstall -y {package_name}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            output_message += f"Error: {result.stderr}\n"
            return jsonify({'status': False, 'message': '卸载包失败', 'output_message': output_message})
        else:
            return jsonify({'status': True, 'message': '卸载包成功'})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


