import json
import time
import os, hashlib
import chardet
from bson import ObjectId
from pymongo import MongoClient, errors, DESCENDING
from config import config, MONGO_CONFIG
from utils.base import Singleton


class MongoDBManager(metaclass=Singleton):
    """目前只需要连接一个库，直接写死配置，后续优化"""

    def __init__(
            self,
            max_connections=10,
    ):
        self.max_connections = max_connections
        self.__client = None
        self.__mongo_data_init()
        self.__connect()

    def __mongo_data_init(self):
        """mongo连接数据初始化"""
        self.host = config.get("mongo", "HOST")
        self.port = config.getint("mongo", "PORT")
        self.database = config.get("mongo", "DATABASE")
        self.auth = config.get("mongo", "AUTH")
        self.password = config.get("mongo", "PASSWORD")

    def __connect(self):
        """连接mongo"""
        try:
            self.__client = MongoClient(
                self.host,
                self.port,
                username=self.auth,
                password=self.password,
                authSource=self.database,
                maxconnecting=self.max_connections,
            )
            # self.db = self.client[self.database]
        except errors.ConnectionFailure as e:
            print(f"Error connecting to MongoDB: {e}")

    def close(self):
        """关闭mongo连接"""
        if self.__client:
            self.__client.close()

    def get_db(self, db_name=None):
        """
        获取指定库的数据库对象
        :param db_name: 库名
        :return: 数据库对象
        """
        if self.__client is None:
            self.__connect()
        if db_name is None:
            return self.__client[self.database]
        return self.__client[db_name]

    @property
    def client(self):
        return self.__client


class DBOperator(metaclass=Singleton):
    """数据库操作类"""
    def __init__(self, collection_config: dict, database_name: str = None):
        self._database_name = database_name
        self.database = None
        self.collection_config = collection_config
        self.__check_collection()

    def __check_collection(self):
        """检查对应的db环境，构建缺少的集合"""
        self.database = MongoDBManager().get_db(self._database_name)
        if self.database is None:
            print(f"无法获取db：{self._database_name}")
            raise ValueError(f"无法获取db：{self._database_name}")

        # 创建带有验证器的集合
        for name, cconf in self.collection_config.items():
            # todo 变更集合格式优化
            if name not in self.database.list_collection_names():
                temp_collection = self.database.create_collection(
                    name, validator=cconf.get("validator", {})
                )
                temp_collection.create_index(cconf.get("index"))
                print(f"{name} collection created")

    def get_all_collections(self):
        return self.database.list_collection_names()

    def get_collection(self, collection_name):
        return self.database[collection_name]


class CollectionOperator:
    """集合操作基类"""
    target_collection = None

    def __init__(self, database_name: str = None):
        self._database_name = database_name
        self._db_op = DBOperator(
            MONGO_CONFIG.get("collection_configs"), self._database_name
        )
        self.collection = self._db_op.get_collection(self.target_collection)


class UrlFileManager(CollectionOperator):
    """文件url管理集合操作类"""
    target_collection = "file_url"

    def match_file_md5(self, file_md5):
        """
        判断文件是否存在
        :param file_md5: 文件MD5
        :return: 文件信息
        """
        return self.collection.find_one({"MD5": file_md5})

    def add_file(self, folder_name, file_name, file_download_url, file_md5, upload_time):
        """
        添加文件到数据库
        :param folder_name: 文件名（同一个文件名字一样）
        :param file_name: 文件名（唯一标识一个文件）
        :param file_download_url: 文件下载地址
        :param file_md5: 文件MD5
        :return: 是否成功
        """
        if self.collection.insert_one({
            "folder_name": folder_name,
            "file_name": file_name,
            "file_download_url": file_download_url,
            "upload_time": upload_time,
            "md5": file_md5
        }):
            return True
        else:
            return False

    def get_all_file(self):
        """
        获取不重复的文件名和上传时间作文件列表
        """
        pipeline = [
            {"$group": {
                "_id": "$folder_name",
                "upload_time": {"$first": "$upload_time"}
            }},
            {"$limit": 20}
        ]
        result = self.collection.aggregate(pipeline)
        return [{"file_name": doc['_id'], "upload_time": doc['upload_time']} for doc in result]

    def get_all_version(self, folder_name):
        """
        获取文件的所有版本信息
        """
        return list(self.collection.find({"folder_name": folder_name}, {"_id": 0}))


