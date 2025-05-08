import datetime
import sys
import threading
from abc import abstractmethod, ABC
from utils.MongoManager import ScriptData, TaskChain
from utils.CacheFile import FileCacheManager
from utils.CacheManager import CacheManager, LRUCache, TaskChainCache, ThreadLocalManager
from utils.base import import_attribute

task_cache = CacheManager().get_cache("taskCache", default_cls=TaskChainCache, capacity=500)
task_info = threading.local()
task_info.task_id = None


# 责任链模式
class TaskHandler(ABC):
    """
    责任链模式抽象基类
    """

    def __init__(self, next_handler=None):
        self.next_handler = next_handler
        self.script_data = ScriptData()
        self.script_cache = FileCacheManager()
        self.param_cache = CacheManager().get_cache("paramCache", default_cls=LRUCache, capacity=500)
        self.request_id = ThreadLocalManager().get('request_id')

    @abstractmethod
    def handle(self, tasks):
        pass


class InputValidator(TaskHandler):
    """
    主要负责第一个脚本的输入参数校验
    """

    @classmethod
    def set_json_data(cls, json_data):
        cls.json_data = json_data

    def handle(self, tasks):
        """
        判断第一个任务的输入参数是否合法
        """
        try:
            self.thread_id = threading.current_thread().ident
            with ThreadLocalManager():
                ThreadLocalManager.set('task_id', 0)
                ThreadLocalManager.set('status', 'pending')
                begin_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                if task_cache.__contains__(self.thread_id):
                    ThreadLocalManager.add_task_cache('task_chain_url', ThreadLocalManager.get('task_chain_url'),
                                                      self.thread_id)
                    ThreadLocalManager.add_task_cache('task_count', tasks.__len__(), self.thread_id)
                    ThreadLocalManager.add_task_cache('begin_time', begin_time, self.thread_id)
                    ThreadLocalManager.add_task_cache('request_id', self.request_id, self.thread_id)
                    ThreadLocalManager.add_task_cache('task_id', 0, self.thread_id)
                    ThreadLocalManager.add_task_cache("status", "pending", self.thread_id)
                    ThreadLocalManager.add_task_cache('input_params', self.json_data, self.thread_id)
            task_cache.task_start(self.thread_id)
            # 先获取第一个要执行的脚本是谁
            path = self.script_cache.find_cache_script(tasks[0])
            res = self.script_data.get_param_info(tasks[0], path)
            if not path:
                content = res["script_content"]
                path = self.script_cache.add_cache_script(tasks[0], content)
            input_params = res["input"]
            # 获取用户给的 json， 然后根据脚本的输入参数, 和用户给的 json 进行比对
            first_input = self.script_data.compare_param_check_value(self.json_data, input_params)
            # 如果正确， 把所有的input、output 存入缓存
            # self.param_cache.put(tasks[0], first_input)
            self.param_cache.put("task0", first_input)  # task0表示 第一个任务的输入
        except Exception as e:
            print(e, file=sys.stderr)
            raise Exception(f"输入参数不合法{e}")

        if self.next_handler:
            self.next_handler.handle(tasks)


def validate_params(input_params, output_params, task_id):
    """
    比对输入参数和输出参数
    :param input_params: 输入参数
    :param output_params: 输出参数
    :param task_id: 任务id
    :return: 匹配不成功就抛出异常
    """
    for param in input_params:
        if param["default"] == "" or param["default"] is None:
            found_in_output = False
            for output_param in output_params:
                if param["name"] == output_param["name"]:
                    found_in_output = True
                    if param["type"] != output_param["type"] and param["type"] != 'Any':
                        raise Exception(
                            f"任务 {task_id} 的输出参数 '{param['name']}'与任务{task_id + 1}的输入类型不一致。"
                            f" 期望类型: {param['type']}，实际类型: {output_param['type']}。"
                            f" 请检查任务 {task_id} 的输出参数类型是否正确。")
                    break
            if not found_in_output:
                print(f"任务 {task_id + 1} 缺少输入参数 '{param['name']}'", file=sys.stderr)
                raise Exception(
                    f"任务 {task_id + 1} 缺少输入参数 '{param['name']}'。"
                    f" 请确保任务 {task_id + 1} 的输入参数在前一个任务的输出参数中存在。")


class ChainValidator(TaskHandler):
    """
    判断能否成链
    """

    def handle(self, tasks):
        """
        判断是否能成链
        """

        # 先比对input的参数够不够用
        for i in range(len(tasks) - 1):
            path = self.script_cache.find_cache_script(tasks[i])
            next_path = self.script_cache.find_cache_script(tasks[i + 1])
            input_params = self.script_data.get_param_info(tasks[i + 1], next_path)["input"]
            output_params = self.script_data.get_param_info(tasks[i], path)["output"]
            validate_params(input_params, output_params, i + 1)

        if self.next_handler:
            self.next_handler.handle(tasks)


