import datetime
import os
import sys
import subprocess
import uuid

from flask import Blueprint, request, jsonify
from utils.TaskChain import InputValidator, TaskChainManager
from utils.base import *
from utils.MongoManager import ScriptData, TaskChain
from utils.CacheFile import FileCacheManager
from utils.CacheManager import CacheManager, LRUCache, TaskChainCache, ThreadLocalManager

# 蓝图
app_orders = Blueprint('app_orders', __name__, template_folder='templates')


# 执行脚本
@app_orders.route('/script/<path:script_url>', methods=['GET', 'POST'])
def run_script(script_url):
    """执行脚本"""
    data = request.get_json()
    try:
        script_data = ScriptData()
        script_cache = FileCacheManager()
        if not script_data.find_script_url(script_url):
            return f"<h1>没有您要执行的脚本<h1>"
        # 获取本地缓存
        path = script_cache.find_cache_script(script_url)
        res = script_data.get_param_info(script_url, path)
        if not path:
            # 如果本地没有 就下载脚本到本地 ，input为最新版的
            content = res["script_content"]
            path = script_cache.add_cache_script(script_url, content)
        else:
            path = path + "/temp.py"
        input_info = res["input"]
        isAlone = res["isAlone"]
        # 看isAlone 能否单独执行
        if not isAlone:
            return f"<h1>该脚本无法单独执行</h1>"
        # 先看有没有main()，没有就直接命令行 ，有的话再从数据库取值，比对参数
        print(f'path:{path + "/temp.py"}')
        with open(path, "r") as file:
            has_main = extract_main_function_parameters(file)
            if not has_main:
                # todo 直接获取用户输入的命令，运行命令
                # cmd = f'python {path} {args}'
                # res = subprocess_run(cmd)
                # if res.stderr:
                #     return f"<h1>执行失败</h1><p>{res.stderr}</p>"
                return f"<h1>执行成功</h1>"
        # 比较参数对不对
        params = script_data.compare_param_check_value(data, input_info)
        # 查看 import缓存中是否有 没有的话要导入模块
        moduleCache = CacheManager.get_cache("moduleCache", default_cls=LRUCache, capacity=150)
        if not moduleCache.__contains__(script_url):
            moduleCache.put(script_url, import_attribute(script_url))
            result = moduleCache.get(script_url).main(**params)
            return f"<h1>执行成功{result}</h1>"
    except Exception as e:
        return f"执行脚本时出错: {str(e)}"
    return f"<h1>执行出错</h1>"


# 执行任务链
@app_orders.route('/task_chain/<path:task_chain_url>', methods=['POST'])
def run_task_chain(task_chain_url):
    """执行任务链"""
    if task_chain_url is None:
        return f"<h1>任务链不存在</h1>"
    task_cache = CacheManager().get_cache("taskCache", default_cls=TaskChainCache, capacity=500)
    try:
        data = request.get_json()
        InputValidator.set_json_data(data)
        thread_id = threading.current_thread().ident
        task_cache.put(thread_id, {})  # 以线程ID为键 弄一个缓存
        task_chain_db = TaskChain()
        if not task_chain_db.collection.find_one({"task_chain_url": task_chain_url}):
            return f"<h1>任务链{task_chain_url}不存在</h1>"
        ThreadLocalManager().set('request_id', str(uuid.uuid4()))
        ThreadLocalManager().set('task_chain_url', task_chain_url)
        task_chain_manager = TaskChainManager()  # 每个线程一个 这个和线程是对应的
        # 缓存记录任务链和当前处理器
        executors = CacheManager().get_cache("executors", default_cls=LRUCache, capacity=100)
        executors.put(ThreadLocalManager().get('request_id'), task_chain_manager.task_executor)
        task_chain_manager.get_tasks_url(task_chain_url)
        tasks = task_chain_db.get_tasks(task_chain_url)
        print(f"任务链{task_chain_url}的任务有{tasks}")
        script_data_db = ScriptData()
        for task in tasks:
            if not script_data_db.find_script_url(task):
                return jsonify({"status": False, "message": f"任务链中的任务{task}不存在"})
            task_chain_manager.add_task(task)
        task_chain_manager.set_skip_chain_validator(True)
        task_chain_manager.validate_and_execute_chain()
        with ThreadLocalManager():
            ThreadLocalManager.local.task_id = 0
            ThreadLocalManager.add_task_cache('end_time',
                                              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                              thread_id)
            if ThreadLocalManager.get('status') == 'cancel':
                ThreadLocalManager.add_task_cache('status', 'cancel', thread_id)
            else:
                ThreadLocalManager.add_task_cache('status', 'success', thread_id)
            task_cache.task_end(thread_id)
            ThreadLocalManager.local.task_id = None  # 标记不再缓存日志
        if executors.__contains__(ThreadLocalManager().get('request_id')):
            executors.put(ThreadLocalManager().get('request_id'), 1)
    except Exception as e:
        with ThreadLocalManager():
            ThreadLocalManager.local.task_id = 0
            ThreadLocalManager.add_task_cache('end_time',
                                              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                              threading.current_thread().ident)
            ThreadLocalManager.add_task_cache('status', 'error', threading.current_thread().ident)
            ThreadLocalManager.local.task_id = None  # 标记不再缓存日志
        print(e, file=sys.stderr)
        task_cache.task_end(threading.current_thread().ident)
        return f'<h1>执行任务链失败{e}</h1>'
    return f"<h1>执行任务链成功</h1>"


if __name__ == '__main__':
    print("开始")
    module = import_attribute("test")
    script_params = {
        "name": "John",
        "score": 100,
        "age": 20
    }
    module.main(**script_params)
