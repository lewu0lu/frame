import logging
import sys
import threading
from utils.CacheManager import CacheManager, TaskChainCache, ThreadLocalManager


class CustomOutput:
    """
    自定义输出类，用于将日志写入文件和控制台。
    """

    def __init__(self, name, is_err=False):
        """
        初始化CustomOutput实例。
        :param name: 日志记录器的名称
        :param is_err: 是否是标准错误输出
        """
        super().__init__()
        self.log_name = name
        self.is_err = is_err
        self.origin = None
        self.task_cache = CacheManager().get_cache("taskCache", default_cls=TaskChainCache, capacity=500)

    def write(self, msg: str):
        """
        重写write方法，将日志写入文件和控制台。
        :param msg: 要写入的消息
        """
        msg = msg.rstrip()
        if not len(msg):
            return
        task_id = ThreadLocalManager.get('task_id')
        if task_id is None:
            return
        logger = logging.getLogger(self.log_name)
        if self.is_err:
            import inspect
            caller = inspect.stack()[1]
            log_msg = f"{caller.filename}({caller.function} : {caller.lineno}):{msg}"
            logger.error(log_msg)
        else:
            log_msg = msg
            logger.info(log_msg)
        thread_id = threading.get_ident()
        self.task_cache.put_info(thread_id, task_id, 'log_msg', log_msg)

    def __getattr__(self, item):
        return object.__getattribute__(self.origin, item)

    def __record_std_output(self):
        """
        记录原始的标准输出或标准错误输出。
        """
        if self.is_err:
            self.origin = (
                sys.stderr
                if not isinstance(sys.stderr, CustomOutput)
                else getattr(sys.stderr, "origin")
            )
        else:
            self.origin = (
                sys.stdout
                if not isinstance(sys.stdout, CustomOutput)
                else getattr(sys.stdout, "origin")
            )

    def hijack_output(self):
        """
        重定向标准输出或标准错误输出到CustomOutput实例。
        """
        self.__record_std_output()
        if self.is_err:
            sys.stderr = self
        else:
            sys.stdout = self


def hijack_std_output(log_name, level="INFO", formatter=None, file=None):
    """
    设置日志记录器，并重定向标准输出和标准错误输出。
    :param log_name: 日志记录器的名称
    :param level: 日志级别
    :param formatter: 日志格式
    :param file: 日志文件路径
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    logger.propagate = False
    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        if formatter is None:
            formatter = logging.Formatter(
                "[%(asctime)s] - %(name)s%(thread)d - %(levelname)s - %(message)s"
            )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    info_op = CustomOutput(log_name)
    err_op = CustomOutput(log_name, is_err=True)
    info_op.hijack_output()
    err_op.hijack_output()
    if file and not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)


if __name__ == "__main__":
    hijack_std_output("test")
    ThreadLocalManager.local.task_id = 1
    print("111")
    print("222")
    raise Exception("test")