class TaskExecutor(TaskHandler):
    """
    责任：执行任务链
    """

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        self.tasks_chain_url = None
        self.stop = False
        self.done_task = []

    def handle(self, tasks):
        """
        执行任务链, 从第一个开始，依次执行脚本
        """
        try:
            self.thread_id = threading.current_thread().ident
            params = self.param_cache.get("task0")
            moduleCache = CacheManager().get_cache("moduleCache", default_cls=LRUCache, capacity=150)
            for i in range(len(tasks)):
                self.check_cache(tasks[i])
                if self.stop is True:
                    with ThreadLocalManager():
                        ThreadLocalManager.add_task_cache('is_stop', 'stop', self.thread_id)
                        print(f'任务链中止执行')
                        ThreadLocalManager.set('status', 'cancel')
                        return
                if not moduleCache.__contains__(tasks[i]):
                    moduleCache.put(tasks[i], import_attribute(tasks[i]))
                try:
                    ThreadLocalManager.add_task_cache('task_status', "process", self.thread_id)
                    begin_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    try:
                        out_params = moduleCache.get(tasks[i]).main(**params)
                    except Exception as e:
                        ThreadLocalManager.add_task_cache('task_status', "error", self.thread_id)
                        raise Exception(f"执行脚本时出错: {str(e)}")
                    ThreadLocalManager.add_task_cache('task_status', "finish", self.thread_id)
                    self.done_task.append(f'任务{i + 1}已执行完')
                    with ThreadLocalManager():
                        ThreadLocalManager.set('task_id', i + 1)
                        print(f'任务{ThreadLocalManager.local.task_id}的结果是{out_params}')
                        if task_cache.__contains__(self.thread_id):
                            ThreadLocalManager.add_task_cache('begin_time', begin_time, self.thread_id)
                            ThreadLocalManager.add_task_cache('request_id', self.request_id, self.thread_id)
                            ThreadLocalManager.add_task_cache('end_time',
                                                              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                                              self.thread_id)
                            ThreadLocalManager.add_task_cache('task_url', tasks[i], self.thread_id)
                            ThreadLocalManager.add_task_cache('task_id', i + 1, self.thread_id)
                            ThreadLocalManager.add_task_cache('out_params', out_params, self.thread_id)
                            ThreadLocalManager.add_task_cache('status', "pending", self.thread_id)
                    self.param_cache.put(f"task{i + 1}", out_params)  # taski表示 第i个任务的输出
                except Exception as e:
                    raise Exception(f"执行脚本时出错: {str(e)}")
                if i == len(tasks) - 1:
                    break
                path = self.script_cache.find_cache_script(tasks[i + 1])
                input_params = self.script_data.get_param_info(tasks[i + 1], path)["input"]
                params = self.script_data.compare_param_check_value(out_params, input_params)
            task_chain = TaskChain()
            if not task_chain.collection.find_one({"task_chain_url": self.tasks_chain_url}):
                task_chain.add_task_chain(self.tasks_chain_url, tasks)
        except Exception as e:
            print(e, file=sys.stderr)
            raise Exception(f"执行脚本时出错: {str(e)}")
        if self.next_handler:
            self.next_handler.handle(tasks)

    def check_cache(self, url):
        """
        如果本地没有缓存，就下载一个
        """
        if not self.script_data.find_script_url(url):
            print(f"脚本 {url} 不存在")
            raise Exception(f"脚本 {url} 不存在")
        path = self.script_cache.find_cache_script(url)
        res = self.script_data.get_param_info(url, path)
        if not path:
            content = res["script_content"]
            path = self.script_cache.add_cache_script(url, content)
        return res


class TaskChainManager:
    """
    任务链管理类
    """

    def __init__(self):
        self.tasks_chain_url = None
        self.tasks = []
        self.input_validator = InputValidator()
        self.chain_validator = ChainValidator()
        self.task_executor = TaskExecutor()
        self.handlers = self.input_validator
        self.input_validator.next_handler = self.chain_validator
        self.chain_validator.next_handler = self.task_executor
        self.skip_chain_validator = False  # 是否跳过责任链验证
        self.skip_task_execute = False  # 是否跳过任务执行

    def add_task(self, task_url):
        self.tasks.append(task_url)

    def get_tasks_url(self, tasks_url):
        """
        设置任务链url
        :param tasks_url: 任务链url
        """
        self.tasks_chain_url = tasks_url
        self.task_executor.tasks_chain_url = tasks_url

    def validate_and_execute_chain(self):
        """
        验证任务链,并执行任务链
        """
        if self.skip_chain_validator:
            self.input_validator.next_handler = self.task_executor
        if self.skip_task_execute:
            self.chain_validator.next_handler = None
        if self.handlers:
            self.handlers.handle(self.tasks)

    def set_handlers(self, handlers):
        self.handlers = handlers

    def set_skip_chain_validator(self, skip):
        """
        如果是复用的任务链，就跳过成链判断
        """
        self.skip_chain_validator = skip

    def set_skip_task_execute(self, skip):
        """
        设置任务链时，做成链判断，但是不执行
        """
        self.skip_task_execute = skip


if __name__ == '__main__':
    # 创建任务链管理器并设置处理者链

    task_chain_manager = TaskChainManager()
    task_chain_manager.add_task("test")
    task_chain_manager.add_task("test1")

    # task_chain_manager.set_handlers(input_validator)
    task_chain_manager.validate_and_execute_chain()