def calculate_md5(file):
    """
    计算文件的md5值
    :param file: 文件对象
    :return: 文件md5值
    """
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        hash_md5.update(chunk)
    file.seek(0)
    return hash_md5.hexdigest()


class ScriptData(CollectionOperator):
    """脚本数据管理集合操作类"""
    target_collection = "script_data"

    def find_script_md5(self, script_md5):
        """
        查找是否已经存在这个脚本
        :param script_md5: 脚本md5
        :return: 是否存在这个脚本md5值
        """
        res = self.collection.find_one({"md5": script_md5})
        return res

    def find_script_url(self, url):
        """
        查找是否已经存在这个脚本url
        """
        result = self.collection.find_one({"url": url})
        return result

    def get_different_script_url(self):
        """
        获取都有哪些脚本文件，返回它们的url列表
        """
        return self.collection.distinct("url")

    def add_script_data(self, url, script_description, script_md5, content, is_alone, input_data, output_data):
        """
        添加脚本数据
        脚本编码格式不知道，不管什么格式都转成字符串放到库里，要存到文件里时记得转成utf-8
        """
        content.seek(0)
        tmp_file = content.read()
        encode = chardet.detect(tmp_file)['encoding']
        if encode is None:
            raise Exception("脚本未知编码格式")
        print(encode)
        script_content = tmp_file.decode(encode)  # 存的是字符串
        upload_time = str(time.time())
        result = self.collection.insert_one(
            {"url": url,
             "description": script_description,
             "md5": script_md5,
             "script_content": script_content,
             "isAlone": is_alone,
             "input": input_data,
             "output": output_data,
             "upload_time": upload_time
             })
        return result

    def get_script_data(self, url, version):
        res = self.collection.find_one({"url": url, "_id": ObjectId(version)})
        return res

    def get_version_info(self, url):
        """
        返回这个url下脚本的所有版本的信息
        :param url: 脚本url
        :return: 脚本信息列表
        """
        res = self.collection.find({"url": url}).sort([("_id", 1)])
        info = []
        for x in res:
            version_info = {
                "url": x["url"],
                "description": x["description"],
                "upload_time": x["upload_time"],
                "is_alone": x["isAlone"],
                "input": x["input"],
                "output":x["output"],
                "version": str(x["_id"]),
            }
            info.append(version_info)
        return info

    def get_latest_version(self, url):
        """ 获得最新的版本号 """
        rows = self.collection.find({"url": url}).sort('_id', -1)
        return next(rows)

    def get_param_info(self, script_url, path):
        """
        获得脚本input信息
        :param script_url:脚本url
        :param path:脚本缓存路径
        :return:数据库中对应input信息
        """
        if not path:
            version = self.get_latest_version(script_url)['_id']
            res = self.get_script_data(script_url, version)
        else:
            temp_file_path = os.path.join(path, "temp.py")
            with open(temp_file_path, "rb", ) as f:
                md5 = calculate_md5(f)
            res = self.find_script_md5(md5)
            if not res:
                raise Exception(f"文件缓存被修改过")
        return res

    def compare_param_check_value(self, param_info, default_input_info):
        """
        比较参数
        :param param_info: 输入的参数信息
        :param default_input_info: 默认的参数信息
        :return: 实际要传的参数信息
        """
        params = {}
        for info_item in default_input_info:
            # 如果给了这个参数
            if info_item["name"] in param_info:
                # 也给了值
                if param_info[info_item["name"]] != None:
                    if type(param_info[info_item["name"]]).__name__ != info_item["type"] and info_item["type"] != 'Any':
                        # 值的类型不对报错
                        raise Exception(
                            f"变量 {info_item['name']} 的类型错误，期望 {info_item['type']}，实际 {type(param_info[info_item['name']]).__name__}")
                    params.update({info_item['name']: param_info[info_item["name"]]})
                elif info_item["default"] == 'null' or info_item["default"] is None:
                    raise Exception(f"缺少变量 {info_item['name']} ")
                else:
                    if not info_item["default"] == 'NotNone':
                        params.update({info_item['name']: info_item["default"]})
            elif info_item["default"] == 'null' or info_item["default"] is None:
                raise Exception(f"缺少变量 {info_item['name']} ")
            else:
                if not info_item["default"] == 'NotNone':
                    params.update({info_item['name']: info_item["default"]})
        return params


