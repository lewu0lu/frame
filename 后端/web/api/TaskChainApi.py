import json
import threading

from bson import json_util
from flask import Blueprint, request, jsonify
from utils.CacheManager import CacheManager, TaskChainCache, LRUCache
from utils.TaskChain import ChainValidator
from utils.MongoManager import TaskChain, ScriptData, ScriptVersion,LogMsg

task_chain_view = Blueprint('task_chain_view', __name__)


@task_chain_view.route('/get_task_chain', methods=['GET'])
def get_chain_list():
    """返回数据库中所有的任务链url"""
    try:
        task_chain_db = TaskChain()
        task_chain_urls = task_chain_db.get_urls()
        return jsonify(task_chain_urls)
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@task_chain_view.route('/set_task_chain', methods=['POST'])
def set_task_chain():
    """设置任务链"""
    data = request.get_json()
    task_chain_url = data.get('task_chain_url', None)
    task_list = data.get('task_list', None)  # 一个列表：任务链中的任务url
    if task_list is None:
        return jsonify({"status": False, "message": "任务链为空"})
    try:
        task_cache = CacheManager().get_cache("taskCache", default_cls=TaskChainCache, capacity=500)
        task_cache.put(threading.current_thread().ident, {})  # 以线程ID为键 弄一个缓存
        script_data = ScriptData()
        for task in task_list:
            if not script_data.find_script_url(task):
                return jsonify({"status": False, "message": f"任务链中的任务{task}不存在"})
        chain_validator = ChainValidator()
        chain_validator.handle(task_list)
        # 放到数据库中
        TaskChain().add_task_chain(task_chain_url, task_list)
        return jsonify({"status": True, "message": "设置任务链成功"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@task_chain_view.route('/delete_task_chain', methods=['POST'])
def delete_task_chain():
    """删除任务链"""
    data = request.get_json()
    task_chain_url = data.get('task_chain_url', None)
    try:
        res = TaskChain().collection.find_one({"task_chain_url": task_chain_url})
        if not res:
            return jsonify({"status": False, "message": f"任务链{task_chain_url}不存在"})
        TaskChain().collection.delete_one({"task_chain_url": task_chain_url})
        return jsonify({"status": True, "message": f"删除任务链{task_chain_url}成功"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@task_chain_view.route('/reset_task_chain', methods=['POST'])
def reset_task_chain():
    """重新设置任务链"""
    data = request.get_json()
    task_chain_url = data.get('task_chain_url', None)
    task_list = data.get('task_list', None)
    try:
        res = TaskChain().collection.find_one({"task_chain_url": task_chain_url})
        if not res:
            return jsonify({"status": False, "message": f"任务链{task_chain_url}不存在"})
        # 成链判断
        task_cache = CacheManager().get_cache("taskCache", default_cls=TaskChainCache, capacity=500)
        task_cache.put(threading.current_thread().ident, {})  # 以线程ID为键 弄一个缓存
        script_data = ScriptData()
        for task in task_list:
            if not script_data.find_script_url(task):
                return jsonify({"status": False, "message": f"任务链中的任务{task}不存在"})
        chain_validator = ChainValidator()
        chain_validator.handle(task_list)
        TaskChain().collection.update_one({"task_chain_url": task_chain_url}, {"$set": {"task_chain": task_list}})
        return jsonify({"status": True, "message": f"重新设置任务链{task_chain_url}成功"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@task_chain_view.route('/get_task_info', methods=['POST'])
def get_task_info():
    """获取任务链中所有脚本的信息"""
    data = request.get_json()
    task_chain_url = data.get('task_chain_url', None)
    try:
        # 先查链中有哪些脚本
        task_list = TaskChain().get_tasks(task_chain_url)
        # 再看是否有指定版本
        script_data_db = ScriptData()
        script_version_db = ScriptVersion()
        task_info = []
        for task in task_list:
            res = script_version_db.find_script_version(task)
            if res:
                version = res["version"]
            else:
                # 没有就返回最新版本的信息
                version = script_data_db.get_latest_version(task)['_id']
            task_info.append(script_data_db.collection.find_one({"_id": version, "url": task}))
        return json.loads(json_util.dumps({"status": True, "message": "获取任务信息成功", "task_info": task_info}))
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@task_chain_view.route('/request_list', methods=['GET'])
def get_request_list():
    """获取任务链历史请求"""
    try:
        task_log_info_db = LogMsg()
        result = task_log_info_db.collection.aggregate([
            {"$match": {"task_id": 0}},
            {"$group": {
                "_id": "$request_id",
                "task_chain_url":{"$first": "$task_chain_url"},
                "begin_time": {"$first": "$begin_time"},
                "end_time": {"$first": "$end_time"},
                "task_count":{"$first": "$task_count"}
            }},
            {"$sort": {"begin_time": -1}}
        ])
        return json.loads(json_util.dumps({"status": True, "message": "获取任务链记录成功", "request_list": list(result)}))
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@task_chain_view.route('/get_task_log', methods=['POST'])
def get_task_log():
    """获取任务链中所有任务的日志和信息"""
    data = request.get_json()
    request_id = data.get('request_id', None)
    try:
        task_log_info_db = LogMsg()
        documents = task_log_info_db.collection.find({"request_id": request_id})

        task_info = []
        for doc in documents:
            task_info.append(doc)
        return json.loads(json_util.dumps({"status": True, "message": "获取任务链日志成功", "task_info": task_info}))
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@task_chain_view.route('/stop_task', methods=['POST'])
def stop_task():
    """中止任务链"""
    data = request.get_json()
    request_id = data.get('request_id', None)
    try:
        executors = CacheManager().get_cache("executors", default_cls=LRUCache, capacity=100)
        executor = executors.get(request_id)
        if executor is None:
            return jsonify({"status": False, "message": f"任务链{request_id}不存在"})
        elif executor == 1:
            return jsonify({"status": False, "message": f"任务链{request_id}已执行完毕，无法中止"})
        executor.stop = True
        return jsonify({"status": True, "message": f"设置成功"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})