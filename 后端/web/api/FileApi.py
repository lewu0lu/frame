import os
import time

from flask import Blueprint, request, jsonify
from utils.MongoManager import UrlFileManager

file_view = Blueprint('file_view', __name__)


@file_view.post('/find')
def find_file():
    """判断文件是否存在并返回一个路径"""
    data = request.get_json()
    MD5 = data.get('file_md5', None)
    file_name = data.get('file_name', None)
    url_file = UrlFileManager()
    res = url_file.match_file_md5(MD5)
    if res:
        return jsonify({"status": False, "message": "文件已存在", "url": res['url']})
    (folder_name, suffix) = os.path.splitext(file_name)
    type_name = suffix.replace('.', '')
    file_path = f'{type_name}/{folder_name}/'
    return jsonify({'file_path': file_path})


@file_view.post('/upload')
def file_upload():
    """将上传文件的信息入库"""
    data = request.get_json()
    folder_name = data['folder_name']
    file_name = data['file_name']
    file_download_url = data['file_url']
    file_md5 = data['file_md5']
    upload_time = time.time()
    url_file = UrlFileManager()
    try:
        res = url_file.add_file(folder_name, file_name, file_download_url, file_md5, upload_time)
        if res:
            return jsonify({"status": True, "message": "上传成功"})
        else:
            return jsonify({"status": False, "message": "上传失败"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@file_view.get('/file_list')
def get_file_list():
    """获取文件列表"""
    url_file = UrlFileManager()
    try:
        folder_names_with_time = url_file.get_all_file()
        return jsonify({"status": True, "message": "成功", "list_info": folder_names_with_time})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@file_view.post('/file_version')
def get_file_version():
    """获取文件版本信息"""
    data = request.get_json()
    folder_name = data.get('file_name', None)
    if not folder_name:
        return jsonify({"status": False, "message": "文件名不能为空"})
    try:
        version_info_list = UrlFileManager().get_all_version(folder_name)
        return jsonify({"status": True, "message": "获取版本信息成功", "version_info": version_info_list})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