class ScriptVersion(CollectionOperator):
    """脚本版本管理集合操作类"""
    target_collection = "script_version"

    def find_script_version(self, url):
        """
        查找是否已经存在这个脚本
        :param url: 脚本url
        :return: 是否存在这个脚本md5值
        """
        return self.collection.find_one({"url": url})

    def update_version(self, script_data, url, version):
        """
        更新版本信息, 如果设置过版本，就更新版本号，否则就新插入一个
        :param script_data:数据库ScriptData对象
        :param url:脚本url
        :param version: 设置的版本号
        """
        if self.find_script_version(url):
            self.collection.update_one(
                {"url": url},
                {"$set": {"version": ObjectId(version)}}
            )
        else:
            self.collection.insert_one({
                "url": url,
                "version": ObjectId(version)
            })
        return script_data.get_script_data(url, version)

    def cancel_version(self, url):
        return self.collection.delete_many({"url": url})


class TaskChain(CollectionOperator):
    """任务链管理集合操作类"""
    target_collection = "task_chain"

    def add_task_chain(self, task_chain_url, task_list):
        """
        添加任务链
        :param task_chain_url: 任务链url
        :param task_list:任务链列表
        """
        if self.collection.find_one({"task_chain_url": task_chain_url}):
            raise Exception("已有这个URL")
        if len(task_list) <= 1:
            raise Exception("任务链长度不能小于2")
        try:
            self.collection.insert_one({
                "task_chain_url": task_chain_url,
                "task_chain": task_list
            })
        except Exception as e:
            raise Exception(f"添加任务链失败{e}")

    def get_tasks(self, task_chain_url):
        """
        获取任务链中的所有脚本
        :param task_chain_url: 任务链url
        :return: 任务链中的所有脚本
        """
        res = self.collection.find_one({"task_chain_url": task_chain_url})
        if res:
            return res["task_chain"]
        else:
            raise Exception("没有这个任务链")

    def get_urls(self):
        return self.collection.distinct("task_chain_url")


class LogMsg(CollectionOperator):
    """日志管理集合操作类"""
    target_collection = "task_log_info"

    def insert_info(self, task_id, request_id, begin_time, end_time, out_params, log_msg, task_url=None,
                    status="pending", input_params=None, is_stop=None, task_count=None, task_chain_url=None):
        """
        插入日志信息
        """
        if request_id is None or task_id is None:
            return
        try:
            if task_id == 0:
                self.collection.update_one(
                    {"request_id": request_id, "task_id": task_id},
                    {"$set": {"task_chain_url": task_chain_url,
                              "status": status,
                              "begin_time": begin_time,
                              "end_time": end_time,
                              "log_msg": log_msg,
                              "input_params": input_params,
                              "task_count": task_count}}, True)
            elif is_stop:
                self.collection.update_one(
                    {"request_id": request_id, "task_id": task_id},
                    {"$set": {"begin_time": begin_time,
                              "end_time": end_time,
                              "out_params": out_params,
                              "log_msg": log_msg,
                              "task_url": task_url,
                              "is_stop": is_stop}}, True)
            else:
                self.collection.update_one(
                    {"request_id": request_id, "task_id": task_id},
                    {"$set": {"task_url": task_url,
                              "begin_time": begin_time,
                              "end_time": end_time,
                              "out_params": out_params,
                              "log_msg": log_msg, }}, True)
        except Exception as e:
            raise Exception(f"插入日志失败{e}")


if __name__ == "__main__":
    from config import MONGO_CONFIG

    script_data = ScriptData()
    file_path = os.path.join(os.path.dirname(os.getcwd()), 'templates', 'testjson.json')
    with open(file_path, 'r') as f:
        data = json.load(f)
    res = input_info = script_data.find_script_md5("51959f6bd78fa299a999f511d07e0fb4")
    script_data.compare_param_check_value(data, res["input"])
