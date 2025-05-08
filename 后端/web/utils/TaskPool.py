import logging
import sched
import threading
import uuid
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from functools import partial
from typing import Optional, Union, Callable, Any, List, Tuple, Dict
from collections import defaultdict

from utils.base import Singleton


class TaskStatus(Enum):
    pending = 0  # 排队中
    running = 1  # 运行中
    done = 2  # 完成
    error = 3  # 错误


@dataclass
class TaskRecord:
    name: str  # 任务名
    status: TaskStatus  # 任务状态
    description: str  # 任务描述
    result: str = field(default=None)  # 任务返回结果
    result_ttl: int = field(default=300)  # 任务结果存续时间
    time_enter: float = field(default_factory=time.time)  # 任务提交时间
    time_start: float = field(default=None)  # 任务执行开始时间
    time_end: float = field(default=None)  # 任务执行结束时间
    on_success: Callable = field(default=None)  # 任务成功回调
    on_failure: Callable = field(default=None)  # 任务失败回调
    on_error: Callable = field(default=None)  # 异常回调

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status.value,
            "description": self.description,
            "result": self.result,
            "time_enter": self.time_enter,
            "time_start": self.time_start,
            "time_end": self.time_end,
        }


class TaskManager(metaclass=Singleton):
    """
    任务管理器

    暂时线程池撑着
    有gil锁的限制，主要耗时的都是io操作，线程的切换开销小
    用进程池直接并行，超过核心数量的进程切换开销大
    但进程后续可以配合协程进行性能优化
    """

    def __init__(self, max_num=16, internal=5):
        """
        任务管理器，单例类
        :param max_num: 线程池最大线程数量，默认16
        :type max_num: int
        :param internal: 回收过期任务的时间间隔，默认5秒
        :type internal: int
        """
        self._pool = ThreadPoolExecutor(max_workers=max_num)
        self._task_record = defaultdict()
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self.timer = threading.Thread(None, self._scheduler.run)
        self.register_sche(10, internal, self.clear_expired_task)

        self.timer.start()

    def process(self, func, *args, **kwargs):
        """
        任务管理器处理方法

        :param func: 执行函数
        :type func: function
        :param args: 函数参数
        :type args: Any
        :param kwargs: 函数具名参数
        :type kwargs: Any
        :return: 任务编号
        :rtype: str
        """
        # 解析出任务池需要的参数
        (
            func,
            timeout,
            result_ttl,
            failure_ttl,
            job_id,
            retry,
            on_success,
            on_failure,
            on_error,
            args,
            kwargs,
        ) = self.parse_args(func, *args, **kwargs)
        # 如果传入job_id已存在，需中断
        if job_id and job_id in self._task_record:
            raise ValueError
        # 放入池子，返回job_id
        res = self.en_pool(
            f=func,
            timeout=timeout,
            result_ttl=result_ttl,
            failure_ttl=failure_ttl,
            job_id=job_id,
            retry=retry,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error,
            args=args,
            kwargs=kwargs,
        )
        return res

    def process_callback(self, job_id):
        """返回一个结束回调方法，用于更新任务状态"""

        def inner(future: Future):
            if job_id not in self._task_record:  # 冗余代码，加个容错
                logging.error(f"任务id不存在，请检查{job_id}!!!")
                return
            try:
                res = future.result()
                self._task_record[job_id].status = TaskStatus.done
                if res:
                    self._task_record[job_id].result = f"{res}"
                    print(f"任务（{job_id}）执行结果：{res}")

            except Exception as e:
                logging.exception(e)
                print(f"任务（{job_id}）执行发生错误")
                self._task_record[job_id].status = TaskStatus.error
            self._task_record[job_id].time_end = time.time()
            print(f"TASK {job_id} finished")

        return inner

    def func_wrapper(self, func, job_id):
        """返回线程池执行的本体，可以在wrapper中绑定日志或其他操作"""

        def inner():
            if job_id in self._task_record:
                print(f"任务（{job_id}）开始执行")
                self._task_record[job_id].status = TaskStatus.running
                self._task_record[job_id].time_start = time.time()
            return func()

        return inner

    def get_uid_task_info(self, uid):
        """
        根据任务编号获取任务信息
        :param uid: 任务编号
        :type uid: str
        :return: 任务信息
        :rtype: dict|None
        """
        if uid in self._task_record:
            return self._task_record[uid].to_dict()
        else:
            return None

    def get_all_processing_task_info(self):
        """
        获取所有任务的信息
        :return: 所有任务信息
        :rtype: dict
        """
        res = {uid: self._task_record[uid].to_dict() for uid in self._task_record}
        return res

    def clear_expired_task(self):
        """清理过期任务信息"""
        count = []
        cur_time = time.time()
        for k, v in self._task_record.items():
            if v.status == TaskStatus.done and v.time_end + v.result_ttl < cur_time:
                count.append(k)
        for i in count:
            print(f"清理过期任务({i})信息：{self._task_record[i]}")
            del self._task_record[i]

    def register_sche(self, delay, internal, func, *args, **kwargs):
        """
        注册定时执行函数

        :param delay: 初次延时
        :type delay: int
        :param internal: 定时间隔
        :type internal: int
        :param func: 执行方法
        :type func: function
        :param args: 方法参数
        :type args: Union[Tuple, List, None]
        :param kwargs: 方法具名参数
        :type kwargs: Optional[Dict]
        """

        def wrapper():
            if internal:
                self._scheduler.enter(internal, 0, wrapper, args, kwargs)
            func(*args, **kwargs)

        self._scheduler.enter(delay, 0, wrapper, args, kwargs)

    def en_pool(
        self,
        f,
        args: Union[Tuple, List, None] = None,
        kwargs: Optional[Dict] = None,
        timeout: Optional[int] = None,
        result_ttl: Optional[int] = None,
        failure_ttl: Optional[int] = None,
        job_id: Optional[str] = None,
        retry: Optional[int] = None,
        on_success: Optional[Callable[..., Any]] = None,
        on_failure: Optional[Callable[..., Any]] = None,
        on_error: Optional[Callable[..., Any]] = None,
    ):
        """任务入池，记录任务信息"""
        if job_id is None:
            job_id = str(uuid.uuid1(threading.get_ident()))
        # 记录任务信息
        job = TaskRecord(
            name=f"{f.__module__}.{f.__qualname__}",
            status=TaskStatus.pending,
            description=f.__doc__,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error,
        )
        if result_ttl:
            job.result_ttl = result_ttl
        self._task_record[job_id] = job
        # 任务入池
        future = self._pool.submit(
            self.func_wrapper(partial(f, *args, **kwargs), job_id)
        )
        future.add_done_callback(self.process_callback(job_id))
        return job_id

    @classmethod
    def parse_args(cls, func, *args, **kwargs):
        """参数解析，新增参数理论上都加这里面, 要确保func的参数没有同名变量"""
        timeout = kwargs.pop("timeout", None)  # 方法超时时间
        result_ttl = kwargs.pop("result_ttl", None)  # 结果生存时间
        failure_ttl = kwargs.pop("failure_ttl", None)  # 失败结果生存时间
        job_id = kwargs.pop("job_id", None)  # 任务标识
        retry = kwargs.pop("retry", None)  # 重试次数
        on_success = kwargs.pop("on_success", None)  # 成功回调
        on_failure = kwargs.pop("on_failure", None)  # 失败回调
        on_stopped = kwargs.pop("on_stopped", None)  # 停止回调

        if "args" in kwargs or "kwargs" in kwargs:
            assert (
                args == ()
            ), "Extra positional arguments cannot be used when using explicit args and kwargs"  # noqa
            args = kwargs.pop("args", None)
            kwargs = kwargs.pop("kwargs", None)

        return (
            func,
            timeout,
            result_ttl,
            failure_ttl,
            job_id,
            retry,
            on_success,
            on_failure,
            on_stopped,
            args,
            kwargs,
        )


if __name__ == "__main__":
    pass
    # from flask import Flask, jsonify
    # import time
    #
    # app = Flask(__name__)
    # pool = TaskManager()
    #
    # def task(num):
    #     """测试方法"""
    #     time.sleep(2)
    #     print(num)
    #     time.sleep(2)
    #     print("end")
    #
    # @app.get("/<num>")
    # def index(num):
    #     job_id = pool.process(task, num)
    #     return jsonify({"status": "ok", "job_id": job_id})
    #
    # @app.get("/status")
    # def status():
    #     res = pool.get_all_processing_task_info()
    #     return jsonify({"status": "ok", "job_id": res})
    #
    # app.run(host="0.0.0.0", port=5000, debug=False)
