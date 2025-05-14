import os
import importlib
from flask import Blueprint, jsonify, request
from utils.MongoManager import ScriptData, ScriptVersion
from utils.base import *
from utils.CacheFile import FileCacheManager
from utils.CacheManager import CacheManager, LRUCache

script_view = Blueprint('script_view', __name__)


@script_view.route('/script_tree', methods=['GET'])
def get_script_tree():
    """返回数据库中所有的脚本url"""
    try:
        script_urls = ScriptData().get_different_script_url()
        return jsonify(script_urls)
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@script_view.route('/upload_script', methods=['POST'])
def upload_script():
    """上传脚本"""
    script_url = request.form.get('script_url', None)
    script_description = request.form.get('script_description', None)
    script_content = request.files.get('file', None)
    script_md5 = request.form.get('script_md5', None)
    is_alone = request.form.get('is_alone', None)
    is_alone = is_alone.lower() == 'true' if is_alone is not None else False
    if script_content is None:
        return jsonify({"status": False, "message": "没提交脚本"})
    if script_md5 is None:
        return jsonify({"status": False, "message": "没提交md5"})
    try:
        # 检查url格式，脚本类型
        if script_url is None or not validate_path(script_url):
            return jsonify({"status": False, "message": "url格式错误或未提交,路径中只能包含英文字母，数字以及-_.~"})
        if not script_content.filename.endswith('.py'):
            return jsonify({"status": False, "message": "文件类型错误，只能上传 .py 文件"})

        script_data = ScriptData()
        if script_data.find_script_md5(script_md5):
            return jsonify({"status": False, "message": "上传失败:已有该脚本"})
        # 解析input、output_params
        script_content.seek(0)
        input_params = extract_main_function_parameters(script_content)
        out_params = extract_class_io(script_content)
        script_data.add_script_data(script_url, script_description, script_md5,
                                    script_content, is_alone, input_params, out_params)
        version_manager = ScriptVersion()
        script_cache = FileCacheManager()

        if not version_manager.find_script_version(script_url):
            # 说明要更新脚本缓存到最新版本，将最新版放到路径下
            script_cache.update_cache_script(script_url, script_content)
            # 查看import缓存 如果有，就要重新reload
            moduleCache = CacheManager.get_cache("moduleCache", default_cls=LRUCache, capacity=150)
            if moduleCache.__contains__(script_url):
                module = moduleCache.get(script_url)
                moduleCache.put(script_url, importlib.reload(module))
        return jsonify({"status": True, "message": "上传成功"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@script_view.route('/script_info', methods=['POST'])
def show_script_info():
    """显示脚本当前版本的信息"""
    data = request.get_json()
    script_url = data.get("script_url", None)
    if script_url is None:
        return jsonify({"status": False, "message": "没有提交脚本url"})
    try:
        version_manager = ScriptVersion()
        script_data = ScriptData()
        # 如果设置过版本，将信息返回
        res = version_manager.find_script_version(script_url)
        if res:
            version_data = script_data.find_script_url(script_url)
        # 如没设置过 就返回最新版的信息
        else:
            version_data = script_data.get_latest_version(script_url)
        version_info = {
            "version": str(version_data["_id"]),
            "url": version_data["url"],
            "description": version_data["description"],
            "upload_time": version_data["upload_time"],
            "is_alone": version_data["isAlone"],
            "input": version_data["input"],
            "output": version_data["output"]
        }
        return jsonify({"status": True, "message": "成功", "version_info": version_info})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@script_view.route('/all_version', methods=['POST'])
def show_all_version():
    """显示所有版本"""
    data = request.get_json()
    script_url = data.get('script_url', None)
    if script_url is None:
        return jsonify({"status": False, "message": "没有提交脚本url"})
    try:
        version_info = ScriptData().get_version_info(script_url)
        return jsonify({"status": True, "message": "成功", "version_info": version_info})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@script_view.route('/set_version', methods=['POST'])
def set_version():
    """设置版本"""
    data = request.get_json()
    script_url = data.get('script_url', None)
    version = data.get('version', None)
    if script_url is None:
        return jsonify({"status": False, "message": "没有提交脚本url"})
    if version is None:
        return jsonify({"status": False, "message": "没有选择要设定的版本"})
    try:
        version_manager = ScriptVersion()
        script_data = ScriptData()
        res = version_manager.update_version(script_data, script_url, version)
        if res is None:
            return jsonify({"status": False, "message": "设置失败"})
        update_cache(res["script_content"], script_url)
        return jsonify({"status": True, "message": f"设置成功,当前版本为{str(version)}"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@script_view.route('/cancel_set_version', methods=['POST'])
def cancel_set_version():
    """取消设置版本"""
    data = request.get_json()
    script_url = data.get('script_url', None)
    if script_url is None:
        return jsonify({"status": False, "message": "没有提交脚本url"})
    try:
        version_manager = ScriptVersion()
        version_manager.cancel_version(script_url)
        result = ScriptData().get_latest_version(script_url)
        content = result["script_content"]
        update_cache(content, script_url)
        return jsonify({"status": True, "message": "取消成功,当前版本为最新版"})

    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@script_view.route('/validate_parameters', methods=['POST'])
def validate_parameters():
    """验证脚本参数，尝试进行类型转换"""
    data = request.get_json()
    script_url = data.get('script_url', None)
    parameters = data.get('parameters', {})
    
    if script_url is None:
        return jsonify({"status": False, "message": "没有提交脚本url"})
    
    try:
        # 获取脚本信息
        script_data = ScriptData()
        script_cache = FileCacheManager()
        
        # 检查脚本是否存在
        if not script_data.find_script_url(script_url):
            return jsonify({"status": False, "message": "找不到指定脚本"})
        
        # 获取本地缓存
        path = script_cache.find_cache_script(script_url)
        res = script_data.get_param_info(script_url, path)
        
        # 获取脚本参数信息
        input_info = res["input"]
        
        # 验证参数并尝试转换
        result = script_data.compare_param_check_value(parameters, input_info)
        
        # 返回验证和转换结果
        return jsonify({
            "status": True, 
            "message": "参数验证成功", 
            "params": result["params"],
            "conversions": result["conversions"]
        })
            
    except Exception as e:
        return jsonify({"status": False, "message": f"参数校验失败: {str(e)}"})

@script_view.route('/run_script', methods=['POST'])
def run_script():
    """运行脚本"""
    data = request.get_json()
    script_url = data.get('script_url', None)
    parameters = data.get('parameters', {})
    force_run = data.get('force_run', False)  # 是否强制运行（即使有类型转换）
    
    if script_url is None:
        return jsonify({"status": False, "message": "没有提交脚本url"})
    
    try:
        # 获取脚本信息
        script_data = ScriptData()
        script_cache = FileCacheManager()
        
        # 检查脚本是否存在
        if not script_data.find_script_url(script_url):
            return jsonify({"status": False, "message": "找不到指定脚本"})
        
        # 获取本地缓存
        path = script_cache.find_cache_script(script_url)
        res = script_data.get_param_info(script_url, path)
        
        # 如果本地没有缓存，就下载脚本到本地
        if not path:
            content = res["script_content"]
            path = script_cache.add_cache_script(script_url, content)
        else:
            path = os.path.join(path, "temp.py")
        
        # 获取脚本参数信息和独立执行标志
        input_info = res["input"]
        isAlone = res["isAlone"]
        
        # 检查脚本是否可以独立执行
        if not isAlone:
            return jsonify({"status": False, "message": "该脚本无法单独执行"})
        
        # 检查脚本是否有main函数
        with open(path, "r", encoding='utf-8') as file:
            has_main = extract_main_function_parameters(file)
            if not has_main:
                # 如果没有main函数，可以考虑直接执行脚本（暂不实现）
                return jsonify({"status": True, "message": "脚本执行成功（无main函数）"})
        
        # 验证参数并尝试转换
        validation_result = script_data.compare_param_check_value(parameters, input_info)
        params = validation_result["params"]
        conversions = validation_result["conversions"]
        
        # 如果有参数类型转换且不是强制运行，则返回转换信息但不执行
        if conversions and not force_run:
            return jsonify({
                "status": False,
                "message": "参数需要类型转换，请检查并确认",
                "conversions": conversions,
                "require_confirmation": True
            })
        
        # 从缓存加载或导入模块
        module_cache = CacheManager.get_cache("moduleCache", default_cls=LRUCache, capacity=150)
        
        if not module_cache.__contains__(script_url):
            # 如果缓存中没有模块，则导入
            module = import_attribute(script_url)
            module_cache.put(script_url, module)
        else:
            module = module_cache.get(script_url)
        
        # 执行脚本的main函数
        try:
            if hasattr(module, 'main'):
                result = module.main(**params)
                return jsonify({
                    "status": True, 
                    "message": "脚本执行成功", 
                    "result": result,
                    "conversions": conversions  # 返回转换信息
                })
            else:
                return jsonify({"status": False, "message": "脚本中没有main函数"})
        except Exception as exec_error:
            return jsonify({
                "status": False, 
                "message": f"脚本执行失败: {str(exec_error)}", 
                "error_type": type(exec_error).__name__
            })
            
    except Exception as e:
        error_message = str(e)
        # 检查是否是参数校验相关的错误
        if '参数校验失败' in error_message or '转换类型失败' in error_message or '类型错误' in error_message:
            return jsonify({"status": False, "message": f"参数校验错误: {error_message}"})
        else:
            return jsonify({"status": False, "message": f"运行脚本时出错: {error_message}"})


def update_cache(content, url):
    """
    更新缓存，并reload import缓存
    """
    script_cache = FileCacheManager()
    moduleCache = CacheManager.get_cache("moduleCache", default_cls=LRUCache, capacity=150)
    # 将版本更新为最新版，再看import缓存，reload
    script_file = "script"
    with open(script_file, "w", encoding='utf-8') as f:
        f.write(content)
        if script_cache.update_cache_script(url, script_file):
            if moduleCache.__contains__(url):
                module = moduleCache.get(url)
                moduleCache.put(url, importlib.reload(module))
