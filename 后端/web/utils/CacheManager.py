import sys
import time
import threading
from collections import OrderedDict
from utils.base import Singleton
from utils.MongoManager import LogMsg


class CacheObject:
    """缓存类基类"""

    def __init__(self, **kwargs):
        self._lock = threading.Lock()

    def lock(self):
        return self._lock

    def get(self, key):
        raise NotImplementedError

    def put(self, key, value=None):
        raise NotImplementedError

    def pop(self, key):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError


class LRUCache(CacheObject):
    def __init__(self, capacity=100, **kwargs):
        super().__init__(capacity=100, **kwargs)
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key, ret=None):
        with self.lock():
            if key not in self.cache:
                return ret
            return self.cache.get(key)

    def put(self, key, value=None):
        """可以不传value"""
        with self.lock():
            self.cache[key] = value

            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def pop(self, key):
        with self.lock():
            return self.cache.pop(key)

    def __contains__(self, key):
        if key in self.cache:
            return True
        return False


class TimeLimitLRUCache(CacheObject):
    def __init__(self, capacity=100, time_limit=600, **kwargs):
        super().__init__(capacity=100, time_limit=600, **kwargs)
        self.capacity = capacity
        self.time_limit = time_limit
        self.cache = OrderedDict()

    def get(self, key, ret=None):
        with self.lock():
            if key not in self.cache or self.is_expired(key):
                self.cache.pop(key, ret)
                return ret
            return self.cache.get(key)

    def put(self, key, value=None):
        """可以不传value"""
        with self.lock():
            # 删除旧值，更新顺序
            if key in self.cache:
                self.cache.pop(key)
            self.cache[key] = (value, time.time())

            if len(self.cache) > self.capacity:
                self.__pop_old()

    def pop(self, key):
        with self.lock():
            return self.cache.pop(key)

    def __contains__(self, key):
        if key in self.cache and not self.is_expired(key):
            return True
        return False

    def is_expired(self, key):
        _, timestamp = self.cache.get(key, (None, 0))
        return time.time() - timestamp > self.time_limit

    def __pop_old(self):
        self.cache.popitem(last=False)  # 移除最旧的元素


class TaskChainCache(CacheObject):
    """
    任务链缓存类
    缓存任务链的信息，用于后续的日志记录和数据库插入
    """

    def __init__(self, capacity=100, **kwargs):
        super().__init__(capacity=100, **kwargs)
        self.cache = {}
        self.task_log_info = LogMsg()

    def get_and_insert_data(self, thread_id):
        """
        将缓存中的信息根据thread_id提取出来,添加到数据库
        """
        # 有几条写几条，先都不删，等到任务结束，再清理
        if self.cache[thread_id] == {}:
            return
        # 先查出来request_id 和 task_id ，然后有什么写什么，
        try:
            for task_id in self.cache[thread_id]:
                task_data = self.cache[thread_id].get(task_id, {})
                request_id = task_data.get('request_id')
                begin_time = task_data.get('begin_time')
                end_time = task_data.get('end_time')
                out_params = task_data.get('out_params')
                log_msg = task_data.get('log_msg')
                input_params = task_data.get('input_params')
                is_stop = task_data.get('is_stop')  # 标记任务是否中止，哪里中止在哪里记录
                status = task_data.get('status')  # 在任务链中记录任务链状态
                task_count = task_data.get('task_count')
                task_chain_url = task_data.get('task_chain_url')
                task_url = task_data.get('task_url')
                self.task_log_info.insert_info(task_id, request_id, begin_time, end_time, out_params, log_msg, task_url,
                                               status, input_params, is_stop, task_count, task_chain_url)
        except Exception as e:
            raise Exception(f"插入数据库失败{e}")

    def task_start(self, thread_id):
        """
        任务开始 将现有缓存写入数据库
        """
        try:
            self.get_and_insert_data(thread_id)
        except Exception as e:
            raise Exception(f"插入数据库失败{e}")

    def task_end(self, thread_id):
        """
        任务结束 将缓存内容全部写入数据库，然后清理缓存
        """
        try:
            self.get_and_insert_data(thread_id)
            dict.pop(self.cache, thread_id)
        except Exception as e:
            raise Exception(f"插入数据库失败{e}")

    def check_and_insert(self, thread_id, task_id):
        """
        检查任务的日志条数，每增加三条，就插入一次数据库
        """
        if len(self.cache[thread_id][task_id].get('log_msg', {})) % 3 == 0:
            self.get_and_insert_data(thread_id)

    def get(self, key):
        with self.lock():
            if key in self.cache:
                return self.cache[key]
            return None

    def put(self, key, value=None):
        """
        向cache[key]中放入value
        """
        with self.lock():
            self.cache[key] = value

    def put_info(self, thread_id, task_id, info_name, info_value=None):
        """
        向cache[key][task_id]中放入{info_name:info_value}
        每次放了一条日志，都要调用check_and_insert
        """
        with self.lock():
            if thread_id not in self.cache:
                self.cache[thread_id] = {}
            if task_id not in self.cache[thread_id]:
                self.cache[thread_id][task_id] = {}
            if info_name == 'log_msg':
                # 追加到列表中
                if 'log_msg' not in self.cache[thread_id][task_id]:
                    self.cache[thread_id][task_id]['log_msg'] = []
                self.cache[thread_id][task_id][info_name].append(info_value)
            else:
                self.cache[thread_id][task_id][info_name] = info_value
            self.check_and_insert(thread_id, task_id)

    def pop(self, key):
        with self.lock():
            if key in self.cache:
                return self.cache.pop(key)
            return None

    def __contains__(self, key):
        with self.lock():
            return key in self.cache


class CacheManager(metaclass=Singleton):
    cache = {}
    lock = threading.Lock()

    @classmethod
    def get_cache(cls, name, default_cls=None, **kwargs):
        """
        获取缓存对象 根据名字获得的对象是唯一的
        :param name: 缓存名
        :param default_cls: 缓存类
        :param kwargs: 其他参数
        :return: 缓存对象
        """
        if default_cls is None:
            default_cls = TimeLimitLRUCache
        with cls.lock:
            if name not in cls.cache:
                cls.cache[name] = default_cls(**kwargs)
            elif not isinstance(cls.cache[name], default_cls):
                print(
                    f"同名cache类型错误：request({default_cls}),found({type(cls.cache[name])})",
                    file=sys.stderr,
                )
            return cls.cache[name]

    @classmethod
    def clear_cache(cls, name):
        with cls.lock:
            if name in cls.cache:
                del cls.cache[name]


class ThreadLocalManager:
    """
    管理线程变量threading.local
    """
    local = threading.local()
    task_cache = CacheManager().get_cache("taskCache", default_cls=TaskChainCache, capacity=500)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            for attr_name in dir(self.local):
                if not attr_name.startswith('_') and attr_name not in ['task_id', 'request_id', 'task_cache',
                                                                       'task_chain_url', 'status']:
                    delattr(self.local, attr_name)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def set(cls, name, value):
        setattr(cls.local, name, value)

    @classmethod
    def get(cls, name):
        if not hasattr(cls.local, name):
            setattr(cls.local, name, None)
        return getattr(cls.local, name)

    @classmethod
    def add_task_cache(cls, name, value, thread_id):
        task_id = cls.get('task_id')
        cls.set(name, value)
        cls.task_cache.put_info(thread_id, task_id, name, cls.get(name))


if __name__ == "__main__":
    manager = CacheManager()
    moduleCache = manager.get_cache("moduleCache", default_cls=LRUCache, capacity=150)
